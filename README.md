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

## Switching LLM provider
Set `LLM_PROVIDER` in `.env` to `groq`, `gemini` or `ollama`.
Run `python scripts/list_models.py` to see which model names your account can use.

## Roadmap
- [x] Step 1: LLM layer, CV parsing, structured extraction
- [x] Step 2: agent workflow (LangGraph), tools, report
- [ ] Step 3: evaluation suite and tracing
- [ ] Step 4: Streamlit UI and deploy
- [ ] Step 5: Docker, CI, demo video
