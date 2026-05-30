#!/usr/bin/env python3
import hashlib
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
EXTRA_ENTRIES = ROOT / "content/extra_entries.json"
POSTS_DIR = ROOT / "content/posts"        # drop a .md here -> a page is generated
EXAMPLE_MD = "example.md"                  # template, always skipped, never archived
PUBLIC = ROOT / "public"
OUT = ROOT / "docs"
CDN = "https://cdn.omegaxyz.com"
SITE_URL = "https://omegaxyz.com"
ASSET_VERSION = "20260530-media1"
LOGO_URL = CDN + "/2017/11/cropped-omegaxyzlogo.jpg"
HOME_LOGO_URL = CDN + "/2020/01/AI-GIF.gif"
FAVICON_URL = CDN + "/2020/02/omegaxyz-logo-100.png"
GITHUB_URL = "https://github.com/xyjigsaw"
GITHUB_ICON = (
    '<svg viewBox="0 0 16 16" width="18" height="18" aria-hidden="true" focusable="false">'
    '<path fill="currentColor" fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 '
    "5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13"
    "-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07"
    "-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82"
    ".64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 "
    "1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38"
    'A8.01 8.01 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>'
)
SOURCE_HOSTS = {"omegaxyz.com", "www.omegaxyz.com", "en.omegaxyz.com"}
EXCLUDE_PAGE_SLUGS = {
    "ai-ml-navigator", "web-running", "js_game", "regular_expression",
    "caculator", "onlinetools", "lab", "hello-world", "acknowledgement",
    "hexconvert", "resource", "resource_software",
}
PAGE_TITLE_EN_OVERRIDE = {
    "makefriends": "Make Friends with Me",
}

FOOTER_LINKS = [
    ("AI研习社", "https://www.yanxishe.com/"),
    ("雷锋网", "https://www.leiphone.com/"),
    ("ChainOE", "https://chainoe.com/"),
    ("Oldpan", "http://www.oldpan.me/"),
    ("OhYee", "https://www.oyohyee.com/"),
    ("科学空间", "https://kexue.fm/"),
    ("谭升的博客", "https://face2ai.com/"),
    ("米虫", "https://www.mebugs.com/"),
    ("StriveZ", "https://www.strivezs.com/"),
    ("AI柠檬", "https://blog.ailemon.me/"),
    ("Python实用宝典", "https://pythondict.com/"),
    ("宇宙湾", "https://yuzhouwan.com/"),
    ("cvosRobot", "http://blog.cvosrobot.com/"),
]

FRIEND_LINKS = [
    ("站点", "AI研习社", "https://www.yanxishe.com/", "https://omegaxyz.com/wp-content/uploads/2020/06/yanxishe2.jpg"),
    ("站点", "雷锋网", "https://www.leiphone.com/", "https://omegaxyz.com/wp-content/uploads/2020/06/leiphone-x.png"),
    ("站点", "ChainOE", "https://chainoe.com/", "https://omegaxyz.com/wp-content/uploads/2022/03/chineOE-e1648304685858.png"),
    ("个人博客", "米虫博客", "http://www.mebugs.com/", "https://omegaxyz.com/wp-content/uploads/2018/04/mebugs.jpg"),
    ("个人博客", "AI柠檬", "https://blog.ailemon.net/", "https://omegaxyz.com/wp-content/uploads/2018/01/machinelearningicon.jpg"),
    ("个人博客", "hannlp", "https://hannlp.github.io/", "https://omegaxyz.com/wp-content/uploads/2018/01/machinelearningicon.jpg"),
    ("个人博客", "StriveZ的博客", "http://www.strivezs.com/", "https://omegaxyz.com/wp-content/uploads/2018/03/striveZ.jpg"),
    ("个人博客", "Oldpan的个人博客", "http://www.oldpan.me/", "https://omegaxyz.com/wp-content/uploads/2018/01/machinelearningicon.jpg"),
    ("个人博客", "itsNekoDeng", "https://nekodeng.gitee.io/", "https://omegaxyz.com/wp-content/uploads/2020/11/nekoDeng.jpg"),
    ("个人博客", "Python实用宝典", "https://pythondict.com/", "https://omegaxyz.com/wp-content/uploads/2020/05/Pythondict.jpg"),
    ("个人博客", "九陌斋", "https://blog.jiumoz.com", "https://omegaxyz.com/wp-content/uploads/2023/04/jiumoz.png"),
    ("个人博客", "科学空间", "https://kexue.fm", "https://omegaxyz.com/wp-content/uploads/2023/12/bojone.png"),
    ("个人博客", "枫糖", "https://blog.maplesugar.top", "https://omegaxyz.com/wp-content/uploads/2019/08/maple-leaf-avatar.jpg"),
    ("个人博客", "Kitcham 的归墟", "https://blog.uiharu.top/", "https://omegaxyz.com/wp-content/uploads/2020/09/Kitcham.png"),
    ("个人博客", "碎言博客", "https://suiyan.cc/", "https://omegaxyz.com/wp-content/uploads/2023/05/suiyan.jpeg"),
    ("个人博客", "海纪元", "https://www.seayj.cn/", "https://omegaxyz.com/wp-content/uploads/2024/10/SeaEpoch.png"),
    ("个人博客", "cvosrobot", "http://blog.cvosrobot.com/", "https://omegaxyz.com/wp-content/uploads/2020/05/cvosrobot.png"),
    ("个人博客", "宇宙湾", "https://yuzhouwan.com/", "https://omegaxyz.com/wp-content/uploads/2020/01/yuzhouwan.png"),
    ("个人博客", "星萌亦派", "https://meta-sns.com/", "https://omegaxyz.com/wp-content/uploads/2023/08/lincoin.png"),
    ("个人博客", "mmuaa", "https://www.mmuaa.com/", "https://omegaxyz.com/wp-content/uploads/2019/07/T19vXDXmNbXXXXXXXX.jpg"),
    ("个人博客", "谭升的博客", "https://face2ai.com", "https://omegaxyz.com/wp-content/uploads/2018/10/tansheng.png"),
    ("个人博客", "OhYee", "https://www.oyohyee.com/", "https://omegaxyz.com/wp-content/uploads/2020/02/oyohyee.png"),
    ("退休", "yoko blog", "", "https://omegaxyz.com/wp-content/uploads/2019/08/default_avatar.jpg"),
    ("退休", "shawnluo", "", "https://omegaxyz.com/wp-content/uploads/2018/06/shawnluo.png"),
    ("退休", "人工智能网", "", "https://omegaxyz.com/wp-content/uploads/2018/01/machinelearningicon.jpg"),
    ("退休", "Python爱好者", "", "https://omegaxyz.com/wp-content/uploads/2020/03/codingdogzxg.jpg"),
]

