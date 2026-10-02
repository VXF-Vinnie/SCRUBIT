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
1. ID Matching: You MUST use the exact ID provided in the user's input post. Do not change it or invent a new ID.
2. Contextual Awareness: Do NOT blindly match keywords. Common figurative expressions (e.g., "killing a presentation") must NOT be flagged as threats. They are No Significant Risk.
3. Objective Analysis: Do not moralize. Evaluate if an employer or background check would view it negatively.
4. Strict Output: Respond using ONLY the requested JSON schema.
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
        result = json.loads(response['message']['content'])
        
        # Hard safeguard: Ensure the ID matches perfectly even if the LLM slips up
        result["id"] = post.get("id")
        return result
        
    except Exception as e:
        return {"id": post.get("id"), "risk": "LOW", "category": "Other", "explanation": f"Error: {e}", "recommendation": "Review manually."}

if __name__ == "__main__":
    # 1. Load sample data
    input_file = "data/posts.json"
    output_file = "data/results.json"
    
    with open(input_file, "r") as f:
        posts = json.load(f)
    
    print(f"Starting local AI analysis on {len(posts)} posts...")
    
    # 2. Process items through the pipeline
    analyzed_results = []
    for item in posts:
        print(f"Analyzing {item.get('id')}...")
        result = analyze_post(item)
        analyzed_results.append(result)
    
    # 3. Save the results cleanly to a local file
    with open(output_file, "w") as f:
        json.dump(analyzed_results, f, indent=2)
        
    print(f"\n🎉 Success! Analysis complete. Results saved to: {output_file}")
