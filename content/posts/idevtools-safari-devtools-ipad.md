---
title: 我给 iPad Safari 做了个 Chrome DevTools
title_en: I Built Chrome DevTools for iPad Safari
date: 2026-06-25
slug: idevtools-safari-devtools-ipad
categories: [APP开发|app|App Development, 技术域|tech|Technology]
tags: [iOS|ios|iOS, iPad|ipad|iPad, Safari|safari|Safari, DevTools|devtools|DevTools, Web开发|web|Web Development, JavaScript|javascript|JavaScript]
excerpt: iDevTools 让 Safari 也能像 Chrome 一样查看元素、监控网络请求和调试网页，把 iPad 上缺失的开发者工具补上。
excerpt_en: iDevTools brings a Chrome DevTools-like inspection workflow to Safari on iPad, making it possible to inspect elements, monitor network requests, and debug pages without leaving iPadOS.
thumbnail: https://cdn.omegaxyz.com/2026/06/idevtools-ipad-elements.webp
---

如果你是一名前端开发者，应该很熟悉这样的场景：

在电脑上打开 Chrome。

按下 F12。

然后你拥有了一切。

查看元素、修改 CSS、监控接口、调试 JavaScript、查看 Storage……Chrome DevTools 已经成为现代 Web 开发最重要的工具之一。

但有一个设备始终让我觉得很遗憾：

iPad。

![iDevTools 在 iPad Safari 中检查网页元素](https://cdn.omegaxyz.com/2026/06/idevtools-ipad-elements.webp)

*iDevTools 在 iPad Safari 中提供接近桌面 DevTools 的元素检查体验。*

## iPad 已经足够强大，但 Safari 依然缺少 DevTools

这些年，iPad 的硬件性能越来越强。

M 系列芯片、外接显示器、Stage Manager、桌面级 Safari……Apple 一直在努力让 iPad 更接近生产力设备。

但对于开发者来说，却始终缺少一个关键组件：

开发者工具。

很多时候我只是想：

- 看一下网页元素结构
- 检查一个 CSS 样式
- 看看接口返回了什么
- 调试一个简单的 JavaScript 问题
- 查看 localStorage、sessionStorage 或 Cookie

这些在 Chrome 里只需要几秒钟。

而在 iPad 上，通常意味着：

打开 Mac，连接设备，打开 Safari 远程调试，找到页面，然后才开始排查。

整个过程有时候比问题本身还复杂。

于是我开始思考：

如果把 Chrome DevTools 最常用的能力直接搬到 Safari，会怎么样？

## 于是有了 iDevTools

iDevTools 是一个专门为 Safari 设计的开发者工具扩展。

它的目标不是完全复刻 Chrome DevTools。那几乎是不可能的事情，也不一定适合移动设备。

我更想解决最常见的 80% 场景：让开发者能够直接在 iPad 上完成基础调试工作。

![iDevTools 的网络请求监控与请求详情](https://cdn.omegaxyz.com/2026/06/idevtools-ipad-network.webp)

目前 iDevTools 已经实现了这些核心能力：

### Elements

- DOM Tree 浏览
- Element Picker
- CSS 查看
- Box Model 信息
- Selector 复制

### Network

- Fetch 请求监控
- XHR 请求监控
- Request / Response 查看
- Header 分析
- Timing 信息

### Console

- Console Log
- Warning
- Error
- Runtime Exception

### Storage

- localStorage
- sessionStorage
- Cookies

### JavaScript

- 页面内执行 JavaScript
- 查看执行结果

它的界面参考了 Chrome / Safari DevTools 的常见布局，可以停靠在页面右侧或底部，也可以根据 iPad 横屏、竖屏、触控、触控板和键盘工作流调整。

## 最大的挑战不是代码，而是 Safari

一开始我以为：

Safari Extension ≈ Chrome Extension。

真正开始开发以后才发现，并不是这样。

Safari 的限制更多。很多 Chrome 中理所当然的能力，在 Safari 里都需要重新设计。

例如：

- Content Script 与页面上下文隔离
- 网络请求捕获方式不同
- Manifest 校验更严格
- Extension 生命周期不同
- App Store 审核要求更多

甚至上传 App Store 的时候，仅仅是一个 manifest 文件，就踩了不少坑。

例如：

```text
The description field must be present and 112 or fewer characters long.

The icons field is required.
```

这些问题在 Chrome Extension 世界里几乎不会遇到。

但也正因为限制多，才更需要把功能做得克制、稳定、清楚。iDevTools 并不试图把桌面浏览器开发工具的所有复杂能力塞进 iPad，而是先把最有价值的调试路径打通。

![iDevTools 在 iPhone Safari 中运行](https://cdn.omegaxyz.com/2026/06/idevtools-iphone-console.webp)

## 为什么我觉得它有意义

过去几年里，iPad 一直在向电脑靠近。

但开发工具生态始终落后一步。

对于开发者来说，生产力不只是性能，更重要的是工具。

如果一个设备无法完成调试工作，那么它始终很难成为真正的开发设备。

我不认为 iPad 会取代 Mac。但我希望，当你只是想快速检查一个网页、调试一个接口、查看一个元素的时候，不必再特地拿出电脑。

打开 Safari。

点击扩展按钮。

然后像 Chrome 一样开始调试。

这就是 iDevTools 想做的事情。

## 后续计划

目前项目仍在持续开发中。后续计划加入：

- HAR 导出
- IndexedDB 查看器
- 页面审计
- SEO 检查
- Accessibility 检查
- AI 辅助调试

如果你经常使用 iPad，并且对网页开发、调试工具或者 Safari Extension 感兴趣，欢迎交流你的想法。

## 下载

- [App Store（中国区）](https://apps.apple.com/cn/app/idevtools/id6782373788)
- [App Store（美国区 / English）](https://apps.apple.com/us/app/idevtools/id6782373788)

你也可以查看完整隐私政策：[iDevTools 隐私政策](https://omegaxyz.com/idevtools-privacy/)。
