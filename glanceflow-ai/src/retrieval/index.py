"""Replaceable retrieval layer. Baseline: BM25 over weighted catalogue fields (no external deps)."""
from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Protocol

from src.schemas import CatalogueItem
from src.utils.text import tokenize


class Retriever(Protocol):
    def search(self, query_tokens: list[str], allowed_ids: set[str] | None = None, k: int = 50) -> list[tuple[str, float]]: ...


class BM25Retriever:
    K1, B = 1.5, 0.75

    def __init__(self, items: list[CatalogueItem]):
        self.ids = [i.item_id for i in items]
        self.postings: dict[str, dict[int, int]] = defaultdict(dict)
        self.lengths: list[int] = []
        for idx, it in enumerate(items):
            toks = (tokenize(it.title) * 3 + tokenize(" ".join(it.tags)) * 3 + tokenize(it.subcategory) * 2
                    + tokenize(it.category) + tokenize(" ".join(it.audience)) + tokenize(it.description))
            self.lengths.append(len(toks))
            for t, c in Counter(toks).items():
                self.postings[t][idx] = c
        self.n = len(items)
        self.avg_len = (sum(self.lengths) / self.n) if self.n else 1.0
        self.pos = {iid: i for i, iid in enumerate(self.ids)}

    def vocabulary(self) -> set[str]:
        return set(self.postings)

    def search(self, query_tokens, allowed_ids=None, k=50):
        scores: dict[int, float] = defaultdict(float)
        allowed = None if allowed_ids is None else {self.pos[i] for i in allowed_ids if i in self.pos}
        for t in set(query_tokens):
            post = self.postings.get(t)
            if not post:
                continue
            df = len(post)
            idf = math.log(1 + (self.n - df + 0.5) / (df + 0.5))
            for idx, tf in post.items():
                if allowed is not None and idx not in allowed:
                    continue
                denom = tf + self.K1 * (1 - self.B + self.B * self.lengths[idx] / self.avg_len)
                scores[idx] += idf * tf * (self.K1 + 1) / denom
        ranked = sorted(scores.items(), key=lambda kv: (-kv[1], self.ids[kv[0]]))[:k]
        return [(self.ids[i], s) for i, s in ranked]
