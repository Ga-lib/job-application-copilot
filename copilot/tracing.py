"""Tiny local tracing: every LLM call is logged to output/traces.jsonl (free, no signup)."""
import json
import os
import time
from pathlib import Path

TRACE_FILE = Path(__file__).resolve().parent.parent / "output" / "traces.jsonl"


def log_call(provider, model, seconds, usage=None, ok=True, error=None):
    """Append one record. Tracing must never crash the app, so all errors are swallowed."""
    if os.getenv("TRACING", "1") == "0":
        return
    try:
        record = {
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "provider": provider,
            "model": model,
            "seconds": round(seconds, 2),
            "prompt_tokens": getattr(usage, "prompt_tokens", None),
            "completion_tokens": getattr(usage, "completion_tokens", None),
            "ok": ok,
            "error": (error or "")[:200] or None,
        }
        TRACE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with TRACE_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        pass


def summarize_traces(path=None) -> dict:
    p = Path(path) if path else TRACE_FILE
    if not p.exists():
        return {"calls": 0, "failed": 0, "avg_seconds": 0, "total_tokens": 0}
    rows = [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
    ok_rows = [r for r in rows if r["ok"]]
    return {
        "calls": len(rows),
        "failed": len(rows) - len(ok_rows),
        "avg_seconds": round(sum(r["seconds"] for r in ok_rows) / len(ok_rows), 2) if ok_rows else 0,
        "total_tokens": sum((r.get("prompt_tokens") or 0) + (r.get("completion_tokens") or 0) for r in rows),
    }
