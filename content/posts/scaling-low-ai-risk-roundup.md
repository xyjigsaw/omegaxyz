---
title: Scaling Low：六条 AI 新闻，回到证据看一眼
title_en: "Scaling Low: Six AI Stories, Back to the Evidence"
date: 2026-11-26
slug: scaling-low-ai-risk-roundup
categories: [tech, machine-learning]
tags: [ai, 事实核查|fact-checking|Fact Checking]
excerpt: 能在照片里圈出零件，和知道它离镜头多远，是两回事。走进 Scaling Low，从 11 月 19 日至 26 日的六条 AI 新闻看懂那些容易被标题省略的区别。
excerpt_en: Finding a part in a photo is not the same as knowing how far away it is. Six stories collected by Scaling Low on November 19–26 show what changes when you read past the headline.
thumbnail: https://cdn.omegaxyz.com/2026/11/scaling-low-ai-risk-roundup/home-zh.webp
---

给模型看一张工作台的照片，请它圈出你说的那个零件，再问它：「机械臂要往前伸多远？」对人来说，这是连在一起的两个动作。对今天的视觉模型来说，能答好前一问，远不意味着能答好后一问。这是我看 [Scaling Low](https://scalinglow.com/) 时最想留下的一条新闻：同一张照片，换个问法，就能看见能力的边界。

## Scaling Low 在做什么？

Scaling Low 是一个中英双语的 AI 风险观察站。[新闻流](https://scalinglow.com/#news)既收录研究进展，也核查围绕这些进展流传的说法。点开条目能找到原始材料；想按问题而不是按日期阅读，可以从[风险地图](https://scalinglow.com/#risks)进入，看看模型可靠性、滥用、治理和基础设施分别发生了什么。

![Scaling Low 中文首页，展示 AI 风险观察站的倒计时与导航](https://cdn.omegaxyz.com/2026/11/scaling-low-ai-risk-roundup/home-zh.webp)

首页最醒目的是倒计时，但它**不是在预测 AI 泡沫哪天破裂**。按站方 11 月 26 日公开的[计算方法](https://scalinglow.com/bubble.json)，一个观察时点留给 GTC 之后的推理性能、成本与供给，另一个留给季度财报里的资本开支、云业务利润和现金流。两者暂时等权。走到那一天，该做的是拿出新数据复盘，而不是宣布预测应验。

## 11 月 19 日至 26 日：六条新闻

以下按 **Scaling Low 收录日期**倒序整理，不一定是论文首发日。

### 11 月 26 日｜模型圈对了零件，却判错了距离

BOP-Refer 用一张图和一句描述考了 17 个视觉语言模型。表现最好的 Gemini 4 Carbon，二维定位的平均精度（AP）为 72.6%，三维定位却只有 12.4%，而且三维评分的重叠要求还更宽松。许多预测框在画面里对准了物体，前后距离却错得比物体本身还大。这正是为什么给机械臂挑视觉模型时，一张画着漂亮边框的演示图还不够。[BOP-Refer 论文](https://arxiv.org/abs/2611.34862)

### 11 月 25 日｜任务完成了，先前的错误还在吗？

SecondChance 从智能体真实犯错后的状态重新开始，看它接手后会不会纠错。在 AppWorld 上，研究者挑出最终成功的 84 次续跑细看，发现其中 40 次仍保留了先前的错误。这不是说 84 个任务里有 40 个失败。恰恰相反，**只看成功记录，才会漏掉这 40 次**。[SecondChance 论文](https://arxiv.org/abs/2611.31586)

### 11 月 24 日｜量子计算省了近十二倍，省的是什么？

Google DeepMind 和 Google Quantum AI 让智能体提出算法改法，再用 Lean 验证。在一条用于计算聚变相关物理量的量子线路上，新方案的估算成本降至原来的约 1/11.8。这里的成本综合了量子比特数和操作数；既不是聚变能量产出提高了 11.8 倍，也不是现有硬件已经把完整模拟跑快了 11.8 倍。[研究团队说明](https://deepmind.google/blog/finding-faster-quantum-algorithms-with-agents-and-formal-verification/)

### 11 月 24 日｜答对问题，能指出答案藏在哪里吗？

RDQA 的 1,350 道题要求系统从文档、录音或视频里找证据。换成这种判分方式，12 种通用智能体配置里最好的一种只得了 24.0%；专门为检索这些材料设计的 RDQA-Skill 则达到 41.1%。下次让研究助手总结一段访谈，可以多问一句：「录音里哪一段支持这个结论？」这与让它写一段听起来合理的总结，是两种不同的考验。[RDQA 论文](https://aclanthology.org/2026.emnlp-main.1855/)

### 11 月 20 日｜每 3.6 个月翻倍的不是工作效率

METR 合并两套评测任务后发现，模型以 50% 成功率能完成的任务，其时长大约每 3.6 个月翻一倍。这里的尺子是**人类专家完成任务需要多久**，不是模型连续运行了多久。这个结果有助于判断哪些更长的研发任务值得交给智能体试一试，但不能直接换算成一个团队的生产率。[METR 季度报告](https://metr.org/blog/2026-11-20-q4-2026-capability-update/)

### 11 月 19 日｜数据中心给电网带来的，是哪一种压力？

美国联邦能源监管委员会（FERC）的冬季报告引用北美电力可靠性委员会的预测：未来十年，北美冬季峰值用电负荷预计增加 245 吉瓦，大型新增用电项目、尤其是数据中心，是重要驱动因素。245 吉瓦说的是**高峰时刻需要多少功率**，不是全年多用了多少电，更不能全记到 AI 头上。报告同时判断，在正常天气下，受评估的美国地区今冬预计有足够资源。这两个判断并不矛盾：一个谈十年增长，一个谈眼前这个冬季。[FERC 冬季评估，见报告第 23 页](https://ferc.gov/news-events/news/2026-2027-winter-energy-market-electric-reliability-assessment)

六条里，我会把 BOP-Refer 和 SecondChance 放在一起读：前者的框画对了，后者的任务也成功了，偏偏最值得知道的信息都不在那个绿色对勾里。带着「这个结果还没检验什么」的问题去翻 [Scaling Low 的最新条目](https://scalinglow.com/#news)，比盯着倒计时更有意思。
