# OmegaXYZ 静态站点维护手册

这个仓库是 OmegaXYZ 从 WordPress 迁移后的静态站点。GitHub Actions 会自动构建静态页面并发布到 GitHub Pages；文章和页面的媒体文件放在 Cloudflare R2，通过 CDN 引用。

## 换机器后怎么开始

1. 准备一台有 `git` 和 `python3` 的机器。
2. 克隆仓库：

```bash
git clone git@github.com:xyjigsaw/omegaxyz.git
cd omegaxyz
```

如果当前机器没有 GitHub SSH key，可以先在 GitHub 加新的 deploy key，或临时使用 HTTPS clone。

3. 修改内容后可以选择本地预览：

```bash
python3 scripts/build_site.py
python3 -m http.server 4173 --directory docs
```

打开 `http://127.0.0.1:4173/zh/`。

这一步不是发布必需步骤；正式发布会由 GitHub Actions 自动构建。

4. 提交并推送源文件：

```bash
git status
git add content
git commit -m "Add new post"
git push origin master
```

GitHub Actions 会在服务器上重新生成 `docs/`，然后部署到 GitHub Pages。日常写文章只需要提交 `content/` 中的正文和元数据；图片等媒体先上传到 R2，不提交原文件或本地生成的 `docs/`。如果构建后发现 `data/media-cdn.json` 有变化，Actions 会自动回写一个清单更新提交。

## 内容从哪里来

迁移后的 WordPress 数据保存在 `data/site.json`。这个文件已经提交到仓库，是换机器后完整重建旧文章、页面、评论、分类和标签的基础数据。日常新增文章放在 `content/`，例如：

- `content/extra_entries.json`：文章元数据
- `content/example.zh.html`：中文正文
- `content/example.en.html`：英文正文

媒体地址清单保存在 `data/media-cdn.json`。它只记录当前站点引用到的 `https://cdn.omegaxyz.com/...` URL，不包含真实图片文件，也不包含任何 Cloudflare 密钥。

`scripts/build_site.py` 会先读取 `data/site.json`，再合并 `content/extra_entries.json` 里的新文章。换机器后只要 clone 仓库，就可以直接构建完整站点。

## 写一篇新文章

1. 在 `content/` 新建正文文件，例如：

```text
content/my-post.zh.html
content/my-post.en.html
```

正文直接写 HTML。图片可以用 `<figure>` 包起来：

```html
<figure>
  <img src="https://cdn.omegaxyz.com/2026/05/demo.png" alt="Demo">
  <figcaption>图片说明。</figcaption>
</figure>
```

2. 在 `content/extra_entries.json` 添加一条记录：

```json
{
  "id": 9001,
  "type": "post",
  "title_zh": "中文标题",
  "title_en": "English Title",
  "excerpt_zh": "中文摘要。",
  "excerpt_en": "English summary.",
  "content_zh_file": "content/my-post.zh.html",
  "content_en_file": "content/my-post.en.html",
  "date": "2026-05-29 00:00:00",
  "modified": "2026-05-29 00:00:00",
  "slug": "my-post",
  "url": "2026/05/29/my-post/",
  "categories": [
    {"name": "技术域", "slug": "tech"}
  ],
  "tags": [
    {"name": "人工智能", "slug": "ai"}
  ],
  "comments": [],
  "thumbnail": "https://cdn.omegaxyz.com/2026/05/demo.png"
}
```

注意：

- `id` 用一个没用过的新数字。
- `url` 决定最终链接，中文和英文分别生成到 `/zh/...` 和 `/en/...`。
- `thumbnail` 是首页最新文章的缩略图。
- 文章自己的 `slug` 和 `url` 建议都写清楚，`slug` 建议只用小写英文、数字和连字符。
- 分类和标签必须写 `slug`，因为它决定分类页、标签页 URL 和前端过滤逻辑。
- 分类和标签的 `name_en` 不是必填；如果不写，系统会优先使用旧站内置映射，仍没有映射时会根据 `slug` 自动生成英文名。

## 文章置顶

任何文章都可配置置顶，不修改真实发布日期。Markdown frontmatter 可写：

```yaml
pinned: true
pin_order: 0
```

`pin_order` 选填，数值越小越靠前；相同优先级按原日期倒序。取消置顶写 `pinned: false` 或移除该字段。双语伴随文件共用主文件元数据，自动归档后设置继续生效。

`content/extra_entries.json` 与 `data/site.json` 的文章记录也支持 JSON 字段 `"pinned": true`、`"pin_order": 0`。首页默认文章流、分类和标签列表置顶优先，标记显示“置顶 / Pinned”；全部文章及分类筛选默认“置顶优先”，选择日期或标题排序会尊重该排序。首页随机模式仍随机抽取；搜索、相似推荐、sitemap 与真实日期不受置顶排序影响。

## 图片和媒体怎么存放

- **Cloudflare R2**：文章和页面用到的正文图片、封面、截图、SVG 插图、音视频和下载附件都上传到 `omegaxyz-image`。这些文件不按大小区分，小图和缩略图也不提交到 GitHub。
- **GitHub**：只提交正文、媒体 URL、配置和站点代码。`public/assets/` 留给站点自身的 CSS、JavaScript 等界面资源，不放文章配图或附件。

