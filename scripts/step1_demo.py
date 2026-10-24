import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from copilot.cv_parser import read_cv
from copilot.extractors import analyze_job, extract_cv_profile


def main():
    parser = argparse.ArgumentParser(description="Step 1 demo: parse CV and job description")
    parser.add_argument("--cv", required=True, help="Path to CV (.pdf, .txt, .md)")
    parser.add_argument("--job", required=True, help="Path to job description (.txt)")
    args = parser.parse_args()

    cv_text = read_cv(args.cv)
    job_text = Path(args.job).read_text(encoding="utf-8")

    print("\n=== CV PROFILE ===")
    print(extract_cv_profile(cv_text).model_dump_json(indent=2))

    print("\n=== JOB REQUIREMENTS ===")
    print(analyze_job(job_text).model_dump_json(indent=2))


if __name__ == "__main__":
    main()
