import json
import os
import ollama

# Optimize text generation performance for Intel CPUs
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
3. Strict Output: Respond using ONLY the requested JSON schema. Do not change the post ID or invent a new one.
"""

def analyze_post(post: dict) -> dict:
    """
    Core entrypoint for the FastAPI backend layer.
    """
    try:
        response = ollama.chat(
            model="llama3.2:3b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze this post data:\n{json.dumps(post)}"}
            ],
            format=ANALYSIS_SCHEMA
        )
        result = json.loads(response['message']['content'])
        
        # Format normalization to ensure exact map parity with backend contracts
        return {
            "risk": str(result.get("risk", "LOW")).strip().upper(),
            "category": result.get("category", "Uncategorized"),
            "explanation": result.get("explanation", ""),
            "recommendation": result.get("recommendation", "")
        }
    except Exception as e:
        return {
            "risk": "LOW",
            "category": "Analysis Error",
            "explanation": f"Local AI processing error: {e}",
            "recommendation": "Review post manually."
        }
