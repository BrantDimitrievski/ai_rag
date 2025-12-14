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
            "corrosion",
            "rust",
            "rouille",
            "corrode",
            "corrodee",
        ],
        "hull": [
            "hull",
            "plating",
            "structural steel",
            "shell plating",
            "coque",
            "bordage",
            "bordee",
        ],
        "AOPV": [
            "aopv",
            "arctic offshore patrol",
            "harry de wolfe",
            "navire de patrouille extracotier et de l'arctique",
            "npea",
            "npeaa",
        ],
        "MCDV": [
            "mcdv",
            "maritime coastal defence vessel",
            "navire de defense cotiere",
        ],
        "HALIFAX": [
            "halifax-class",
            "halifax class",
            "ffh",
            "classe halifax",
        ],
        "submarine": [
            "victoria class",
            "victoria-class",
            "ssk",
            "submarine",
            "sous-marin",
            "sous marin",
        ],
        "NETE": [
            "nete",
            "test and evaluation",
            "trial report",
            "sea trial",
            "centre d'essais",
            "essais en mer",
        ],
        "manpower": [
            "attrition",
            "retention",
            "manning",
            "staffing",
            "personnel",
            "dotation",
            "effectifs",
        ],
        "engineering": [
            "propulsion",
            "diesel generator",
            "gas turbine",
            "combat system",
            "propulseur",
            "generatrice diesel",
            "turbine a gaz",
            "systeme de combat",
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


def detect_doc_type(text: str, path: Path | None = None) -> str:
    """Heuristic doc type detection based on filename and keywords."""
    name = (path.name if path else "").lower()
    t = text.lower()

    if any(kw in name for kw in ("report", "rpt")) or "report" in t:
        return "report"
    if any(kw in name for kw in ("memo", "memorandum")) or "memo" in t:
        return "memo"
    if "presentation" in t or name.endswith((".ppt", ".pptx")):
        return "presentation"
    if "statement of work" in t or "sow" in t:
        return "statement_of_work"
    return "unknown"


def detect_year(text: str) -> int | None:
    """Return the most recent 4-digit year (1900-2099) found in the text."""
    years = [int(m.group()) for m in re.finditer(r"\b(19|20)\d{2}\b", text)]
    return max(years) if years else None
