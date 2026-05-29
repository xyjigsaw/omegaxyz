#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse


CDN = "https://cdn.omegaxyz.com"


def collect_urls(root):
    pattern = re.compile(r"https://cdn\.omegaxyz\.com/[^\s\"'<>)]*", re.I)
    urls = set()
    for file in sorted(root.rglob("*")):
        if not file.is_file():
            continue
        if file.suffix.lower() not in {".html", ".json", ".xml", ".txt", ".css", ".js"}:
            continue
        text = file.read_text(encoding="utf-8", errors="ignore")
        for match in pattern.finditer(text):
            urls.add(match.group(0).rstrip(".,;"))
    return sorted(urls)


def build_manifest(urls):
    assets = []
    for url in urls:
        parsed = urlparse(url)
        assets.append({
            "path": parsed.path.lstrip("/"),
            "url": url,
        })
    return {
        "cdn": CDN,
        "count": len(assets),
        "assets": assets,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate a Cloudflare CDN media manifest from generated site files.")
    parser.add_argument("--root", default="docs", help="Directory to scan, usually docs after build_site.py")
    parser.add_argument("--output", default="data/media-cdn.json")
    args = parser.parse_args()

    root = Path(args.root)
    output = Path(args.output)
    urls = collect_urls(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(build_manifest(urls), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(urls)} CDN media URLs to {output}")


if __name__ == "__main__":
    main()
