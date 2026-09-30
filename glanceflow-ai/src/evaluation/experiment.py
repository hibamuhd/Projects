"""Deterministic experiment assignment + exposure logging. No significance claims are made by this module."""
from __future__ import annotations

import hashlib

EXPERIMENTS = {
    "exp1_retrieval": ("control_keyword", "treatment_intent_ranked"),
    "exp2_cards": ("control_generic_text", "treatment_reasoned_text"),
}


def assign(session_id: str, experiment: str, salt: str = "v1") -> str:
    """Session-level, stable, roughly 50/50 assignment via hashing."""
    control, treatment = EXPERIMENTS[experiment]
    h = int(hashlib.sha256(f"{salt}:{experiment}:{session_id}".encode()).hexdigest(), 16)
    return treatment if h % 2 else control


def required_sample_per_arm(baseline_rate: float, mde_abs: float, alpha_z: float = 1.96, power_z: float = 0.84) -> int:
    """Two-proportion normal-approximation sample size per arm (planning aid only)."""
    p1, p2 = baseline_rate, baseline_rate + mde_abs
    pbar = (p1 + p2) / 2
    n = ((alpha_z * (2 * pbar * (1 - pbar)) ** 0.5 + power_z * (p1 * (1 - p1) + p2 * (1 - p2)) ** 0.5) ** 2) / (mde_abs ** 2)
    return int(n) + 1
