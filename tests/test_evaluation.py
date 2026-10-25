import json
from pathlib import Path

from copilot.evaluation import check_case, numbers_in, results_to_markdown, summarize, unsupported_numbers
from copilot.llm import clean_text
from copilot.tools import skill_overlap

CASES = json.loads((Path(__file__).resolve().parent.parent / "evals" / "cases.json").read_text(encoding="utf-8"))


def test_numbers_in():
    assert numbers_in("89.33% on 1.52 M samples in 2026") == {"89.33", "1.52", "2026"}


def test_unsupported_numbers_flags_invented_figures():
    cv = "Reached 91% accuracy on 3 projects"
    letter = "I reached 91% accuracy and 99% recall on 3 projects"
    assert unsupported_numbers(letter, cv, "job text") == ["99"]


def test_check_case_band_and_routing():
    expect = {"min_score": 70, "max_score": 100, "letter": True}
    ok = check_case(expect, 85, "Dear X, 91%", "91% cv", "job")
    assert ok["band_ok"] and ok["letter_ok"] and ok["unsupported_numbers"] == []
    bad = check_case(expect, 40, None, "cv", "job")
    assert not bad["band_ok"] and bad["letter_ok"] is False


def test_check_case_letter_not_checked_when_null():
    assert check_case({"min_score": 0, "max_score": 40, "letter": None}, 20, None, "", "")["letter_ok"] is None


def test_summarize_and_markdown():
    results = [
        {"id": "a", "expect": {"min_score": 70, "max_score": 100}, "error": None, "score": 80, "seconds": 10.0,
         "band_ok": True, "letter_ok": True, "unsupported_numbers": [],
         "judge": {"relevance": 5, "honesty": 4, "tone": 4, "comment": "x"}},
        {"id": "b", "expect": {"min_score": 0, "max_score": 40}, "error": "boom"},
    ]
    s = summarize(results)
    assert s["cases"] == 2 and s["errors"] == 1 and s["band_pass_rate"] == 1.0 and s["avg_honesty"] == 4.0
    md = results_to_markdown(results, s, "test-model")
    assert "| a | 80 |" in md and "| b | error |" in md


def test_clean_text_replaces_odd_characters():
    assert clean_text("must\u2011have eager\u202fto") == "must-have eager to"


def test_cases_file_ground_truth_matches_rule_based_tool():
    """The expected 'missing' lists in cases.json must agree with the skill matcher."""
    for case in CASES["cases"]:
        cv, job = CASES["cvs"][case["cv"]], CASES["jobs"][case["job"]]
        result = skill_overlap(cv["skills"], job["must_have"], cv["text"])
        assert sorted(result["missing"]) == sorted(case["expect"]["missing_must_have"]), case["id"]
