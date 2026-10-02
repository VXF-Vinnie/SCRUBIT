# SCRUBIT — Teammate 2 Handoff: Data / Backend / Integration

## READ THIS FIRST
We have approximately **3 hours total** for this hackathon build. Your job is not to build a production social-media ingestion platform. Your job is to make a small, reliable bridge between an uploaded test archive, our local AI component, and the frontend.

## What SCRUBIT Is
SCRUBIT is a privacy-first social-media reputation auditing tool. A user provides their own social-media data/archive. SCRUBIT extracts relevant post text and runs it through a locally running open-weight AI model. The frontend then displays HIGH, MEDIUM, and LOW risk posts with explanations.

Our core demo flow is:

```text
Upload sample archive
        ↓
Extract post text
        ↓
Normalize posts
        ↓
Local AI classification
        ↓
Return results
        ↓
Frontend dashboard
```

## Your Exact Responsibility
Own the **data ingestion + backend integration** layer.

Your first priority is NOT supporting every social platform. Support one simple test format/archive reliably.

You need to:
1. Accept an uploaded file/archive from the frontend.
2. Extract/parse the relevant post text.
3. Convert every post into the team's standard post format.
4. Pass normalized posts to the Local AI teammate's `analyze_post()` function or equivalent endpoint.
5. Return the classifications to the frontend.

## Recommended Stack
Use **Python + FastAPI** because it is fast to build and integrates naturally with the Python/local-AI side.

Avoid adding databases unless absolutely necessary. For the hackathon demo, results can remain in memory or be returned immediately.

## STANDARD POST FORMAT — DO NOT CHANGE WITHOUT TELLING TEAM
Every social-media parser should eventually produce this:

```json
{
  "id": "post_001",
  "platform": "instagram",
  "date": "2025-08-12",
  "text": "Had a great weekend at the hackathon!"
}
```

Required fields:
- `id`
- `platform`
- `text`

`date` may be null if unavailable.

This normalization is important because the AI should not care whether the original content came from Instagram, Facebook, X, or LinkedIn.

Future architecture:

```text
Instagram parser ─┐
Facebook parser  ─┤
X parser         ─┼─> Standard SCRUBIT Post -> AI
LinkedIn parser  ─┘
```

TODAY: make ONE parser/test archive work.

## Start With a Synthetic Demo Archive
Do this immediately so we have a guaranteed demo even if a real social-media export is difficult.

Create something like:

```text
scrubit_demo/
    posts.json
```

Example `posts.json`:

```json
[
  {
    "id": "post_001",
    "platform": "instagram",
    "date": "2026-09-20",
    "text": "Just finished my first hackathon! Learned a ton about React."
  },
  {
    "id": "post_002",
    "platform": "instagram",
    "date": "2025-06-14",
    "text": "Called out sick today but actually went to Vegas lol."
  },
  {
    "id": "post_003",
    "platform": "instagram",
    "date": "2025-02-01",
    "text": "I'm going to kill this presentation tomorrow."
  },
  {
    "id": "post_004",
    "platform": "instagram",
    "date": "2024-11-03",
    "text": "Finally moved! My new address is 123 Example Street."
  },
  {
    "id": "post_005",
    "platform": "instagram",
    "date": "2024-08-21",
    "text": "Can't believe our company is announcing Project Phoenix next week. Nobody knows yet."
  }
]
```

Zip this if the frontend expects ZIP upload.

## Suggested Backend API
Keep it tiny.

### Health check

```text
GET /health
```

Response:

```json
{"status": "ok"}
```

### Scan archive

```text
POST /scan
```

Input: uploaded ZIP or JSON file.

Conceptual backend flow:

```python
@app.post("/scan")
async def scan(file: UploadFile):
    posts = parse_archive(file)
    results = []

    for post in posts:
        result = analyze_post(post)
        results.append({**post, **result})

    return build_scan_response(results)
```

Exact implementation can change, but keep the external contract simple.

## Suggested Final Response to Frontend
Return something like:

