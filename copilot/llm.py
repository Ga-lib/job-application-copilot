import json
import os
import time
from typing import Type, TypeVar

from openai import OpenAI
from pydantic import BaseModel, ValidationError

from copilot import config, tracing

T = TypeVar("T", bound=BaseModel)

# Some models emit special invisible/non-breaking characters. Replace them with plain ones.
_CLEAN = str.maketrans(
    {"\u2011": "-", "\u2010": "-", "\u202f": " ", "\u00a0": " ", "\u2009": " ", "\u200b": None}
)


def clean_text(text: str) -> str:
    return text.translate(_CLEAN)


def get_client() -> OpenAI:
    cfg = config.PROVIDERS[config.LLM_PROVIDER]
    key_env = cfg["key_env"]
    api_key = os.getenv(key_env) if key_env else "ollama"  # Ollama ignores the key
    if not api_key:
        raise RuntimeError(f"Missing {key_env}. Add it to your .env file.")
    return OpenAI(base_url=cfg["base_url"], api_key=api_key)


def chat(messages: list[dict], temperature: float = 0.2, json_mode: bool = False,
         retries: int = 4, max_tokens: int = 4096) -> str:
    """Send a chat request. Retries with backoff (free tiers have rate limits) and traces each call."""
    client = get_client()
    kwargs = {
        "model": config.LLM_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,  # reasoning models spend tokens "thinking", so keep this generous
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    for attempt in range(retries):
        start = time.perf_counter()
        try:
            response = client.chat.completions.create(**kwargs)
            content = clean_text(response.choices[0].message.content or "")
            tracing.log_call(config.LLM_PROVIDER, config.LLM_MODEL,
                             time.perf_counter() - start, getattr(response, "usage", None))
            return content
        except Exception as e:
            tracing.log_call(config.LLM_PROVIDER, config.LLM_MODEL,
                             time.perf_counter() - start, ok=False, error=str(e))
            if attempt == retries - 1:
                raise
            wait = 3 * 2 ** attempt
            print(f"[llm] error: {e}. Retrying in {wait}s...")
            time.sleep(wait)


def chat_structured(system: str, user: str, schema: Type[T], retries: int = 3) -> T:
    """Ask the LLM for JSON and validate it against a Pydantic schema."""
    schema_json = json.dumps(schema.model_json_schema())
    system_prompt = (
        f"{system}\n\nRespond with ONLY a valid JSON object matching this JSON schema. "
        f"No markdown, no extra text.\n{schema_json}"
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user},
    ]

    last_error = None
    for _ in range(retries):
        raw = chat(messages, json_mode=True)
        try:
            return schema.model_validate_json(raw)
        except ValidationError as e:
            last_error = e
            messages.append({"role": "assistant", "content": raw})
            messages.append({
                "role": "user",
                "content": f"That JSON was invalid: {e}. Fix it and return only the JSON.",
            })
    raise ValueError(f"Could not get valid structured output: {last_error}")
