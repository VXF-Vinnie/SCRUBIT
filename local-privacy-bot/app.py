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
You are a highly critical, strict corporate digital footprint and privacy compliance auditor. 
Your objective is to identify any text that could compromise a user's professional reputation during a background check or employer review.

CRITICAL RISK EVALUATION RULES:
1. HIGH RISK FLAGS: Any clear instance of fraud, bragging about faking sick days/lying to employers, illegal behavior, substance abuse, or exposing highly sensitive data (like full home addresses or unannounced corporate projects) MUST be classified as HIGH or MEDIUM risk. Do not excuse them because of casual text like "lol".
2. CONTEXT AWARENESS: Differentiate between literal statements and clear figurative common expressions. Phrases like "killing a presentation" are low risk.
3. OUTPUT: Return only the strictly formatted JSON map.
"""

def analyze_post(post: dict) -> dict:
    try:
        response = ollama.chat(
        model="llama3.2:3b",
        messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Analyze this post data:\n{json.dumps(post)}"}
        ],
        format=ANALYSIS_SCHEMA,
        options={"num_ctx": 2048, "temperature": 0.0} # Lower temperature forces deterministic, strict flag matching
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
