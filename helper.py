from pathlib import Path
import re


def get_title(elements: list[dict], fallback: str) -> str:
    for el in elements:
        el_type = (el.get("type") or "").lower()
        text = (el.get("text") or "").strip()
        if el_type in {"title", "header"} and text:
            return text
    return fallback


def get_full_text(elements: list[dict]) -> str:
    parts = []
    for el in elements:
        text = (el.get("text") or "").strip()
        if text:
            parts.append(text)
    return "\n\n".join(parts)


def detect_domain(text: str) -> list[str]:
    t = text.lower()
    domain_keywords = {
        "corrosion": [
            "corrosion", "rust",
            "rouille", "corrodé", "corrodée",
        ],
        "hull": [
            "hull", "plating", "structural steel", "shell plating",
            "coque", "bordé", "tôle de bordé",
        ],
        "AOPV": [
            "aopv", "arctic offshore patrol", "harry de wolfe",
            "navire de patrouille extracôtier et de l'arctique",
            "npea", "npeaa",
        ],
        "MCDV": [
            "mcdv", "maritime coastal defence vessel",
            "navire de défense côtière",
        ],
        "HALIFAX": [
            "halifax-class", "halifax class", "ffh",
            "classe halifax",
        ],
        "submarine": [
            "victoria class", "victoria-class", "ssk", "submarine",
            "sous-marin", "sous marin",
        ],
        "NETE": [
            "nete", "test and evaluation", "trial report", "sea trial",
            "centre d'essais", "essais en mer",
        ],
        "manpower": [
            "attrition", "retention", "manning", "staffing", "personnel",
            "rétention", "dotation", "effectifs",
        ],
        "engineering": [
            "propulsion", "diesel generator", "gas turbine", "combat system",
            "propulseur", "génératrice diesel", "turbine à gaz", "système de combat",
        ],
    }

    scores: dict[str, int] = {}
    for tag, kws in domain_keywords.items():
        score = 0
        for kw in kws:
            score += t.count(kw)
        if score > 0:
            scores[tag] = score

    sorted_tags = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_tags = [tag for tag, _ in sorted_tags[:3]]
    return top_tags