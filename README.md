# OmegaXYZ 静态站点维护手册

这个仓库是 OmegaXYZ 从 WordPress 迁移后的静态站点。GitHub Pages 直接发布 `docs/` 目录，图片等大文件优先放到 Cloudflare R2/CDN。

## 换机器后怎么开始

1. 准备一台有 `git` 和 `python3` 的机器。
2. 克隆仓库：

```bash
git clone git@github.com:xyjigsaw/omegaxyz.git
cd omegaxyz
```

如果当前机器没有 GitHub SSH key，可以先在 GitHub 加新的 deploy key，或临时使用 HTTPS clone。

3. 修改内容后重建静态站：

```bash
python3 scripts/build_site.py
```

4. 本地预览：

```bash
python3 -m http.server 4173 --directory docs
```

打开 `http://127.0.0.1:4173/zh/`。

5. 提交并推送：

```bash
git status
git add content public docs scripts README.md
git commit -m "Add new post"
git push origin master
```

GitHub Actions 会把 `docs/` 部署到 GitHub Pages。

## 内容从哪里来

迁移后的 WordPress 数据保存在 `data/site.json`。这个文件已经提交到仓库，是换机器后完整重建旧文章、页面、评论、分类和标签的基础数据。日常新增文章放在 `content/`，例如：

- `content/extra_entries.json`：文章元数据
- `content/example.zh.html`：中文正文
- `content/example.en.html`：英文正文

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
- `slug`、分类 slug、标签 slug 建议只用小写英文、数字和连字符。

## 上传图片

小型站内图可以放到 `public/assets/`，例如：

```text
public/assets/my-diagram.svg
```

正文里引用：

```html
<img src="../../../../../assets/my-diagram.svg" alt="My diagram">
```

首页缩略图也可以写：

```json
"thumbnail": "/assets/my-diagram.svg"
```

大图片、截图、历史媒体建议上传到 Cloudflare R2，并通过 CDN 使用：

```text
https://cdn.omegaxyz.com/2026/05/image.png
```

批量上传脚本：

```bash
export CF_API_TOKEN="不要写进仓库"
export CF_ACCOUNT_ID="不要写进仓库"

python3 scripts/upload_r2.py \
  --root .media/uploads/uploads \
  --account-id "$CF_ACCOUNT_ID" \
  --bucket omegaxyz-image
```

不要把 Cloudflare token、S3 key、`.cache/`、`.media/`、原始备份包、翻译缓存或上传缓存提交到 GitHub。`data/` 目录里只提交 `data/site.json`。

## 分类和标签怎么注册

不需要手动注册页面。只要文章元数据里写了：

```json
"categories": [{"name": "自然语言处理", "slug": "nlp"}],
"tags": [{"name": "LLM", "slug": "llm"}]
```

构建时会自动生成：

- 分类索引：`/zh/categories/`、`/en/categories/`
- 标签索引：`/zh/tags/`、`/en/tags/`
- 分类专页：`/zh/category/nlp/`、`/en/category/nlp/`
- 标签专页：`/zh/tag/llm/`、`/en/tag/llm/`
- 文章归档页筛选按钮
- 分类页下方的标签筛选按钮

当前逻辑：归档页会展示全部分类和全部标签；分类页会展示该分类下出现过的全部标签。首页的“知识结构”只展示文章数最多的前 8 个分类，这是首页布局选择，不影响专页和筛选。

英文分类/标签名来自 `scripts/build_site.py` 里的 `TERM_EN`。如果新增 slug 没写英文映射，英文页面会暂时显示中文名。要补英文名，在 `TERM_EN` 加一行：

```python
"my-tag": "My Tag",
```

## 构建逻辑摘要

- `scripts/build_site.py` 读取 `data/site.json`
- 合并 `content/extra_entries.json`
- 复制 `public/` 到 `docs/`
- 生成中英文首页、文章页、页面索引、归档页、分类页、标签页、搜索索引、sitemap、robots 和 CNAME

GitHub Pages workflow 不会重新生成站点，它只发布仓库里的 `docs/`。所以每次改内容后都要本地运行：

```bash
python3 scripts/build_site.py
```

然后把 `content/`、`public/`、`scripts/` 和 `docs/` 的相关变化一起提交。
