---
title: Scaling Low：一家给 AI 泡沫查账的编辑部
title_en: "Scaling Low: The AI Boom’s Uninvited Auditor"
date: 2026-11-26
slug: scaling-low-ai-risk-roundup
categories: [tech, machine-learning]
tags: [ai, 事实核查|fact-checking|Fact Checking]
excerpt: Scaling Low 在首页挂了一只倒计时，等的是下一轮财报。这周它翻开的六份材料里，有会认零件却摸不着零件的模型，也有全篇最守时的一位：电表。
excerpt_en: Scaling Low put a countdown on its homepage and set it to earnings season. This week’s reading runs from a robot arm that might grasp thin air to the one part of the AI business already billing by the hour.
thumbnail: https://cdn.omegaxyz.com/2026/11/scaling-low-ai-risk-roundup/home-zh.webp
---

[Scaling Low](https://scalinglow.com/) 在首页挂了一只倒计时。头一回点进去，我以为终于有人敢给 AI 泡沫挑个破裂的黄道吉日。点开[算法](https://scalinglow.com/bubble.json)一看，编辑部等的是两件扫兴的小事：英伟达 GTC 开完，看看推理成本和算力供应；云厂商交完季度财报，再看看资本开支、利润和现金流。两个日期，各占一半。别人倒数，是等新品发布；这家倒数，是等发票到齐。

这大致就是 Scaling Low 的脾气。它是一家中英双语的 AI 风险观察站：[新闻栏](https://scalinglow.com/#news)把流行说法和原始材料摆在一起，[风险地图](https://scalinglow.com/#risks)按可靠性、滥用、治理、基础设施等问题给条目分类。用空头的眼光逛这里，有个好处：**不必赌模型会变笨，只要问一问，模型变聪明省下的那笔钱，究竟落在谁的账上。**

![Scaling Low 中文首页：刊名旁的倒计时，等的是技术和财务数据的下一次复盘](https://cdn.omegaxyz.com/2026/11/scaling-low-ai-risk-roundup/home-zh.webp)

## 这周，Scaling Low 翻了哪些账？

下面六则按网站收录日期排列，取自 2026 年 11 月 19 日至 26 日的新闻栏。

### 11 月 26 日｜演示只需画个框，交货得把零件拿起来

[BOP-Refer](https://arxiv.org/abs/2611.34862) 让 17 个视觉语言模型凭一张照片找指定物体。成绩最好的 Gemini 4 Carbon，二维定位平均精度为 72.6%，到了三维只剩 12.4%。不少框从正面看严丝合缝，深度却估错了一个物体身位还多。做演示，我会把画面停在框亮起来的那一帧。做采购，我想坐到机械臂旁边，看它抓的是零件还是空气。

### 11 月 25 日｜任务成功了，谁留下来善后？

[SecondChance](https://arxiv.org/abs/2611.31586) 把智能体放回先前犯错的现场，让它接着干。研究者在 AppWorld 里翻出 84 次最终判定成功的续跑，其中 40 次把旧错误原样留了下来。要是我负责卖这套软件，84 次都是成功案例。要是我负责下周一接班，能不能先把那 40 张工单发过来？

### 11 月 24 日｜11.8 倍，值得把单位一起印出来

Google DeepMind 和 Google Quantum AI 让智能体修改量子算法，再用 Lean 验证。用于计算一项聚变相关物理量的量子线路，按量子比特数和操作数估算，成本降到了原来的 **1/11.8**。这是本周我最喜欢的多头证据：真省了，省在哪儿也说得清。只是从一条更便宜的量子线路走到一座卖电的电站，中间还有些工程要做。好在删掉标题里的「线路」两个字，只需一秒。[研究团队原文](https://deepmind.google/blog/finding-faster-quantum-algorithms-with-agents-and-formal-verification/)

### 11 月 24 日｜研究助理交了报告，请它标一下页码

[RDQA](https://aclanthology.org/2026.emnlp-main.1855/) 出了 1,350 道题，材料是文档、录音和视频。除了给答案，还得找出支持答案的证据。12 种通用智能体配置里，最好的得分是 24.0%；专门为这类检索设计的 RDQA-Skill 得了 41.1%。下次采购「自动研究员」，我会把试用安排在同一次会议里：前半场让它写一页摘要，后半场请它在录音里找到那句话。省掉的是谁的工时，散会时就有数了。

### 11 月 20 日｜翻倍曲线到了财务部

[METR 的季度评测](https://metr.org/blog/2026-11-20-q4-2026-capability-update/)有一条漂亮的曲线：合并两套测试后，智能体在 50% 成功率下能承担的任务长度，约每 3.6 个月翻一倍。「长度」按人类专家做这道题要花多久来量。研发主管看完，可以挑些更长的活让模型试。财务主管要填的那格麻烦一点：失败那一半，谁来发现，谁来重做，一共花了几个钟头？

### 11 月 19 日｜终于，电表出场了

美国联邦能源监管委员会的[冬季评估](https://ferc.gov/news-events/news/2026-2027-winter-energy-market-electric-reliability-assessment)（报告第 23 页）引用预测：未来十年，北美冬季峰值用电负荷将增加约 245 吉瓦；数据中心是大型新增负荷里的重要一项。电网要为高峰时刻备足容量，机房要按合同付钱。至于机房那头的客户会不会续订，是另一份合同上的事。AI 生意里，最让我放心的收费模式属于电力公司。

## 空头的下次约会

六条看完，我最想并排打开的是 METR 的曲线和云厂商的现金流量表。一张告诉我模型终于能做多长的活；另一张有机会告诉我，为了接这些活先垫了多少钱。等到客户愿意续费、返工少了、每单挣下的钱足以养机房，这笔空头账自然得改。那才是 [Scaling Low 首页](https://scalinglow.com/)那只钟值得再看一眼的时候。
