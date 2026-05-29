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
EXTRA_ENTRIES = ROOT / "content/extra_entries.json"
PUBLIC = ROOT / "public"
OUT = ROOT / "docs"
CDN = "https://cdn.omegaxyz.com"
SITE_URL = "https://omegaxyz.com"
ASSET_VERSION = "20260529-deepreport"
LOGO_URL = CDN + "/2017/11/cropped-omegaxyzlogo.jpg"
HOME_LOGO_URL = CDN + "/2020/01/AI-GIF.gif"
CLUSTRMAPS_QUERY = "cl=080808&w=350&t=t&d=FE7PVw_CLT837rM_LSa4opyrN4W5MYhHu86bM_MzIIM&co=f2f5f7&cmo=3acc3a&cmn=ff5353&ct=808080"
SOURCE_HOSTS = {"omegaxyz.com", "www.omegaxyz.com", "en.omegaxyz.com"}

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
    ("按钮", "申请友链", "https://omegaxyz.com/makefriends/", ""),
    ("退休", "yoko blog", "", "https://omegaxyz.com/wp-content/uploads/2019/08/default_avatar.jpg"),
    ("退休", "shawnluo", "", "https://omegaxyz.com/wp-content/uploads/2018/06/shawnluo.png"),
    ("退休", "人工智能网", "", "https://omegaxyz.com/wp-content/uploads/2018/01/machinelearningicon.jpg"),
    ("退休", "Python爱好者", "", "https://omegaxyz.com/wp-content/uploads/2020/03/codingdogzxg.jpg"),
]

