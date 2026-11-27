---
# 这是模板示例，构建时会被自动跳过（文件名为 example.md），也不会被归档。
# 写新文章时，复制这个文件、改个文件名（例如 my-first-post.md）放在 content/posts/ 下即可。
# This template (example.md) is always skipped by the build and never archived.
# To publish: copy this file, rename it (e.g. my-first-post.md), drop it in content/posts/.

# title 和 date 必填；其余选填。注释请单独写一行。
title: 一篇用 Markdown 写的文章
title_en: A Post Written in Markdown
date: 2026-05-30
slug: example-markdown-post
categories: [tech, machine-learning]
tags: [AI, LLM, 想法生成|idea-generation]
excerpt: 一句话摘要，会显示在列表页和分享卡片里。
excerpt_en: A one-line summary for list pages and share cards.
thumbnail: https://cdn.omegaxyz.com/2020/01/AI-GIF.gif
---

正文从这里开始，用标准 Markdown 书写即可。

## 二级标题

支持 **加粗**、*斜体*、~~删除线~~、`行内代码`，以及[站内外链接](https://omegaxyz.com)。

### 列表

- 无序列表项一
- 无序列表项二
  - 嵌套子项
- 无序列表项三

1. 有序列表项一
2. 有序列表项二

### 代码块（会用 highlight.js 高亮）

```python
def hello(name: str) -> str:
    return f"Hello, {name}!"
```

### 公式（文章页已加载 KaTeX）

行内公式 $E = mc^2$，独立公式：

$$
\int_{0}^{1} x^2 \, dx = \frac{1}{3}
$$

### 引用与表格

> 这是一段引用。

| 方法 | 准确率 | 备注 |
| --- | --- | --- |
| A | 91% | 基线 |
| B | 94% | 本文 |

### 图片

![示意图](https://cdn.omegaxyz.com/2020/01/AI-GIF.gif)

---

写双语正文（可选）：在同目录放一个同名的 `<文件名>.en.md`，里面只写英文正文（也可带 frontmatter，会忽略其元数据只取正文）。不放则中英文共用同一份正文。
