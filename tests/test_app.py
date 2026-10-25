from pathlib import Path

from streamlit.testing.v1 import AppTest
from test_graph import fake_chat_factory

from copilot import graph, llm

APP = str(Path(__file__).resolve().parent.parent / "app.py")
JOB = "Junior ML Engineer at Acme. Requirements: Python, SQL, Docker. Build APIs and deploy models."


def fill_and_run(at, cv="Python SQL Git developer", job=JOB):
    at.radio[0].set_value("Paste text").run()
    at.text_area(key="cv_paste").set_value(cv)
    at.text_area(key="job_text").set_value(job)
    at.button[0].click().run()
    return at


def test_app_end_to_end(monkeypatch):
    monkeypatch.setattr(llm, "chat", fake_chat_factory(80))
    monkeypatch.setattr(graph, "web_search_company", lambda company: "")
    at = fill_and_run(AppTest.from_file(APP, default_timeout=30).run())
    assert not at.exception
    assert at.metric[0].value == "80/100"
    assert at.metric[2].value == "Written"


def test_app_skips_letter_for_weak_fit(monkeypatch):
    monkeypatch.setattr(llm, "chat", fake_chat_factory(10))
    monkeypatch.setattr(graph, "web_search_company", lambda company: "")
    at = fill_and_run(AppTest.from_file(APP, default_timeout=30).run())
    assert at.metric[2].value == "Skipped"


def test_app_warns_when_cv_missing():
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.text_area(key="job_text").set_value(JOB)
    at.button[0].click().run()
    assert any("CV" in w.value for w in at.warning)


def test_app_run_limit(monkeypatch):
    monkeypatch.setattr(llm, "chat", fake_chat_factory(80))
    monkeypatch.setattr(graph, "web_search_company", lambda company: "")
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.session_state["runs"] = 5
    fill_and_run(at)
    assert any("limit" in w.value for w in at.warning)