I18N = {
    "zh": {
        "tagline": "徐奕的专栏",
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
        "footer_more_friends": "更多(非首页友链)...",
        "visitor_map": "访问统计地图",
    },
    "en": {
        "tagline": "Xu Yi's column",
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
        "footer_more_friends": "More friends...",
        "visitor_map": "Visitor map",
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
    extras = load_extra_entries()
    if extras:
        extra_urls = {entry["url"] for entry in extras}
        site["entries"] = extras + [entry for entry in site["entries"] if entry.get("url") not in extra_urls]
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
    return entries


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
        return TERM_EN.get(term["slug"], term["name"])
    return term["name"]


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
    logo_url = HOME_LOGO_URL if current_file in (OUT / "index.html", path_to_file(f"{lang}/")) else LOGO_URL
    links = [
        (t["home"], f"{lang}/", False),
        (t["archive"], archive_path(lang), False),
        (t["pages"], f"{lang}/pages/", False),
        (t["categories"], f"{lang}/categories/", False),
        (t["about"], "https://cv.omegaxyz.com/", True),
    ]
    link_html = "".join(
        f'<a href="{esc(path)}" target="_blank" rel="noopener noreferrer">{esc(label)}</a>'
        if external else
        f'<a href="{rel_url(current_file, path_to_file(path))}">{esc(label)}</a>'
        for label, path, external in links
    )
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
          <a href="{alt}">{esc(t['language'])}</a>
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
    return f"""
  <footer class="site-footer">
    <div class="wrap footer-grid">
      <section class="footer-brand">
        <a class="footer-logo" href="{rel_url(current_file, path_to_file(f'{lang}/'))}">
          <img src="{LOGO_URL}" alt="" width="42" height="42">
          <span>OmegaXYZ</span>
        </a>
        <p>{esc(t["footer_license"])}</p>
        <p>{esc(t["footer_copyright"])} <span class="footer-sep">|</span> {esc(t["footer_icp"])} <span class="footer-sep">|</span> {esc(t["footer_business"])}:<a href="mailto:noverfitting@gmail.com">noverfitting@gmail.com</a> <span class="footer-sep">|</span> <a href="{privacy}">{esc(t["privacy"])}</a></p>
      </section>
      <section class="footer-map" aria-label="{esc(t["visitor_map"])}">
        <div class="clustrmaps-widget">
          <div class="map-placeholder" aria-hidden="true">
            <span>{esc(t["visitor_map"])}</span>
            <i></i><i></i><i></i><i></i><i></i>
          </div>
          <img class="clustrmaps-fallback" src="https://www.clustrmaps.com/map_v2.png?{CLUSTRMAPS_QUERY}" alt="Visitor map" loading="eager" decoding="async" width="350" height="175">
          <script type="text/javascript" id="clustrmaps" src="//cdn.clustrmaps.com/map_v2.js?{CLUSTRMAPS_QUERY}"></script>
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


def layout(current_file, lang, title, body, description="", alt_path=""):
    css = rel_url(current_file, OUT / "assets/site.css") + f"?v={ASSET_VERSION}"
    js = rel_url(current_file, OUT / "assets/site.js") + f"?v={ASSET_VERSION}"
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
  <link rel="icon" href="{LOGO_URL}" type="image/jpeg">
  <link rel="apple-touch-icon" href="{LOGO_URL}">
  <link rel="stylesheet" href="{katex}">
  <link rel="stylesheet" href="{css}">
</head>
<body>
  {nav(current_file, lang, title, alt_path)}
  {body}
  <script src="{js}"></script>
  {footer(current_file, lang)}
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/contrib/auto-render.min.js"></script>
  {analytics_scripts()}
</body>
</html>
"""


def render_card(entry, lang, current_file, compact=False):
    title = entry[f"title_{lang}"]
    excerpt = short_text(entry[f"excerpt_{lang}"], 112 if compact else 150)
    href = rel_url(current_file, path_to_file(entry_path(entry, lang)))
    pills = render_term_pills(entry, lang, current_file, 2, 2)
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
    pills = render_term_pills(entry, lang, current_file, 2, 2)
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
    pills = render_term_pills(entry, lang, current_file, 2, 2)
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
          <div class="hero-title">
            <img class="hero-logo" src="{HOME_LOGO_URL}" alt="" width="74" height="74">
            <h1>OmegaXYZ</h1>
          </div>
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
    if entry["url"].strip("/") == "friends":
        return render_friends_entry(entry, lang)
    current = path_to_file(entry_path(entry, lang))
    other = "en" if lang == "zh" else "zh"
    title = entry[f"title_{lang}"]
    content = rewrite_content(entry[f"content_{lang}"], lang, current, legacy)
    excerpt = entry[f"excerpt_{lang}"]
    term_links = render_term_pills(entry, lang, current, 8, 12)
    comments = render_comments(entry, lang)
    body = f"""
    <main class="wrap layout">
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
    """
    return layout(current, lang, title, body, excerpt, entry_path(entry, other))


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
                  <a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(visit_label)}</a>
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
    current = path_to_file(archive_path(lang))
    items = "".join(render_archive_item(e, lang, current, interactive=True) for e in posts)
    category_counts = {}
    tag_counts = {}
    for entry in posts:
        for term in entry["categories"]:
            key = term["slug"]
            category_counts.setdefault(key, {"name": term["name"], "slug": key, "count": 0})
            category_counts[key]["count"] += 1
        for term in entry["tags"]:
            key = term["slug"]
            tag_counts.setdefault(key, {"name": term["name"], "slug": key, "count": 0})
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
        <div class="archive-count"><strong data-archive-count>{len(posts)}</strong><span>{esc(I18N[lang]["results"])}</span></div>
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
    return f"""
    <article class="archive-item"{attrs}>
      <time>{esc(date_only(entry['date']))}</time>
      <div>
        <h2><a href="{href}">{esc(entry[f'title_{lang}'])}</a></h2>
        <p>{esc(short_text(entry[f'excerpt_{lang}'], 150))}</p>
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
            kind_label = "分类" if kind == "category" and lang == "zh" else "标签" if kind == "tag" and lang == "zh" else "CAT" if kind == "category" else "TAG"
            chips.append(f'<a class="pill term-pill term-{kind}" data-label="{esc(kind_label)}" href="{href}"><span>{esc(display_label)}</span><strong>{len(entries)}</strong></a>')
            term_current = path_to_file(term_path(kind, slug, lang))
            if kind == "category":
                tag_counts = {}
                for entry in entries:
                    for term in entry["tags"]:
                        tag_counts.setdefault(term["slug"], {"name": term["name"], "slug": term["slug"], "count": 0})
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
                    <div class="archive-count"><strong data-archive-count>{len(entries)}</strong><span>{esc(I18N[lang]["results"])}</span></div>
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
        body = f'<main class="wrap band term-index"><div class="section-head"><h1>{esc(I18N[lang][label])}</h1></div><div class="terms term-cloud {kind}-cloud">{"".join(chips)}</div></main>'
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
        render_pages_index(site, lang)
        render_terms(site, lang)
        render_search(site, lang)
    write(OUT / "index.html", render_home(site, "zh", OUT / "index.html"))
    for entry in site["entries"]:
        for lang in ("zh", "en"):
            write(path_to_file(entry_path(entry, lang)), render_entry(entry, lang, legacy))
        render_redirect(entry["url"], entry_path(entry, "zh"))
    for lang in ("zh", "en"):
        render_archive(site, lang)
    for path in collect_legacy_paths(site, legacy):
        render_redirect(path, "zh/search/")
    render_redirect("archive/", "zh/archive/")
    render_site_index_files()
    print(f"built {OUT}")


if __name__ == "__main__":
    main()
