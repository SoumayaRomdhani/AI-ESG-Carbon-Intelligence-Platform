from __future__ import annotations

import re


ENV_KEYWORDS = {
    "emissions", "carbon", "co2", "renewable", "energy", "waste", "water",
    "decarbonization", "climate", "scope 1", "scope 2", "scope 3", "net zero",
}
SOC_KEYWORDS = {
    "safety", "workers", "training", "diversity", "inclusion", "community",
    "human rights", "employees", "well-being", "equity",
}
GOV_KEYWORDS = {
    "board", "audit", "compliance", "ethics", "governance", "anti-corruption",
    "oversight", "risk committee", "controls", "policy",
}
VAGUE_TERMS = {
    "leading", "committed", "ambition", "aspire", "world-class", "best-in-class",
    "aim", "vision", "responsible", "future-ready", "sustainable journey",
}
MEASURABLE_PATTERNS = [
    r"\b\d+(\.\d+)?\s?%",
    r"\b\d{4}\b",
    r"\b\d+(\.\d+)?\s?(tco2e|tons|mwh|kwh|hours|employees|injuries)\b",
]
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def analyze_text(text: str) -> dict:
    sentences = [_normalize(s) for s in SENTENCE_SPLIT.split(text) if _normalize(s)]
    if not sentences:
        raise ValueError("Empty or invalid report text.")

    env_hits, soc_hits, gov_hits = [], [], []
    measurable_kpis, commitments, red_flags, evidence = [], [], [], []

    vague_count = 0
    measurable_count = 0

    for sentence in sentences:
        s_lower = sentence.lower()
        is_env = any(k in s_lower for k in ENV_KEYWORDS)
        is_soc = any(k in s_lower for k in SOC_KEYWORDS)
        is_gov = any(k in s_lower for k in GOV_KEYWORDS)

        meas = sum(1 for pattern in MEASURABLE_PATTERNS if re.search(pattern, s_lower))
        if meas:
            measurable_count += 1
            measurable_kpis.append(sentence)

        if any(term in s_lower for term in VAGUE_TERMS):
            vague_count += 1

        if "target" in s_lower or "commit" in s_lower or "by 20" in s_lower or "will" in s_lower:
            commitments.append(sentence)

        if is_env:
            env_hits.append(sentence)
            evidence.append({"sentence": sentence, "label": "environment", "score": round(0.55 + 0.15 * meas, 2)})
        if is_soc:
            soc_hits.append(sentence)
            evidence.append({"sentence": sentence, "label": "social", "score": round(0.55 + 0.10 * meas, 2)})
        if is_gov:
            gov_hits.append(sentence)
            evidence.append({"sentence": sentence, "label": "governance", "score": round(0.55 + 0.10 * meas, 2)})

        if ("net zero" in s_lower or "carbon neutral" in s_lower) and not meas:
            red_flags.append(f"Claim may be insufficiently quantified: {sentence}")
        if "sustainable" in s_lower and not meas and not (is_env or is_soc or is_gov):
            red_flags.append(f"Vague sustainability wording: {sentence}")

    env_score = min(100.0, 35 + len(env_hits) * 5 + measurable_count * 1.8)
    soc_score = min(100.0, 35 + len(soc_hits) * 5 + measurable_count * 1.2)
    gov_score = min(100.0, 35 + len(gov_hits) * 5 + measurable_count * 1.1)
    greenwashing_risk = min(100.0, max(5.0, vague_count * 9 - measurable_count * 4 + len(red_flags) * 7))
    overall_score = round(0.45 * env_score + 0.25 * soc_score + 0.30 * gov_score - 0.12 * greenwashing_risk, 1)

    evidence = sorted(evidence, key=lambda x: x["score"], reverse=True)[:10]

    return {
        "overall_score": round(overall_score, 1),
        "environment_score": round(env_score, 1),
        "social_score": round(soc_score, 1),
        "governance_score": round(gov_score, 1),
        "greenwashing_risk": round(greenwashing_risk, 1),
        "commitments": list(dict.fromkeys(commitments))[:8],
        "measurable_kpis": list(dict.fromkeys(measurable_kpis))[:8],
        "red_flags": list(dict.fromkeys(red_flags))[:8],
        "evidence": evidence,
    }