I18N = {
    "zh": {
        "tagline": "徐奕的专栏",
        "skip": "跳到正文",
        "message": "留言",
        "tab_latest": "最新",
        "tab_random": "随机",
        "shuffle_topics": "换一批",
        "home": "主页",
        "archive": "文章",
        "pages": "页面",
        "categories": "分类",
        "about": "关于",
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
        "intro": "OmegaXYZ",
        "archive_search_placeholder": "搜索标题、摘要、标签...",
        "sort": "排序",
        "sort_newest": "最新优先",
        "sort_oldest": "最早优先",
        "sort_title": "标题 A-Z",
        "filter_all": "全部",
        "results": "篇文章",
        "no_results": "没有匹配的文章",
        "filter_by_tag": "按标签筛选",
        "footer_license": "该网站原创代码采用 Apache 2.0 授权，原创文章采用 BY-NC-SA 4.0 授权",
        "footer_copyright": "Copyright © 2026 OmegaXYZ 版权所有 转载请注明出处",
        "footer_icp": "皖ICP备:17007601",
        "footer_business": "商业合作",
        "privacy": "隐私政策",
        "sitemap": "站点地图",
        "footer_more_friends": "更多(非首页友链)...",
    },
    "en": {
        "tagline": "Xu Yi's column",
        "skip": "Skip to content",
        "message": "Message",
        "tab_latest": "Latest",
        "tab_random": "Shuffle",
        "shuffle_topics": "Shuffle",
        "home": "Home",
        "archive": "Archive",
        "pages": "Pages",
        "categories": "Categories",
        "about": "About",
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
        "intro": "OmegaXYZ",
        "archive_search_placeholder": "Search titles, summaries, and tags...",
        "sort": "Sort",
        "sort_newest": "Newest",
        "sort_oldest": "Oldest",
        "sort_title": "Title A-Z",
        "filter_all": "All",
        "results": "posts",
        "no_results": "No matching posts",
        "filter_by_tag": "Filter by tag",
        "footer_license": "Original code on this site is licensed under Apache 2.0; original articles are licensed under BY-NC-SA 4.0.",
        "footer_copyright": "Copyright © 2026 OmegaXYZ. Please cite the source when reposting.",
        "footer_icp": "ICP record: 皖ICP备17007601",
        "footer_business": "Business",
        "privacy": "Privacy Policy",
        "sitemap": "Sitemap",
        "footer_more_friends": "More friends...",
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
    "ai": "Artificial Intelligence",
    "llm": "Large Language Models",
    "academic-big-data": "Academic Big Data",
    "idea-generation": "Idea Generation",
    "deepreport": "DeepReport",
}


def load_site():
    site = json.loads(DATA.read_text(encoding="utf-8"))
    reverse_zh = {}
    for entry in site["entries"]:
        for term in entry.get("categories", []) + entry.get("tags", []):
            reverse_zh.setdefault(term["slug"], term.get("name") or term["slug"])
    extras = load_extra_entries() + load_markdown_entries(reverse_zh)
    if extras:
        extra_urls = {entry["url"] for entry in extras}
        site["entries"] = extras + [entry for entry in site["entries"] if entry.get("url") not in extra_urls]
    site["entries"] = [
        entry for entry in site["entries"]
        if not (entry.get("type") == "page" and entry.get("slug") in EXCLUDE_PAGE_SLUGS)
    ]
    for entry in site["entries"]:
        override = PAGE_TITLE_EN_OVERRIDE.get(entry.get("slug"))
        if override:
            entry["title_en"] = override
        # Strip the stray WordPress [latexpage] shortcode wherever it leaked.
        for field in ("excerpt_zh", "excerpt_en", "title_zh", "title_en"):
            if entry.get(field):
                entry[field] = re.sub(r"\[latexpage\]\s*", "", entry[field], flags=re.I).strip()
    site["entries"].sort(key=lambda entry: entry.get("date", ""), reverse=True)
    site["summary"] = build_summary(site["entries"])
    return site


def load_extra_entries():
    if not EXTRA_ENTRIES.exists():
        return []
    entries = json.loads(EXTRA_ENTRIES.read_text(encoding="utf-8"))
    for entry in entries:
        for lang in ("zh", "en"):
            key = f"content_{lang}_file"
            if key in entry:
                entry[f"content_{lang}"] = (ROOT / entry.pop(key)).read_text(encoding="utf-8")
        for term in entry.get("categories", []) + entry.get("tags", []):
            if not (term.get("name_en") or term.get("label_en")):
                term["name_en"] = TERM_EN.get(term.get("slug"), auto_english_term_label(term))
    return entries


# ---------------------------------------------------------------------------
# Markdown posts: drop a .md into content/posts/ and a page is generated. The
# build reads content/posts/**.md (including the archive/ subfolder, where CI
# moves processed files), so an archived post keeps serving its page on every
# rebuild — the move is only for tidiness. example.md and *.en.md companions
# are skipped as standalone posts.
# ---------------------------------------------------------------------------
def load_markdown_entries(reverse_zh):
    if not POSTS_DIR.exists():
        return []
    entries = []
    for path in sorted(POSTS_DIR.rglob("*.md")):
        if path.name == EXAMPLE_MD or path.name.lower() == "readme.md" or path.name.endswith(".en.md"):
            continue
        try:
            entry = markdown_file_to_entry(path, reverse_zh)
        except Exception as exc:  # one bad file shouldn't break the whole build
            print(f"  markdown skip {path.relative_to(ROOT)}: {exc}")
            continue
        if entry:
            entries.append(entry)
            print(f"  markdown post: /{entry['url']}  <- {path.relative_to(ROOT)}")
    entries.sort(key=lambda e: e["date"], reverse=True)
    return entries


def markdown_file_to_entry(path, reverse_zh):
    meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    title = meta.get("title") or meta.get("title_zh")
    if not title or not meta.get("date"):
        print(f"  markdown skip {path.name}: needs 'title' and 'date' frontmatter")
        return None
    slug = (meta.get("slug") or path.stem).strip()
    date = meta["date"].strip()
    if len(date) <= 10:
        date += " 00:00:00"
    year, month, day = date_only(date).split("-")[:3]
    url = meta.get("url") or f"{year}/{month}/{day}/{slug}/"
    if not url.endswith("/"):
        url += "/"
    content_zh = markdown_to_html(body)
    en_path = path.with_name(path.stem + ".en.md")
    if not en_path.exists() and path.parent.name == "archive":
        en_path = POSTS_DIR / f"{path.stem}.en.md"
    if en_path.exists():
        _, en_body = parse_frontmatter(en_path.read_text(encoding="utf-8"))
        content_en = markdown_to_html(en_body)
    else:
        content_en = content_zh
    excerpt_zh = meta.get("excerpt") or meta.get("excerpt_zh") or short_text(content_zh, 140)
    excerpt_en = meta.get("excerpt_en") or (short_text(content_en, 140) if en_path.exists() else excerpt_zh)
    return {
        "id": 900000 + int(hashlib.md5(slug.encode("utf-8")).hexdigest()[:7], 16) % 99999,
        "type": meta.get("type", "post"),
        "title_zh": title,
        "title_en": meta.get("title_en") or title,
        "excerpt_zh": excerpt_zh,
        "excerpt_en": excerpt_en,
        "content_zh": content_zh,
        "content_en": content_en,
        "date": date,
        "modified": meta.get("modified", date),
        "slug": slug,
        "url": url,
        "categories": resolve_md_terms(meta.get("categories", []), reverse_zh),
        "tags": resolve_md_terms(meta.get("tags", []), reverse_zh),
        "comments": [],
        "thumbnail": meta.get("thumbnail", ""),
    }


def resolve_md_terms(tokens, reverse_zh):
    """Token forms: "slug" | "中文名|slug" | "中文名|slug|English Name".
    A bare slug reuses an existing same-slug term's Chinese name when known.
    name_en follows the site's standard priority: explicit value here, else the
    built-in TERM_EN map, else auto-generated from the slug."""
    terms = []
    for token in tokens:
        token = str(token).strip()
        if not token:
            continue
        explicit_en = ""
        if "|" in token:
            parts = [part.strip() for part in token.split("|")]
            name = parts[0]
            slug = parts[1] if len(parts) > 1 and parts[1] else parts[0]
            explicit_en = parts[2] if len(parts) > 2 else ""
        else:
            slug = token
            name = reverse_zh.get(slug, slug)
        term = {"name": name, "slug": slug}
        term["name_en"] = explicit_en or TERM_EN.get(slug, auto_english_term_label(term))
        terms.append(term)
    return terms


def parse_frontmatter(text):
    """Minimal YAML-ish frontmatter: `key: value` lines between leading --- fences.
    `[a, b, c]` and comma lists become lists; everything else is a string."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    match = re.match(r"^---[ \t]*\n(.*?)\n---[ \t]*\n?", text, re.S)
    if not match:
        return {}, text
    meta = {}
    for line in match.group(1).split("\n"):
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if value.startswith("[") and value.endswith("]"):
            value = [v.strip().strip("\"'") for v in value[1:-1].split(",") if v.strip()]
        else:
            value = value.strip("\"'")
        meta[key] = value
    return meta, text[match.end():]


# ---- Markdown -> HTML (stdlib only; covers the common blog subset) ----
def _md_escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def md_inline(text):
    # Protect math ($$..$$, $..$) and inline code from markdown processing so
    # emphasis/escaping can't mangle them; the math delimiters are left intact
    # for KaTeX to render client-side.
    keep = []

    def hold(fragment):
        keep.append(fragment)
        return f"\x00{len(keep) - 1}\x00"

    text = re.sub(r"\$\$(.+?)\$\$", lambda m: hold("$$" + _md_escape(m.group(1)) + "$$"), text)
    text = re.sub(r"(?<!\$)\$([^$\n]+?)\$(?!\$)", lambda m: hold("$" + _md_escape(m.group(1)) + "$"), text)
    text = re.sub(r"`([^`]+)`", lambda m: hold(f"<code>{_md_escape(m.group(1))}</code>"), text)
    text = _md_escape(text)
    text = re.sub(
        r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"([^\"]*)\")?\)",
        lambda m: f'<img src="{m.group(2)}" alt="{m.group(1)}"' + (f' title="{m.group(3)}"' if m.group(3) else "") + ">",
        text,
    )
    text = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)(?:\s+\"([^\"]*)\")?\)",
        lambda m: f'<a href="{m.group(2)}"' + (f' title="{m.group(3)}"' if m.group(3) else "") + f">{m.group(1)}</a>",
        text,
    )
    text = re.sub(r"\*\*([^*]+)\*\*|__([^_]+)__", lambda m: f"<strong>{m.group(1) or m.group(2)}</strong>", text)
    text = re.sub(r"~~([^~]+)~~", r"<del>\1</del>", text)
    text = re.sub(r"\*(?=\S)([^*\n]+?)(?<=\S)\*", r"<em>\1</em>", text)
    text = re.sub(r"(?<![A-Za-z0-9_])_(?=\S)([^_\n]+?)(?<=\S)_(?![A-Za-z0-9_])", r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: keep[int(m.group(1))], text)


def _md_list(lines, i, base_indent):
    items, ordered, n = [], None, len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            nxt = i + 1
            if nxt < n and re.match(r"^\s*([-*+]|\d+\.)\s+", lines[nxt]) and (len(lines[nxt]) - len(lines[nxt].lstrip())) >= base_indent:
                i = nxt
                continue
            break
        indent = len(line) - len(line.lstrip())
        match = re.match(r"^([-*+]|\d+\.)\s+(.*)$", line.strip())
        if not match or indent < base_indent:
            break
        if indent > base_indent:
            i, sub = _md_list(lines, i, indent)
            if items:
                items[-1] = items[-1][:-len("</li>")] + sub + "</li>"
            continue
        this_ordered = bool(re.match(r"^\d+\.$", match.group(1)))
        if ordered is None:
            ordered = this_ordered
        elif this_ordered != ordered:
            break  # marker type changed at same indent -> a new list starts
        items.append(f"<li>{md_inline(match.group(2).strip())}</li>")
        i += 1
    tag = "ol" if ordered else "ul"
    return i, f"<{tag}>{''.join(items)}</{tag}>"


def _md_table(lines, i):
    header = [c.strip() for c in lines[i].strip().strip("|").split("|")]
    i += 2  # header row + the ---|--- separator
    rows, n = [], len(lines)
    while i < n and lines[i].strip() and "|" in lines[i]:
        rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
        i += 1
    head = "".join(f"<th>{md_inline(c)}</th>" for c in header)
    body = "".join("<tr>" + "".join(f"<td>{md_inline(c)}</td>" for c in row) + "</tr>" for row in rows)
    return i, f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def markdown_to_html(text):
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out, para, i, n = [], [], 0, len(lines)

    def flush():
        if para:
            out.append("<p>" + md_inline(" ".join(para).strip()) + "</p>")
            para.clear()

    while i < n:
        line, stripped = lines[i], lines[i].strip()
        fence = re.match(r"^(```|~~~)(.*)$", stripped)
        if fence:
            flush()
            mark, hint, code, i = fence.group(1), fence.group(2).strip(), [], i + 1
            while i < n and lines[i].strip()[:3] != mark:
                code.append(lines[i])
                i += 1
            i += 1
            cls = f' class="language-{_md_escape(hint)}"' if hint else ""
            out.append(f"<pre><code{cls}>{_md_escape(chr(10).join(code))}</code></pre>")
            continue
        if not stripped:
            flush()
            i += 1
            continue
        heading = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if heading:
            flush()
            level = len(heading.group(1))
            out.append(f"<h{level}>{md_inline(heading.group(2).strip())}</h{level}>")
            i += 1
            continue
        if re.match(r"^([*\-_])(?:\s*\1){2,}\s*$", stripped):
            flush()
            out.append("<hr>")
            i += 1
            continue
        if stripped.startswith(">"):
            flush()
            quote = []
            while i < n and lines[i].strip().startswith(">"):
                quote.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append(f"<blockquote>{markdown_to_html(chr(10).join(quote))}</blockquote>")
            continue
        if "|" in line and i + 1 < n and re.match(r"^\s*\|?(\s*:?-+:?\s*\|)+\s*:?-+:?\s*\|?\s*$", lines[i + 1]):
            flush()
            i, table = _md_table(lines, i)
            out.append(table)
            continue
        if re.match(r"^\s*([-*+]|\d+\.)\s+", line):
            flush()
            i, lst = _md_list(lines, i, len(line) - len(line.lstrip()))
            out.append(lst)
            continue
        para.append(stripped)
        i += 1
    flush()
    return "\n".join(out)


def build_summary(entries):
    posts = [entry for entry in entries if entry["type"] == "post"]
    pages = [entry for entry in entries if entry["type"] == "page"]
    return {
        "posts": len(posts),
        "pages": len(pages),
        "comments": sum(len(entry.get("comments", [])) for entry in entries),
        "categories": len({term["slug"] for entry in entries for term in entry.get("categories", [])}),
        "tags": len({term["slug"] for entry in entries for term in entry.get("tags", [])}),
    }


def auto_english_term_label(term):
    explicit = term.get("name_en") or term.get("label_en")
    if explicit:
        return explicit
    slug = term.get("slug", "")
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*", slug):
        acronyms = {"ai", "api", "css", "gpt", "gui", "html", "ios", "llm", "mvc", "nlp", "sql", "svm"}
        words = []
        for part in slug.split("-"):
            words.append(part.upper() if part.lower() in acronyms else part.capitalize())
        return " ".join(words)
    return term.get("name", slug)


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


def asset_url(value):
    parsed = urlparse(value or "")
    if parsed.netloc.lower() in SOURCE_HOSTS and parsed.path.startswith("/wp-content/uploads/"):
        return CDN + parsed.path.removeprefix("/wp-content/uploads")
    return value or ""


def term_label(term, lang):
    if lang == "en":
        return term.get("name_en") or term.get("label_en") or TERM_EN.get(term["slug"], term["name"])
    return term["name"]


def term_info(term, count=0):
    info = {"name": term["name"], "slug": term["slug"], "count": count}
    for key in ("name_en", "label_en"):
        if term.get(key):
            info[key] = term[key]
    return info


def term_pill(term, lang, kind, href=""):
    label = term_label(term, lang)
    text = esc(label)
    cls = f"pill term-pill term-{kind}"
    kind_label = "分类" if kind == "category" and lang == "zh" else "标签" if kind == "tag" and lang == "zh" else "CAT" if kind == "category" else "TAG"
    if href:
        return f'<a class="{cls}" data-label="{esc(kind_label)}" href="{href}"><span>{text}</span></a>'
    return f'<span class="{cls}" data-label="{esc(kind_label)}"><span>{text}</span></span>'


def render_term_pills(entry, lang, current, limit_categories=3, limit_tags=5):
    pills = []
    for category in entry["categories"][:limit_categories]:
        href = rel_url(current, path_to_file(term_path("category", category["slug"], lang))) if current else ""
        pills.append(term_pill(category, lang, "category", href))
    for tag in entry["tags"][:limit_tags]:
        href = rel_url(current, path_to_file(term_path("tag", tag["slug"], lang))) if current else ""
        pills.append(term_pill(tag, lang, "tag", href))
    return "".join(pills)


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


def fix_post_footer(markup):
    """The migrated WordPress site footer is appended as raw text with bare
    newlines (so it collapses into one line). When it appears as raw text at the
    very end, give its lines real <br> breaks. Skip footers already wrapped in a tag."""
    m = re.search(r"(更多内容访问|For more, visit)", markup)
    if not m:
        return markup
    i = m.start()
    if (i > 0 and markup[i - 1] == ">") or (len(markup) - i > 700):
        return markup  # already wrapped, or not the trailing footer
    head = re.sub(r"(?:\s|&nbsp;|\r|\n)+$", "", markup[:i])
    lines = [ln.strip() for ln in re.split(r"\r?\n", markup[i:]) if ln.strip() and ln.strip() != "&nbsp;"]
    return head + '\n<p class="post-footer">' + "<br>".join(lines) + "</p>"


# Migrated reference lists are raw text lines ("[1] ...") separated by blank
# lines, so they collapse onto a single line in HTML. Give each one its own line.
REF_RUN_RE = re.compile(r"\[\d+\][^\r\n]*(?:\r?\n\r?\n\[\d+\][^\r\n]*)+")


def fix_reference_list(markup):
    def repl(match):
        lines = re.split(r"\r?\n\r?\n", match.group(0))
        return "<br>".join(line.strip() for line in lines)

    return REF_RUN_RE.sub(repl, markup)


# WordPress migration cruft: headings that are empty (whitespace/&nbsp;/<br>) or
# wrap nothing but an image, plus empty paragraphs that add stray vertical gaps.
# Drop the empty ones; unwrap image-only headings so the image survives without
# the bogus heading semantics.
EMPTY_HEADING_RE = re.compile(r"<h([1-6])\b[^>]*>(?:\s|&nbsp;|<br\s*/?>)*</h\1>", re.I)
IMG_ONLY_HEADING_RE = re.compile(
    r"<h([1-6])\b[^>]*>\s*((?:<a\b[^>]*>\s*)?<img\b[^>]*?>\s*(?:</a>\s*)?)</h\1>", re.I
)
EMPTY_PARA_RE = re.compile(r"<p\b[^>]*>(?:\s|&nbsp;|<br\s*/?>)*</p>", re.I)


def clean_block_cruft(markup):
    markup = IMG_ONLY_HEADING_RE.sub(lambda m: m.group(2).strip(), markup)
    markup = EMPTY_HEADING_RE.sub("", markup)
    markup = EMPTY_PARA_RE.sub("", markup)
    return markup


def img_attr(attrs, name):
    match = re.search(rf'\b{name}=(["\'])(.*?)\1', attrs, flags=re.I)
    return match.group(2) if match else ""


def append_img_class(attrs, class_name):
    if not class_name:
        return attrs
    match = re.search(r'\bclass=(["\'])(.*?)\1', attrs, flags=re.I)
    if match:
        classes = match.group(2).split()
        if class_name not in classes:
            classes.append(class_name)
        return attrs[:match.start(2)] + " ".join(classes) + attrs[match.end(2):]
    return attrs.rstrip() + f' class="{class_name}"'


def enhance_img_tag(match):
    attrs = match.group(1)
    if not re.search(r"\bloading=", attrs, flags=re.I):
        attrs += ' loading="lazy"'
    if not re.search(r"\bdecoding=", attrs, flags=re.I):
        attrs += ' decoding="async"'
    try:
        width = int(float(img_attr(attrs, "width")))
        height = int(float(img_attr(attrs, "height")))
    except ValueError:
        width = height = 0
    if width and height:
        ratio = width / height
        if ratio < 0.78:
            attrs = append_img_class(attrs, "image-portrait")
        elif ratio > 1.45:
            attrs = append_img_class(attrs, "image-wide")
        if width <= 420:
            attrs = append_img_class(attrs, "image-small")
    return f"<img{attrs}>"


def rewrite_content(markup, lang, current_file, legacy):
    markup = markup or ""
    markup = re.sub(r"\[latexpage\]\s*", "", markup, flags=re.I)
    markup = re.sub(
        r"\[([^\]\n]+)\]\((https?://[^)\s]+)\)",
        r'<a href="\2">\1</a>',
        markup,
    )
    markup = fix_post_footer(markup)
    markup = fix_reference_list(markup)
    markup = clean_block_cruft(markup)

    def repl(match):
        attr, quote_char, value = match.groups()
        if attr.lower() == "srcset":
            rewritten = rewrite_srcset(value, lang, current_file, legacy)
        else:
            rewritten = rewrite_url(value, lang, current_file, legacy)
        return f'{attr}={quote_char}{html.escape(rewritten, quote=True)}{quote_char}'

    rewritten = re.sub(r'\b(href|src|srcset)=(["\'])(.*?)\2', repl, markup, flags=re.I)
    rewritten = re.sub(r"<img\b([^>]*)>", enhance_img_tag, rewritten, flags=re.I)
    return rewritten


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


def _nav_icon(inner):
    return ('<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" '
            'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            + inner + "</svg>")


NAV_ICONS = {
    "home": _nav_icon('<path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 10v9.5h13V10"/>'),
    "archive": _nav_icon('<path d="M4 6h16"/><path d="M4 12h16"/><path d="M4 18h10"/>'),
    "pages": _nav_icon('<path d="M8 3h6l4 4v14H8z"/><path d="M14 3v4h4"/>'),
    "categories": _nav_icon('<path d="M3 7a1 1 0 0 1 1-1h4.5l2 2H20a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/>'),
    "about": _nav_icon('<circle cx="12" cy="8" r="3.2"/><path d="M5.5 19.5c1.2-3.3 3.8-4.8 6.5-4.8s5.3 1.5 6.5 4.8"/>'),
    "lang": _nav_icon('<circle cx="12" cy="12" r="9"/><path d="M3.5 12h17"/><path d="M12 3c3 3.2 3 14.8 0 18M12 3c-3 3.2-3 14.8 0 18"/>'),
    "comment": _nav_icon('<path d="M4 5h16a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H9l-4 4V6a1 1 0 0 1 1-1z"/>'),
}


def nav(current_file, lang, title, alt_path):
    t = I18N[lang]
    other = "en" if lang == "zh" else "zh"
    logo_url = HOME_LOGO_URL
    # (label, path, external, icon, show_on_mobile)
    links = [
        (t["home"], f"{lang}/", False, NAV_ICONS["home"], False),
        (t["archive"], archive_path(lang), False, NAV_ICONS["archive"], True),
        (t["pages"], f"{lang}/pages/", False, NAV_ICONS["pages"], False),
        (t["categories"], f"{lang}/categories/", False, NAV_ICONS["categories"], False),
        (t["message"], f"{lang}/comment/", False, NAV_ICONS["comment"], False),
        (t["about"], "https://cv.omegaxyz.com/", True, NAV_ICONS["about"], True),
    ]
    items = []
    for label, path, external, icon, mobile in links:
        cls = "nav-item" if mobile else "nav-item nav-hide-m"
        href = esc(path) if external else rel_url(current_file, path_to_file(path))
        target = ' target="_blank" rel="noopener noreferrer"' if external else ""
        items.append(f'<a class="{cls}" href="{href}"{target} title="{esc(label)}">{icon}<span class="nav-label">{esc(label)}</span></a>')
    link_html = "".join(items)
    alt = rel_url(current_file, path_to_file(alt_path)) if alt_path else rel_url(current_file, path_to_file(f"{other}/"))
    return f"""
    <header class="site-header">
      <nav class="nav">
        <a class="brand" href="{rel_url(current_file, path_to_file(f'{lang}/'))}">
          <img src="{logo_url}" alt="" width="32" height="32">
          <span class="brand-text"><strong>OmegaXYZ</strong></span>
        </a>
        <div class="nav-links">
          {link_html}
          <a class="nav-item nav-lang" href="{alt}" title="{esc(t['language'])}">{NAV_ICONS["lang"]}<span class="nav-label">{esc(t['language'])}</span></a>
          <a class="icon-button nav-github nav-hide-m" href="{esc(GITHUB_URL)}" target="_blank" rel="noopener noreferrer" aria-label="GitHub">{GITHUB_ICON}</a>
          <button class="icon-button" type="button" data-theme-toggle aria-label="Theme">◐</button>
        </div>
      </nav>
    </header>
    """


def footer(current_file, lang):
    t = I18N[lang]
    friend_links = "".join(
        f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)}</a>'
        for label, url in FOOTER_LINKS
    )
    more = rel_url(current_file, path_to_file(f"{lang}/friends/"))
    privacy = rel_url(current_file, path_to_file(f"{lang}/privacy/"))
    sitemap = rel_url(current_file, OUT / "sitemap.xml")
    return f"""
  <footer class="site-footer">
    <div class="wrap footer-grid">
      <section class="footer-brand">
        <a class="footer-logo" href="{rel_url(current_file, path_to_file(f'{lang}/'))}">
          <img src="{FAVICON_URL}" alt="" width="38" height="38">
          <span>OmegaXYZ</span>
        </a>
        <div class="footer-decl">
          <p>{esc(t["footer_license"])}</p>
          <p>{esc(t["footer_copyright"])} <span class="footer-sep">|</span> {esc(t["footer_icp"])} <span class="footer-sep">|</span> {esc(t["footer_business"])}:<a href="mailto:noverfitting@gmail.com">noverfitting@gmail.com</a> <span class="footer-sep">|</span> <a href="{privacy}">{esc(t["privacy"])}</a> <span class="footer-sep">|</span> <a href="{sitemap}">{esc(t["sitemap"])}</a></p>
        </div>
      </section>
      <nav class="footer-friends" aria-label="友情链接">
        {friend_links}
        <a class="more-link" href="{more}">{esc(t["footer_more_friends"])}</a>
      </nav>
    </div>
  </footer>
    """


def analytics_scripts():
    return """
  <script>
    var _hmt = _hmt || [];
    (function() {
      var hm = document.createElement("script");
      hm.src = "https://hm.baidu.com/hm.js?1ff2438a5cf31d5625e00ac67e811160";
      var s = document.getElementsByTagName("script")[0];
      s.parentNode.insertBefore(hm, s);
    })();
  </script>
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-B96MD38Q4R"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag("js", new Date());
    gtag("config", "G-B96MD38Q4R");
  </script>
    """


THEME_SCRIPT = (
    '<script>(function(){try{var t=localStorage.getItem("theme");'
    'if(!t)t=matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light";'
    'document.documentElement.dataset.theme=t;}catch(e){}})();</script>'
)
ARTICLE_ASSETS = (
    """
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/contrib/auto-render.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/languages/matlab.min.js"></script>"""
)


