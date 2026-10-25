"""Evaluation helpers: rule-based checks, an LLM judge, and result summaries."""
import re

from copilot.llm import chat_structured
from copilot.schemas import JudgeResult


def numbers_in(text: str) -> set[str]:
    return set(re.findall(r"\d+(?:[.,]\d+)*", text))


def unsupported_numbers(letter: str, *sources: str) -> list[str]:
    """Numbers in the letter that appear in none of the sources: a cheap hallucination alarm."""
    allowed: set[str] = set()
    for s in sources:
        allowed |= numbers_in(s)
    return sorted(n for n in numbers_in(letter) if n not in allowed)


def check_case(expect: dict, score: int, letter_body: str | None, cv_text: str, job_text: str) -> dict:
    want_letter = expect.get("letter")
    written = letter_body is not None
    return {
        "band_ok": expect["min_score"] <= score <= expect["max_score"],
        "letter_written": written,
        "letter_ok": None if want_letter is None else (written == want_letter),
        "unsupported_numbers": unsupported_numbers(letter_body, cv_text, job_text) if written else [],
    }


JUDGE_SYSTEM = (
    "You are a strict evaluator of cover letters. You get the candidate CV, the job description "
    "and the letter. Score relevance, honesty and tone from 1 to 5. Honesty is 5 ONLY if every claim "
    "in the letter is supported by the CV; deduct heavily for invented experience, skills or numbers."
)


def judge_cover_letter(cv_text: str, job_text: str, letter_body: str) -> JudgeResult:
    user = f"CV:\n{cv_text}\n\nJOB:\n{job_text}\n\nCOVER LETTER:\n{letter_body}"
    return chat_structured(JUDGE_SYSTEM, user, JudgeResult)


def _avg(values: list) -> float | None:
    values = [v for v in values if v is not None]
    return round(sum(values) / len(values), 2) if values else None


def summarize(results: list[dict]) -> dict:
    ok = [r for r in results if not r.get("error")]
    judged = [r["judge"] for r in ok if r.get("judge")]
    letter_checks = [r["letter_ok"] for r in ok if r.get("letter_ok") is not None]
    return {
        "cases": len(results),
        "errors": len(results) - len(ok),
        "band_pass_rate": _avg([1 if r["band_ok"] else 0 for r in ok]),
        "letter_routing_pass_rate": _avg([1 if v else 0 for v in letter_checks]),
        "letters_with_unsupported_numbers": sum(1 for r in ok if r["unsupported_numbers"]),
        "avg_relevance": _avg([j["relevance"] for j in judged]),
        "avg_honesty": _avg([j["honesty"] for j in judged]),
        "avg_tone": _avg([j["tone"] for j in judged]),
        "avg_seconds": _avg([r["seconds"] for r in ok]),
    }


def _yn(value) -> str:
    return "-" if value is None else ("pass" if value else "FAIL")


def results_to_markdown(results: list[dict], summary: dict, model: str) -> str:
    lines = [
        "# Evaluation results",
        f"\nModel: `{model}`. Web search is disabled during evals so runs are repeatable.\n",
        "| Case | Score | Expected | In band | Letter routing | Unsupported numbers | Judge (rel/honest/tone) | Seconds |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        exp = f"{r['expect']['min_score']}-{r['expect']['max_score']}"
        if r.get("error"):
            lines.append(f"| {r['id']} | error | {exp} | - | - | - | - | - |")
            continue
        j = r.get("judge")
        judge = f"{j['relevance']}/{j['honesty']}/{j['tone']}" if j else "-"
        nums = ", ".join(r["unsupported_numbers"]) or "none"
        lines.append(
            f"| {r['id']} | {r['score']} | {exp} | {_yn(r['band_ok'])} | {_yn(r['letter_ok'])} "
            f"| {nums} | {judge} | {r['seconds']} |"
        )
    lines += [
        "\n## Summary",
        f"- Cases run: {summary['cases']} (errors: {summary['errors']})",
        f"- Score in expected band: {summary['band_pass_rate']}",
        f"- Cover-letter routing correct: {summary['letter_routing_pass_rate']}",
        f"- Letters with unsupported numbers: {summary['letters_with_unsupported_numbers']}",
        f"- Judge averages (1-5): relevance {summary['avg_relevance']}, "
        f"honesty {summary['avg_honesty']}, tone {summary['avg_tone']}",
        f"- Average seconds per case: {summary['avg_seconds']}",
    ]
    return "\n".join(lines) + "\n"
