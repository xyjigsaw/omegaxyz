#!/usr/bin/env python3
import argparse
import gzip
import hashlib
import html
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote

try:
    from bs4 import BeautifulSoup, NavigableString
except Exception:
    BeautifulSoup = None
    NavigableString = None


POST_COLUMNS = [
    "ID", "post_author", "post_date", "post_date_gmt", "post_content", "post_title",
    "post_excerpt", "post_status", "comment_status", "ping_status", "post_password",
    "post_name", "to_ping", "pinged", "post_modified", "post_modified_gmt",
    "post_content_filtered", "post_parent", "guid", "menu_order", "post_type",
    "post_mime_type", "comment_count",
]
COMMENT_COLUMNS = [
    "comment_ID", "comment_post_ID", "comment_author", "comment_author_email",
    "comment_author_url", "comment_author_IP", "comment_date", "comment_date_gmt",
    "comment_content", "comment_karma", "comment_approved", "comment_agent",
    "comment_type", "comment_parent", "user_id", "comment_mail_notify",
]
POSTMETA_COLUMNS = ["meta_id", "post_id", "meta_key", "meta_value"]
TERMS_COLUMNS = ["term_id", "name", "slug", "term_group", "term_type", "term_font_icon"]
TERM_TAX_COLUMNS = ["term_taxonomy_id", "term_id", "taxonomy", "description", "parent", "count"]
TERM_REL_COLUMNS = ["object_id", "term_taxonomy_id", "term_order"]
OPTIONS_COLUMNS = ["option_id", "option_name", "option_value", "autoload"]

TABLES = {
    "wp1_posts": POST_COLUMNS,
    "wp1_comments": COMMENT_COLUMNS,
    "wp1_postmeta": POSTMETA_COLUMNS,
    "wp1_terms": TERMS_COLUMNS,
    "wp1_term_taxonomy": TERM_TAX_COLUMNS,
    "wp1_term_relationships": TERM_REL_COLUMNS,
    "wp1_options": OPTIONS_COLUMNS,
}

CDN = "https://cdn.omegaxyz.com"
UPLOAD_URL_PATTERNS = [
    re.compile(r"https?://(?:www\.)?omegaxyz\.com/wp-content/uploads/", re.I),
    re.compile(r"https?://120\.26\.77\.114/wp-content/uploads/", re.I),
    re.compile(r"https?://120\.24\.217\.209/wp-content/uploads/", re.I),
]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backup-dir", default="..")
    parser.add_argument("--output", default="data/site.json")
    parser.add_argument("--translation-cache", default="data/translations.json")
    parser.add_argument("--extract-media", default="")
    parser.add_argument("--translate", action="store_true")
    parser.add_argument("--provider", choices=["argos", "google"], default="argos")
    parser.add_argument("--limit", type=int, default=0, help="Debug limit for posts/pages")
    return parser.parse_args()


def find_db(backup_dir):
    matches = sorted(Path(backup_dir).glob("*-db.gz"))
    if not matches:
        raise FileNotFoundError("No *-db.gz backup found")
    return matches[0]


def sql_unescape(value):
    out = []
    i = 0
    while i < len(value):
        ch = value[i]
        if ch == "\\" and i + 1 < len(value):
            nxt = value[i + 1]
            out.append({
                "0": "\0",
                "n": "\n",
                "r": "\r",
                "t": "\t",
                "b": "\b",
                "Z": "\x1a",
            }.get(nxt, nxt))
            i += 2
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def parse_values(values_sql):
    rows = []
    i = 0
    n = len(values_sql)
    while i < n:
        while i < n and values_sql[i] not in "(":
            i += 1
        if i >= n:
            break
        i += 1
        row = []
        token = []
        quoted = False
        was_quoted = False
        while i < n:
            ch = values_sql[i]
            if quoted:
                if ch == "\\" and i + 1 < n:
                    token.append(ch)
                    token.append(values_sql[i + 1])
                    i += 2
                    continue
                if ch == "'":
                    quoted = False
                    i += 1
                    continue
                token.append(ch)
                i += 1
                continue
            if ch == "'":
                quoted = True
                was_quoted = True
                i += 1
                continue
            if ch == ",":
                raw = "".join(token).strip()
                row.append(sql_unescape(raw) if was_quoted else (None if raw.upper() == "NULL" else raw))
                token = []
                was_quoted = False
                i += 1
                continue
            if ch == ")":
                raw = "".join(token).strip()
                row.append(sql_unescape(raw) if was_quoted else (None if raw.upper() == "NULL" else raw))
                rows.append(row)
                i += 1
                break
            token.append(ch)
            i += 1
    return rows