def layout(current_file, lang, title, body, description="", alt_path="", article_assets=False, image=""):
    css = rel_url(current_file, OUT / "assets/site.css") + f"?v={ASSET_VERSION}"
    js = rel_url(current_file, OUT / "assets/site.js") + f"?v={ASSET_VERSION}"
    katex = "https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/katex.min.css"
    desc = description or I18N[lang]["intro"]
    canonical = site_url_for_file(current_file)
    other = "en" if lang == "zh" else "zh"
    alternate = site_url_for_file(path_to_file(alt_path)) if alt_path else site_url_for_file(path_to_file(f"{other}/"))
    og_image = image or LOGO_URL
    head_katex = (
        '\n  <link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>'
        f'\n  <link rel="stylesheet" href="{katex}">'
    ) if article_assets else ""
    body_assets = ARTICLE_ASSETS if article_assets else ""
    return f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="preconnect" href="https://cdn.omegaxyz.com">
  <link rel="preconnect" href="https://cv.omegaxyz.com">
  {THEME_SCRIPT}
  <title>{esc(title)} · OmegaXYZ</title>
  <meta name="description" content="{esc(desc)}">
  <meta name="theme-color" content="#008d98">
  <link rel="canonical" href="{esc(canonical)}">
  <link rel="alternate" hreflang="{other}" href="{esc(alternate)}">
  <link rel="alternate" hreflang="{lang}" href="{esc(canonical)}">
  <meta property="og:site_name" content="OmegaXYZ">
  <meta property="og:type" content="{'article' if article_assets else 'website'}">
  <meta property="og:title" content="{esc(title)} · OmegaXYZ">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:image" content="{esc(og_image)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)} · OmegaXYZ">
  <meta name="twitter:description" content="{esc(desc)}">
  <meta name="twitter:image" content="{esc(og_image)}">
  <link rel="icon" href="{FAVICON_URL}" type="image/png">
  <link rel="apple-touch-icon" href="{FAVICON_URL}">{head_katex}
  <link rel="stylesheet" href="{css}">
