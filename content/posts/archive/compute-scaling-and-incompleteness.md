---
title: 从黎曼猜想到矩阵乘法下界：AI 正在改变科研的哪笔成本？
title_en: "From Riemann to Matrix Multiplication: Which Cost of Research Is AI Changing?"
date: 2026-11-27
slug: compute-scaling-and-incompleteness
categories: [machine-learning, jotting]
tags: [llm, 可计算性|computability|Computability, 模型扩展|model-scaling|Model Scaling]
excerpt: 五天内，研究者相继公开了黎曼猜想、VP 与 VNP 分离和矩阵乘法下界的证明材料。结合此前的流体方程研究，最值得追踪的不只是模型解出了什么，还有寻找、核验和理解一项发现，各要付出多少代价。
excerpt_en: Five days brought proof releases on the Riemann hypothesis, VP versus VNP and the matrix multiplication exponent. Alongside work on fluid equations, they offer a way to distinguish the cost of finding a result from the cost of checking and understanding it.
thumbnail: https://cdn.omegaxyz.com/2026/11/compute-scaling-and-incompleteness/search-boundary.webp
---

11 月 20 日，数学家 Levent Alpöge 用四页纸宣布，他与 Claude 找到了黎曼猜想的证明。供同行检查的论证不在这四页纸里，而在随文发布的约 1700 万行 Lean 代码里。次日，Lean 与 Mathlib 团队给出了一份颇不寻常的核验意见：他们确认，机器检查通过的确实是数学家所说的那个黎曼猜想。至于怎样把这条证明路线讲清楚，Alpöge 在[发布说明](https://alpo.ge/remark.pdf)中说，这仍是他接下来的工作。

随后三天，Anthropic 和 OpenAI 又先后发布了关于代数复杂性和矩阵乘法的证明材料。算力投入究竟换来了什么？截至 2026 年 11 月 27 日，这批材料给出的答案比“AI 又解了几道题”更具体：寻找证明、核对证明、理解证明，已不必由同一批人以相同的速度完成。这三件事的成本也不能再用一个跑分衡量。

## 黎曼猜想：一天核验，不等于一天读懂

黎曼猜想要求黎曼 ζ 函数的每一个非平凡零点都落在实部等于二分之一的直线上。把前面再多的零点核对一遍，也无法排除后面还有一个例外。Alpöge 与 Claude 交付的不是一份更长的零点清单，而是一段声称对所有这些零点都成立的推导。

[Lean 与 Mathlib 的联合声明](https://leanprover-community.github.io/blog/posts/riemann-hypothesis/)解释了核验为何有分量。检查者先从已有数学库中单独取出经过专家审定的黎曼猜想表述，再用两套工具确认它与提交代码最终证明的命题一致；导出的证明随后通过了多个检查器。这里既查了“推得对不对”，也查了“推的是不是原题”。后一项尤其重要：若把待证命题写弱了，代码通过检查也说明不了原题。

从发现的角度看，更值得留意的是作者叙述的分工：Alpöge 从一个较简单的情形出发，把问题引到适合推广的位置，Claude 则提出如何把若干已有的数学构造接起来。这不是让模型对同一个结论多投几票，而是让它尝试一条此前没有走通的证明路线。形式核验使别人无须先复述全部思路，就能检查终点。

## 流体方程：88 小时买到了什么

在四个方向中，Navier–Stokes（NS）方程留下了一份少见的投入记录。按 [OpenAI 9 月 8 日披露的数据](https://openai.com/index/navier-stokes-solution/)，找到论证的那一组有约一万个智能体并行工作。从首批智能体启动到给出结果历时约 88 小时，形式化与核验另用了 17 小时；仅 NS 问题就消耗了约 1300 亿个输出 token。这是并行任务的经过时间和输出量，不是一台机器的工时，更不是可以据以结算的电费。

团队报告的结果有明确条件：三维不可压缩流体从静止出发，受到光滑外力作用，解可以在有限时间内出现奇性。它不是说所有流动都会失稳，也不是说已证明无外力情形下会出现同样结果。研究组把不同版本的问题分给不同小组，在看到一条有希望的路线后，才将其他组的资源调过来。新增算力的用途不只是同时多试几次，还有在中途发现线索后及时改投方向。

复核另有成本。10 月，Alexander Bastounis 等人在[一篇核查论文](https://arxiv.org/abs/2610.08144)中指出，OpenAI 发布的 Lean 推导与自然语言手稿中的爆破解法并不对应。这是对两份材料能否互相作证的质疑，不等于已构造出反例。11 月 20 日，Alpöge 与 Tristan Buckmaster 又公布了[另一份 NS 论文及代码](https://github.com/tristanbuckmaster/navier-stokes)：按作者自己的说明，该版本没有附上论证所用的数值证书，检查证书的区间运算也不在形式证明内。同样叫“公开了 Lean 代码”，复核者实际拿到的东西并不相同。

## 两个下界：没找到捷径，还是根本没有捷径

11 月 23 日，[Anthropic](https://github.com/anthropics/formal-math/tree/main/vp-vnp) 和 [OpenAI](https://github.com/openai/math/tree/main/preprints/VP-and-VNP-are-different-November-23-2026) 分别发布预印本，主张在每个域上都有 **VP ≠ VNP**。这里研究的是用加法和乘法等算术运算计算多项式，要用多大的电路。两篇工作的方向都是“分离”：VNP 中存在一些多项式族，不能由规模随输入仅按多项式增长的算术电路计算。它不是布尔计算中的 P 与 NP 问题。Anthropic 在发布时说明，论文和 Lean 形式化均由模型撰写，当时尚无数学家核查整份证明。

次日，OpenAI 发布的[矩阵乘法预印本](https://github.com/openai/math/tree/main/preprints/The-matrix-multiplication-exponent-is-nine-fourths-November-24-2026)主张，任意域上方阵乘法的算术复杂度指数恰为 $9/4$。新闻点在**下界**。找出一种更省运算的算法，可以把已知上界往下推；现在作者要证明的是，无论怎样重排运算，在所讨论的模型里，指数都不可能再小。配套 Lean 结果明确覆盖不含除法、按形式多项式恒等式计算的电路情形。这个指数描述矩阵不断变大时运算量的增长，不是对今天一块 GPU 运行时间的预测。

这两项工作所需的证据，恰与反复试错的直觉相反。找到一条捷径，展示它就够了；断言没有捷径，试过一万亿条都不够，必须给出能排除整类路线的理由。算力在后一个任务上仍然有用，只不过搜索目标从“更快的算法”换成了“为什么不可能更快的证明”。

## 发现的成本

我的判断是，今天许多基础科学问题的瓶颈，仍是一次有效试错太贵，而不是已经碰到了[哥德尔不完备定理](https://doi.org/10.2307/2269028)的边界。后者说的是：在一致、可有效公理化且足以表达基本算术的理论中，总有命题及其否定都不能在该理论内得到证明。它不告诉我们眼前这个问题属于哪一类。反过来，只要一份有限证明确实存在、候选可以逐一枚举和核验，原则上搜索就能找到它。scaling 有实际意义的地方，是让一次原本赶不上研究者职业生涯的搜索有机会提前结束。

就规律本身而言，我相信只有发现，没有发明。人可以发明证明语言和测量仪器，但不能决定一个零点落在哪里，也不能替流体选择怎样运动。判断下一笔科研算力值不值得投，我更想看到一项对照：给两组人同样多的实验机会，只给其中一组更多推理算力，看谁能先提出、并经独立检验确认一个原先不知道的关系。比起又生成了多少页论文，这个时间差更接近发现的价值。
