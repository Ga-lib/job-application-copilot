from copilot import llm
from copilot.schemas import JobRequirements


def test_chat_structured_retries_on_bad_json(monkeypatch):
    replies = iter([
        "not json at all",
        '{"title": "ML Engineer", "seniority": "junior", "must_have_skills": ["Python"],'
        ' "nice_to_have_skills": [], "responsibilities": ["build APIs"]}',
    ])
    monkeypatch.setattr(llm, "chat", lambda *a, **k: next(replies))

    result = llm.chat_structured("sys", "user", JobRequirements)
    assert result.title == "ML Engineer"
    assert result.must_have_skills == ["Python"]
