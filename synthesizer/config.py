"""
Central OpenRouter config for the synthesizer component.

Same connection pattern as router/tier3_fallback.py: base_url https://openrouter.ai/api/v1,
OpenAI-compatible chat-completions endpoint, single OPENROUTER_API_KEY that works across
all OpenRouter models. The key is read from the environment first, falling back to the
git-ignored synapse/.env file so scripts work without a manual export.

No Anthropic/OpenAI-direct/any other provider SDKs -- plain HTTPS to OpenRouter only.
"""
import os
from pathlib import Path

BASE_URL = "https://openrouter.ai/api/v1"
CHAT_URL = f"{BASE_URL}/chat/completions"

_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"   # synapse/.env


def get_openrouter_key():
    """OPENROUTER_API_KEY from the environment, else from synapse/.env, else None."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key
    if _ENV_FILE.exists():
        for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
            if line.startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip() or None
    return None
