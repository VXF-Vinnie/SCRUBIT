"""SCRUBIT backend. Run: uvicorn main:app --reload --port 8000"""

import time

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from ai_adapter import AI_MODE, analyze
from parser import ArchiveError, parse_archive


# ==========================================
# CONFIGURATION
# ==========================================

MAX_UPLOAD_BYTES = 50 * 1024 * 1024

# Controls the order posts appear in results.
# Serious posts appear first, followed by posts
# worth reviewing, then clear posts.
RISK_ORDER = {
    "HIGH": 0,
    "LOW": 1,
    "CLEAR": 2,
    "UNKNOWN": 3
}


# ==========================================
# FASTAPI APPLICATION
# ==========================================

app = FastAPI(title="SCRUBIT")


# Allow the local frontend to communicate
# with the local backend.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/health")
def health():

    return {
        "status": "ok",
        "ai_mode": AI_MODE
    }


# ==========================================
# SCAN SOCIAL MEDIA ARCHIVE
# ==========================================

@app.post("/scan")
def scan(file: UploadFile = File(...)):

    # --------------------------------------
    # Read uploaded archive
    # --------------------------------------

    data = file.file.read(
        MAX_UPLOAD_BYTES + 1
    )


    # --------------------------------------
    # Validate file size
    # --------------------------------------

    if len(data) > MAX_UPLOAD_BYTES:

        raise HTTPException(
            413,
            "File too large (max 50 MB)."
        )


    # --------------------------------------
    # Parse archive
    # --------------------------------------

    try:

        posts, file_stats = parse_archive(
            file.filename,
            data
        )

    except ArchiveError as e:

        raise HTTPException(
            400,
            str(e)
        )


    # --------------------------------------
    # Start analysis timer
    # --------------------------------------

    started = time.time()


    # --------------------------------------
    # Analyze posts with local AI
    # --------------------------------------

    results = [
        {
            **post,
            **analyze(post)
        }

        for post in posts
    ]


    # --------------------------------------
    # Sort by risk
    # --------------------------------------

    results.sort(
        key=lambda result:
            RISK_ORDER.get(
                result["risk"],
                9
            )
    )


    # --------------------------------------
    # Create summary
    # --------------------------------------

    summary = {
        "high": 0,
        "low": 0,
        "clear": 0,
        "unknown": 0
    }


    for result in results:

        risk = result["risk"].lower()

        if risk in summary:
            summary[risk] += 1

        else:
            summary["unknown"] += 1


    # --------------------------------------
    # API RESPONSE
    # --------------------------------------

    return {

        "total_posts":
            len(results),

        "summary":
            summary,

        "results":
            results,

        "privacy": {

            "posts_found":
                len(posts),

            "posts_analyzed":
                len(results)
                - summary["unknown"],

            "private_messages_analyzed":
                0,

            **file_stats,
        },

        "ai_mode":
            AI_MODE,

        "processing_seconds":
            round(
                time.time() - started,
                2
            ),
    }