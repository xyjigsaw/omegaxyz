#!/usr/bin/env python3
import html
import json
import math
import re
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/site.json"
PUBLIC = ROOT / "public"
OUT = ROOT / "docs"
CDN = "https://cdn.omegaxyz.com"
SITE_URL = "https://omegaxyz.com"
SOURCE_HOSTS = {"omegaxyz.com", "www.omegaxyz.com", "en.omegaxyz.com"}

I18N = {
    "zh": {
        "tagline": "徐奕的专栏",
        "home": "主页",
        "archive": "文章",
        "pages": "页面",
        "categories": "分类",
        "tags": "标签",
        "search": "搜索",
        "latest": "最新笔记",
        "latest_desc": "近期更新与长期整理的技术、研究和知识工程笔记。",
        "featured": "知识结构",
        "comments": "评论",
        "toc": "目录",
        "all_posts": "全部文章",
        "all_pages": "全部页面",
        "language": "English",
        "search_placeholder": "搜索文章、页面、标签...",
        "explore": "探索知识库",
        "intro": "面向编程、机器学习、知识工程与数学的长期笔记库。",
    },
    "en": {
        "tagline": "Xu Yi's column",
        "home": "Home",
        "archive": "Archive",
        "pages": "Pages",
        "categories": "Categories",
        "tags": "Tags",
        "search": "Search",
        "latest": "Latest Notes",
        "latest_desc": "Recent updates and long-running notes on engineering, research, and knowledge systems.",
        "featured": "Knowledge Map",
        "comments": "Comments",
        "toc": "Contents",
        "all_posts": "All Posts",
        "all_pages": "All Pages",
        "language": "中文",
        "search_placeholder": "Search posts, pages, and tags...",
        "explore": "Explore the archive",
        "intro": "A long-running notebook for programming, machine learning, knowledge engineering, and mathematics.",
    },
}

TERM_EN = {
    "tech": "Technology",
    "machine-learning": "Machine Learning",
    "deep-learning": "Deep Learning",
    "nlp": "Natural Language Processing",
    "algorithm": "Algorithms",
    "database": "Databases",
    "data-structure": "Data Structures",
    "evolutionary-algorithm": "Evolutionary Algorithms",
    "math": "Mathematics",
    "programming": "Programming",
    "高级语言": "Programming Languages",
    "python": "Python",
    "c": "C",
    "cpp": "C++",
    "cc": "C & C++",
    "java": "Java",
    "linux": "Linux",
    "matlab": "MATLAB",
    "ideas": "Ideas",
    "software-engineering": "Software Engineering",
    "knowledge-graph": "Knowledge Graphs",
    "programmer": "Developer Life",
    "life": "Life",
    "essay": "Essays",
    "trans": "Reposts",
    "tools": "Tools",
    "web": "Web",
    "game": "Games",
}


def load_site():
    return json.loads(DATA.read_text(encoding="utf-8"))


def ensure_dir(path):
    path.parent.mkdir(parents=True, exist_ok=True)


def write(path, text):
    ensure_dir(path)
    path.write_text(text, encoding="utf-8")


def date_only(value):
    return value.split(" ", 1)[0]


def rel_url(from_file, target):
    from_dir = Path(from_file).parent
    return Path(
        __import__("os").path.relpath(target, from_dir)
    ).as_posix()


def page_file(path):
    clean = path.strip("/")
    if not clean:
        return OUT / "index.html"
    return OUT / clean / "index.html"


def site_url_for_file(file):
    try:
        rel = Path(file).resolve().relative_to(OUT.resolve()).as_posix()
    except ValueError:
        rel = "index.html"
    if rel == "index.html":
        path = ""
    elif rel.endswith("/index.html"):
        path = rel[:-len("index.html")]
    else:
        path = rel
    return SITE_URL.rstrip("/") + "/" + path


def path_to_file(path):
    return page_file(path)


def entry_path(entry, lang):
    return f"{lang}/{entry['url']}"