```json
{
  "total_posts": 5,
  "summary": {
    "high": 2,
    "medium": 1,
    "low": 2
  },
  "results": [
    {
      "id": "post_002",
      "platform": "instagram",
      "date": "2025-06-14",
      "text": "Called out sick today but actually went to Vegas lol.",
      "risk": "HIGH",
      "category": "Professional Conduct",
      "explanation": "The post publicly suggests dishonesty about missing work.",
      "recommendation": "Review the post and consider changing its visibility."
    }
  ]
}
```

The frontend teammate can build the entire dashboard from this response.

## CORS
The React frontend will probably run on a different local port from FastAPI. If needed, configure FastAPI CORS early so integration does not get blocked by the browser.

During the hackathon, allowing the local frontend origin is enough. Do not spend time designing production security configuration.

## Privacy / Data Minimization
A core SCRUBIT idea is that we should not blindly feed someone's entire social archive to AI.

Our parser should eventually extract only what the audit needs:
- posts;
- captions/text;
- basic metadata such as date/platform when useful.

We should intentionally ignore unrelated sensitive content such as private messages and credentials.

For the demo, make this visible in the response/UI if possible:

```json
{
  "posts_found": 20,
  "posts_analyzed": 20,
  "private_messages_analyzed": 0
}
```

Do not claim a privacy property the implementation does not actually have.

## Integration With AI Teammate
The AI teammate's intended function contract is:

```python
def analyze_post(post: dict) -> dict:
    ...
```

Input:

```json
{
  "id": "post_002",
  "platform": "instagram",
  "date": "2025-06-14",
  "text": "Called out sick today but actually went to Vegas lol."
}
```

Expected output:

```json
{
  "id": "post_002",
  "risk": "HIGH",
  "category": "Professional Conduct",
  "explanation": "...",
  "recommendation": "..."
}
```

If their AI implementation is not ready yet, **mock this function immediately** so your backend can be completed independently.

Example temporary mock:

```python
def analyze_post(post):
    return {
        "id": post["id"],
        "risk": "MEDIUM",
        "category": "Professional Conduct",
        "explanation": "Temporary demo classification.",
        "recommendation": "Review this post."
    }
```

Then replace the mock with the real function when they are ready.

## Integration With Frontend Teammate
Tell the frontend teammate:
- backend base URL;
- `/scan` endpoint;
- accepted file type;
- exact response JSON;
- whether scans may take several seconds because local AI is processing posts.

The frontend should be able to POST an archive and render your response without knowing how parsing/AI works internally.

## Definition of Done
Your component is DONE when:
- a sample JSON/ZIP can be uploaded;
- backend extracts a list of normalized posts;
- backend can call either the mock or real `analyze_post()`;
- `/scan` returns total + High/Medium/Low counts + detailed results;
- frontend teammate knows exactly how to call it.

## DO NOT BUILD YET
Unless the MVP is working end-to-end, do NOT spend time on:
- four real social-media parsers;
- scraping Instagram/X/etc.;
- authentication/OAuth;
- PostgreSQL;
- user accounts;
- cloud storage;
- image/video extraction;
- production deployment;
- elaborate file validation.

We have 3 hours.

## If You Finish Early
Best improvements, in order:
1. Parse a real export from one platform.
2. Add clear parsing statistics (`posts_found`, `posts_analyzed`).
3. Improve malformed-file errors.
4. Add a second platform parser ONLY if everything else is stable.

## Prompt to Give Your AI Assistant
Copy this entire file into your AI assistant and say:

> I am Teammate 2 on this three-person hackathon project. I own the Data / Backend / Integration component described here. We only have about 3 hours total. Help me implement the smallest reliable FastAPI backend immediately. Preserve the JSON contracts in this document. Start with a synthetic posts.json/ZIP so the project can be demonstrated even without a real social-media export. Give me exact commands, file names, and code step-by-step. Do not add databases, authentication, cloud infrastructure, or other unnecessary features unless the core pipeline is already working.

## Communicate These Things to the Team
As soon as possible, tell us:
- backend URL/port;
- endpoint names;
- accepted upload format;
- exact response shape;
- any dependency/install commands;
- whether you are currently using mock AI or real AI;
- any changes required to the shared JSON contract.

**Primary objective: uploaded demo archive -> normalized posts -> classifications -> frontend-ready JSON.**
