# Job Application Copilot

An LLM agent that reads your CV and a job description, then produces a match score,
CV improvement tips and a tailored cover letter. Built with free tools only
(Groq / Gemini free tiers or local Ollama).

> Work in progress. Step 1 (foundation) is done: provider-agnostic LLM layer,
> CV parsing, and structured extraction of CV + job description.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    |  Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env  (then add your free API key)
pytest
python scripts/step1_demo.py --cv data/cv_samples/my_cv.pdf --job data/job_samples/job1.txt
```

## Switching LLM provider
Set `LLM_PROVIDER` in `.env` to `groq`, `gemini` or `ollama`.