def term_path(kind, slug, lang):
    return f"{lang}/{kind}/{slug}/"


def archive_path(lang, page=1):
    return f"{lang}/archive/" if page == 1 else f"{lang}/archive/page/{page}/"


def esc(value):
    return html.escape(str(value or ""), quote=True)


def term_label(term, lang):
    if lang == "en":
        return TERM_EN.get(term["slug"], term["name"])
    return term["name"]


def normalize_legacy_path(value):
    parsed = urlparse(value)
    raw_path = parsed.path if parsed.scheme or parsed.netloc else value.split("?", 1)[0].split("#", 1)[0]
    path = unquote(raw_path).strip("/")
    if path and not path.endswith("/"):
        path += "/"
    return path


def build_legacy_map(site):
    legacy = {"": {"zh": "zh/", "en": "en/"}}
    for entry in site["entries"]:
        path = normalize_legacy_path(entry["url"])
        legacy[path] = {"zh": entry_path(entry, "zh"), "en": entry_path(entry, "en")}
    terms_by_kind = {"category": {}, "tag": {}}
    for entry in site["entries"]:
        for kind, key in (("category", "categories"), ("tag", "tags")):
            for term in entry[key]:
                terms_by_kind[kind][term["slug"]] = term
    for kind, collection in terms_by_kind.items():
        wp_kind = "category" if kind == "category" else "tag"
        for term in collection.values():
            path = normalize_legacy_path(f"{wp_kind}/{term['slug']}/")
            legacy[path] = {
                "zh": term_path(kind, term["slug"], "zh"),
                "en": term_path(kind, term["slug"], "en"),
            }
    return legacy


def internal_target(value, lang, legacy):
    if not value:
        return ""
    if value.startswith("//"):
        value = "https:" + value
    parsed = urlparse(value)
    if parsed.scheme in ("mailto", "tel", "javascript"):
        return ""
    if parsed.netloc and parsed.netloc.lower() not in SOURCE_HOSTS:
        return ""
    target_lang = "en" if parsed.netloc.lower() == "en.omegaxyz.com" else lang

    path = normalize_legacy_path(value)
    if path.startswith("wp-content/uploads/"):
        return CDN + "/" + path.removeprefix("wp-content/uploads/")
    if path in legacy:
        return legacy[path][target_lang]
    if path.startswith(("wp-admin/", "wp-login.php", "feed/", "comments/")):
        return f"{target_lang}/"
    if parsed.netloc.lower() in SOURCE_HOSTS or value.startswith("/"):
        return f"{target_lang}/search/"
    return ""


def rewrite_url(value, lang, current_file, legacy):
    cleaned = value.strip().strip("“”‘’")
    if re.match(r"^[A-Za-z]:[\\/]", cleaned):
        return "#"
    if cleaned != value and urlparse(cleaned if not cleaned.startswith("//") else "https:" + cleaned).scheme in ("http", "https"):
        value = cleaned
    target = internal_target(value, lang, legacy)
    if not target:
        return value
    if target.startswith("https://"):
        return target
    fragment = urlparse(value).fragment
    href = rel_url(current_file, path_to_file(target))
    return f"{href}#{fragment}" if fragment else href


def rewrite_srcset(value, lang, current_file, legacy):
    pieces = []
    for candidate in value.split(","):
        bits = candidate.strip().split()
        if not bits:
            continue
        bits[0] = rewrite_url(bits[0], lang, current_file, legacy)
        pieces.append(" ".join(bits))
    return ", ".join(pieces)


def rewrite_content(markup, lang, current_file, legacy):
    def repl(match):
        attr, quote_char, value = match.groups()
        if attr.lower() == "srcset":
            rewritten = rewrite_srcset(value, lang, current_file, legacy)
        else:
            rewritten = rewrite_url(value, lang, current_file, legacy)
        return f'{attr}={quote_char}{html.escape(rewritten, quote=True)}{quote_char}'

    return re.sub(r'\b(href|src|srcset)=(["\'])(.*?)\2', repl, markup or "", flags=re.I)


