"""Run the agent on every test case and score the results.

Usage:
    python evals/run_evals.py --limit 3        # quick check (3 cases)
    python evals/run_evals.py                  # all cases
    python evals/run_evals.py --no-judge       # skip the LLM judge (fewer API calls)
"""
import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from copilot import config, graph, tracing
from copilot.evaluation import check_case, judge_cover_letter, results_to_markdown, summarize
from copilot.graph import run_agent


def main():
    parser = argparse.ArgumentParser(description="Evaluate the Job Application Copilot")
    parser.add_argument("--cases", default=str(ROOT / "evals" / "cases.json"))
    parser.add_argument("--limit", type=int, default=None, help="Only run the first N cases")
    parser.add_argument("--only", default=None, help="Run a single case by id")
    parser.add_argument("--no-judge", action="store_true", help="Skip the LLM-as-judge step")
    parser.add_argument("--delay", type=float, default=3.0, help="Seconds to wait between cases (free-tier limits)")
    args = parser.parse_args()

    # Evals must be repeatable, so no live web search.
    graph.web_search_company = lambda company: ""

    data = json.loads(Path(args.cases).read_text(encoding="utf-8"))
    cases = data["cases"]
    if args.only:
        cases = [c for c in cases if c["id"] == args.only]
    if args.limit:
        cases = cases[: args.limit]

    results = []
    for i, case in enumerate(cases, 1):
        cv_text = data["cvs"][case["cv"]]["text"]
        job_text = data["jobs"][case["job"]]["text"]
        print(f"[{i}/{len(cases)}] {case['id']} ...", flush=True)
        rec = {"id": case["id"], "expect": case["expect"], "error": None}
        start = time.perf_counter()
        try:
            state = run_agent(cv_text, job_text)
            rec["seconds"] = round(time.perf_counter() - start, 1)
            score = state["match"].overall_score
            letter = state.get("cover_letter")
            body = letter.body if letter else None
            rec["score"] = score
            rec.update(check_case(case["expect"], score, body, cv_text, job_text))
            rec["judge"] = None
            if body and not args.no_judge:
                rec["judge"] = judge_cover_letter(cv_text, job_text, body).model_dump()
            print(f"    score={score} expected={case['expect']['min_score']}-{case['expect']['max_score']} "
                  f"band={'pass' if rec['band_ok'] else 'FAIL'} letter={'yes' if body else 'no'}")
        except Exception as e:
            rec["error"] = str(e)[:300]
            print(f"    ERROR: {rec['error']}")
        results.append(rec)
        if i < len(cases):
            time.sleep(args.delay)

    summary = summarize(results)
    out_dir = ROOT / "output"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "eval_results.json").write_text(
        json.dumps({"summary": summary, "results": results}, indent=2), encoding="utf-8"
    )
    markdown = results_to_markdown(results, summary, config.LLM_MODEL)
    (ROOT / "evals" / "RESULTS.md").write_text(markdown, encoding="utf-8")

    print("\n" + markdown)
    print("LLM call trace summary:", tracing.summarize_traces())
    print("Saved: evals/RESULTS.md and output/eval_results.json")


if __name__ == "__main__":
    main()
