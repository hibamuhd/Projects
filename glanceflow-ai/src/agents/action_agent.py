"""Agent E - Action. Validated, permission-checked, idempotent actions. Success is reported only after
the persisted state is re-read. No purchases or external actions exist by design."""
from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from src.schemas import ActionRequest, ActionResult, CatalogueItem, Constraints
from src.storage.database import Database, PersistenceError
from src.storage.repositories import DismissalRepo, EventRepo, FeedbackRepo, ShortlistRepo
from src.tools.analytics import EventLogger
from src.tools.shortlist import comparison_table


class ActionAgent:
    def __init__(self, db: Database, catalogue: list[CatalogueItem], logger: EventLogger):
        self.by_id = {i.item_id: i for i in catalogue}
        self.short, self.dis, self.fb = ShortlistRepo(db), DismissalRepo(db), FeedbackRepo(db)
        self.events = EventRepo(db)
        self.logger = logger

    def execute_raw(self, payload: dict[str, Any]) -> ActionResult:
        if str(payload.get("action", "")).lower() in {"purchase", "buy", "checkout", "order", "pay"}:
            return ActionResult(success=False, status="unsupported_action",
                                message="This prototype cannot purchase or pay for items. You can save or compare them instead.")
        try:
            req = ActionRequest(**payload)
        except ValidationError as e:
            return ActionResult(success=False, status="invalid_request", message=f"Invalid action request: {e.errors()[0]['msg']}")
        return self.execute(req)

    def execute(self, req: ActionRequest) -> ActionResult:
        unknown = [i for i in req.item_ids if i not in self.by_id]
        if unknown:
            return ActionResult(success=False, status="unknown_item", message=f"Unknown item id(s): {', '.join(unknown)}")
        try:
            return getattr(self, f"_{req.action}")(req)
        except PersistenceError as e:
            return ActionResult(success=False, status="persistence_failed", message=f"Could not save this change ({e}). Nothing was changed.")

    # --- actions -----------------------------------------------------------------------------
    def _permitted(self, req: ActionRequest) -> ActionResult | None:
        for i in req.item_ids:
            if not self.events.item_was_viewed(req.session_id, i) and not self.short.contains(i):
                return ActionResult(success=False, status="not_permitted", message="You can only act on items that were shown to you in this session.")
        return None

    def _save(self, req: ActionRequest) -> ActionResult:
        if (deny := self._permitted(req)):
            return deny
        item_id = req.item_ids[0]
        if self.short.contains(item_id):
            return ActionResult(success=True, status="already_saved", message="Already in your shortlist - nothing changed.")
        self.short.add(item_id, req.session_id, req.fit_reason)
        if not self.short.contains(item_id):  # confirm before claiming success
            return ActionResult(success=False, status="persistence_failed", message="Save could not be confirmed.")
        self.logger.log("recommendation_saved", req.session_id, item_id, {"category": self.by_id[item_id].category})
        self.logger.log("action_completed", req.session_id, item_id, {"action": "save"})
        return ActionResult(success=True, status="saved", message=f"Saved '{self.by_id[item_id].title}' to your shortlist.")

    def _unsave(self, req: ActionRequest) -> ActionResult:
        item_id = req.item_ids[0]
        if not self.short.contains(item_id):
            return ActionResult(success=True, status="not_in_shortlist", message="That item is not in your shortlist.")
        if not req.confirm:
            return ActionResult(success=False, status="confirmation_required", message="Please confirm removal from your shortlist.")
        self.short.remove(item_id)
        if self.short.contains(item_id):
            return ActionResult(success=False, status="persistence_failed", message="Removal could not be confirmed.")
        self.logger.log("action_completed", req.session_id, item_id, {"action": "unsave"})
        return ActionResult(success=True, status="removed", message="Removed from your shortlist.")

    def _dismiss(self, req: ActionRequest) -> ActionResult:
        if (deny := self._permitted(req)):
            return deny
        item_id = req.item_ids[0]
        new = self.dis.add(item_id, req.session_id)
        if not self.dis.contains(item_id):
            return ActionResult(success=False, status="persistence_failed", message="Dismissal could not be confirmed.")
        if new:
            self.logger.log("recommendation_dismissed", req.session_id, item_id, {"category": self.by_id[item_id].category})
            self.logger.log("action_completed", req.session_id, item_id, {"action": "dismiss"})
        return ActionResult(success=True, status="dismissed" if new else "already_dismissed",
                            message="Dismissed. It won't be shown again." if new else "Already dismissed.")

    def _feedback(self, req: ActionRequest) -> ActionResult:
        if req.reason is None:
            return ActionResult(success=False, status="invalid_request", message="Pick a reason for your feedback.")
        if (deny := self._permitted(req)):
            return deny
        item_id = req.item_ids[0]
        self.fb.add(req.session_id, item_id, req.reason)
        self.logger.log("feedback_submitted", req.session_id, item_id, {"reason": req.reason})
        self.logger.log("action_completed", req.session_id, item_id, {"action": "feedback"})
        return ActionResult(success=True, status="feedback_recorded", message="Thanks - feedback recorded.")

    def _compare(self, req: ActionRequest) -> ActionResult:
        if len(req.item_ids) < 2 or len(set(req.item_ids)) != len(req.item_ids):
            return ActionResult(success=False, status="invalid_request", message="Pick 2 to 4 different items to compare.")
        if (deny := self._permitted(req)):
            return deny
        sl = {r["item_id"]: r["fit_reason"] for r in self.short.all()}
        table = comparison_table([self.by_id[i] for i in req.item_ids], sl)
        self.logger.log("comparison_started", req.session_id, None, {"n_items": len(req.item_ids)})
        self.logger.log("action_completed", req.session_id, None, {"action": "compare"})
        return ActionResult(success=True, status="compared", message="Comparison ready.", data={"table": table})
