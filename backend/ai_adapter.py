"""
Bridge between the SCRUBIT backend and the local AI model.

Real model:
    backend/local_ai.py
    analyze_post(post) -> dict

The real local AI is used automatically when available.

To force mock mode:
    SCRUBIT_AI=mock
"""

import os


# ==========================================
# VALID CLASSIFICATIONS
# ==========================================

VALID_RISKS = ("HIGH", "LOW", "CLEAR")


# ==========================================
# LOAD REAL LOCAL AI
# ==========================================

_real_analyze = None

if os.getenv("SCRUBIT_AI", "").lower() != "mock":

    try:
        from local_ai import analyze_post as _real_analyze

    except ImportError:
        _real_analyze = None


AI_MODE = "real" if _real_analyze else "mock"


# ==========================================
# MOCK AI
# ==========================================

def _mock_analyze(post):
    """
    Simple fallback used when the real local AI
    model is unavailable.

    This is only for development/testing.
    """

    text = post.get("text", "").lower()


    # Serious professional concern
    if "called out sick" in text:

        result = (
            "HIGH",
            "Professional Conduct",
            "The post publicly suggests dishonesty "
            "about missing work.",
            "Review the post and consider removing it "
            "or changing its visibility."
        )


    # Serious privacy concern
    elif "address" in text or "street" in text:

        result = (
            "HIGH",
            "Personal Information / Privacy",
            "The post may disclose sensitive location "
            "or home-address information.",
            "Review the post and remove sensitive "
            "location information."
        )


    # Possible confidential information
    elif "nobody knows" in text or "announcing" in text:

        result = (
            "LOW",
            "Confidential Information",
            "The post may contain information that was "
            "not intended to be publicly available.",
            "Review whether the information was public "
            "at the time of posting."
        )


    # Example of contextual language handling
    elif "kill" in text:

        result = (
            "CLEAR",
            "No Significant Risk",
            "The wording may sound severe in isolation, "
            "but it can be harmless depending on context.",
            "No action needed unless the surrounding "
            "context changes its meaning."
        )


    # Normal post
    else:

        result = (
            "CLEAR",
            "No Significant Risk",
            "No meaningful professional or reputational "
            "risk was detected.",
            "No action needed."
        )


    return dict(
        zip(
            (
                "risk",
                "category",
                "explanation",
                "recommendation"
            ),
            result
        )
    )


# ==========================================
# PUBLIC AI INTERFACE
# ==========================================

def analyze(post):
    """
    Calls the real local AI when available.

    Falls back to the mock analyzer if the
    local AI module is unavailable.

    Normalizes the result before returning it
    to the rest of the backend.
    """

    fn = _real_analyze or _mock_analyze


    try:

        output = fn(dict(post)) or {}


    except Exception as e:

        print(
            f"AI analysis failed: "
            f"{type(e).__name__}: {e}"
        )

        return {
            "risk": "UNKNOWN",

            "category": "Analysis Error",

            "explanation":
                "The AI could not analyze this post.",

            "recommendation":
                "Review this post manually."
        }


    # ======================================
    # NORMALIZE RISK
    # ======================================

    risk = str(
        output.get("risk", "")
    ).strip().upper()


    if risk not in VALID_RISKS:

        risk = "UNKNOWN"


    # ======================================
    # NORMALIZED RESULT
    # ======================================

    return {
        "risk": risk,

        "category":
            output.get("category")
            or "Other",

        "explanation":
            output.get("explanation")
            or "",

        "recommendation":
            output.get("recommendation")
            or ""
    }