"""Static Markdown editions and bilingual, content-dated RSS/Atom feeds."""
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from urllib.parse import urljoin
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup
from markdownify import MarkdownConverter


ATOM = "http://www.w3.org/2005/Atom"
ZONE = timezone(timedelta(hours=8))
LIMIT = 50
SPECIAL_BODIES = {"webhistory": ".history-log", "friends": ".directory-body",
                  "makefriends": ".makefriends-hero p, .makefriends-grid, .makefriends-submit"}


def editorial(entry):
    return entry["type"] in ("post", "page") and entry["url"].strip("/") not in {"archive", "article-graph", "comment"}


class ReaderMarkdown(MarkdownConverter):
    def convert_pre(self, el, text, parent_tags):
        code = el.get_text().replace("\r\n", "\n").strip("\n")
        fence = "`" * max([3] + [len(run) + 1 for run in re.findall(r"`+", code)])
        classes = (el.code or el).get("class", [])
        lang = next((c[9:] for c in classes if c.startswith("language-")), el.get("lang", ""))
        return f"\n\n{fence}{lang}\n{code}\n{fence}\n\n"


def markdown_body(fragment, canonical):
    soup = BeautifulSoup(fragment.replace("\r\n", "\n"), "html.parser")
    for tag in soup.select("script, style, iframe, form, noscript, svg, .md-tools, .post-footer, [hidden]"):
        tag.decompose()
    for tag in soup.select("a[href], img[src]"):
        key = "href" if tag.name == "a" else "src"
        value = tag[key]
        if value.strip().lower().startswith(("javascript:", "data:")):
            del tag[key]
        else:
            tag[key] = urljoin(canonical, value)
    for img in soup.select("img.ql-img-inline-formula[alt],img.ql-img-displayed-equation[alt]"):
        delim = "$" if "ql-img-inline-formula" in img.get("class", []) else "$$"
        img.replace_with(delim + img["alt"] + delim)
    # The WordPress export also has bare text with blank lines instead of <p>.
    boundary = "\ue000"
    while boundary in fragment:
        boundary += "\ue000"
    for node in soup.find_all(string=re.compile(r"\n[ \t]*\n")):
        if node.strip() and not node.find_parent(["pre", "code"]):
            node.replace_with(re.sub(r"\n[ \t]*\n+", boundary, str(node)))
    for br in soup.select("pre br"):
        br.replace_with("\n")
    converter = ReaderMarkdown(heading_style="ATX", bullets="-", escape_underscores=False,
                               escape_asterisks=False, keep_inline_images_in=["a", "p", "td", "th", "figure", "span"],
                               table_infer_header=True, sub_symbol="<sub>", sup_symbol="<sup>")
    return converter.convert_soup(soup).replace(boundary, "\n\n").strip()


def special_body(page, selector, canonical):
    soup = BeautifulSoup(page, "html.parser")
    parts = soup.select(selector)
    if not parts:
        raise ValueError(f"Missing editorial body for {canonical}")
    return markdown_body("\n".join(map(str, parts)), canonical)


def authored_markdown(raw, resolve):
    # Keep the author's fences, math and formatting verbatim. Make inline
    # destinations in the site's Markdown dialect portable outside the website.
    inline = re.compile(r"(?P<tick>`+).*?(?P=tick)|(?P<prefix>\]\()(?P<url><?[^\s)]+>?)")
    def repl(m):
        if not m["prefix"]:
            return m[0]
        dest = m["url"]
        if dest.startswith("<") and dest.endswith(">"):
            return "](<" + resolve(dest[1:-1]) + ">"
        return "](" + resolve(dest)
    fence = None
    out = []
    for line in raw.strip().splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if marker:
            mark = marker[1]
            if fence is None:
                fence = mark
            elif mark.startswith(fence) and not line[marker.end():].strip():
                fence = None
        elif not fence:
            line = inline.sub(repl, line)
        out.append(line)
    return "\n".join(out)


