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

Examples of the TYPES of concerns that may justify HIGH include:
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

Examples of the TYPES of concerns that may justify LOW include:
- rude or insulting comments
- mild workplace or school criticism
- questionable professional judgment
- excessive profanity
- minor privacy concerns
- ambiguous content that could be interpreted negatively

CLEAR:
Use CLEAR when there is no meaningful professional or reputational
risk.

Normal everyday posts, achievements, hobbies, food, travel,
celebrations, school activities, ordinary opinions, and harmless
conversation should generally be CLEAR.

IMPORTANT ANALYSIS RULES:

1. Analyze the complete meaning of the post.

2. Do NOT classify something as risky merely because it contains a
word associated with violence, drugs, crime, sex, or another risky
topic.

3. Understand figurative language, jokes, slang, and ordinary
expressions in context.

4. Do not invent circumstances that are not present in the post.

5. Do not classify ordinary personal information as risky unless
the post actually creates a meaningful privacy or safety concern.

6. The category must describe the actual reason for the
classification. Do not select an unrelated category.

7. If risk is CLEAR, normally use "No Significant Risk" as the
category.

8. If the post contains multiple concerns, classify it according to
the most serious concern.

9. Evaluate reputational risk objectively. Do not moralize or punish
someone merely for expressing a normal personal opinion.

10. HIGH should be reserved for substantial concerns. LOW is for
content worth reviewing. CLEAR is for content requiring no meaningful
review.

11. The explanation must specifically explain the classification
based on what the post actually says.

12. The recommendation should give a short practical action, such as
reviewing the post, considering removal, limiting visibility, or
taking no action.

13. You MUST return the exact ID supplied with the input post.

14. Respond ONLY using the requested JSON structure.
"""


# ==========================================
# ANALYZE ONE POST
# ==========================================

def analyze_post(post: dict) -> dict:

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

            # Lower temperature = more consistent classifications
            options={
                "temperature": 0.1
            }
        )

        result = json.loads(
            response["message"]["content"]
        )

        # Always preserve the original post ID.
        result["id"] = post.get("id")

        return result


    except Exception as e:

        print(
            f"Error analyzing {post.get('id')}: {e}"
        )

        # An AI failure should NOT silently classify
        # a post as safe.
        return {
            "id": post.get("id"),
            "risk": "LOW",
            "category": "Other",
            "explanation":
                "The automated analysis could not be completed.",
            "recommendation":
                "Review this post manually."
        }


# ==========================================
# RUN LOCALLY
# ==========================================

if __name__ == "__main__":

    input_file = "data/posts.json"
    output_file = "data/results.json"


    # Load posts
    with open(
        input_file,
        "r",
        encoding="utf-8"
    ) as f:

        posts = json.load(f)


    print(
        f"Starting local AI analysis on "
        f"{len(posts)} posts..."
    )


    analyzed_results = []


    # Analyze each post individually
    for item in posts:

        print(
            f"Analyzing {item.get('id')}..."
        )

        result = analyze_post(item)

        analyzed_results.append(result)


    # Save results locally
    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            analyzed_results,
            f,
            indent=2
        )


    print(
        f"\nAnalysis complete. "
        f"Results saved to: {output_file}"
    )