# content/posts —— 用 Markdown 发文章

把一个 `.md` 放进**这个目录**，push 到 `master`，GitHub Actions 会自动：
**构建出页面 → 部署上线 → 把这个 md 和同名 `.en.md` 移到 `archive/` 子目录**（并回提一个 `[skip ci]` 提交，不会再触发一轮构建）。

> `archive/` 里的文件仍会被每次构建读取——`docs/` 是 CI 每次重新生成的，所以归档只是“收件箱清空”，页面不会消失，URL 也不变。想下线某篇就删掉 `archive/` 里那个 md。

`example.md`（模板）和 `README.md`（本文件）、以及 `*.en.md`（英文正文伴随文件）都会被构建跳过，不会单独生成页面；同名 `.en.md` 会跟随主文章一起归档。

## 发布流程

```bash
# 1. 写好 my-post.md，放进 content/posts/
git add content/posts/my-post.md
git commit -m "post: my-post"
git push origin master
# 2. 稍等片刻 Actions 跑完，再 git pull —— 本地的 md 也会同步成“已归档”状态
git pull
```

不 pull 也能发布，但本地会留着原文件，下次 push 容易和 `archive/` 里那份重复，建议每次发完 `git pull` 一下。

## frontmatter 字段

```markdown
---
title: 中文标题            # 必填
title_en: English Title    # 选填（缺省 = title）
date: 2026-05-30           # 必填，决定 URL 与排序（URL = /年/月/日/slug/）
slug: my-post              # 选填，缺省用文件名；建议只用小写英文、数字、连字符
categories: [tech, machine-learning]
tags: [ai, llm]
excerpt: 一句话摘要         # 选填，缺省自动从正文截取
excerpt_en: One-line summary.
thumbnail: https://cdn.omegaxyz.com/2026/05/demo.png   # 选填，列表缩略图 / og:image
---
正文……
```

缺 `title` 或 `date` 的文件会被静默跳过（不报错、也不生成页面）。

## 分类 / 标签的写法（和根目录 README 的逻辑一致，没有改）

每个分类/标签项有三种写法：

| 写法 | 例子 | 说明 |
| --- | --- | --- |
| 纯 slug | `tech` | 复用旧站同 slug 的中文名；没有就用 slug 当名字 |
| 中文名｜slug | `自然语言处理\|nlp` | 显式给中文名 |
| 中文名｜slug｜英文名 | `全新主题\|brand-new-topic\|Brand New Topic` | 再显式给英文名 |

**英文名 `name_en` 的决定顺序与全站一致**（见根目录 `README.md` “分类和标签怎么注册”一节）：

1. 这里显式写的英文名（第三段）
2. 脚本内置映射 `TERM_EN`
3. 按 slug 自动生成（如 `large-language-model` → `Large Language Model`）

所以：复用已有分类/标签时，写个 slug 就够；新建分类/标签且想要好看的英文名时，用三段式 `中文名|slug|English` 一次写全。`slug` 决定分类页/标签页 URL 和前端筛选，务必稳定。

## 正文支持的 Markdown

标题、**粗体**/*斜体*/~~删除线~~/`行内代码`、有序无序及嵌套列表、围栏代码块（` ``` ` 自动 highlight.js 高亮）、`$..$` 行内与 `$$..$$` 块级公式（文章页已加载 KaTeX）、引用、表格、图片、链接。图片建议用完整的 `https://cdn.omegaxyz.com/...` 地址。

**双语正文**：同目录放一个同名 `my-post.en.md`，只写英文正文（带不带 frontmatter 都行，只取正文）；不放则中英文共用同一份正文。

完整示例见同目录的 `example.md`。