1. 先把媒体上传到 R2。新文件可按 `YYYY/MM/文章-slug/文件名` 组织，例如 `2026/11/my-post/cover.webp`。替换已发布的媒体时使用新文件名，并更新引用，避免 CDN 继续返回旧文件。
2. 通过 `https://cdn.omegaxyz.com/` 加对象路径访问，确认能打开后再提交文章。不要把带凭据的链接或 R2 的 S3 API 地址写入正文。
3. 中英文正文在 Markdown 链接或 HTML 的 `src` / `href` 中使用完整 CDN URL；首页封面在主 Markdown 的 `thumbnail` 字段或 `content/extra_entries.json` 对应记录的 `thumbnail` 字段填写完整 CDN URL。

可以用 Cloudflare 控制台上传，也可以用脚本批量上传。先在本机设置 `CF_API_TOKEN` 和 `CF_ACCOUNT_ID`，只上传本次要发布的媒体目录：

```bash
python3 scripts/upload_r2.py \
  --root "$HOME/Pictures/my-post" \
  --prefix 2026/11/my-post \
  --account-id "$CF_ACCOUNT_ID" \
  --bucket omegaxyz-image
```

不要把 Cloudflare token、S3 key、`.cache/`、`.media/`、原始备份包、翻译缓存或上传缓存提交到 GitHub。`data/` 目录里只提交 `data/site.json` 和 `data/media-cdn.json`。

新文章引用 CDN 媒体时，不需要手动修改 `data/site.json` 或 `data/media-cdn.json`。前者是旧 WordPress 的迁移数据；后者由 GitHub Actions 扫描构建产物后自动更新。换机器写文章只需 clone 仓库，不需要下载已有媒体。若要在本地检查 CDN 清单，可以先构建再运行：

```bash
python3 scripts/build_site.py
python3 scripts/generate_media_manifest.py
```

这会扫描 `docs/`，更新 `data/media-cdn.json`。

## 分类和标签怎么注册

不需要手动注册页面。只要文章元数据里写了：

```json
"categories": [{"name": "自然语言处理", "name_en": "Natural Language Processing", "slug": "nlp"}],
"tags": [{"name": "大语言模型", "name_en": "Large Language Models", "slug": "llm"}]
```

构建时会自动生成：

- 分类索引：`/zh/categories/`、`/en/categories/`
- 标签索引：`/zh/tags/`、`/en/tags/`
- 分类专页：`/zh/category/nlp/`、`/en/category/nlp/`
- 标签专页：`/zh/tag/llm/`、`/en/tag/llm/`
- 文章归档页筛选按钮
- 分类页下方的标签筛选按钮

当前逻辑：归档页展示全部分类和标签；分类专页可用该分类下出现的标签筛选。首页分类栏默认显示文章数最多的 6 个分类，换一批时从前 24 个分类中抽选。中英文分类总览的「文章地形」包含所有有文章的分类，每座峰的高度随分类文章数按对数比例变化。新增文章或分类后，下次构建会自动更新，不需要维护地形数据。

首页的「ΩXYZ」立体字标与文章地形共用一个全宽背景，地形和分类总览的交互地图使用同一套文章计数及地形生成逻辑。两页使用站内固定版本的 Three.js（`public/assets/vendor/`）。首页的桌面、手机及浅色、深色静态预览图放在 CDN 的 `design/section-omega/` 下；更新模型外观时用新文件名上传预览图，再更新场景样式中的 URL。普通文章页不加载 3D 模块。

英文分类/标签名不需要再手动改脚本。构建时会按这个优先级自动决定英文显示名：

1. 文章元数据里的 `name_en` 或 `label_en`
2. 旧站内置映射
3. 根据 slug 自动生成，例如 `large-language-model` 会显示为 `Large Language Model`

所以新增分类或标签时，`slug` 要写，`name_en` 可省。推荐写法是 `name`、`name_en` 和 `slug` 都写；偷懒时可以只写 `name` 和 `slug`。

## 构建逻辑摘要

`public/robots.txt` 是源站的爬虫规则，允许百度和 Google 搜索，保留其他已配置的爬虫限制。Cloudflare 的托管 robots.txt 可能在它前面追加规则。修改后要检查主域名实际返回的 `https://omegaxyz.com/robots.txt`，不只看仓库。如果百度同时出现 `Disallow: /` 和 `Allow: /`，应在 Cloudflare 的域名设置中停止同步冲突的 robots 规则，并检查 AI Crawl Control 是否单独拦截 Baiduspider；不需要关闭整站防护。

构建后运行 `python3 scripts/check_site_indexes.py` 可以检查 sitemap、规范地址、中英文互链、搜索索引和源站爬虫规则；GitHub Actions 发布前也会自动执行。

- `scripts/build_site.py` 读取 `data/site.json`
- 合并 `content/extra_entries.json`
- 复制 `public/` 到 `docs/`
- 生成中英文首页、文章页、页面索引、归档页、分类页、标签页、搜索索引、sitemap、robots 和 CNAME
- `scripts/generate_media_manifest.py` 从生成后的 `docs/` 扫描 Cloudflare CDN 媒体 URL 清单

`.github/workflows/static.yml` 会在每次 push 到 `master` 时执行：

```bash
python scripts/build_site.py
python scripts/generate_media_manifest.py
```

然后把生成后的 `docs/` 作为 GitHub Pages artifact 发布。也就是说，日常更新内容不再需要本地构建并提交 `docs/`；需要预览或排查问题时再本地运行构建即可。

如果 `data/media-cdn.json` 发生变化，workflow 会自动提交：

```bash
Update CDN media manifest [skip ci]
```