</head>
<body>
  <a class="skip-link" href="#main-content">{esc(I18N[lang]["skip"])}</a>
  {nav(current_file, lang, title, alt_path)}
  <a id="main-content" tabindex="-1"></a>
  {body}
  <script src="{js}"></script>
  {footer(current_file, lang)}{body_assets}
  {analytics_scripts()}
</body>
</html>
"""


def render_page_link(entry, lang, current_file):
    href = rel_url(current_file, path_to_file(entry_path(entry, lang)))
    return f"""
    <a class="page-link" href="{href}">
      <strong>{esc(entry[f'title_{lang}'])}</strong>
      <span class="page-link-go" aria-hidden="true">→</span>
    </a>
    """


def render_page_card(entry, lang, current_file):
    href = rel_url(current_file, path_to_file(entry_path(entry, lang)))
    excerpt = short_text(entry.get(f"excerpt_{lang}") or strip_tags(entry.get(f"content_{lang}", "")), 132)
    return f"""
    <a class="page-card" href="{href}">
      <span class="page-card-date">{esc(date_only(entry['date']))}</span>
      <strong>{esc(entry[f'title_{lang}'])}</strong>
      <span class="page-card-excerpt">{esc(excerpt)}</span>
      <span class="page-card-go" aria-hidden="true">→</span>
    </a>
    """


def render_latest_row(entry, lang, current_file, eager=False):
    href = rel_url(current_file, path_to_file(entry_path(entry, lang)))
    image = first_image(entry)
    if image:
        loading = "eager" if eager else "lazy"
        priority = ' fetchpriority="high"' if eager else ""
        image_html = f'<img src="{esc(image)}" alt="" loading="{loading}" decoding="async"{priority} width="200" height="132">'
    else:
        image_html = '<span>OmegaXYZ</span>'
    pills = render_term_pills(entry, lang, current_file, 2, 2)
    return f"""
    <article class="latest-row">
      <a class="latest-media" href="{href}">{image_html}</a>
      <div class="latest-copy">
        <h3><a href="{href}">{esc(entry[f'title_{lang}'])}</a></h3>
        <div class="meta">{esc(date_only(entry['date']))}</div>
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
    all_rows = [render_latest_row(e, lang, current) for e in posts]
    home_data_file = current.parent / "home-rows.json"
    write(home_data_file, json.dumps(all_rows, ensure_ascii=False))
    home_data_url = rel_url(current, home_data_file)
    latest_rows = "".join(render_latest_row(e, lang, current, eager=i == 0) for i, e in enumerate(posts[:9]))
    priority_slugs = ["friends", "webhistory", "makefriends", "comment"]
    home_pages = [p for p in pages if p["slug"] not in ("evolutionary-algorithm-navigator", "menu-bar-privacy")]
    ordered_pages = sorted(
        home_pages,
        key=lambda p: priority_slugs.index(p["slug"]) if p["slug"] in priority_slugs else len(priority_slugs),
    )
    about_label = "关于我" if lang == "zh" else "About Me"
    page_links = "".join(render_page_link(e, lang, current) for e in ordered_pages[:5])
    page_links += (
        '<a class="page-link" href="https://cv.omegaxyz.com/" target="_blank" rel="noopener noreferrer">'
        f'<strong>{esc(about_label)}</strong><span class="page-link-go" aria-hidden="true">↗</span></a>'
    )
    term_counts = {}
    for entry in posts:
        for term in entry["categories"]:
            term_counts.setdefault(term["slug"], term_info(term))
            term_counts[term["slug"]]["count"] += 1
    topic_pool = sorted(term_counts.values(), key=lambda item: item["count"], reverse=True)[:24]
    topic_links = "".join(
        f'<a class="topic-chip" data-topic-item href="{rel_url(current, path_to_file(term_path("category", term["slug"], lang)))}">'
        f'<span>{esc(term_label(term, lang))}</span><strong>{term.get("count", 0)}</strong></a>'
        for term in topic_pool
    )
    t = I18N[lang]
    search_index = rel_url(current, OUT / f"{lang}/search-index.json")
    stat_archive = rel_url(current, path_to_file(archive_path(lang)))
    stat_pages = rel_url(current, path_to_file(f"{lang}/pages/"))
    stat_comment = rel_url(current, path_to_file(f"{lang}/comment/"))
    stat_terms = rel_url(current, path_to_file(f"{lang}/categories/"))
    body = f"""
    <main class="wrap">
      <section class="hero">
        <p class="hero-kicker">{esc(t['tagline'])}</p>
        <h1 class="hero-line"><span class="spinner-verb" data-spinner-verb>Pondering</span><span class="spinner-dots" aria-hidden="true">…</span></h1>
        <p class="spinner-def" data-spinner-def></p>
        <section class="search-box home-search" data-search="{search_index}">
          <input type="search" placeholder="{esc(t['search_placeholder'])}" aria-label="{esc(t['search'])}">
          <div class="search-results" data-search-results></div>
        </section>
      </section>
      <ul class="stats-row" aria-label="Site statistics">
        <li><a href="{stat_archive}"><strong>{stats['posts']}</strong><span>{esc(t['archive'])}</span></a></li>
        <li><a href="{stat_pages}"><strong>{stats['pages']}</strong><span>{esc(t['pages'])}</span></a></li>
        <li><a href="{stat_comment}"><strong>{stats['comments']}</strong><span>{esc(t['comments'])}</span></a></li>
        <li><a href="{stat_terms}"><strong>{stats['tags']}</strong><span>{esc(t['tags'])}</span></a></li>
      </ul>
      <section class="home-panel" data-home-topics>
        <div class="topic-bar">
          <div class="topic-rail" data-topic-rail aria-label="{esc(t['categories'])}">
            {topic_links}
          </div>
          <button class="topic-refresh" type="button" data-topic-refresh aria-label="{esc(t['shuffle_topics'])}" title="{esc(t['shuffle_topics'])}">↻</button>
        </div>
      </section>
      <section class="band" data-home-latest data-home-data="{home_data_url}">
        <div class="section-head">
          <h2>{esc(t['latest'])}</h2>
          <div class="home-tabs" role="tablist">
            <button class="home-tab is-active" type="button" data-home-mode="latest">{esc(t['tab_latest'])}</button>
            <button class="home-tab" type="button" data-home-mode="random">{esc(t['tab_random'])}</button>
          </div>
        </div>
        <div class="latest-list" data-home-list>{latest_rows}</div>
      </section>
      <section class="band">
        <div class="section-head"><div><h2>{esc(t['pages'])}</h2></div></div>
        <div class="page-strip">{page_links}</div>
      </section>
    </main>
    """
    return layout(current, lang, "OmegaXYZ", body, t["intro"], f"{'en' if lang == 'zh' else 'zh'}/")


