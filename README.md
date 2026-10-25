# Job Application Copilot

An LLM agent that reads your CV and a job description, then produces a match score,
CV improvement tips and a tailored cover letter. Built with **free tools only**
(Groq / Gemini free tiers or local Ollama).

## How it works

```
parse_cv -> analyze_job -> research_company (web search) -> score_match
         -> cv_tips -> [score >= 35?] -> cover_letter
```

- **LangGraph** orchestrates the steps and routes conditionally (weak fit = no cover letter).
- **Pydantic** schemas make every LLM answer validated JSON, with automatic retry on bad output.
- **Rule-based skill matching** gives the LLM hard evidence, so the score is not just vibes.
- **Provider-agnostic**: switch between Groq, Gemini and Ollama with one environment variable.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    |  Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env  (then add your free API key)
pytest
python scripts/step2_demo.py --cv data/cv_samples/my_cv.pdf --job data/job_samples/job1.txt
```

The report is printed and saved to `output/report.md`.

## Evaluation

The agent is tested like a real product, not just demoed.

```bash
python evals/run_evals.py --limit 3     # quick run
python evals/run_evals.py               # all 7 cases
```

Each case pairs a CV with a job and checks:
- **Score band**: is the match score in the expected range? (strong fit vs weak fit)
- **Routing**: weak candidates must NOT get a cover letter.
- **Hallucination alarm**: numbers in the cover letter that appear in neither CV nor job are flagged.
- **LLM-as-judge**: a second model call rates relevance, honesty and tone (1-5).

Results are written to [`evals/RESULTS.md`](evals/RESULTS.md). Every LLM call is also traced
(latency, tokens, failures) to `output/traces.jsonl`.

## Switching LLM provider
Set `LLM_PROVIDER` in `.env` to `groq`, `gemini` or `ollama`.
Run `python scripts/list_models.py` to see which model names your account can use.

## Roadmap
- [x] Step 1: LLM layer, CV parsing, structured extraction
- [x] Step 2: agent workflow (LangGraph), tools, report
- [x] Step 3: evaluation suite and tracing
- [ ] Step 4: Streamlit UI and deploy
- [ ] Step 5: Docker, CI, demo video
