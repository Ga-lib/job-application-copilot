import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from copilot import config
from copilot.llm import get_client

client = get_client()
print(f"Provider: {config.LLM_PROVIDER}\n")
for m in sorted(client.models.list().data, key=lambda m: m.id):
    print(m.id)