TIMELINE = [
    {"date": "2026.5.27", "zh": "弃用阿里云，网站从 WordPress 下架，迁移到 GitHub + Cloudflare", "en": "Dropped Alibaba Cloud; retired WordPress and migrated to GitHub + Cloudflare"},
    {"date": "2023.3.29", "zh": "进入 AI 纪元", "en": "Entered the AI era"},
    {"date": "2022.1.24", "zh": "网站 UI 重新设计", "en": "Website UI redesigned"},
    {"date": "2021.6.16", "zh": "服务器优化与迁移（开发者服务器）", "en": "Server optimization and migration (developer server)"},
    {"date": "2020.2.5", "zh": "网站总访问量突破 100 万", "en": "Total site visits surpassed 1,000,000"},
    {"date": "2020.1.6", "zh": "网站配套微信小程序上线", "en": "Companion WeChat mini-program launched"},
    {"date": "2020.1.4", "zh": "服务器重置、数据库清理、冗余插件清理、HTTPS 配置", "en": "Server reset, database cleanup, plugin pruning, and HTTPS configured"},
    {"date": "2019.1.15", "zh": "网站速度提升，开启 Cache", "en": "Faster site; caching enabled"},
    {"date": "2018.5.3", "zh": "增加 IP BAN，提高反爬虫能力（2020.1.4 已下线）", "en": "Added IP banning to deter scrapers (retired 2020.1.4)"},
    {"date": "2018.3.28", "zh": "CSS 优化，进一步提高网站响应速度", "en": "CSS optimization for faster response times"},
    {"date": "2018.1.15", "zh": "增加文章评分功能，搜索关键字高亮显示", "en": "Added article ratings and search keyword highlighting"},
    {"date": "2018.1.9", "zh": "评论模块优化，增加网站订阅功能（2020.1.4 已下线）", "en": "Comment module improved; site subscriptions added (retired 2020.1.4)"},
    {"date": "2017.8.25", "zh": "文章采用 BY-NC-SA 4.0 授权", "en": "Articles licensed under CC BY-NC-SA 4.0"},
    {"date": "2017.7.27", "zh": "更换阿里云 ECS，实现网站整体迁移", "en": "Switched to Alibaba Cloud ECS; full site migration"},
    {"date": "2017.7.25", "zh": "建立 TuringXY（图灵技术域）微信公众号，并绑定网站，实现公众号全站搜索", "en": "Founded the TuringXY WeChat official account, linked to the site for full-site search"},
    {"date": "2017.4.18", "zh": "网站上线", "en": "Website went live"},
    {"date": "2017.4.12", "zh": "工信部备案成功", "en": "MIIT (ICP) filing approved"},
    {"date": "2017.4.6", "zh": "申请阿里云 ECS，制作网站并测试安装插件", "en": "Provisioned Alibaba Cloud ECS; built the site and tested plugins"},
    {"date": "2017.4.1", "zh": "申请 OmegaXYZ.com 域名并提交备案", "en": "Registered OmegaXYZ.com and submitted the ICP filing"},
]


