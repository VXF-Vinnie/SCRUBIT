"""
SCRUBIT archive parser.
Turns an uploaded .json or .zip into standard SCRUBIT posts:
    {"id": str, "platform": str, "date": str | None, "text": str}
Privacy: read in memory only (never extracted to disk). Only post files are
opened; anything that looks like messages/inbox is skipped without reading.
"""
import io
import json
import zipfile
from datetime import datetime, timezone

IGNORED_PATH_HINTS = ("message", "inbox", "chat", "password", "login", "account_information")
POST_FILE_NAMES = ("posts.json",)
INSTAGRAM_POST_PREFIX = "posts_"


class ArchiveError(ValueError):
    """Raised for files we can't parse. Message is safe to show the user."""


def parse_archive(filename, data):
    name = (filename or "").lower()
    stats = {"files_in_archive": 0, "files_read": 0, "files_ignored": 0}
    if name.endswith(".json"):
        stats["files_in_archive"] = stats["files_read"] = 1
        posts = _parse_json_bytes(data, source=name)
    elif name.endswith(".zip"):
        posts = _parse_zip(data, stats)
    else:
        raise ArchiveError("Unsupported file type. Upload a .json or .zip file.")
    if not posts:
        raise ArchiveError("No posts with text were found in the upload.")
    return posts, stats


def _parse_zip(data, stats):
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        raise ArchiveError("That file is not a valid ZIP archive.")
    posts = []
    with zf:
        for info in zf.infolist():
            if info.is_dir() or "__MACOSX" in info.filename:
                continue
            stats["files_in_archive"] += 1
            path = info.filename.lower()
            base = path.rsplit("/", 1)[-1]
            is_post_file = base in POST_FILE_NAMES or (
                base.startswith(INSTAGRAM_POST_PREFIX) and base.endswith(".json"))
            if not is_post_file or any(h in path for h in IGNORED_PATH_HINTS):
                stats["files_ignored"] += 1
                continue
            stats["files_read"] += 1
            posts.extend(_parse_json_bytes(zf.read(info), source=info.filename))
    seen = set()
    for i, p in enumerate(posts, start=1):
        if p["id"] in seen:
            p["id"] = f"post_{i:03d}"
        seen.add(p["id"])
    return posts


def _parse_json_bytes(data, source):
    try:
        raw = json.loads(data.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ArchiveError(f"Could not read {source}: not valid JSON.")
    if isinstance(raw, dict) and isinstance(raw.get("posts"), list):
        raw = raw["posts"]
    if not isinstance(raw, list):
        raise ArchiveError(f"{source} should contain a list of posts.")
    posts = []
    for i, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            continue
        post = _from_scrubit(item, i) if "text" in item else _from_instagram(item, i)
        if post and post["text"].strip():
            posts.append(post)
    return posts


def _from_scrubit(item, i):
    return {
        "id": str(item.get("id") or f"post_{i:03d}"),
        "platform": str(item.get("platform") or "unknown").lower(),
        "date": item.get("date") or None,
        "text": str(item.get("text") or ""),
    }


def _from_instagram(item, i):
    """Best-effort parser for Instagram's posts_N.json export."""
    media = item.get("media") or [{}]
    first = media[0] if isinstance(media, list) and media else {}
    text = item.get("title") or first.get("title") or ""
    ts = item.get("creation_timestamp") or first.get("creation_timestamp")
    if not text:
        return None
    return {"id": f"post_{i:03d}", "platform": "instagram",
            "date": _ts_to_date(ts), "text": _fix_meta_encoding(text)}


def _ts_to_date(ts):
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d")
    except (TypeError, ValueError, OSError):
        return None


def _fix_meta_encoding(s):
    """Meta exports double-encode UTF-8 (garbled emoji). Undo it."""
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s