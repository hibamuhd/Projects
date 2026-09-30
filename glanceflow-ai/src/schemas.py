"""Typed contracts between agents, tools, storage and UI."""
from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

Availability = Literal["in_stock", "low_stock", "out_of_stock"]


class CatalogueItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    item_id: str = Field(min_length=3)
    title: str = Field(min_length=2)
    category: str = Field(min_length=2)
    subcategory: str = Field(min_length=2)
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    price_inr: float = Field(gt=0)
    audience: list[str] = Field(default_factory=list)
    attributes: dict[str, Any] = Field(default_factory=dict)
    availability: Availability
    image_url: str = ""
    source: str = "synthetic"
    quality_flags: list[str] = Field(default_factory=list)


class Constraints(BaseModel):
    """Structured request. Hard constraints: category (UI filter), budget, exclusions,
    availability. Everything else is a soft preference."""
    category: Optional[str] = None
    budget_min: Optional[float] = Field(default=None, ge=0)
    budget_max: Optional[float] = Field(default=None, ge=0)
    interests: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    recipient: Optional[str] = None
    occasion: Optional[str] = None
    exclusions: list[str] = Field(default_factory=list)
    preferred_attributes: list[str] = Field(default_factory=list)
    avoid_generic: bool = False
    is_gift: bool = False

    @field_validator("interests", "keywords", "exclusions", "preferred_attributes")
    @classmethod
    def _dedupe(cls, v: list[str]) -> list[str]:
        seen, out = set(), []
        for x in v:
            x = x.strip().lower()
            if x and x not in seen:
                seen.add(x)
                out.append(x)
        return out


class IntentResult(BaseModel):
    constraints: Constraints
    needs_clarification: bool = False
    clarification_question: Optional[str] = None
    conflicts: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    unsupported_action: Optional[str] = None
    source: Literal["rules", "llm", "rules_fallback"] = "rules"


class Candidate(BaseModel):
    item: CatalogueItem
    retrieval_score: float


class RankedItem(BaseModel):
    item: CatalogueItem
    score: float
    components: dict[str, float]
    reasons: list[str]
    budget_status: str


class VerificationIssue(BaseModel):
    code: str
    item_id: Optional[str] = None
    message: str
    severity: Literal["hard", "soft"] = "hard"


class VerificationReport(BaseModel):
    passed: bool
    issues: list[VerificationIssue] = Field(default_factory=list)
    checked_count: int = 0
    removed_ids: list[str] = Field(default_factory=list)
    needs_revision: bool = False
    audit_only: bool = False


class TraceStep(BaseModel):
    stage: str
    tool: str
    status: Literal["ok", "warning", "failed", "skipped"] = "ok"
    duration_ms: float = 0.0
    summary: str = ""


class Recommendation(BaseModel):
    rank: int
    item: CatalogueItem
    score: float
    explanation: str
    generic_text: str
    reasons: list[str]
    budget_status: str
    checks: dict[str, bool]


WorkflowStatus = Literal["ok", "needs_clarification", "unsupported", "no_results", "fallback", "error"]


class WorkflowRequest(BaseModel):
    query: str = ""
    session_id: str
    category_filter: Optional[str] = None
    budget_filter: Optional[float] = None
    previous_constraints: Optional[Constraints] = None
    refine_text: Optional[str] = None
    previous_max_price: Optional[float] = None
    retrieval_arm: Literal["treatment", "control"] = "treatment"
    card_arm: Literal["treatment", "control"] = "treatment"
    use_llm: bool = False
    excluded_ids: list[str] = Field(default_factory=list)


class WorkflowResult(BaseModel):
    run_id: str
    status: WorkflowStatus
    message: str = ""
    intent: Optional[IntentResult] = None
    recommendations: list[Recommendation] = Field(default_factory=list)
    verification: Optional[VerificationReport] = None
    initial_verification_failed: bool = False
    pre_verification_violations: int = 0
    trace: list[TraceStep] = Field(default_factory=list)
    revisions: int = 0
    latency_ms: float = 0.0
    llm_used: bool = False
    input_tokens: int = 0
    output_tokens: int = 0
    est_cost_usd: Optional[float] = None
    constraints: Optional[Constraints] = None


ActionName = Literal["save", "unsave", "dismiss", "compare", "feedback"]
FeedbackReason = Literal["irrelevant", "too_expensive", "not_my_style", "already_have", "other"]


class ActionRequest(BaseModel):
    action: ActionName
    session_id: str
    item_ids: list[str] = Field(min_length=1, max_length=4)
    confirm: bool = False
    reason: Optional[FeedbackReason] = None
    fit_reason: str = ""


class ActionResult(BaseModel):
    success: bool
    status: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
