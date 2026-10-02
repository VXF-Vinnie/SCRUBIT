import json
import os
import ollama

# Optimize performance for local inference
os.environ["OLLAMA_FLASH_ATTENTION"] = "1"


# ==========================================
# STRUCTURED AI OUTPUT
# ==========================================

ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {
            "type": "string"
        },

        "risk": {
            "type": "string",
            "enum": ["HIGH", "LOW", "CLEAR"]
        },

        "category": {
            "type": "string",
            "enum": [
                "Professional Conduct",
                "Harassment / Hostility",
                "Discriminatory Content",
                "Illegal / Reckless Conduct",
                "Drugs / Alcohol",
                "Sexual / Explicit Content",
                "Violence / Threats",
                "Personal Information / Privacy",
                "Confidential Information",
                "Offensive Language",
                "Other",
                "No Significant Risk"
            ]
        },

        "explanation": {
            "type": "string"
        },

        "recommendation": {
            "type": "string"
        }
    },

    "required": [
        "id",
        "risk",
        "category",
        "explanation",
        "recommendation"
    ]
}


# ==========================================
# AI INSTRUCTIONS
# ==========================================

SYSTEM_PROMPT = """
You are a digital-footprint risk analysis system.

Your task is to analyze social-media posts and determine whether
the content could create a meaningful professional or reputational
risk if viewed publicly by an employer, recruiter, school,
professional organization, or other third party.

Evaluate the meaning and context of the post, not simply individual
keywords.

RISK LEVELS:

HIGH:
Use HIGH when the post contains behavior or statements that could
reasonably create a serious professional or reputational concern.

Types of concerns that may justify HIGH include:
- admitting to illegal or seriously reckless behavior
- credible threats or advocacy of violence
- discriminatory or hateful statements
- severe harassment or targeted hostility
- disclosure of confidential information
- explicit content that could cause substantial professional concern
- serious workplace misconduct
- admissions of behavior showing major dishonesty or irresponsibility

LOW:
Use LOW when there is a legitimate concern worth reviewing, but the
content is not severe enough to represent a major reputational risk.

Types of concerns that may justify LOW include:
- rude or insulting comments
- mild workplace or school criticism
- questionable professional judgment
- excessive profanity
- minor privacy concerns
- ambiguous content that could reasonably be interpreted negatively

CLEAR:
Use CLEAR when there is no meaningful professional or reputational
risk.

Normal everyday posts, achievements, hobbies, food, travel,
celebrations, school activities, ordinary opinions, and harmless
conversation should generally be CLEAR.

IMPORTANT RULES:

1. Analyze the complete meaning and context of the post.

2. Do NOT classify something as risky merely because it contains
a word associated with violence, drugs, crime, sex, or another
risky topic.

3. Understand figurative language, jokes, slang, and ordinary
expressions in context.

4. Do not invent circumstances that are not present in the post.

5. Do not classify ordinary personal information as risky unless
the post actually creates a meaningful privacy or safety concern.

6. The category must describe the actual reason for the
classification.

7. If risk is CLEAR, normally use "No Significant Risk" as the
category.

8. If a post contains multiple concerns, classify it according to
the most serious concern.

9. Evaluate reputational risk objectively. Do not moralize.

10. HIGH is for substantial concerns. LOW is for content worth
reviewing. CLEAR is for content requiring no meaningful review.

11. The explanation must specifically explain why the actual
content received its classification.

12. The recommendation should provide a short practical action.

13. You MUST preserve the exact post ID provided in the input.

14. Respond ONLY using the requested JSON structure.
"""


# ==========================================
# ANALYZE POST
# ==========================================

def analyze_post(post: dict) -> dict:
    """
    Takes a normalized post dictionary and returns
    structured local AI analysis.
    """

    try:
        response = ollama.chat(
            model="llama3.2:3b",

            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content":
                        f"Analyze this social-media post:\n"
                        f"{json.dumps(post)}"
                }
            ],

            format=ANALYSIS_SCHEMA,

            # Low temperature makes classification
            # more deterministic and consistent.
            options={
                "temperature": 0.1
            }
        )

        result = json.loads(
            response["message"]["content"]
        )

        # Normalize the model's risk output.
        risk = str(
            result.get("risk", "LOW")
        ).strip().upper()

        # Safety check in case the model returns
        # an unexpected value.
        if risk not in ["HIGH", "LOW", "CLEAR"]:
            risk = "LOW"

        return {
            "risk": risk,

            "category":
                result.get(
                    "category",
                    "Other"
                ),

            "explanation":
                result.get(
                    "explanation",
                    ""
                ),

            "recommendation":
                result.get(
                    "recommendation",
                    ""
                )
        }

    except Exception as e:

        print(
            f"Local AI analysis error: {e}"
        )

        # An AI failure should not silently be
        # treated as safe/clear.
        return {
            "risk": "LOW",

            "category": "Other",

            "explanation":
                "The local AI model could not complete "
                "the analysis.",

            "recommendation":
                "Review this post manually."
        }