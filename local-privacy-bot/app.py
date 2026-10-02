import json
import os
import ollama

# Optimize performance for Intel CPU
os.environ["OLLAMA_FLASH_ATTENTION"] = "1"

ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "risk": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]},
        "category": {
            "type": "string", 
            "enum": [
                "Professional Conduct", "Harassment / Hostility", "Discriminatory Content",
                "Illegal Activity", "Drugs / Alcohol", "Sexual / Explicit Content",
                "Violence / Threats", "Personal Information / Privacy", 
                "Confidential Information", "Offensive Language", "Other", "No Significant Risk"
            ]
        },
        "explanation": {"type": "string"},
        "recommendation": {"type": "string"}
    },
    "required": ["id", "risk", "category", "explanation", "recommendation"]
}

SYSTEM_PROMPT = """
You are an expert digital footprint and privacy compliance auditor. Analyze social media posts for potential professional or personal risks.
CRITICAL RULES:
1. Contextual Awareness: Do NOT blindly match keywords. Common figurative expressions (e.g., "killing a presentation") must NOT be flagged as threats. They are No Significant Risk.
2. Objective Analysis: Do not moralize. Evaluate if an employer or background check would view it negatively.
3. Strict Output: Respond using ONLY the requested JSON schema.
"""

def analyze_post(post: dict) -> dict:
    try:
        response = ollama.chat(
            model="llama3.2:3b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze this post data:\n{json.dumps(post)}"}
            ],
            format=ANALYSIS_SCHEMA
        )
        return json.loads(response['message']['content'])
    except Exception as e:
        return {"id": post.get("id"), "risk": "LOW", "category": "Other", "explanation": f"Error: {e}", "recommendation": "Review manually."}

if __name__ == "__main__":
    # Load sample data
    with open("data/posts.json", "r") as f:
        posts = json.load(f)
    
    # Process and print results
    print("Starting local AI analysis...")
    for item in posts:
        result = analyze_post(item)
        print(json.dumps(result, indent=2))
