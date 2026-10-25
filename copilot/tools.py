"""Tools the agent can use. Plain Python functions, no LLM needed for the first one."""
import re


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9+#.\s]", " ", text.lower()).strip()


def _contains(haystack: str, needle: str) -> bool:
    """Whole-word match, so 'c' does not match inside 'ci' and 'java' not inside 'javascript'."""
    if not needle:
        return False
    pattern = rf"(?<![a-z0-9+#]){re.escape(needle)}(?![a-z0-9+#])"
    return re.search(pattern, haystack) is not None


def _alternatives(requirement: str) -> list[str]:
    """'PyTorch or TensorFlow' -> ['pytorch', 'tensorflow']"""
    parts = re.split(r"\s+or\s+|/|,|;|\(|\)", requirement, flags=re.IGNORECASE)
    return [p for p in (_norm(x) for x in parts) if p]


def _matches(alt: str, skills_norm: list[str], text_norm: str) -> bool:
    in_skills = any(_contains(s, alt) or _contains(alt, s) for s in skills_norm if s)
    return in_skills or _contains(text_norm, alt)


def skill_overlap(cv_skills: list[str], required: list[str], cv_text: str = "") -> dict:
    """Rule-based check: which required skills appear in the CV (skills list or full text)."""
    skills_norm = [_norm(s) for s in cv_skills]
    text_norm = _norm(cv_text)
    matched, missing = [], []
    for req in required:
        alts = _alternatives(req)
        if any(_matches(a, skills_norm, text_norm) for a in alts):
            matched.append(req)
        else:
            missing.append(req)
    coverage = round(100 * len(matched) / len(required)) if required else 0
    return {"matched": matched, "missing": missing, "coverage_pct": coverage}


def web_search_company(company: str | None, max_results: int = 3) -> str:
    """Free web search (DuckDuckGo, no API key). Returns short notes, or '' if it fails."""
    if not company:
        return ""
    try:
        from ddgs import DDGS

        results = DDGS().text(f"{company} company about", max_results=max_results)
        return "\n".join(f"- {r.get('title', '')}: {r.get('body', '')}" for r in (results or []))
    except Exception as e:  # network problems must never crash the agent
        print(f"[tools] company search failed: {e}")
        return ""
