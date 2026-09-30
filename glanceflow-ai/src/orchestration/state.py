"""Explicit workflow state machine. Illegal transitions raise; total steps are capped."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

from src.schemas import TraceStep


class Stage(str, Enum):
    INTENT = "intent"
    CLARIFY = "clarify"
    REFUSE = "refuse"
    DISCOVER = "discover"
    RANK = "rank"
    VERIFY = "verify"
    REVISE = "revise"
    EXPLAIN = "explain"
    FALLBACK = "fallback"
    EMPTY = "empty"
    DONE = "done"


TRANSITIONS: dict[Stage, set[Stage]] = {
    Stage.INTENT: {Stage.CLARIFY, Stage.REFUSE, Stage.DISCOVER},
    Stage.DISCOVER: {Stage.RANK, Stage.REVISE, Stage.EMPTY},
    Stage.RANK: {Stage.VERIFY},
    Stage.VERIFY: {Stage.REVISE, Stage.EXPLAIN, Stage.FALLBACK, Stage.EMPTY},
    Stage.REVISE: {Stage.DISCOVER},
    Stage.EXPLAIN: {Stage.DONE},
    Stage.FALLBACK: {Stage.EXPLAIN, Stage.EMPTY},
    Stage.CLARIFY: {Stage.DONE}, Stage.REFUSE: {Stage.DONE}, Stage.EMPTY: {Stage.DONE}, Stage.DONE: set(),
}


class InvalidTransition(RuntimeError):
    pass


class StepLimitExceeded(RuntimeError):
    pass


@dataclass
class WorkflowState:
    max_steps: int = 12
    stage: Stage = Stage.INTENT
    steps: int = 0
    revisions: int = 0
    history: list[Stage] = field(default_factory=lambda: [Stage.INTENT])
    trace: list[TraceStep] = field(default_factory=list)

    def go(self, nxt: Stage) -> None:
        if nxt not in TRANSITIONS[self.stage]:
            raise InvalidTransition(f"{self.stage.value} -> {nxt.value}")
        self.steps += 1
        if self.steps > self.max_steps:
            raise StepLimitExceeded(f"exceeded {self.max_steps} workflow steps")
        self.stage = nxt
        self.history.append(nxt)

    def record(self, stage: str, tool: str, started: float, summary: str, status: str = "ok") -> None:
        self.trace.append(TraceStep(stage=stage, tool=tool, status=status,  # type: ignore[arg-type]
                                    duration_ms=round((time.perf_counter() - started) * 1000, 2), summary=summary))
