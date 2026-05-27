#!/usr/bin/env python3
import html
import json
import math
import re
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/site.json"
PUBLIC = ROOT / "public"
OUT = ROOT / "docs"

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
        "latest_desc": "从 WordPress 迁移而来的文章、页面、评论和公式内容。",
        "featured": "知识结构",
        "comments": "评论",
        "toc": "目录",
        "all_posts": "全部文章",
        "all_pages": "全部页面",
        "language": "English",
        "intro": "OmegaXYZ 是一个长期积累的学习与研究笔记库，内容覆盖编程、机器学习、知识工程、数学与个人思考。现在它被迁移为静态站点，页面更轻，链接更稳，公式和图片仍旧可读。",
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
        "latest_desc": "Posts, pages, comments, media, and formulas migrated from WordPress.",
        "featured": "Knowledge Map",
        "comments": "Comments",
        "toc": "Contents",
        "all_posts": "All Posts",
        "all_pages": "All Pages",
        "language": "中文",
        "intro": "OmegaXYZ is a long-running notebook for study and research across programming, machine learning, knowledge engineering, mathematics, and personal ideas. It is now a static site: lighter pages, steadier links, and preserved formulas and media.",
    },
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
    return Path(target).relative_to(OUT).as_posix() if False else Path(
        __import__("os").path.relpath(target, from_dir)
    ).as_posix()


def page_file(path):
    clean = path.strip("/")
    if not clean:
        return OUT / "index.html"
    return OUT / clean / "index.html"


def path_to_file(path):
    return page_file(path)


def entry_path(entry, lang):
    return f"{lang}/{entry['url']}"


def term_path(kind, slug, lang):
    return f"{lang}/{kind}/{quote(slug, safe='')}/"


def archive_path(lang, page=1):
    return f"{lang}/archive/" if page == 1 else f"{lang}/archive/page/{page}/"


def esc(value):
    return html.escape(str(value or ""), quote=True)


def strip_tags(markup):
    text = re.sub(r"<(script|style|pre|code)[^>]*>.*?</\1>", " ", markup or "", flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


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
    return f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} · OmegaXYZ</title>
  <meta name="description" content="{esc(desc)}">
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


def render_card(entry, lang, current_file):
    title = entry[f"title_{lang}"]
    excerpt = entry[f"excerpt_{lang}"]
    href = rel_url(current_file, path_to_file(entry_path(entry, lang)))
    terms = entry["categories"][:2] or entry["tags"][:2]
    pills = "".join(f'<span class="pill">{esc(t["name"])}</span>' for t in terms)
    return f"""
    <article class="post-card">
      <div class="meta">{esc(date_only(entry['date']))}</div>
      <h3><a href="{href}">{esc(title)}</a></h3>
      <p>{esc(excerpt)}</p>
      <div class="terms">{pills}</div>
    </article>
    """


def render_home(site, lang):
    current = path_to_file(f"{lang}/")
    posts = [e for e in site["entries"] if e["type"] == "post"]
    pages = [e for e in site["entries"] if e["type"] == "page"]
    stats = site["summary"]
    cards = "".join(render_card(e, lang, current) for e in posts[:6])
    page_links = "".join(render_card(e, lang, current) for e in pages[:3])
    t = I18N[lang]
    body = f"""
    <main class="wrap">
      <section class="hero">
        <div>
          <div class="eyebrow">{esc(t['tagline'])}</div>
          <h1>OmegaXYZ</h1>
          <p>{esc(t['intro'])}</p>
        </div>
        <div class="stats">
          <div class="stat"><strong>{stats['posts']}</strong><span>{esc(t['archive'])}</span></div>
          <div class="stat"><strong>{stats['pages']}</strong><span>{esc(t['pages'])}</span></div>
          <div class="stat"><strong>{stats['comments']}</strong><span>{esc(t['comments'])}</span></div>
          <div class="stat"><strong>{stats['tags']}</strong><span>{esc(t['tags'])}</span></div>
        </div>
      </section>
      <section class="band">
        <div class="section-head"><div><h2>{esc(t['latest'])}</h2><p>{esc(t['latest_desc'])}</p></div></div>
        <div class="grid">{cards}</div>
      </section>
      <section class="band">
        <div class="section-head"><div><h2>{esc(t['pages'])}</h2><p>{esc(t['featured'])}</p></div></div>
        <div class="grid">{page_links}</div>
      </section>
    </main>
    """
    return layout(current, lang, "OmegaXYZ", body, t["intro"], f"{'en' if lang == 'zh' else 'zh'}/")


def render_entry(entry, lang):
    current = path_to_file(entry_path(entry, lang))
    other = "en" if lang == "zh" else "zh"
    title = entry[f"title_{lang}"]
    content = entry[f"content_{lang}"]
    excerpt = entry[f"excerpt_{lang}"]
    term_links = []
    for c in entry["categories"]:
        href = rel_url(current, path_to_file(term_path("category", c["slug"], lang)))
        term_links.append(f'<a class="pill" href="{href}">{esc(c["name"])}</a>')
    for tag in entry["tags"][:8]:
        href = rel_url(current, path_to_file(term_path("tag", tag["slug"], lang)))
        term_links.append(f'<a class="pill" href="{href}">{esc(tag["name"])}</a>')
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
            chips.append(f'<a class="pill" href="{href}">{esc(name)} · {len(entries)}</a>')
            term_current = path_to_file(term_path(kind, slug, lang))
            items = "".join(render_archive_item(e, lang, term_current) for e in entries)
            body = f'<main class="wrap band"><div class="section-head"><h1>{esc(name)}</h1></div><div class="archive-list">{items}</div></main>'
            write(term_current, layout(term_current, lang, name, body, alt_path=term_path(kind, slug, "en" if lang == "zh" else "zh")))
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
            "tags": " ".join(t["name"] for t in entry["tags"] + entry["categories"]),
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


def copy_public():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(PUBLIC, OUT, dirs_exist_ok=True)
    write(OUT / ".nojekyll", "")


def main():
    site = load_site()
    copy_public()
    for lang in ("zh", "en"):
        write(path_to_file(f"{lang}/"), render_home(site, lang))
        render_archive(site, lang)
        render_pages_index(site, lang)
        render_terms(site, lang)
        render_search(site, lang)
    write(OUT / "index.html", render_home(site, "zh"))
    for entry in site["entries"]:
        for lang in ("zh", "en"):
            write(path_to_file(entry_path(entry, lang)), render_entry(entry, lang))
        render_redirect(entry["url"], entry_path(entry, "zh"))
    render_redirect("archive/", "zh/archive/")
    print(f"built {OUT}")


if __name__ == "__main__":
    main()
