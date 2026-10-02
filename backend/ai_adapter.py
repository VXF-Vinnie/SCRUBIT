"""
Bridge to the Local AI teammate.
Hardwired directly to your real local_ai module for the hackathon presentation.
"""
from local_ai import analyze_post as _real_analyze

# Hard-code the adapter contract to bypass the mock entirely
AI_MODE = "real"
VALID_RISKS = ("HIGH", "MEDIUM", "LOW")

def analyze(post):
    """Calls your local Ollama AI model and normalizes the output layout."""
    try:
        # Cast post as a plain dictionary and pass to your model
        out = _real_analyze(dict(post)) or {}
    except Exception as e:
        return {
            "risk": "UNKNOWN", 
            "category": "Analysis Error",
            "explanation": f"The local AI engine threw an exception ({type(e).__name__}).",
            "recommendation": "Review this post manually."
        }
    
    risk = str(out.get("risk", "")).strip().upper()
    return {
        "risk": risk if risk in VALID_RISKS else "UNKNOWN",
        "category": out.get("category") or "Uncategorized",
        "explanation": out.get("explanation") or "",
        "recommendation": out.get("recommendation") or "",
    }