def iter_insert_statements(db_path):
    current = []
    table = None
    prefix = "INSERT INTO `"
    with gzip.open(db_path, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if table is None:
                if not line.startswith(prefix):
                    continue
                candidate = line[len(prefix):].split("`", 1)[0]
                if candidate not in TABLES:
                    continue
                table = candidate
                current = [line]
            else:
                current.append(line)
            if table and line.rstrip().endswith(";"):
                yield table, "".join(current)
                table = None
                current = []


def parse_database(db_path):
    data = {name: [] for name in TABLES}
    for table, statement in iter_insert_statements(db_path):
        values = statement.split(" VALUES ", 1)[1].rstrip().rstrip(";")
        columns = TABLES[table]
        for row in parse_values(values):
            if len(row) != len(columns):
                raise ValueError(f"{table}: expected {len(columns)} values, got {len(row)}")
            data[table].append(dict(zip(columns, row)))
    return data


def int_value(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return datetime(1970, 1, 1)


def slugify(value, fallback):
    value = unquote(value or "").strip().strip("/")
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"[^\w\-\u4e00-\u9fff%]+", "-", value, flags=re.U)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or fallback


def rewrite_upload_urls(text):
    for pattern in UPLOAD_URL_PATTERNS:
        text = pattern.sub(CDN + "/", text)
    return text


def clean_shortcodes(text):
    text = text.replace("[toc]", '<nav class="inline-toc side-box" data-toc></nav>')
    text = text.replace("[mView]", "")
    text = re.sub(r"\[latex\](.*?)\[/latex\]", lambda m: r"\(" + m.group(1).strip() + r"\)", text, flags=re.S)
    text = re.sub(r"\[siteorigin_widget[^\]]*\]\s*<input[^>]*>\s*\[/siteorigin_widget\]", "", text, flags=re.S)
    text = re.sub(r"\[siteorigin_widget[^\]]*\]\s*<input[^>]*/>\s*\[/siteorigin_widget\]", "", text, flags=re.S)
    text = re.sub(r"\[/?su_[^\]]+\]", "", text)
    return text


def clean_html(content):
    content = rewrite_upload_urls(content or "")
    content = clean_shortcodes(content)
    content = re.sub(r"<pre([^>]*)class=\"([^\"]*lang:([a-zA-Z0-9_+#-]+)[^\"]*)\"([^>]*)>", r'<pre\1\4><code class="language-\3">', content)
    content = re.sub(r"</pre>", "</code></pre>", content)
    return content


def text_excerpt(markup, length=170):
    if BeautifulSoup:
        soup = BeautifulSoup(markup or "", "html.parser")
        for tag in soup(["script", "style", "pre", "code"]):
            tag.decompose()
        text = soup.get_text(" ", strip=True)
    else:
        text = re.sub(r"<[^>]+>", " ", markup or "")
    text = html.unescape(re.sub(r"\s+", " ", text)).strip()
    if len(text) <= length:
        return text
    return text[:length].rstrip() + "..."


def has_cjk(text):
    return bool(re.search(r"[\u3400-\u9fff]", text or ""))


class Translator:
    def __init__(self, cache_path, enabled, provider="argos"):
        self.enabled = enabled
        self.provider = provider
        self.cache_path = Path(cache_path)
        self.cache = {}
        self.translate_func = None
        self.fallback_func = None
        if self.cache_path.exists():
            self.cache = json.loads(self.cache_path.read_text(encoding="utf-8"))
        if enabled and provider == "argos":
            from argostranslate import translate
            self.translate_func = lambda text: translate.translate(text, "zh", "en")
        elif enabled and provider == "google":
            from deep_translator import GoogleTranslator
            from argostranslate import translate as argos_translate
            google = GoogleTranslator(source="zh-CN", target="en")
            self.translate_func = google.translate
            self.fallback_func = lambda text: argos_translate.translate(text, "zh", "en")

    def save(self):
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(json.dumps(self.cache, ensure_ascii=False, indent=2), encoding="utf-8")

    def text(self, value):
        value = value or ""
        if not self.enabled or not has_cjk(value):
            return value
        protected = []

        def protect(match):
            protected.append(match.group(0))
            return f" __KEEP_{len(protected) - 1}__ "

        safe = re.sub(r"(\$\$.*?\$\$|\$[^$\n]{1,220}\$|\\\(.+?\\\)|\\\[.+?\\\])", protect, value, flags=re.S)
        key = hashlib.sha256(safe.encode("utf-8")).hexdigest()
        if key not in self.cache:
            chunks = [p for p in re.split(r"(\n{2,})", safe) if p]
            translated = []
            for chunk in chunks:
                if not has_cjk(chunk):
                    translated.append(chunk)
                    continue
                translated.append(self.translate_chunk(chunk[:4500]))
            self.cache[key] = "".join(translated)
        result = self.cache[key]
        for idx, original in enumerate(protected):
            result = result.replace(f"__KEEP_{idx}__", original)
        return result

    def translate_chunk(self, chunk):
        try:
            return self.translate_func(chunk)
        except Exception:
            if self.fallback_func:
                try:
                    return self.fallback_func(chunk)
                except Exception:
                    pass
            return chunk

    def html(self, markup):
        if not self.enabled or not has_cjk(markup):
            return markup
        if not BeautifulSoup:
            return self.text(markup)
        soup = BeautifulSoup(markup, "html.parser")
        blocked = {"pre", "code", "script", "style", "kbd", "samp"}
        for node in soup.find_all(string=True):
            if not isinstance(node, NavigableString):
                continue
            if node.parent and node.parent.name in blocked:
                continue
            value = str(node)
            if not has_cjk(value) or not value.strip():
                continue
            node.replace_with(self.text(value))
        return str(soup)


def build_terms(raw):
    terms = {int_value(t["term_id"]): t for t in raw["wp1_terms"]}
    tax = {int_value(t["term_taxonomy_id"]): t for t in raw["wp1_term_taxonomy"]}
    rels = defaultdict(list)
    for rel in raw["wp1_term_relationships"]:
        rels[int_value(rel["object_id"])].append(int_value(rel["term_taxonomy_id"]))
    return terms, tax, rels


def term_list(post_id, rels, tax, terms, taxonomy):
    items = []
    seen = set()
    for tax_id in rels.get(post_id, []):
        item = tax.get(tax_id)
        if not item or item.get("taxonomy") != taxonomy:
            continue
        term = terms.get(int_value(item["term_id"]))
        if not term:
            continue
        slug = slugify(term.get("slug"), str(term["term_id"]))
        if slug in seen:
            continue
        seen.add(slug)
        items.append({"name": html.unescape(term.get("name") or slug), "slug": slug})
    return items


def media_from_meta(raw):
    attached = {}
    thumbs = {}
    for meta in raw["wp1_postmeta"]:
        key = meta["meta_key"]
        post_id = int_value(meta["post_id"])
        if key == "_wp_attached_file":
            attached[post_id] = rewrite_upload_urls(CDN + "/" + meta["meta_value"].lstrip("/"))
        elif key == "_thumbnail_id":
            thumbs[post_id] = int_value(meta["meta_value"])
    return attached, thumbs


def make_post_url(post):
    dt = parse_date(post["post_date"])
    slug = slugify(post["post_name"], str(post["ID"]))
    if post["post_type"] == "post":
        return f"{dt:%Y/%m/%d}/{slug}/"
    return f"{slug}/"


def migrate(raw, translator, limit=0):
    terms, tax, rels = build_terms(raw)
    attached, thumbs = media_from_meta(raw)
    options = {o["option_name"]: o["option_value"] for o in raw["wp1_options"]}
    published = [
        p for p in raw["wp1_posts"]
        if p["post_status"] == "publish" and p["post_type"] in ("post", "page") and not p["post_password"]
    ]
    published.sort(key=lambda p: parse_date(p["post_date"]), reverse=True)
    if limit:
        published = published[:limit]
    published_ids = {int_value(p["ID"]) for p in published}

    comments_by_post = defaultdict(list)
    for c in raw["wp1_comments"]:
        post_id = int_value(c["comment_post_ID"])
        if post_id not in published_ids or c["comment_approved"] != "1" or c["comment_type"] not in ("", "comment"):
            continue
        content_zh = html.escape(c["comment_content"]).replace("\n", "<br>")
        comments_by_post[post_id].append({
            "id": int_value(c["comment_ID"]),
            "parent": int_value(c["comment_parent"]),
            "author": html.escape(c["comment_author"] or "Anonymous"),
            "url": c["comment_author_url"] if c["comment_author_url"].startswith(("http://", "https://")) else "",
            "date": c["comment_date"],
            "content_zh": content_zh,
            "content_en": content_zh,
        })

    entries = []
    for index, p in enumerate(published, 1):
        post_id = int_value(p["ID"])
        if translator.enabled:
            print(f"translating {index}/{len(published)} #{post_id} {p['post_type']} {p['post_title'][:70]}", file=sys.stderr)
        content_zh = clean_html(p["post_content"])
        title_zh = html.unescape(p["post_title"] or "Untitled")
        excerpt_zh = html.unescape(p["post_excerpt"] or text_excerpt(content_zh))
        categories = term_list(post_id, rels, tax, terms, "category")
        tags = term_list(post_id, rels, tax, terms, "post_tag")
        thumb = attached.get(thumbs.get(post_id, 0), "")
        entry = {
            "id": post_id,
            "type": p["post_type"],
            "title_zh": title_zh,
            "title_en": translator.text(title_zh),
            "excerpt_zh": excerpt_zh,
            "excerpt_en": translator.text(excerpt_zh),
            "content_zh": content_zh,
            "content_en": translator.html(content_zh),
            "date": p["post_date"],
            "modified": p["post_modified"],
            "slug": slugify(p["post_name"], str(post_id)),
            "url": make_post_url(p),
            "categories": categories,
            "tags": tags,
            "comments": comments_by_post.get(post_id, []),
            "thumbnail": thumb,
        }
        entries.append(entry)
        if translator.enabled and index % 5 == 0:
            translator.save()
            print(f"translated {index}/{len(published)} entries", file=sys.stderr)

    site = {
        "meta": {
            "name": options.get("blogname", "OmegaXYZ"),
            "description_zh": options.get("blogdescription", "徐奕的专栏"),
            "description_en": translator.text(options.get("blogdescription", "Xu Yi's column")),
            "source": "https://omegaxyz.com",
            "cdn": CDN,
            "generated_at": datetime.utcnow().isoformat() + "Z",
        },
        "entries": entries,
        "summary": {
            "posts": sum(1 for e in entries if e["type"] == "post"),
            "pages": sum(1 for e in entries if e["type"] == "page"),
            "comments": sum(len(e["comments"]) for e in entries),
            "categories": len({c["slug"] for e in entries for c in e["categories"]}),
            "tags": len({t["slug"] for e in entries for t in e["tags"]}),
        },
    }
    return site


def extract_media(backup_dir, destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    archives = sorted(Path(backup_dir).glob("*-uploads*.zip"))
    total = 0
    for archive in archives:
        with zipfile.ZipFile(archive) as zf:
            for member in zf.infolist():
                if member.is_dir():
                    continue
                target = destination / member.filename
                if target.exists() and target.stat().st_size == member.file_size:
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member) as src, target.open("wb") as dst:
                    shutil.copyfileobj(src, dst)
                total += 1
        print(f"extracted {archive.name}", file=sys.stderr)
    return total


def write_media_manifest(root, output):
    root = Path(root)
    items = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            items.append({
                "key": rel,
                "size": path.stat().st_size,
                "content_type": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
            })
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(items)


def main():
    args = parse_args()
    db_path = find_db(args.backup_dir)
    print(f"reading {db_path}", file=sys.stderr)
    raw = parse_database(db_path)
    translator = Translator(args.translation_cache, args.translate, args.provider)
    site = migrate(raw, translator, args.limit)
    translator.save()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(site, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {output} with {site['summary']}", file=sys.stderr)
    if args.extract_media:
        count = extract_media(args.backup_dir, args.extract_media)
        manifest_count = write_media_manifest(args.extract_media, "data/media-manifest.json")
        print(f"extracted/manifest media files: {count}/{manifest_count}", file=sys.stderr)


if __name__ == "__main__":
    main()