def render_timeline(lang):
    items = "".join(
        f"""
        <li class="timeline-item">
          <span class="timeline-marker" aria-hidden="true"></span>
          <time class="timeline-date">{esc(item['date'])}</time>
          <p class="timeline-event">{esc(item[lang])}</p>
        </li>"""
        for item in TIMELINE
    )
    return f'<ol class="timeline">{items}</ol>'


def render_timeline_page(entry, lang):
    current = path_to_file(entry_path(entry, lang))
    other = "en" if lang == "zh" else "zh"
    title = entry[f"title_{lang}"]
    body = f"""
    <main class="wrap band timeline-page">
      <div class="section-head"><h1>{esc(title)}</h1></div>
      {render_timeline(lang)}
    </main>
    """
    return layout(current, lang, title, body, entry[f"excerpt_{lang}"], entry_path(entry, other))


def render_entry(entry, lang, legacy):
    if entry["url"].strip("/") == "friends":
        return render_friends_entry(entry, lang)
    if entry["url"].strip("/") == "webhistory":
        return render_timeline_page(entry, lang)
    current = path_to_file(entry_path(entry, lang))
    other = "en" if lang == "zh" else "zh"
    title = entry[f"title_{lang}"]
    content = rewrite_content(entry[f"content_{lang}"], lang, current, legacy)
    excerpt = entry[f"excerpt_{lang}"]
    term_links = render_term_pills(entry, lang, current, 8, 12)
    comments = render_comments(entry, lang)
    og_image = entry.get("thumbnail") or first_image(entry)
    ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "datePublished": date_only(entry["date"]),
        "dateModified": date_only(entry.get("modified") or entry["date"]),
        "author": {"@type": "Person", "name": "Xu Yi"},
        "publisher": {"@type": "Organization", "name": "OmegaXYZ",
                      "logo": {"@type": "ImageObject", "url": LOGO_URL}},
        "mainEntityOfPage": site_url_for_file(current),
    }
    if og_image:
        ld["image"] = og_image
    ld_json = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
    page_class = {"comment": " donate-page", "privacy": " privacy-page"}.get(entry.get("slug"), "")
    body = f"""
    <main class="wrap layout{page_class}">
      <article class="article">
        <div class="meta">{esc(date_only(entry['date']))}</div>
        <h1>{esc(title)}</h1>
        <div class="terms">{term_links}</div>
        <div class="article-content">{content}</div>
        {comments}
      </article>
      <aside class="sidebar">
        <section class="side-box"><h2>{esc(I18N[lang]['toc'])}</h2><nav data-toc></nav></section>
      </aside>
    </main>
    <script type="application/ld+json">{ld_json}</script>
    """
    return layout(current, lang, title, body, excerpt, entry_path(entry, other), article_assets=True, image=og_image)


def render_friends_entry(entry, lang):
    current = path_to_file(entry_path(entry, lang))
    other = "en" if lang == "zh" else "zh"
    title = "友情链接" if lang == "zh" else "Friends"
    desc = "长期阅读、技术写作与知识分享的朋友链接。" if lang == "zh" else "A curated set of long-running blogs and technical communities."
    apply_label = "申请友链" if lang == "zh" else "Apply for a link"
    visit_label = "访问" if lang == "zh" else "Visit"
    retired_label = "已退休" if lang == "zh" else "Retired"
    groups = []
    for category, label, url, logo in FRIEND_LINKS:
        if category not in groups:
            groups.append(category)
    sections = []
    for category in groups:
        cards = []
        for item_category, label, url, logo in FRIEND_LINKS:
            if item_category != category:
                continue
            card_logo = asset_url(logo) if logo else LOGO_URL
            if category == "按钮":
                href = rel_url(current, path_to_file(f"{lang}/makefriends/"))
                cards.append(f"""
                <a class="friend-card friend-action" href="{href}">
                  <img src="{LOGO_URL}" alt="" loading="lazy" width="52" height="52">
                  <div><h2>{esc(label)}</h2><p>{esc(desc)}</p></div>
                </a>
                """)
            elif url:
                cards.append(f"""
                <article class="friend-card">
                  <img src="{esc(card_logo)}" alt="" loading="lazy" width="52" height="52">
                  <div><h2>{esc(label)}</h2><p>{esc(url.replace('https://', '').replace('http://', '').strip('/'))}</p></div>
                  <a class="friend-visit" href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(visit_label)} <span aria-hidden="true">↗</span></a>
                </article>
                """)
            else:
                cards.append(f"""
                <article class="friend-card is-retired">
                  <img src="{esc(card_logo)}" alt="" loading="lazy" width="52" height="52">
                  <div><h2>{esc(label)}</h2><p>{esc(retired_label)}</p></div>
                </article>
                """)
        sections.append(f"""
        <section class="friend-section">
          <div class="section-head"><div><h2>{esc(category)}</h2></div></div>
          <div class="friends-grid">{''.join(cards)}</div>
        </section>
        """)
    body = f"""
    <main class="wrap band friends-page">
      <section class="friends-hero">
        <div>
          <div class="eyebrow">OmegaXYZ</div>
          <h1>{esc(title)}</h1>
          <p>{esc(desc)}</p>
        </div>
        <a class="button primary" href="{rel_url(current, path_to_file(f'{lang}/makefriends/'))}">{esc(apply_label)}</a>
      </section>
      {''.join(sections)}
    </main>
    """
    body = "\n".join(line.rstrip() for line in body.splitlines())
    return layout(current, lang, title, body, desc, entry_path(entry, other))


