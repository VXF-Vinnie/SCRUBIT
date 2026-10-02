"""SCRUBIT backend. Run: uvicorn main:app --reload --port 8000"""
import time

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from ai_adapter import AI_MODE, analyze
from parser import ArchiveError, parse_archive

from fastapi import FastAPI, UploadFile, File
# 1. Import the CORS middleware module
from fastapi.middleware.cors import CORSMiddleware
from ai_adapter import analyze
import json

app = FastAPI()

# 2. Allow your local frontend port to communicate securely
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows POST, GET, etc.
    allow_headers=["*"],
)

# ... leave the rest of your teammate's routes and endpoints below exactly as they are


MAX_UPLOAD_BYTES = 50 * 1024 * 1024
RISK_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "UNKNOWN": 3}

app = FastAPI(title="SCRUBIT")
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "ai_mode": AI_MODE}


@app.post("/scan")
def scan(file: UploadFile = File(...)):
    data = file.file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "File too large (max 50 MB).")
    try:
        posts, file_stats = parse_archive(file.filename, data)
    except ArchiveError as e:
        raise HTTPException(400, str(e))

    started = time.time()
    results = [{**post, **analyze(post)} for post in posts]
    results.sort(key=lambda r: RISK_ORDER.get(r["risk"], 9))

    summary = {"high": 0, "medium": 0, "low": 0, "unknown": 0}
    for r in results:
        summary[r["risk"].lower()] += 1

    return {
        "total_posts": len(results),
        "summary": summary,
        "results": results,
        "privacy": {
            "posts_found": len(posts),
            "posts_analyzed": len(results) - summary["unknown"],
            "private_messages_analyzed": 0,
            **file_stats,
        },
        "ai_mode": AI_MODE,
        "processing_seconds": round(time.time() - started, 2),
    }