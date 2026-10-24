import os
from dotenv import load_dotenv

load_dotenv()

# All three providers speak the OpenAI-compatible API, so one client works for all.
PROVIDERS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "key_env": "GROQ_API_KEY",
        "default_model": "llama-3.3-70b-versatile",
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "key_env": "GEMINI_API_KEY",
        "default_model": "gemini-2.5-flash",
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "key_env": None,
        "default_model": "llama3.2:3b",
    },
}

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()

if LLM_PROVIDER not in PROVIDERS:
    raise ValueError(f"Unknown LLM_PROVIDER '{LLM_PROVIDER}'. Choose from {list(PROVIDERS)}")

LLM_MODEL = os.getenv("LLM_MODEL") or PROVIDERS[LLM_PROVIDER]["default_model"]