COMMENT_EMOJIS = [
    "🦊", "🐱", "🐼", "🦉", "🐧", "🦁", "🐯", "🐨", "🐸", "🐙",
    "🦄", "🐝", "🦋", "🐬", "🦝", "🐺", "🦅", "🐢", "🦒", "🐳",
    "🦦", "🐰", "🐶", "🐭", "🦔", "🐹", "🦜", "🐲", "🦓", "🐮",
]


def comment_avatar(author):
    key = (author or "anon").strip().lower()
    digest = hashlib.md5(key.encode("utf-8")).hexdigest()
    emoji = COMMENT_EMOJIS[int(digest, 16) % len(COMMENT_EMOJIS)]
    hue = int(digest[8:14], 16) % 360
    return emoji, hue


def render_comments(entry, lang):
    comments = entry["comments"]
    if not comments:
        return ""
    parts = [f'<section class="comments"><h2>{esc(I18N[lang]["comments"])} ({len(comments)})</h2>']
    for c in comments:
        cls = "comment reply" if c["parent"] else "comment"
        name = esc(c["author"] or "Anonymous")
        author = f'<a href="{esc(c["url"])}" target="_blank" rel="nofollow noopener">{name}</a>' if c["url"] else name
        emoji, hue = comment_avatar(c["author"])
        parts.append(f"""
        <div class="{cls}" id="comment-{c['id']}">
          <div class="comment-avatar" aria-hidden="true" style="background:hsl({hue} 68% 84%)">{emoji}</div>
          <div class="comment-body">
            <div class="comment-head"><strong>{author}</strong><time>{esc(c['date'])}</time></div>
            <div class="comment-text">{c[f'content_{lang}']}</div>
          </div>
        </div>
        """)
    parts.append("</section>")
    return "".join(parts)


def archive_count_box(value, lang):
    icon = (
        '<span class="archive-count-icon" aria-hidden="true">'
        '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" '
        'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 3l8 4.5-8 4.5-8-4.5z"/><path d="M4 12l8 4.5 8-4.5"/>'
        '<path d="M4 16.5l8 4.5 8-4.5"/></svg></span>'
    )
    return (
        f'<div class="archive-count">{icon}'
        f'<span class="archive-count-body"><strong data-archive-count>{value}</strong>'
        f'<span>{esc(I18N[lang]["results"])}</span></span></div>'
    )


def render_archive(site, lang):
    posts = [e for e in site["entries"] if e["type"] == "post"]
    current = path_to_file(archive_path(lang))
    items = "".join(render_archive_item(e, lang, current, interactive=True) for e in posts)
    category_counts = {}
    tag_counts = {}
    for entry in posts:
        for term in entry["categories"]:
            key = term["slug"]
            category_counts.setdefault(key, term_info(term))
            category_counts[key]["count"] += 1
        for term in entry["tags"]:
            key = term["slug"]
            tag_counts.setdefault(key, term_info(term))
            tag_counts[key]["count"] += 1
    top_categories = sorted(category_counts.values(), key=lambda item: (-item["count"], term_label(item, lang).lower()))
    top_tags = sorted(tag_counts.values(), key=lambda item: (-item["count"], term_label(item, lang).lower()))
    all_chip = f'<button class="filter-chip is-active" type="button" data-archive-kind="" data-archive-term="" onclick="window.omegaArchiveTag&&window.omegaArchiveTag(this)">{esc(I18N[lang]["filter_all"])}</button>'
    category_chips = "".join(
        f'<button class="filter-chip category-filter" type="button" data-archive-kind="category" data-archive-term="{esc(term["slug"])}" onclick="window.omegaArchiveTag&&window.omegaArchiveTag(this)">{esc(term_label(term, lang))}<span>{term["count"]}</span></button>'
        for term in top_categories
    )
    tag_chips = "".join(
        f'<button class="filter-chip tag-filter" type="button" data-archive-kind="tag" data-archive-term="{esc(term["slug"])}" onclick="window.omegaArchiveTag&&window.omegaArchiveTag(this)">{esc(term_label(term, lang))}<span>{term["count"]}</span></button>'
        for term in top_tags
    )
    body = f"""
    <main class="wrap band archive-page" data-archive>
      <div class="section-head">
        <div><h1>{esc(I18N[lang]["all_posts"])}</h1><p>{esc(I18N[lang]["latest_desc"])}</p></div>
        {archive_count_box(len(posts), lang)}
      </div>
      <section class="archive-tools">
        <div class="archive-search">
          <input type="search" data-archive-query oninput="window.omegaArchiveApply&&window.omegaArchiveApply(this)" placeholder="{esc(I18N[lang]["archive_search_placeholder"])}" aria-label="{esc(I18N[lang]["search"])}">
        </div>
        <label class="archive-sort">
          <span>{esc(I18N[lang]["sort"])}</span>
          <select data-archive-sort onchange="window.omegaArchiveApply&&window.omegaArchiveApply(this)" aria-label="{esc(I18N[lang]["sort"])}">
            <option value="newest">{esc(I18N[lang]["sort_newest"])}</option>
            <option value="oldest">{esc(I18N[lang]["sort_oldest"])}</option>
            <option value="title">{esc(I18N[lang]["sort_title"])}</option>
          </select>
        </label>
      </section>
      <section class="archive-filters" aria-label="{esc(I18N[lang]["tags"])}">
        <div class="filter-group filter-group-all">{all_chip}</div>
        <div class="filter-group">
          <h2>{esc(I18N[lang]["categories"])}</h2>
          <div>{category_chips}</div>
        </div>
        <div class="filter-group">
          <h2>{esc(I18N[lang]["tags"])}</h2>
          <div>{tag_chips}</div>
        </div>
      </section>
      <div class="archive-list archive-index">{items}</div>
      <p class="archive-empty" data-archive-empty hidden>{esc(I18N[lang]["no_results"])}</p>
    </main>
    """
    write(current, layout(current, lang, I18N[lang]["all_posts"], body, alt_path=archive_path("en" if lang == "zh" else "zh")))
    pages = max(1, math.ceil(len(posts) / 24))
    for page in range(2, pages + 1):
        render_redirect(archive_path(lang, page), archive_path(lang))


