from pathlib import Path
import re


def get_title(elements: list[dict], fallback: str) -> str:
    """Use first Title-like element, else fallback (e.g. filename)."""
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
    """
    Choose up to top 3 domain tags based on keyword hits.
    Example tags: corrosion, hull, AOPV, MCDV, HALIFAX, NETE, manpower, etc.
    """
    t = text.lower()

    domain_keywords = {
        "corrosion": ["corrosion", "rust"],
        "hull": ["hull", "plating", "structural steel", "shell plating"],
        "AOPV": ["aopv", "arctic offshore patrol", "harry de wolfe"],
        "MCDV": ["mcdv", "maritime coastal defence vessel"],
        "HALIFAX": ["halifax-class", "halifax class", "ffh"],
        "submarine": ["victoria class", "victoria-class", "ssk", "submarine"],
        "NETE": ["nete", "test and evaluation", "trial report", "sea trial"],
        "manpower": ["attrition", "retention", "manning", "staffing", "personnel"],
        "engineering": ["propulsion", "diesel generator", "gas turbine", "combat system"],
    }

    scores = {}
    for tag, kws in domain_keywords.items():
        score = 0
        for kw in kws:
            score += t.count(kw)
        if score > 0:
            scores[tag] = score

    # sort by score desc and keep top 3
    sorted_tags = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_tags = [tag for tag, _ in sorted_tags[:3]]

    return top_tags


def detect_doc_type(text: str, file_path: Path) -> str:
    """Very simple doc_type classification."""
    t = text.lower()

    # file extension hints
    ext = file_path.suffix.lower()
    if ext in {".ppt", ".pptx"}:
        return "presentation"

    # text-based hints
    if "briefing note" in t or "briefing" in t:
        return "briefing"
    if "technical assessment" in t or "technical analysis" in t:
        return "technical_analysis"
    if "research objectives" in t or "literature review" in t or "methodology" in t:
        return "research"
    if "report" in t or "executive summary" in t:
        return "report"

    return "other"


def detect_year(text: str) -> int:
    """
    Find a year like 2010–2099 in the text; return first one as int.
    """
    years = re.findall(r"\b(20[0-9]{2})\b", text)
    if years:
        try:
            return int(years[0])
        except ValueError:
            return None
    return None