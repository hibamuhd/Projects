"""Stateful orchestration: intent -> discover -> rank -> verify -> (one bounded revision) -> explain.
Every transition goes through WorkflowState.go(), so illegal or runaway flows raise instead of looping."""
from __future__ import annotations

import time
import uuid
from typing import Optional

from src.agents.critic_agent import CriticAgent
from src.agents.discovery_agent import DiscoveryAgent
from src.agents.intent_agent import IntentAgent, parse_refinement
from src.agents.ranking_agent import RankingAgent, explain, generic_description, template_explanation
from src.config import Settings
from src.llm import LLMClient
from src.orchestration.state import Stage, StepLimitExceeded, WorkflowState
from src.retrieval.index import BM25Retriever, Retriever
from src.schemas import (CatalogueItem, Constraints, IntentResult, Recommendation, WorkflowRequest, WorkflowResult)
from src.storage.database import Database, PersistenceError
from src.storage.repositories import DismissalRepo, PreferenceRepo, interaction_profile
from src.tools.analytics import EventLogger
from src.tools.preference_store import remember_explicit
from src.utils.cost_tracking import CostTracker
from src.utils.logging_config import get_logger

log = get_logger("workflow")


class DiscoveryWorkflow:
    def __init__(self, settings: Settings, catalogue: list[CatalogueItem], db: Database,
                 llm: Optional[LLMClient] = None, retriever: Optional[Retriever] = None):
        self.s, self.catalogue, self.db, self.llm = settings, catalogue, db, llm
        self.by_id = {i.item_id: i for i in catalogue}
        self.retriever = retriever or BM25Retriever(catalogue)
        self.intent_agent = IntentAgent(llm, settings.max_retries, settings.llm_timeout_s)
        self.discovery = DiscoveryAgent(self.retriever, catalogue)
        self.ranking = RankingAgent(settings.top_n)
        self.critic = CriticAgent(catalogue, settings.min_relevance, settings.min_results)
        self.logger = EventLogger(db)

    # ------------------------------------------------------------------------------------------
    def run(self, req: WorkflowRequest) -> WorkflowResult:
        t0 = time.perf_counter()
        run_id = uuid.uuid4().hex[:12]
        st = WorkflowState(max_steps=self.s.max_workflow_steps)
        cost = CostTracker(self.s.price_in_per_mtok, self.s.price_out_per_mtok)
        llm = self.llm if (req.use_llm and self.llm is not None) else None
        is_refine = bool(req.refine_text and req.previous_constraints)
        text = req.refine_text if is_refine else req.query
        self.logger.log("query_submitted", req.session_id, run_id, {"is_refinement": is_refine, "category_filter": req.category_filter,
                                                                    "has_budget_filter": req.budget_filter is not None, "query_chars": len(text or "")})
        if is_refine:
            self.logger.log("query_refined", req.session_id, run_id, {})
        try:
            result = self._run(req, st, run_id, text or "", is_refine, llm, cost)
        except StepLimitExceeded as e:
            log.error("workflow aborted: %s", e)
            result = WorkflowResult(run_id=run_id, status="error", message="The request could not be completed safely. Please try rephrasing.", trace=st.trace)
        except Exception as e:  # noqa: BLE001 - never surface a stack trace or fake success to the user
            log.exception("workflow failure")
            result = WorkflowResult(run_id=run_id, status="error", message="Something went wrong while searching. Nothing was saved.", trace=st.trace)
            st.record("error", type(e).__name__, time.perf_counter(), "Unhandled error converted to a safe failure", "failed")
            result.trace = st.trace
        result.latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        result.revisions = st.revisions
        result.input_tokens, result.output_tokens = cost.input_tokens, cost.output_tokens
        result.est_cost_usd = cost.estimated_cost_usd()
        result.llm_used = llm is not None and (cost.input_tokens + cost.output_tokens) > 0
        self._log_outcome(req, result, is_refine)
        return result

    # ------------------------------------------------------------------------------------------
    def _run(self, req: WorkflowRequest, st: WorkflowState, run_id: str, text: str, is_refine: bool, llm, cost: CostTracker) -> WorkflowResult:
        # ---- Stage 1: intent ----
        t = time.perf_counter()
        if is_refine:
            ref_price = req.previous_max_price
            intent: IntentResult = parse_refinement(text, req.previous_constraints, ref_price)  # type: ignore[arg-type]
            if req.category_filter:
                intent.constraints.category = req.category_filter
            if req.budget_filter is not None:
                intent.constraints.budget_max = req.budget_filter
        else:
            agent = IntentAgent(llm, self.s.max_retries, self.s.llm_timeout_s)
            intent = agent.run(text, req.category_filter, req.budget_filter, cost)
        c = intent.constraints
        st.record("intent", "IntentAgent." + intent.source, t, self._intent_summary(intent))
        discovery_signal = bool(c.interests or c.keywords or c.category)
        if intent.unsupported_action and not discovery_signal:
            st.go(Stage.REFUSE)
            st.go(Stage.DONE)
            return WorkflowResult(run_id=run_id, status="unsupported", intent=intent, constraints=c, trace=st.trace,
                                  message="I can't buy or pay for items in this prototype - it only helps you discover, save and compare. Tell me what you're looking for and I'll find options.")
        if intent.needs_clarification:
            st.go(Stage.CLARIFY)
            st.go(Stage.DONE)
            return WorkflowResult(run_id=run_id, status="needs_clarification", intent=intent, constraints=c, trace=st.trace,
                                  message=intent.clarification_question or "Could you tell me a bit more?")
        st.go(Stage.DISCOVER)

        # ---- Stage 2-4: discover -> rank -> verify (with one bounded revision) ----
        excluded = set(req.excluded_ids) | DismissalRepo(self.db).ids() if self._db_ok() else set(req.excluded_ids)
        profile = interaction_profile(self.db, self.by_id) if self._db_ok() else {}
        control = req.retrieval_arm == "control" and not is_refine
        relax = 0
        kept: list = []
        report = None
        initial_failed = False
        pre_violations = 0
        while True:
            t = time.perf_counter()
            if control:
                out = self.discovery.run_baseline(text, k=self.s.top_n)
            else:
                out = self.discovery.run(c, relax=relax, excluded_ids=excluded)
            st.record("discover", "search_catalogue" + ("+relaxed" if relax else "") if not control else "keyword_baseline", t,
                      f"pool={out.pool_size} candidates={len(out.candidates)} dupes_dropped={len(out.dropped_duplicates)}")
            if not out.candidates:
                if st.revisions < self.s.max_revisions and not control:
                    st.go(Stage.REVISE); st.revisions += 1; relax += 1
                    st.record("revise", "relax_query", time.perf_counter(), "No candidates; broadening interests to related themes (budget stays hard)", "warning")
                    st.go(Stage.DISCOVER)
                    continue
                st.go(Stage.EMPTY); st.go(Stage.DONE)
                return WorkflowResult(run_id=run_id, status="no_results", intent=intent, constraints=c, trace=st.trace, initial_verification_failed=initial_failed,
                                      message=self._empty_message(c))
            st.go(Stage.RANK)
            t = time.perf_counter()
            if control:
                ranked = self.ranking.rank_baseline(out.candidates, c)
                full = ranked
            else:
                ranked, full = self.ranking.run(out.candidates, c, profile)
            st.record("rank", "RankingAgent" if not control else "keyword_order", t, f"scored={len(full)} selected={len(ranked)}")
            st.go(Stage.VERIFY)
            t = time.perf_counter()
            kept, report = self.critic.run(ranked, c, audit_only=control)
            hard = [i for i in report.issues if i.severity == "hard"]
            if st.revisions == 0:
                pre_violations = len({i.item_id for i in hard if i.item_id})
                initial_failed = bool(hard) or report.needs_revision
            if hard:
                self.logger.log("agent_verification_failed", req.session_id, run_id, {"codes": sorted({i.code for i in hard}), "removed": len(report.removed_ids), "audit_only": control})
            st.record("verify", "CriticAgent(audit)" if control else "CriticAgent", t,
                      f"checked={report.checked_count} hard_issues={len(hard)} removed={len(report.removed_ids)} passed={report.passed}",
                      "ok" if report.passed else "warning")
            if report.needs_revision and st.revisions < self.s.max_revisions:
                st.go(Stage.REVISE); st.revisions += 1; relax += 1
                st.record("revise", "relax_query", time.perf_counter(), "Too few verified results; one bounded revision with broader related themes", "warning")
                st.go(Stage.DISCOVER)
                continue
            break

        status = "ok"
        message = ""
        if not report.passed:
            st.go(Stage.FALLBACK)
            if not kept:
                st.go(Stage.EMPTY); st.go(Stage.DONE)
                return WorkflowResult(run_id=run_id, status="no_results", intent=intent, constraints=c, trace=st.trace, verification=report,
                                      initial_verification_failed=True, pre_verification_violations=pre_violations, message=self._empty_message(c))
            status = "fallback"
            message = f"Only {len(kept)} option(s) passed verification. Showing what I could verify - try widening your budget or interests for more."
            st.go(Stage.EXPLAIN)
        else:
            st.go(Stage.EXPLAIN)

        # ---- Stage 5: explain (grounded) ----
        t = time.perf_counter()
        recs: list[Recommendation] = []
        used_llm = 0
        for n, r in enumerate(kept, 1):
            text_exp, used = explain(r, c, llm, cost, self.s.max_retries, self.s.llm_timeout_s) if not control else (template_explanation(r), False)
            used_llm += int(used)
            checks = {"within_budget": r.budget_status != "over budget", "in_stock": r.item.availability != "out_of_stock",
                      "verified_against_catalogue": True}
            recs.append(Recommendation(rank=n, item=r.item, score=r.score, explanation=text_exp, generic_text=generic_description(r),
                                       reasons=r.reasons, budget_status=r.budget_status, checks=checks))
        st.record("explain", "ranking_agent.explain", t, f"{len(recs)} explanations ({used_llm} LLM-written, rest template)")
        st.go(Stage.DONE)
        return WorkflowResult(run_id=run_id, status=status, message=message, intent=intent, constraints=c, recommendations=recs,
                              verification=report, initial_verification_failed=initial_failed, pre_verification_violations=pre_violations, trace=st.trace)

    # ------------------------------------------------------------------------------------------
    def _db_ok(self) -> bool:
        try:
            with self.db.connect() as c:
                c.execute("SELECT 1")
            return True
        except PersistenceError:
            return False

    @staticmethod
    def _intent_summary(i: IntentResult) -> str:
        c = i.constraints
        parts = [f"budget<=₹{int(c.budget_max):,}" if c.budget_max else "no budget", f"interests={c.interests or '-'}",
                 f"prefs={c.preferred_attributes or '-'}", f"exclude={c.exclusions or '-'}"]
        if i.needs_clarification:
            parts.append("needs clarification")
        if i.unsupported_action:
            parts.append(f"unsupported:{i.unsupported_action}")
        return "; ".join(parts) + f" [{i.source}]"

    @staticmethod
    def _empty_message(c: Constraints) -> str:
        bits = []
        if c.budget_max:
            bits.append(f"a maximum of ₹{int(c.budget_max):,}")
        if c.interests:
            bits.append("interests: " + ", ".join(c.interests))
        if c.exclusions:
            bits.append("excluding " + ", ".join(c.exclusions))
        return ("Nothing in the catalogue matched " + ("; ".join(bits) if bits else "that request") +
                ". Try raising the budget, removing an exclusion, or describing the interest differently.")

    def _log_outcome(self, req: WorkflowRequest, r: WorkflowResult, is_refine: bool) -> None:
        if r.status == "needs_clarification":
            self.logger.log("clarification_requested", req.session_id, r.run_id, {"conflicts": len(r.intent.conflicts) if r.intent else 0})
            return
        final_viol = sum(1 for x in r.recommendations if not all(x.checks.values()))
        c = r.constraints
        self.logger.log("results_generated", req.session_id, r.run_id, {
            "status": r.status, "n_results": len(r.recommendations), "latency_ms": r.latency_ms, "revisions": r.revisions,
            "llm_used": r.llm_used, "est_cost_usd": r.est_cost_usd, "input_tokens": r.input_tokens, "output_tokens": r.output_tokens,
            "pre_verification_violations": r.pre_verification_violations, "final_violations": final_viol,
            "retrieval_arm": req.retrieval_arm, "card_arm": req.card_arm, "has_budget": bool(c and c.budget_max), "is_refinement": is_refine})
        for x in r.recommendations:
            self.logger.log("recommendation_viewed", req.session_id, x.item.item_id, {"rank": x.rank, "run_id": r.run_id})
        if r.status in ("ok", "fallback") and c is not None:
            try:
                remember_explicit(PreferenceRepo(self.db), c)
            except PersistenceError:
                log.warning("preferences not stored")