def render_archive_item(entry, lang, current, interactive=False):
    href = rel_url(current, path_to_file(entry_path(entry, lang)))
    terms = entry["categories"] + entry["tags"]
    pills = render_term_pills(entry, lang, current, 3, 4)
    if interactive:
        search_text = " ".join(
            [entry[f"title_{lang}"], entry[f"excerpt_{lang}"]]
            + [term_label(t, lang) for t in terms]
            + [t["slug"] for t in terms]
        ).lower()
        category_slugs = " ".join(t["slug"] for t in entry["categories"])
        tag_slugs = " ".join(t["slug"] for t in entry["tags"])
        attrs = (
            f' data-archive-item data-title="{esc(entry[f"title_{lang}"].lower())}"'
            f' data-date="{esc(date_only(entry["date"]))}"'
            f' data-categories="{esc(category_slugs)}"'
            f' data-tags="{esc(tag_slugs)}"'
            f' data-search="{esc(search_text)}"'
        )
    else:
        attrs = ""
    summary = short_text(entry[f"excerpt_{lang}"], 150)
    summary_html = f"\n        <p>{esc(summary)}</p>" if summary else ""
    return f"""
    <article class="archive-item"{attrs}>
      <time>{esc(date_only(entry['date']))}</time>
      <div>
        <h2><a href="{href}">{esc(entry[f'title_{lang}'])}</a></h2>{summary_html}
        <div class="terms">{pills}</div>
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
    items = "".join(render_page_card(e, lang, current) for e in pages)
    body = f'<main class="wrap band pages-page"><div class="section-head"><h1>{esc(I18N[lang]["all_pages"])}</h1></div><div class="page-card-grid">{items}</div></main>'
    write(current, layout(current, lang, I18N[lang]["all_pages"], body, alt_path=f"{'en' if lang == 'zh' else 'zh'}/pages/"))


def render_terms(site, lang):
    tag_cloud_html = ""
    for kind, label in (("tag", "tags"), ("category", "categories")):
        grouped = defaultdict(list)
        representatives = {}
        for entry in site["entries"]:
            for term in entry["categories" if kind == "category" else "tags"]:
                key = (term["slug"], term["name"])
                grouped[key].append(entry)
                representatives.setdefault(key, term_info(term))
        current = path_to_file(f"{lang}/{label}/")
        chips = []
        for (slug, name), entries in sorted(grouped.items(), key=lambda i: (-len(i[1]), i[0][1])):
            href = rel_url(current, path_to_file(term_path(kind, slug, lang)))
            display_label = term_label(representatives[(slug, name)], lang)
            kind_label = "分类" if kind == "category" and lang == "zh" else "标签" if kind == "tag" and lang == "zh" else "CAT" if kind == "category" else "TAG"
            chips.append(f'<a class="pill term-pill term-{kind}" data-label="{esc(kind_label)}" href="{href}"><span>{esc(display_label)}</span><strong>{len(entries)}</strong></a>')
            term_current = path_to_file(term_path(kind, slug, lang))
            if kind == "category":
                tag_counts = {}
                for entry in entries:
                    for term in entry["tags"]:
                        tag_counts.setdefault(term["slug"], term_info(term))
                        tag_counts[term["slug"]]["count"] += 1
                top_tags = sorted(tag_counts.values(), key=lambda item: (-item["count"], term_label(item, lang).lower()))
                all_chip = f'<button class="filter-chip is-active" type="button" data-archive-kind="" data-archive-term="" onclick="window.omegaArchiveTag&&window.omegaArchiveTag(this)">{esc(I18N[lang]["filter_all"])}</button>'
                tag_chips = "".join(
                    f'<button class="filter-chip tag-filter" type="button" data-archive-kind="tag" data-archive-term="{esc(term["slug"])}" onclick="window.omegaArchiveTag&&window.omegaArchiveTag(this)">{esc(term_label(term, lang))}<span>{term["count"]}</span></button>'
                    for term in top_tags
                )
                items = "".join(render_archive_item(e, lang, term_current, interactive=True) for e in entries)
                body = f"""
                <main class="wrap band term-page" data-archive>
                  <div class="section-head">
                    <div><h1>{esc(display_label)}</h1><p>{esc(I18N[lang]["categories"])} · {esc(I18N[lang]["filter_by_tag"])}</p></div>
                    {archive_count_box(len(entries), lang)}
                  </div>
                  <section class="archive-tools">
                    <div class="archive-search">
                      <input type="search" data-archive-query oninput="window.omegaArchiveApply&&window.omegaArchiveApply(this)" placeholder="{esc(I18N[lang]["archive_search_placeholder"])}" aria-label="{esc(I18N[lang]["search"])}">
                    </div>
                    <label class="archive-sort">
                      <span>{esc(I18N[lang]["sort"])}</span>
                      <select data-archive-sort onchange="window.omegaArchiveApply&&window.omegaArchiveApply(this)" aria-label="{esc(I18N[lang]["sort"])}">
                        <option value="newest">{esc(I18N[lang]["sort_newest"])}</option>
                        <option value="oldest">{esc(I18N[lang]["sort_oldest"])}</option>
                        <option value="title">{esc(I18N[lang]["sort_title"])}</option>
                      </select>
                    </label>
                  </section>
                  <section class="archive-filters tag-only-filters" aria-label="{esc(I18N[lang]["tags"])}">
                    <div class="filter-group filter-group-all">{all_chip}</div>
                    <div class="filter-group">
                      <h2>{esc(I18N[lang]["tags"])}</h2>
                      <div>{tag_chips}</div>
                    </div>
                  </section>
                  <div class="archive-list archive-index">{items}</div>
                  <p class="archive-empty" data-archive-empty hidden>{esc(I18N[lang]["no_results"])}</p>
                </main>
                """
                body = "\n".join(line.rstrip() for line in body.splitlines())
            else:
                items = "".join(render_archive_item(e, lang, term_current) for e in entries)
                body = f'<main class="wrap band term-page"><div class="section-head"><h1>{esc(display_label)}</h1><p>{esc(I18N[lang][label])}</p></div><div class="archive-list">{items}</div></main>'
            write(term_current, layout(term_current, lang, display_label, body, alt_path=term_path(kind, slug, "en" if lang == "zh" else "zh")))
        cloud_html = "".join(chips)
        if kind == "tag":
            tag_cloud_html = cloud_html
            body = f'<main class="wrap band term-index"><div class="section-head"><h1>{esc(I18N[lang][label])}</h1></div><div class="terms term-cloud tag-cloud">{cloud_html}</div></main>'
        else:
            body = (
                '<main class="wrap band term-index">'
                f'<div class="section-head"><h1>{esc(I18N[lang]["categories"])}</h1></div>'
                f'<div class="terms term-cloud category-cloud">{cloud_html}</div>'
                f'<div class="section-head term-index-sub"><h2>{esc(I18N[lang]["tags"])}</h2></div>'
                f'<div class="terms term-cloud tag-cloud">{tag_cloud_html}</div>'
                '</main>'
            )
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


def render_site_index_files(site):
    lastmod = {}
    for entry in site["entries"]:
        mod = date_only(entry.get("modified") or entry["date"])
        for lang in ("zh", "en"):
            lastmod[site_url_for_file(path_to_file(entry_path(entry, lang)))] = mod
    rows = []
    for file in sorted(OUT.rglob("*.html")):
        if file.name == "404.html":
            continue
        head = file.read_text(encoding="utf-8", errors="ignore")[:300].lower()
        if 'http-equiv="refresh"' in head or 'name="robots" content="noindex"' in head:
            continue
        url = site_url_for_file(file)
        mod = lastmod.get(url)
        if mod:
            rows.append(f"  <url><loc>{esc(url)}</loc><lastmod>{esc(mod)}</lastmod></url>")
        else:
            rows.append(f"  <url><loc>{esc(url)}</loc></url>")
    xml_urls = "\n".join(rows)
    write(OUT / "sitemap.xml", f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{xml_urls}
</urlset>
""")
    write(OUT / "robots.txt", f"""User-agent: *
Allow: /

Sitemap: {SITE_URL.rstrip("/")}/sitemap.xml
""")


def render_404():
    css = f"/assets/site.css?v={ASSET_VERSION}"
    write(OUT / "404.html", f"""<!doctype html>
<html lang="zh">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="preconnect" href="https://cdn.omegaxyz.com">
  <link rel="preconnect" href="https://cv.omegaxyz.com">
  {THEME_SCRIPT}
  <title>404 · OmegaXYZ</title>
  <meta name="robots" content="noindex">
  <meta name="theme-color" content="#008d98">
  <link rel="icon" href="{FAVICON_URL}" type="image/png">
  <link rel="stylesheet" href="{css}">
</head>
<body>
  <header class="site-header">
    <nav class="nav">
      <a class="brand" href="/zh/">
        <img src="{HOME_LOGO_URL}" alt="" width="40" height="40">
        <span class="brand-text"><strong>OmegaXYZ</strong></span>
      </a>
      <div class="nav-links">
        <a href="/zh/">主页 · Home</a>
        <a href="/zh/archive/">文章 · Archive</a>
        <a href="/zh/search/">搜索 · Search</a>
      </div>
    </nav>
  </header>
  <main class="wrap">
    <section class="hero">
      <p class="hero-kicker">404</p>
      <h1 class="hero-line">页面走丢了 · Page not found</h1>
      <p class="notfound-msg">这个链接可能已被移动或删除。This page may have been moved or removed.</p>
      <div class="hero-actions">
        <a class="button primary" href="/zh/">返回首页 / Home</a>
        <a class="button" href="/zh/search/">搜索 / Search</a>
      </div>
    </section>
  </main>
</body>
</html>
""")


def render_root_redirect():
    canonical = SITE_URL.rstrip("/") + "/zh/"
    write(OUT / "index.html", (
        '<!doctype html><html lang="zh"><head><meta charset="utf-8">'
        '<title>OmegaXYZ</title>'
        f'<link rel="canonical" href="{canonical}">'
        '<meta http-equiv="refresh" content="0; url=zh/">'
        '<script>(function(){var l;try{l=localStorage.getItem("lang")}catch(e){}'
        'if(l!=="zh"&&l!=="en")l=String(navigator.language||"").toLowerCase().indexOf("en")===0?"en":"zh";'
        'location.replace(l+"/");})();</script>'
        '</head><body></body></html>'
    ))


def main():
    site = load_site()
    legacy = build_legacy_map(site)
    copy_public()
    for lang in ("zh", "en"):
        write(path_to_file(f"{lang}/"), render_home(site, lang))
        render_pages_index(site, lang)
        render_terms(site, lang)
        render_search(site, lang)
    render_root_redirect()
    for entry in site["entries"]:
        for lang in ("zh", "en"):
            write(path_to_file(entry_path(entry, lang)), render_entry(entry, lang, legacy))
        render_redirect(entry["url"], entry_path(entry, "zh"))
    for lang in ("zh", "en"):
        render_archive(site, lang)
    for path in collect_legacy_paths(site, legacy):
        render_redirect(path, "zh/search/")
    render_redirect("archive/", "zh/archive/")
    render_site_index_files(site)
    render_404()
    print(f"built {OUT}")


if __name__ == "__main__":
    main()
