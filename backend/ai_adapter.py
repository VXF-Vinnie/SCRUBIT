"""
Bridge to the Local AI teammate.
Real model: put their local_ai.py (with analyze_post(post) -> dict) next to
this file; it's picked up automatically. Force mock with SCRUBIT_AI=mock.
The mock is a keyword fallback for demos only -- it is NOT real AI.
"""
import os
import re

VALID_RISKS = ("HIGH", "MEDIUM", "LOW")

_real_analyze = None
if os.getenv("SCRUBIT_AI", "").lower() != "mock":
    try:
        from local_ai import analyze_post as _real_analyze
    except ImportError:
        _real_analyze = None

AI_MODE = "real" if _real_analyze else "mock"

# (regex, risk, category, explanation, recommendation) -- first match wins.
MOCK_RULES = [
    (r"drove away|hit and run|hit-and-run", "HIGH", "Legal Risk",
     "The post describes leaving the scene after damaging a vehicle, which can be a crime.",
     "Delete this post."),
    (r"\bweed\b|\bhigh\b|\bstoned\b|\bsmoke[ds]?\b|\bsmoking\b", "HIGH", "Substance Use",
     "The post references drug use, which employers and schools may screen for.",
     "Delete or archive this post."),
    (r"called out sick", "HIGH", "Professional Conduct",
     "The post publicly suggests dishonesty about missing work.",
     "Review the post and consider changing its visibility."),
    (r"\baddress\b|\bstreet\b", "HIGH", "Personal Information",
     "The post discloses a home address that could identify where you live.",
     "Delete or edit the post to remove the address."),
    (r"nobody knows|announcing", "MEDIUM", "Confidential Information",
     "The post may reveal unannounced company information.",
     "Check whether this was public at the time; consider removing it."),
    (r"\bprofessor \w+", "MEDIUM", "Disparaging Named People",
     "The post criticizes a named professor, which can read as unprofessional.",
     "Consider deleting or rewording to remove the name."),
    (r"no memory|drinking|\bdrunk\b|blackout|one drink|absolutely gone|never happened", "MEDIUM", "Alcohol",
     "The post describes heavy drinking or memory loss.",
     "Consider archiving this post."),
    (r"not paying|unpaid|pulled over|speeding|\d+ in a \d+", "MEDIUM", "Legal / Financial Responsibility",
     "The post describes traffic violations or unpaid fines.",
     "Consider archiving this post."),
    (r"\bkill\b", "LOW", "Language",
     "Contains violent wording, but in context it is a common figure of speech.",
     "Likely fine; no action needed."),
]


def _mock_analyze(post):
    t = post["text"].lower()
    for pattern, risk, cat, expl, rec in MOCK_RULES:
        if re.search(pattern, t):
            return {"risk": risk, "category": cat, "explanation": expl, "recommendation": rec}
    return {"risk": "LOW", "category": "None",
            "explanation": "No reputational risk detected.", "recommendation": "No action needed."}


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