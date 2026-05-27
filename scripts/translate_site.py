#!/usr/bin/env python3
import argparse
import hashlib
import html
import json
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString
from deep_translator import GoogleTranslator


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/site.notranslate.json")
    parser.add_argument("--output", default="data/site.json")
    parser.add_argument("--cache", default="data/translations.json")
    parser.add_argument("--workers", type=int, default=8)
    return parser.parse_args()


def has_cjk(text):
    return bool(re.search(r"[\u3400-\u9fff]", text or ""))


class ParallelTranslator:
    def __init__(self, cache_path):
        self.cache_path = Path(cache_path)
        self.cache = {}
        self.lock = threading.Lock()
        self.local = threading.local()
        if self.cache_path.exists():
            self.cache = json.loads(self.cache_path.read_text(encoding="utf-8"))

    def save(self):
        with self.lock:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.cache_path.write_text(json.dumps(self.cache, ensure_ascii=False, indent=2), encoding="utf-8")

    def client(self):
        if not hasattr(self.local, "client"):
            self.local.client = GoogleTranslator(source="zh-CN", target="en")
        return self.local.client

    def text(self, value):
        value = value or ""
        if not has_cjk(value):
            return value
        protected = []

        def protect(match):
            protected.append(match.group(0))
            return f" __KEEP_{len(protected) - 1}__ "

        safe = re.sub(r"(\$\$.*?\$\$|\$[^$\n]{1,220}\$|\\\(.+?\\\)|\\\[.+?\\\])", protect, value, flags=re.S)
        key = hashlib.sha256(safe.encode("utf-8")).hexdigest()
        with self.lock:
            cached = self.cache.get(key)
        if cached is None:
            parts = []
            for chunk in split_text(safe):
                if not has_cjk(chunk):
                    parts.append(chunk)
                    continue
                try:
                    parts.append(self.client().translate(chunk))
                except Exception:
                    parts.append(chunk)
            cached = "".join(parts)
            with self.lock:
                self.cache[key] = cached
        result = cached
        for idx, original in enumerate(protected):
            result = result.replace(f"__KEEP_{idx}__", original)
        return result

    def markup(self, markup):
        if not has_cjk(markup):
            return markup
        soup = BeautifulSoup(markup or "", "html.parser")
        blocked = {"pre", "code", "script", "style", "kbd", "samp"}
        for node in soup.find_all(string=True):
            if not isinstance(node, NavigableString):
                continue
            if node.parent and node.parent.name in blocked:
                continue
            value = str(node)
            if value.strip() and has_cjk(value):
                node.replace_with(self.text(value))
        return str(soup)


def split_text(text, limit=4300):
    paragraphs = re.split(r"(\n{2,})", text)
    chunks = []
    current = ""
    for part in paragraphs:
        if len(current) + len(part) <= limit:
            current += part
            continue
        if current:
            chunks.append(current)
            current = ""
        while len(part) > limit:
            chunks.append(part[:limit])
            part = part[limit:]
        current = part
    if current:
        chunks.append(current)
    return chunks


def translate_entry(entry, translator):
    entry = dict(entry)
    entry["title_en"] = translator.text(entry.get("title_zh", ""))
    entry["excerpt_en"] = translator.text(entry.get("excerpt_zh", ""))
    entry["content_en"] = translator.markup(entry.get("content_zh", ""))
    for comment in entry.get("comments", []):
        comment["content_en"] = comment.get("content_zh", "")
    return entry


def main():
    args = parse_args()
    site = json.loads(Path(args.input).read_text(encoding="utf-8"))
    translator = ParallelTranslator(args.cache)
    entries = site["entries"]
    translated = [None] * len(entries)
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(translate_entry, entry, translator): idx for idx, entry in enumerate(entries)}
        completed = 0
        for future in as_completed(futures):
            idx = futures[future]
            translated[idx] = future.result()
            completed += 1
            if completed % 10 == 0:
                translator.save()
                print(f"translated {completed}/{len(entries)}", file=sys.stderr)
    site["entries"] = translated
    translator.save()
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(site, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
