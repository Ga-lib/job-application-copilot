import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from copilot.cv_parser import read_cv
from copilot.graph import run_agent
from copilot.report import format_report


def main():
    parser = argparse.ArgumentParser(description="Step 2 demo: run the full Job Application Copilot agent")
    parser.add_argument("--cv", required=True, help="Path to CV (.pdf, .txt, .md)")
    parser.add_argument("--job", required=True, help="Path to job description (.txt)")
    parser.add_argument("--out", default="output/report.md", help="Where to save the report")
    args = parser.parse_args()

    cv_text = read_cv(args.cv)
    job_text = Path(args.job).read_text(encoding="utf-8")

    print("Running the agent...")
    state = run_agent(cv_text, job_text, verbose=True)

    report = format_report(state)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")

    print("\n" + report)
    print(f"Saved to {out}")


if __name__ == "__main__":
    main()
