from types import SimpleNamespace

from copilot import tracing


def test_log_and_summarize(tmp_path, monkeypatch):
    monkeypatch.setattr(tracing, "TRACE_FILE", tmp_path / "traces.jsonl")
    usage = SimpleNamespace(prompt_tokens=100, completion_tokens=50)
    tracing.log_call("groq", "m", 2.0, usage)
    tracing.log_call("groq", "m", 4.0, usage)
    tracing.log_call("groq", "m", 1.0, ok=False, error="429")
    s = tracing.summarize_traces()
    assert s == {"calls": 3, "failed": 1, "avg_seconds": 3.0, "total_tokens": 300}


def test_tracing_can_be_disabled(tmp_path, monkeypatch):
    monkeypatch.setattr(tracing, "TRACE_FILE", tmp_path / "traces.jsonl")
    monkeypatch.setenv("TRACING", "0")
    tracing.log_call("groq", "m", 1.0)
    assert tracing.summarize_traces()["calls"] == 0
