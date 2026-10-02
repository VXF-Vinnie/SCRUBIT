"""
SCRUBIT archive parser.

Turns an uploaded .json, .js, or .zip into a list of standard SCRUBIT posts:
    {"id": str, "platform": str, "date": str | None, "text": str}

Privacy: the archive is read in memory only (never extracted to disk), and
only post files are opened. Anything that looks like messages/inbox is skipped
without being read.
"""
import io
import re
import json
import zipfile
from datetime import datetime, timezone

# Path fragments we refuse to open at all (private messages, account data).
IGNORED_PATH_HINTS = ("message", "inbox", "chat", "password", "login", "account_information")

# Files we will try to parse as posts.
POST_FILE_NAMES = ("posts.json",)              # synthetic demo format
INSTAGRAM_POST_PREFIX = "posts_"               # real IG export: .../content/posts_1.json
X_TWEETS_FILE = re.compile(r"^tweets?(-part\d+)?\.js$")  # X export: data/tweets.js


class ArchiveError(ValueError):
    """Raised for files we can't parse. Message is safe to show the user."""


def parse_archive(filename: str, data: bytes) -> tuple[list[dict], dict]:
    """Returns (posts, stats). stats is used for the privacy panel."""
    name = (filename or "").lower()
    stats = {"files_in_archive": 0, "files_read": 0, "files_ignored": 0}

    if name.endswith(".json"):
        stats["files_in_archive"] = stats["files_read"] = 1
        posts = _parse_json_bytes(data, source=name)
    elif name.endswith(".js"):
        stats["files_in_archive"] = stats["files_read"] = 1
        posts = _parse_x_js(data, source=name)
    elif name.endswith(".zip"):
        posts = _parse_zip(data, stats)
    else:
        raise ArchiveError("Unsupported file type. Upload a .json, .js, or .zip file.")

    if not posts:
        raise ArchiveError("No posts with text were found in the upload.")
    return posts, stats


def _parse_zip(data: bytes, stats: dict) -> list[dict]:
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        raise ArchiveError("That file is not a valid ZIP archive.")

    posts: list[dict] = []
    with zf:
        for info in zf.infolist():
            if info.is_dir() or "__MACOSX" in info.filename:
                continue
            stats["files_in_archive"] += 1
            path = info.filename.lower()
            base = path.rsplit("/", 1)[-1]

            is_x_file = bool(X_TWEETS_FILE.match(base))
            is_post_file = is_x_file or base in POST_FILE_NAMES or (
                base.startswith(INSTAGRAM_POST_PREFIX) and base.endswith(".json")
            )
            if not is_post_file or any(h in path for h in IGNORED_PATH_HINTS):
                stats["files_ignored"] += 1
                continue

            stats["files_read"] += 1
            if is_x_file:
                posts.extend(_parse_x_js(zf.read(info), source=info.filename))
            else:
                posts.extend(_parse_json_bytes(zf.read(info), source=info.filename))

    # Guarantee unique ids across multiple files.
    seen = set()
    for i, p in enumerate(posts, start=1):
        if p["id"] in seen:
            p["id"] = f"post_{i:03d}"
        seen.add(p["id"])
    return posts


def _parse_json_bytes(data: bytes, source: str) -> list[dict]:
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


def _from_scrubit(item: dict, i: int) -> dict:
    """Already in (or close to) the standard format."""
    return {
        "id": str(item.get("id") or f"post_{i:03d}"),
        "platform": str(item.get("platform") or "unknown").lower(),
        "date": item.get("date") or None,
        "text": str(item.get("text") or ""),
    }


def _from_instagram(item: dict, i: int) -> dict | None:
    """Best-effort parser for Instagram's posts_N.json export format.
    Caption lives in item["title"] (multi-photo posts) or media[0]["title"]."""
    media = item.get("media") or [{}]
    first = media[0] if isinstance(media, list) and media else {}
    text = item.get("title") or first.get("title") or ""
    ts = item.get("creation_timestamp") or first.get("creation_timestamp")
    if not text:
        return None
    return {
        "id": f"post_{i:03d}",
        "platform": "instagram",
        "date": _ts_to_date(ts),
        "text": _fix_meta_encoding(text),
    }


def _ts_to_date(ts) -> str | None:
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d")
    except (TypeError, ValueError, OSError):
        return None


def _fix_meta_encoding(s: str) -> str:
    """Meta exports double-encode UTF-8 (garbled emoji). Undo it."""
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def _parse_x_js(data: bytes, source: str) -> list[dict]:
    """X/Twitter archive: data/tweets.js is JavaScript like
    `window.YTD.tweets.part0 = [ {"tweet": {...}}, ... ];`. Strip the prefix,
    parse the JSON list, and ignore anything after it (like a trailing ;)."""
    try:
        text = data.decode("utf-8-sig")
        raw, _ = json.JSONDecoder().raw_decode(text[text.index("["):])
    except (UnicodeDecodeError, ValueError):
        raise ArchiveError(f"Could not read {source}: not a valid X/Twitter tweets file.")
    posts = []
    for item in raw if isinstance(raw, list) else []:
        t = item.get("tweet", item) if isinstance(item, dict) else None
        if not isinstance(t, dict):
            continue
        body = t.get("full_text") or t.get("text") or ""
        if not body.strip():
            continue
        posts.append({
            "id": f"tweet_{t.get('id_str') or t.get('id') or len(posts) + 1}",
            "platform": "x",
            "date": _x_date(t.get("created_at")),
            "text": body,
        })
    return posts


def _x_date(s) -> str | None:
    """X uses dates like 'Wed Oct 10 20:19:24 +0000 2018'."""
    try:
        return datetime.strptime(s, "%a %b %d %H:%M:%S %z %Y").strftime("%Y-%m-%d")
    except (TypeError, ValueError):
        return None