from __future__ import annotations

import numpy as np
import pandas as pd

from ..config import KNOWLEDGE_DIR, PROCESSED_DIR

COMPANIES_PATH = PROCESSED_DIR / "company_profiles.csv"


def _tokenize(text: str):
    return [tok for tok in text.lower().replace("/", " ").replace("-", " ").split() if tok]


class ESGRAGEngine:
    def __init__(self):
        self.docs = []
        self.sources = []
        self.doc_tokens = []
        self._load()

    def _load(self):
        for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            self.docs.append(text)
            self.sources.append(path.name)
            self.doc_tokens.append(set(_tokenize(text)))

        if COMPANIES_PATH.exists():
            companies = pd.read_csv(COMPANIES_PATH)
            for _, row in companies.iterrows():
                doc = (
                    f"Company profile for {row['company_name']} in {row['sector']}. "
                    f"Country {row['country']}. ESG score {row['esg_score']}. "
                    f"Environmental score {row['environmental_score']}. Social score {row['social_score']}. "
                    f"Governance score {row['governance_score']}. Renewable share {row['renewable_share_pct']} percent. "
                    f"Target year {row['climate_target_year']}. Controversies {row['controversies_count']}."
                )
                self.docs.append(doc)
                self.sources.append(f"company::{row['company_id']}")
                self.doc_tokens.append(set(_tokenize(doc)))

    def answer(self, question: str, company_id: str | None = None):
        q_tokens = set(_tokenize(question + (" " + company_id if company_id else "")))
        scores = []
        for tokens in self.doc_tokens:
            inter = len(q_tokens & tokens)
            union = max(len(q_tokens | tokens), 1)
            scores.append(inter / union)
        top_idx = np.argsort(scores)[::-1][:4]

        retrieved = []
        for idx in top_idx:
            snippet = self.docs[idx][:360].replace("\n", " ")
            retrieved.append(f"[{self.sources[idx]}] {snippet}")

        answer_parts = [
            "The strongest ESG posture comes from measurable targets, annual baselines, and governance ownership.",
            "A weak posture usually shows vague sustainability language, limited quantified KPIs, and unclear accountability.",
        ]
        if "risk" in question.lower():
            answer_parts.append("Main risk indicators include controversy exposure, low renewable share, weak quantified targets, and poor governance controls.")
        if "improve" in question.lower() or "action" in question.lower():
            answer_parts.append("Priority actions: increase renewable energy share, publish annual emissions progress, expand supplier tracking, and strengthen board oversight.")
        if "report" in question.lower():
            answer_parts.append("Reporting maturity improves when claims include baselines, target years, scope boundaries, and auditable evidence.")

        return {"answer": " ".join(answer_parts), "retrieved_chunks": retrieved}


_ENGINE = None

def get_engine():
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = ESGRAGEngine()
    return _ENGINE