def strip_tags(markup):
    text = re.sub(r"<(script|style|pre|code)[^>]*>.*?</\1>", " ", markup or "", flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def first_image(entry):
    if entry.get("thumbnail"):
        return entry["thumbnail"]
    match = re.search(r'<img[^>]+src=(["\'])(.*?)\1', entry.get("content_zh", ""), flags=re.I)
    return match.group(2) if match else ""


def short_text(value, length=92):
    text = re.sub(r"\s+", " ", strip_tags(value)).strip()
    if len(text) <= length:
        return text
    return text[:length].rstrip() + "..."


def nav(current_file, lang, title, alt_path):
    t = I18N[lang]
    other = "en" if lang == "zh" else "zh"
    links = [
        (t["home"], f"{lang}/"),
        (t["archive"], archive_path(lang)),
        (t["pages"], f"{lang}/pages/"),
        (t["categories"], f"{lang}/categories/"),
        (t["search"], f"{lang}/search/"),
    ]
    link_html = "".join(
        f'<a href="{rel_url(current_file, path_to_file(path))}">{esc(label)}</a>' for label, path in links
    )
    alt = rel_url(current_file, path_to_file(alt_path)) if alt_path else rel_url(current_file, path_to_file(f"{other}/"))
    return f"""
    <header class="site-header">
      <nav class="nav">
        <a class="brand" href="{rel_url(current_file, path_to_file(f'{lang}/'))}">OmegaXYZ <span>{esc(t['tagline'])}</span></a>
        <div class="nav-links">
          {link_html}
          <a href="{alt}">{esc(t['language'])}</a>
          <button class="icon-button" type="button" data-theme-toggle aria-label="Theme">◐</button>
        </div>
      </nav>
    </header>
    """


def layout(current_file, lang, title, body, description="", alt_path=""):
    css = rel_url(current_file, OUT / "assets/site.css")
    js = rel_url(current_file, OUT / "assets/site.js")
    katex = "https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/katex.min.css"
    desc = description or I18N[lang]["intro"]
    canonical = site_url_for_file(current_file)
    other = "en" if lang == "zh" else "zh"
    alternate = site_url_for_file(path_to_file(alt_path)) if alt_path else site_url_for_file(path_to_file(f"{other}/"))
    return f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} · OmegaXYZ</title>
  <meta name="description" content="{esc(desc)}">
  <link rel="canonical" href="{esc(canonical)}">
  <link rel="alternate" hreflang="{other}" href="{esc(alternate)}">
  <link rel="alternate" hreflang="{lang}" href="{esc(canonical)}">
  <meta property="og:site_name" content="OmegaXYZ">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(title)} · OmegaXYZ">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:url" content="{esc(canonical)}">
  <link rel="icon" href="{rel_url(current_file, OUT / 'favicon.svg')}" type="image/svg+xml">
  <link rel="stylesheet" href="{katex}">
  <link rel="stylesheet" href="{css}">
</head>
<body>
  {nav(current_file, lang, title, alt_path)}
  {body}
  <footer class="site-footer">
    <div class="wrap">OmegaXYZ · Migrated from WordPress · Images served by Cloudflare R2</div>
  </footer>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/contrib/auto-render.min.js"></script>
  <script defer src="{js}"></script>
