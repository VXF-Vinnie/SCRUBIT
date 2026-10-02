"""
Bridge to the teammate's Ollama bot in ../local-privacy-bot.
Finds the .py file there that defines analyze_post() and calls it.
If the bot reports an error (it returns explanation "Error: ..."), we raise,
so the backend marks the post UNKNOWN instead of a misleading LOW.
"""
import importlib.util
from pathlib import Path

BOT_DIR = Path(__file__).resolve().parent.parent / "local-privacy-bot"


def _load_bot():
    for path in sorted(BOT_DIR.glob("*.py")):
        if "def analyze_post" in path.read_text(encoding="utf-8", errors="ignore"):
            spec = importlib.util.spec_from_file_location("privacy_bot", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module.analyze_post
    raise ImportError(f"No analyze_post() found in {BOT_DIR}")


_bot_analyze = _load_bot()


def analyze_post(post: dict) -> dict:
    result = _bot_analyze(post)
    if str(result.get("explanation", "")).startswith("Error:"):
        raise RuntimeError(result["explanation"])
    return result