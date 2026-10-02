"""
Bridge to the Local AI teammate.
Real model: put their local_ai.py (with analyze_post(post) -> dict) next to
this file; it's picked up automatically. Force mock with SCRUBIT_AI=mock.
"""
import os

VALID_RISKS = ("HIGH", "MEDIUM", "LOW")

_real_analyze = None
if os.getenv("SCRUBIT_AI", "").lower() != "mock":
    try:
        from local_ai import analyze_post as _real_analyze
    except ImportError:
        _real_analyze = None

AI_MODE = "real" if _real_analyze else "mock"


def _mock_analyze(post):
    t = post["text"].lower()
    if "called out sick" in t:
        r = ("HIGH", "Professional Conduct",
             "The post publicly suggests dishonesty about missing work.",
             "Review the post and consider changing its visibility.")
    elif "address" in t or "street" in t:
        r = ("HIGH", "Personal Information",
             "The post discloses a home address that could identify where you live.",
             "Delete or edit the post to remove the address.")
    elif "nobody knows" in t or "announcing" in t:
        r = ("MEDIUM", "Confidential Information",
             "The post may reveal unannounced company information.",
             "Check whether this was public at the time; consider removing it.")
    elif "kill" in t:
        r = ("LOW", "Language",
             "Contains violent wording, but in context it is a common figure of speech.",
             "Likely fine; no action needed.")
    else:
        r = ("LOW", "None", "No reputational risk detected.", "No action needed.")
    return dict(zip(("risk", "category", "explanation", "recommendation"), r))


def analyze(post):
    """Calls real or mock AI and normalizes the output. Never raises."""
    fn = _real_analyze or _mock_analyze
    try:
        out = fn(dict(post)) or {}
    except Exception as e:
        return {"risk": "UNKNOWN", "category": "Analysis Error",
                "explanation": f"The AI could not analyze this post ({type(e).__name__}).",
                "recommendation": "Review this post manually."}
    risk = str(out.get("risk", "")).strip().upper()
    return {
        "risk": risk if risk in VALID_RISKS else "UNKNOWN",
        "category": out.get("category") or "Uncategorized",
        "explanation": out.get("explanation") or "",
        "recommendation": out.get("recommendation") or "",
    }