</body>
</html>
"""


def render_card(entry, lang, current_file, compact=False):
    title = entry[f"title_{lang}"]
    excerpt = short_text(entry[f"excerpt_{lang}"], 112 if compact else 150)
    href = rel_url(current_file, path_to_file(entry_path(entry, lang)))
    terms = entry["categories"][:2] or entry["tags"][:2]
    pills = "".join(f'<span class="pill">{esc(term_label(t, lang))}</span>' for t in terms)
    image = first_image(entry)
    image_html = f'<a class="card-media" href="{href}"><img src="{esc(image)}" alt=""></a>' if image and not compact else ""
    return f"""
    <article class="post-card">
      {image_html}
      <div class="meta">{esc(date_only(entry['date']))}</div>
      <h3><a href="{href}">{esc(title)}</a></h3>
      <p>{esc(excerpt)}</p>
      <div class="terms">{pills}</div>
    </article>
    """


def render_feature(entry, lang, current_file):
    href = rel_url(current_file, path_to_file(entry_path(entry, lang)))
    image = first_image(entry)
    terms = entry["categories"][:2] or entry["tags"][:2]
    pills = "".join(f'<span class="pill">{esc(term_label(t, lang))}</span>' for t in terms)
    image_html = f'<img src="{esc(image)}" alt="">' if image else '<div class="media-fallback">OmegaXYZ</div>'
    return f"""
    <article class="feature-card">
      <a class="feature-media" href="{href}">{image_html}</a>
      <div class="feature-copy">
        <div class="meta">{esc(date_only(entry['date']))}</div>
        <h3><a href="{href}">{esc(entry[f'title_{lang}'])}</a></h3>
        <p>{esc(short_text(entry[f'excerpt_{lang}'], 132))}</p>
        <div class="terms">{pills}</div>
      </div>
    </article>
    """


def render_quick_item(entry, lang, current_file):
    href = rel_url(current_file, path_to_file(entry_path(entry, lang)))
    term = (entry["categories"] or entry["tags"] or [{"name": "", "slug": ""}])[0]
    return f"""
    <a class="quick-item" href="{href}">
      <time>{esc(date_only(entry['date']))}</time>
      <strong>{esc(entry[f'title_{lang}'])}</strong>
      <span>{esc(term_label(term, lang))}</span>
    </a>
    """


def render_page_link(entry, lang, current_file):
    href = rel_url(current_file, path_to_file(entry_path(entry, lang)))
    return f"""
    <a class="page-link" href="{href}">
      <span>{esc(date_only(entry['date']))}</span>
      <strong>{esc(entry[f'title_{lang}'])}</strong>
    </a>
    """


def render_latest_row(entry, lang, current_file):
    href = rel_url(current_file, path_to_file(entry_path(entry, lang)))
    image = first_image(entry)
    image_html = f'<img src="{esc(image)}" alt="">' if image else '<span>OmegaXYZ</span>'
    terms = entry["categories"][:2] or entry["tags"][:2]
    pills = "".join(f'<span class="pill">{esc(term_label(t, lang))}</span>' for t in terms)
    return f"""
    <article class="latest-row">
      <a class="latest-media" href="{href}">{image_html}</a>
      <div class="latest-copy">
        <div class="meta">{esc(date_only(entry['date']))}</div>
        <h3><a href="{href}">{esc(entry[f'title_{lang}'])}</a></h3>
        <p>{esc(short_text(entry[f'excerpt_{lang}'], 160))}</p>
        <div class="terms">{pills}</div>
      </div>
    </article>
    """


def render_home(site, lang, current=None):
    current = current or path_to_file(f"{lang}/")
    posts = [e for e in site["entries"] if e["type"] == "post"]
    pages = [e for e in site["entries"] if e["type"] == "page"]
    stats = site["summary"]
    latest_rows = "".join(render_latest_row(e, lang, current) for e in posts[:9])
    page_links = "".join(render_page_link(e, lang, current) for e in pages[:6])
    term_counts = {}
    for entry in posts:
        for term in entry["categories"]:
            term_counts.setdefault(term["slug"], {"name": term["name"], "slug": term["slug"], "count": 0})
            term_counts[term["slug"]]["count"] += 1
    top_terms = sorted(term_counts.values(), key=lambda item: item["count"], reverse=True)[:8]
    topic_links = "".join(
        f'<a href="{rel_url(current, path_to_file(term_path("category", term["slug"], lang)))}">'
        f'<span>{esc(term_label(term, lang))}</span><strong>{term.get("count", 0)}</strong></a>'
        for term in top_terms
    )
    t = I18N[lang]
    search_index = rel_url(current, OUT / f"{lang}/search-index.json")
    body = f"""
    <main class="wrap">
      <section class="search-hero">
        <div class="search-shell">
          <div class="eyebrow">{esc(t['tagline'])}</div>
          <h1>OmegaXYZ</h1>
          <p>{esc(t['intro'])}</p>
          <section class="search-box home-search" data-search="{search_index}">
            <input type="search" placeholder="{esc(t['search_placeholder'])}" aria-label="{esc(t['search'])}">
            <div class="search-results" data-search-results></div>
          </section>
          <div class="hero-actions">
            <a class="button primary" href="{rel_url(current, path_to_file(archive_path(lang)))}">{esc(t['explore'])}</a>
            <a class="button" href="{rel_url(current, path_to_file(f'{lang}/pages/'))}">{esc(t['pages'])}</a>
          </div>
        </div>
      </section>
      <section class="stats-strip" aria-label="Site statistics">
        <div><strong>{stats['posts']}</strong><span>{esc(t['archive'])}</span></div>
        <div><strong>{stats['pages']}</strong><span>{esc(t['pages'])}</span></div>
        <div><strong>{stats['comments']}</strong><span>{esc(t['comments'])}</span></div>
        <div><strong>{stats['tags']}</strong><span>{esc(t['tags'])}</span></div>
      </section>
      <section class="home-panel">
        <div class="topic-rail" aria-label="{esc(t['categories'])}">
          {topic_links}
        </div>
      </section>
      <section class="band">
        <div class="section-head"><div><h2>{esc(t['latest'])}</h2><p>{esc(t['latest_desc'])}</p></div></div>
        <div class="latest-list">{latest_rows}</div>
      </section>
      <section class="band">
        <div class="section-head"><div><h2>{esc(t['pages'])}</h2><p>{esc(t['featured'])}</p></div></div>
        <div class="page-strip">{page_links}</div>
      </section>
    </main>
    """
    return layout(current, lang, "OmegaXYZ", body, t["intro"], f"{'en' if lang == 'zh' else 'zh'}/")


def render_entry(entry, lang, legacy):
    current = path_to_file(entry_path(entry, lang))
    other = "en" if lang == "zh" else "zh"
    title = entry[f"title_{lang}"]
    content = rewrite_content(entry[f"content_{lang}"], lang, current, legacy)
    excerpt = entry[f"excerpt_{lang}"]
    term_links = []
    for c in entry["categories"]:
        href = rel_url(current, path_to_file(term_path("category", c["slug"], lang)))
        term_links.append(f'<a class="pill" href="{href}">{esc(term_label(c, lang))}</a>')
    for tag in entry["tags"][:8]:
        href = rel_url(current, path_to_file(term_path("tag", tag["slug"], lang)))
        term_links.append(f'<a class="pill" href="{href}">{esc(term_label(tag, lang))}</a>')
    comments = render_comments(entry, lang)
    body = f"""
    <main class="wrap layout">
      <article class="article">
        <div class="meta">{esc(date_only(entry['date']))}</div>
        <h1>{esc(title)}</h1>
        <div class="terms">{''.join(term_links)}</div>
        <div class="article-content">{content}</div>
        {comments}
      </article>
      <aside class="sidebar">
        <section class="side-box"><h2>{esc(I18N[lang]['toc'])}</h2><nav data-toc></nav></section>
      </aside>
    </main>
    """
    return layout(current, lang, title, body, excerpt, entry_path(entry, other))


def render_comments(entry, lang):
    comments = entry["comments"]
    if not comments:
        return ""
    parts = [f'<section class="comments"><h2>{esc(I18N[lang]["comments"])} ({len(comments)})</h2>']
    for c in comments:
        cls = "comment reply" if c["parent"] else "comment"
        author = f'<a href="{esc(c["url"])}" rel="nofollow">{c["author"]}</a>' if c["url"] else c["author"]
        parts.append(f"""
        <div class="{cls}" id="comment-{c['id']}">
          <strong>{author}</strong>
          <time>{esc(c['date'])}</time>
          <div>{c[f'content_{lang}']}</div>
        </div>
        """)
    parts.append("</section>")
    return "".join(parts)


def render_archive(site, lang):
    posts = [e for e in site["entries"] if e["type"] == "post"]
    per_page = 24
    pages = max(1, math.ceil(len(posts) / per_page))
    for page in range(1, pages + 1):
        current = path_to_file(archive_path(lang, page))
        subset = posts[(page - 1) * per_page:page * per_page]
        items = "".join(render_archive_item(e, lang, current) for e in subset)
        pager = render_pager(lang, current, page, pages)
        body = f'<main class="wrap band"><div class="section-head"><h1>{esc(I18N[lang]["all_posts"])}</h1></div><div class="archive-list">{items}</div>{pager}</main>'
        write(current, layout(current, lang, I18N[lang]["all_posts"], body, alt_path=archive_path("en" if lang == "zh" else "zh", page if page <= pages else 1)))


def render_archive_item(entry, lang, current):
    href = rel_url(current, path_to_file(entry_path(entry, lang)))
    return f"""
    <article class="archive-item">
      <time>{esc(date_only(entry['date']))}</time>
      <div>
        <h2><a href="{href}">{esc(entry[f'title_{lang}'])}</a></h2>
        <p>{esc(entry[f'excerpt_{lang}'])}</p>
      </div>
    </article>
    """


def render_pager(lang, current, page, pages):
    links = []
    if page > 1:
        links.append(f'<a class="pill" href="{rel_url(current, path_to_file(archive_path(lang, page - 1)))}">Previous</a>')
    if page < pages:
        links.append(f'<a class="pill" href="{rel_url(current, path_to_file(archive_path(lang, page + 1)))}">Next</a>')
    return f'<nav class="terms">{"".join(links)}</nav>' if links else ""


def render_pages_index(site, lang):
    current = path_to_file(f"{lang}/pages/")
    pages = [e for e in site["entries"] if e["type"] == "page"]
    items = "".join(render_archive_item(e, lang, current) for e in pages)
    body = f'<main class="wrap band"><div class="section-head"><h1>{esc(I18N[lang]["all_pages"])}</h1></div><div class="archive-list">{items}</div></main>'
    write(current, layout(current, lang, I18N[lang]["all_pages"], body, alt_path=f"{'en' if lang == 'zh' else 'zh'}/pages/"))


def render_terms(site, lang):
    for kind, label in (("category", "categories"), ("tag", "tags")):
        grouped = defaultdict(list)
        for entry in site["entries"]:
            for term in entry["categories" if kind == "category" else "tags"]:
                grouped[(term["slug"], term["name"])].append(entry)
        current = path_to_file(f"{lang}/{label}/")
        chips = []
        for (slug, name), entries in sorted(grouped.items(), key=lambda i: (-len(i[1]), i[0][1])):
            href = rel_url(current, path_to_file(term_path(kind, slug, lang)))
            display_label = term_label({"slug": slug, "name": name}, lang)
            chips.append(f'<a class="pill" href="{href}">{esc(display_label)} · {len(entries)}</a>')
            term_current = path_to_file(term_path(kind, slug, lang))
            items = "".join(render_archive_item(e, lang, term_current) for e in entries)
            body = f'<main class="wrap band"><div class="section-head"><h1>{esc(display_label)}</h1></div><div class="archive-list">{items}</div></main>'
            write(term_current, layout(term_current, lang, display_label, body, alt_path=term_path(kind, slug, "en" if lang == "zh" else "zh")))
        body = f'<main class="wrap band"><div class="section-head"><h1>{esc(I18N[lang][label])}</h1></div><div class="terms">{"".join(chips)}</div></main>'
        write(current, layout(current, lang, I18N[lang][label], body, alt_path=f"{'en' if lang == 'zh' else 'zh'}/{label}/"))


def render_search(site, lang):
    current = path_to_file(f"{lang}/search/")
    index_file = OUT / f"{lang}/search-index.json"
    index = []
    for entry in site["entries"]:
        index.append({
            "title": entry[f"title_{lang}"],
            "excerpt": entry[f"excerpt_{lang}"],
            "tags": " ".join(term_label(t, lang) for t in entry["tags"] + entry["categories"]),
            "url": rel_url(index_file, path_to_file(entry_path(entry, lang))),
        })
    write(index_file, json.dumps(index, ensure_ascii=False))
    body = f"""
    <main class="wrap band">
      <div class="section-head"><h1>{esc(I18N[lang]['search'])}</h1></div>
      <section class="search-box" data-search="{rel_url(current, index_file)}">
        <input type="search" placeholder="{esc(I18N[lang]['search'])}">
        <div class="search-results" data-search-results></div>
      </section>
    </main>
    """
    write(current, layout(current, lang, I18N[lang]["search"], body, alt_path=f"{'en' if lang == 'zh' else 'zh'}/search/"))


def render_redirect(path, target):
    file = path_to_file(path)
    target_file = path_to_file(target)
    href = rel_url(file, target_file)
    write(file, f'<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={href}"><link rel="canonical" href="{href}">')


def collect_legacy_paths(site, legacy):
    found = set()
    pattern = re.compile(r'\b(?:href|src)=["\']([^"\']+)["\']|(?:https?:)?//(?:www\.)?omegaxyz\.com/([^"\'\s<>)]+)', re.I)
    for entry in site["entries"]:
        for lang in ("zh", "en"):
            for match in pattern.finditer(entry.get(f"content_{lang}", "")):
                value = match.group(1) or ("https://omegaxyz.com/" + (match.group(2) or ""))
                parsed = urlparse(value if not value.startswith("//") else "https:" + value)
                if parsed.netloc and parsed.netloc.lower() not in SOURCE_HOSTS:
                    continue
                if not parsed.netloc and not value.startswith("/"):
                    continue
                path = normalize_legacy_path(value)
                if not path or path in legacy:
                    continue
                if path.startswith(("wp-content/uploads/", "wp-admin/", "wp-login.php")):
                    continue
                found.add(path)
    return found


def copy_public():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(PUBLIC, OUT, dirs_exist_ok=True)
    write(OUT / ".nojekyll", "")
    write(OUT / "CNAME", "omegaxyz.com\n")


def render_site_index_files():
    urls = []
    for file in sorted(OUT.rglob("*.html")):
        head = file.read_text(encoding="utf-8", errors="ignore")[:300].lower()
        if 'http-equiv="refresh"' in head:
            continue
        urls.append(site_url_for_file(file))
    xml_urls = "\n".join(f"  <url><loc>{esc(url)}</loc></url>" for url in urls)
    write(OUT / "sitemap.xml", f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{xml_urls}
</urlset>
""")
    write(OUT / "robots.txt", f"""User-agent: *
Allow: /

Sitemap: {SITE_URL.rstrip("/")}/sitemap.xml
""")


def main():
    site = load_site()
    legacy = build_legacy_map(site)
    copy_public()
    for lang in ("zh", "en"):
        write(path_to_file(f"{lang}/"), render_home(site, lang))
        render_archive(site, lang)
        render_pages_index(site, lang)
        render_terms(site, lang)
        render_search(site, lang)
    write(OUT / "index.html", render_home(site, "zh", OUT / "index.html"))
    for entry in site["entries"]:
        for lang in ("zh", "en"):
            write(path_to_file(entry_path(entry, lang)), render_entry(entry, lang, legacy))
        render_redirect(entry["url"], entry_path(entry, "zh"))
    for path in collect_legacy_paths(site, legacy):
        render_redirect(path, "zh/search/")
    render_redirect("archive/", "zh/archive/")
    render_site_index_files()
    print(f"built {OUT}")


if __name__ == "__main__":
    main()
