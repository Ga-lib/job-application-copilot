import json

from copilot import graph, llm
from copilot.report import format_report

CV = {
    "name": "Test Candidate", "email": None, "summary": "ML grad.",
    "skills": ["Python", "SQL", "Git"], "experience": ["Freelancer"],
    "projects": ["RAG app"], "education": ["BSc CSE"],
}
JOB = {
    "title": "Junior ML Engineer", "company": "Acme", "seniority": "junior",
    "must_have_skills": ["Python", "SQL", "Docker"], "nice_to_have_skills": ["AWS"],
    "responsibilities": ["build APIs"],
}
TIPS = {"tips": ["t1", "t2"], "keywords_to_add": ["FastAPI"], "rewritten_summary": "Tailored."}
LETTER = {"subject": "Application", "body": "Dear Hiring Manager, ..."}


def fake_chat_factory(score, job=None):
    """Pretend LLM: picks the reply by looking at which JSON schema is in the system prompt."""
    match = {"overall_score": score, "strengths": ["Python"], "gaps": ["Docker"], "reasoning": "ok"}

    def fake_chat(messages, **kwargs):
        system = messages[0]["content"]
        if "overall_score" in system:
            return json.dumps(match)
        if "rewritten_summary" in system:
            return json.dumps(TIPS)
        if "subject" in system:
            return json.dumps(LETTER)
        if "must_have_skills" in system:
            return json.dumps(job or JOB)
        if "education" in system:
            return json.dumps(CV)
        raise AssertionError("unexpected prompt")

    return fake_chat


def run(monkeypatch, score):
    monkeypatch.setattr(llm, "chat", fake_chat_factory(score))
    monkeypatch.setattr(graph, "web_search_company", lambda company: "- Acme: a company")
    return graph.run_agent("Python SQL Git CV text", "job text")


def test_full_run_writes_cover_letter(monkeypatch):
    state = run(monkeypatch, score=80)
    assert state["match"].overall_score == 80
    assert state["overlap"]["must_have"]["missing"] == ["Docker"]
    assert state["cover_letter"].subject == "Application"
    assert "Cover letter" in format_report(state)


def test_weak_fit_skips_cover_letter(monkeypatch):
    state = run(monkeypatch, score=10)
    assert state["cover_letter"] is None
    assert "Skipped" in format_report(state)


def test_low_must_have_coverage_skips_cover_letter(monkeypatch):
    """A high LLM score must not produce a letter when the CV covers under half the must-haves."""
    hard_job = dict(JOB, must_have_skills=["Rust", "Go", "Kubernetes", "Python"])
    monkeypatch.setattr(llm, "chat", fake_chat_factory(80, job=hard_job))
    monkeypatch.setattr(graph, "web_search_company", lambda company: "")
    state = graph.run_agent("Python SQL Git CV text", "job text")
    assert state["overlap"]["must_have"]["coverage_pct"] == 25
    assert state["cover_letter"] is None
