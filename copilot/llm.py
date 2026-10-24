import json
import os
import time
from typing import Type, TypeVar

from openai import OpenAI
from pydantic import BaseModel, ValidationError

from copilot import config

T = TypeVar("T", bound=BaseModel)


def get_client() -> OpenAI:
    cfg = config.PROVIDERS[config.LLM_PROVIDER]
    key_env = cfg["key_env"]
    api_key = os.getenv(key_env) if key_env else "ollama"  # Ollama ignores the key
    if not api_key:
        raise RuntimeError(f"Missing {key_env}. Add it to your .env file.")
    return OpenAI(base_url=cfg["base_url"], api_key=api_key)


def chat(messages: list[dict], temperature: float = 0.2,
         json_mode: bool = False, retries: int = 3) -> str:
    """Send a chat request. Retries with backoff (free tiers have rate limits)."""
    client = get_client()
    kwargs = {"model": config.LLM_MODEL, "messages": messages, "temperature": temperature}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            if attempt == retries - 1:
                raise
            wait = 2 ** (attempt + 1)
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
