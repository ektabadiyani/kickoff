"""Check that every quote Claude attributes to the contract actually appears in it.

Language models can paraphrase or invent a supporting quote. A plan is only trustworthy
if each requirement points at words the customer actually signed, so every quote is
matched against the source text before anything is planned from it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from enum import StrEnum

from .models import ContractExtract, Source

APPROXIMATE_THRESHOLD = 0.85


class Match(StrEnum):
    VERIFIED = "verified"        # appears word for word (ignoring case, punctuation style and formatting)
    APPROXIMATE = "approximate"  # a close variant appears; worth a glance
    NOT_FOUND = "not_found"      # nothing like it in the contract; treat the item as unsupported


_REPLACEMENTS = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"',
                               "–": "-", "—": "-", " ": " "})


def normalise(text: str) -> str:
    text = text.translate(_REPLACEMENTS).lower()
    text = re.sub(r"[*_#>`]", "", text)          # Markdown emphasis and headings
    text = re.sub(r"\[page \d+\]", " ", text)    # page markers added to PDFs
    return re.sub(r"\s+", " ", text).strip()


@dataclass(frozen=True)
class TraceResult:
    item_id: str
    kind: str
    section: str
    quote: str
    match: Match
    similarity: float


class Tracer:
    def __init__(self, document: str):
        self.document = normalise(document)
        self.words = self.document.split(" ")

    def check(self, quote: str) -> tuple[Match, float]:
        q = normalise(quote).strip(" .;:,\"'")
        if not q:
            return Match.NOT_FOUND, 0.0
        if q in self.document:
            return Match.VERIFIED, 1.0
        best = self._best_window(q)
        return (Match.APPROXIMATE if best >= APPROXIMATE_THRESHOLD else Match.NOT_FOUND), best

    def _best_window(self, quote: str) -> float:
        n = len(quote.split(" "))
        best = 0.0
        matcher = SequenceMatcher(autojunk=False)
        matcher.set_seq2(quote)
        for start in range(0, max(1, len(self.words) - n + 1)):
            matcher.set_seq1(" ".join(self.words[start:start + n]))
            if matcher.real_quick_ratio() <= best or matcher.quick_ratio() <= best:
                continue
            best = max(best, matcher.ratio())
        return best


def trace_extract(extract: ContractExtract, document: str) -> list[TraceResult]:
    tracer = Tracer(document)
    items: list[tuple[str, str, Source]] = (
        [(r.id, "requirement", r.source) for r in extract.requirements]
        + [(c.id, "customer dependency", c.source) for c in extract.customer_dependencies]
        + [(k.id, "risk", k.source) for k in extract.risks]
        + [(f"M{i}", "milestone", m.source) for i, m in enumerate(extract.milestones, start=1)]
        + [(f"X{i}", "exclusion", s) for i, s in enumerate(extract.out_of_scope, start=1)]
        + [(f"P{i}", "payment term", p.source) for i, p in enumerate(extract.payment_terms, start=1)]
    )
    results = []
    for item_id, kind, source in items:
        match, similarity = tracer.check(source.quote)
        results.append(TraceResult(item_id, kind, source.section, source.quote, match, round(similarity, 3)))
    return results