def timestamp(value):
    dt = datetime.fromisoformat(value)
    return (dt if dt.tzinfo else dt.replace(tzinfo=ZONE)).astimezone(timezone.utc).replace(microsecond=0)


def record(entry, lang, url, body, previous, now):
    title, summary = entry[f"title_{lang}"], entry[f"excerpt_{lang}"]
    published = timestamp(entry["date"])
    explicit = max(published, timestamp(entry.get("modified") or entry["date"]))
    key = url.split("://", 1)[1].partition("/")[2]
    source = (body if entry["url"].strip("/") in SPECIAL_BODIES else
              entry.get("_markdown", {}).get(lang, entry.get(f"content_{lang}", body)))
    payload = json.dumps([title, summary, source.strip().replace("\r\n", "\n")], ensure_ascii=False, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()
    old = previous.get(key)
    if old and old[0] == digest:
        updated = max(explicit, timestamp(old[1]))
    else:
        updated = max(explicit, now) if previous else explicit
    doc = (f"# {title}\n\n" + ("作者" if lang == "zh" else "Author") + ": Yi Xu  \n"
           + ("发布日期" if lang == "zh" else "Published") + f": {entry['date'][:10]}  \n"
           + ("原文" if lang == "zh" else "Source") + f": <{url}>\n\n{body}\n")
    return doc, (key, [digest, updated.isoformat()]), (updated, published, url, title, summary)


def feeds(rows, lang, origin):
    home = f"{origin}/{lang}/"
    title = "OmegaXYZ · " + ("文章与页面" if lang == "zh" else "Posts and pages")
    rows = sorted(rows, key=lambda row: (-row[0].timestamp(), row[2]))[:LIMIT]
    newest = rows[0][0] if rows else timestamp("1970-01-01T00:00:00+00:00")
    def child(parent, name, text):
        ET.SubElement(parent, name).text = text
    rss = ET.Element("rss", {"version": "2.0", "xmlns:atom": ATOM})
    channel = ET.SubElement(rss, "channel")
    for name, text in (("title", title), ("link", home), ("description", title), ("language", lang),
                       ("lastBuildDate", format_datetime(newest, usegmt=True))):
        child(channel, name, text)
    ET.SubElement(channel, "atom:link", rel="self", href=home+"rss.xml", type="application/rss+xml")
    atom = ET.Element("feed", {"xmlns": ATOM, "xml:lang": lang})
    child(atom, "title", title)
    child(atom, "id", home+"atom.xml")
    child(atom, "updated", newest.isoformat())
    child(ET.SubElement(atom, "author"), "name", "Yi Xu")
    ET.SubElement(atom, "link", rel="self", href=home+"atom.xml", type="application/atom+xml")
    ET.SubElement(atom, "link", rel="alternate", href=home, type="text/html")
    for updated, published, url, name, summary in rows:
        item = ET.SubElement(channel, "item")
        for tag, text in (("title", name), ("guid", url), ("link", url), ("description", summary or name),
                          ("pubDate", format_datetime(published, usegmt=True)), ("atom:updated", updated.isoformat())):
            child(item, tag, text)
        ET.SubElement(item, "atom:link", rel="alternate", type="text/markdown", href=url+"index.md")
        item = ET.SubElement(atom, "entry")
        for tag, text in (("title", name), ("id", url), ("published", published.isoformat()),
                          ("updated", updated.isoformat()), ("summary", summary or name)):
            child(item, tag, text)
        ET.SubElement(item, "link", rel="alternate", type="text/html", href=url)
        ET.SubElement(item, "link", rel="alternate", type="text/markdown", href=url+"index.md")
    def serialize(root):
        ET.indent(root)
        return ET.tostring(root, encoding="utf-8", xml_declaration=True).decode() + "\n"
    return {"rss.xml": serialize(rss), "atom.xml": serialize(atom)}
