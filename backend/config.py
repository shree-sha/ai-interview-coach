import os
from pathlib import Path


def _load_env_file() -> None:
    """Load local backend settings without overriding real environment variables."""
    env_file = Path(__file__).with_name(".env")
    if not env_file.exists():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


_load_env_file()

OLLAMA_GENERATE_URL = os.getenv("OLLAMA_GENERATE_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
OLLAMA_STREAM = os.getenv("OLLAMA_STREAM", "false").strip().lower() == "true"
