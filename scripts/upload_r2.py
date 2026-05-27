#!/usr/bin/env python3
import argparse
import json
import mimetypes
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

ALLOWED_SUFFIXES = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".avif", ".ico",
    ".pdf", ".mp3", ".m4a", ".wav", ".ogg", ".mp4", ".webm",
    ".zip", ".rar", ".7z", ".tar", ".gz",
    ".txt", ".csv",
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--account-id", required=True)
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--prefix", default="")
    parser.add_argument("--state", default=".cache/r2-uploaded.json")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--max-size-mb", type=float, default=0)
    return parser.parse_args()


def load_state(path):
    path = Path(path)
    if path.exists():
        return set(json.loads(path.read_text(encoding="utf-8")))
    return set()


def save_state(path, state):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(state), indent=2), encoding="utf-8")


def upload_file(account_id, bucket, token, key, file_path):
    encoded_key = quote(key, safe="/-._~")
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/r2/buckets/{bucket}/objects/{encoded_key}"
    content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    data = file_path.read_bytes()
    req = Request(url, method="PUT", data=data, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": content_type,
        "Cache-Control": "public, max-age=31536000, immutable",
    })
    with urlopen(req, timeout=120) as response:
        body = response.read()
        if response.status >= 300:
            raise RuntimeError(body.decode("utf-8", "replace"))


def main():
    args = parse_args()
    token = os.environ.get("CF_API_TOKEN")
    if not token:
        raise SystemExit("Set CF_API_TOKEN in the environment")
    root = Path(args.root)
    state = load_state(args.state)
    lock = threading.Lock()
    files = [
        p for p in sorted(root.rglob("*"))
        if p.is_file() and p.suffix.lower() in ALLOWED_SUFFIXES
    ]
    if args.max_size_mb:
        max_bytes = int(args.max_size_mb * 1024 * 1024)
        files = [p for p in files if p.stat().st_size <= max_bytes]
    pending = []
    for path in files:
        rel = path.relative_to(root).as_posix()
        key = (args.prefix.rstrip("/") + "/" + rel).lstrip("/")
        signature = f"{key}:{path.stat().st_size}:{int(path.stat().st_mtime)}"
        if signature in state:
            continue
        pending.append((key, path, signature))
        if args.limit and len(pending) >= args.limit:
            break

    def upload_one(item):
        key, path, signature = item
        for attempt in range(4):
            try:
                upload_file(args.account_id, args.bucket, token, key, path)
                return signature
            except Exception:
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt)
        return signature

    done = 0
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = [executor.submit(upload_one, item) for item in pending]
        for future in as_completed(futures):
            signature = future.result()
            with lock:
                state.add(signature)
                done += 1
                if done % 10 == 0:
                    save_state(args.state, state)
                    print(f"uploaded {done} new files", flush=True)
    save_state(args.state, state)
    print(f"uploaded {done} new files; {len(state)} total recorded")


if __name__ == "__main__":
    main()
