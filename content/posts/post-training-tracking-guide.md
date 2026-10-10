---
title: 后训练 Tracking 怎么看：从 PPO、GRPO 到 OPD 的指标与组合诊断
title_en: Reading Post-Training Tracking: Metrics and Joint Diagnostics for PPO, GRPO and OPD
date: 2026-10-10
slug: post-training-tracking-guide
categories: [技术域|tech|Technology, 机器学习|machine-learning|Machine Learning, 自然语言处理|nlp|Natural Language Processing]
tags: [人工智能|ai|Artificial Intelligence, 大语言模型|llm|Large Language Models, 强化学习|reinforcement-learning|Reinforcement Learning, 后训练|post-training|Post-Training]
excerpt: Reward 上涨不等于能力提升。按算法、统计口径和联合证据解读 reward、advantage、KL、entropy、clip 与评估，用 14 组诊断组合定位 PPO、GRPO 和 OPD 的问题。
excerpt_en: Reward growth is not proof of capability. Interpret reward, advantage, KL, entropy, clipping and evaluation through algorithm definitions and 14 evidence-based diagnostic combinations.
thumbnail: /assets/post-training-tracking.svg
---

打开一次大语言模型后训练的 dashboard，几十条曲线很容易让人产生错觉：reward 涨了就是训练成功，entropy 低了就是坍缩，KL 降了就是蒸馏有效。

这些判断都跳过了最关键的一步：**指标到底统计了什么，变化是否转化成了独立评估中的收益？**

本文讨论 PPO、GRPO 与 on-policy distillation（OPD），给出可以直接用于 W&B、TensorBoard 或其他 tracking 系统的阅读顺序、指标清单和组合诊断表。没有通用的“健康数值”，也没有所有训练都必须遵循的健康曲线。下文中的例子均为教学示例，不是实测结果。

![后训练指标阅读流程：先确认定义，再同时检查效果、信号、更新和行为](../../../../../assets/post-training-tracking.svg)

*原创阅读流程示意，不代表实测曲线或因果关系。各组证据需要互相核对。*

## 1. 看曲线前，先写清这张指标卡

同一个 `kl`、`reward` 或 `clipfrac` 名字，在不同实现里可能是不同东西。至少记录：

1. **算法和目标**：PPO、GRPO 还是直接最小化蒸馏 loss？OPD 是数据生成方式，不自动意味着有 PPO、critic 或 advantage。
2. **数据和版本**：训练/验证集、prompt 模板、reward/verifier、teacher、reference、tokenizer、代码 commit 和配置。
3. **采样设置**：temperature、top-p/top-k、每题样本数、最大长度、EOS/stop 规则；评估设置要单独记录。
4. **统计单位**：token、response、prompt group 还是 minibatch？是否只算 response mask？是每条先平均再跨样本平均，还是所有 token 一起平均？
5. **变换与系数**：reward 是否加 KL 惩罚，advantage 是否 whitening，KL 方向与 estimator，loss reduction，以及各项权重。
6. **横轴与时序**：global step 对应 rollout 还是 optimizer step？评估来自哪个 checkpoint？多次更新是否复用旧 rollout？

长回答会在 token 平均中占更多权重；不同长度的 run 即使 loss 名称相同，也不一定可比。平滑曲线方便看趋势，但尖峰、尾部分位数和有效样本数应保留。跨 run 比较时同时看已处理 token、GPU 时间或成本，不能只比较 step。

## 2. PPO、GRPO、OPD：先确定哪些指标应该出现

| 路线 | 学习信号与更新 | 优先看的专属指标 | 不应默认存在 |
| --- | --- | --- | --- |
| PPO | reward/return、value baseline 与常见 GAE；用 old/new ratio 的 clipped surrogate 更新 actor | value loss、explained variance、ratio、approx KL、clip 指标 | teacher KL |
| GRPO 及其变体 | 同 prompt 多个回答构成组，利用相对 reward；常配合 PPO 风格更新 | 组内 reward std、全对/全错组占比、有效组比例、ratio/clip | 独立 critic；所有变体都除以组内 std |
| OPD / GKD | 在 student 生成的前缀上得到 teacher 反馈；可直接优化分布距离，也可结合 RL | 明确方向的 teacher KL/KD loss、gap 分布、teacher 覆盖与成本 | critic、advantage、PPO ratio 和 clip |

[PPO 原论文](https://arxiv.org/abs/1707.06347)定义了 clipped surrogate；[DeepSeekMath](https://arxiv.org/abs/2402.03300)介绍 GRPO；[GKD](https://arxiv.org/abs/2306.13649)说明自生成轨迹上的蒸馏可以采用不同分布目标并与 RL 结合。算法名只能帮助定位，最终仍应检查当前实现。

### Reward、return、advantage 和 critic 的关系

Reward 是评分器提供的反馈；return 是按算法汇总的未来奖励；advantage 衡量某个动作相对于 baseline 的优势。PPO 常用：

$$
\delta_t=r_t+\gamma V(s_{t+1})-V(s_t),\qquad \hat A_t=\sum_{l\ge0}(\gamma\lambda)^l\delta_{t+l}.
$$

求和在轨迹末端结束，terminal、截断与 bootstrap 处理要按实现核对。简单的 $A=R-V$ 适合直观解释，不能替代所有 token-level GAE。Critic 预测的是状态之后的 return，不是独立的“答案对错裁判”。

对 outcome-reward GRPO，一个常见定义是：

$$
\hat A_i=\frac{R_i-\bar R_g}{\sigma_g+\epsilon}.
$$

这里 $g$ 是**同一个 prompt 的采样组**。有的变体不除以标准差；[VERL GRPO 配置](https://verl.readthedocs.io/en/latest/algo/grpo.html)和[advantage 源码](https://github.com/verl-project/verl/blob/1876b06d0a3e4e71e06230be10af14492ca8a75b/verl/trainer/ppo/core_algos.py)可用于核对。

一个教学例子：两道题的组分别为 `[1,1,1,1]` 和 `[0,0,0,0]`。整个 batch 的 reward std 不为零，但每组的 std 都为零；在上述组内相对目标下，两组都没有 reward 区分信号。反过来，`[1,0,1,0]` 有明确组内差异。

归一化后的 advantage std 接近固定尺度可能只是定义使然。它不直接测量学习强度：还要看未归一化信号、非零 advantage 的有效比例、采样质量、mask 和实际梯度。全对与全错都可能形成零方差组，处置却不同。零方差只消除该组居中的 outcome-PG 信号，不代表 KL 等其他项没有梯度。序列 advantage 居中后，广播到不同长度的 token 再加权平均，日志均值也未必为零；均值或 scalar loss 为零，仍可能有非零梯度。

## 3. 把指标分成六组，避免只盯 loss

表中名称是概念名或常见日志名，不保证与你的 trainer 一一对应。尤其 `critic/…` 前缀不保证指标一定来自一个 critic；请沿日志写入点回查。

### A. 效果：训练是否值得继续

| 指标 | 用途 / 适用范围 | 需要避免的误读 |
| --- | --- | --- |
| Raw reward mean、分位数、reward 分项 | 有 reward 的训练；观察评分及长尾 | reward model/verifier 是代理目标，上涨不证明泛化 |
| Penalized reward / return | 使用 KL 或其他 shaping 的 RL；解释实际优化信号 | 必须与 raw score 分开；惩罚变了也会导致均值变动 |
| Held-out accuracy、pass@1、pass@k | 所有路线；固定预算下检验任务收益 | k、温度、长度或判分器不同不能直接横比；pass@k 不是单次成功率 |
| 分任务/难度/长度评估、通用能力回归 | 所有路线；查平均值掩盖的退化 | 评估样本量太小或数据泄漏可造成虚假提升 |

对同一组题目比较 checkpoint，报告样本数和不确定性；可按 prompt 做配对分析或 bootstrap，避免把同题多条回答当独立题目。若评估协议变化，先重跑基线。

### B. 信号：数据是否告诉模型该怎么学

| 指标 | 用途 / 适用范围 | 需要避免的误读 |
| --- | --- | --- |
| Batch reward std 与同 prompt 组内 std | 有 reward 的训练；GRPO 尤其需要后者 | batch 差异可能只是题目难度不同 |
| 全对组、全错组、非零方差组比例 | GRPO；区分任务饱和与探索失败 | std 小不能直接判断训练已收敛 |
| Advantage mean/std、P(A>0)、零值比例 | 使用 advantage 的 RL；核对 baseline、mask、归一化 | mean≈0 常是中心化结果；正比例无需接近 50%；归一化 std 非学习强度 |
| 有效 prompt/response/token 数、过滤比例 | 所有路线；检验实际训练覆盖 | 名义 batch 很大，过滤后的有效 batch 可能很小 |
| Value loss、explained variance | 有 critic 的 PPO 等；评估 return 预测 | loss 依赖尺度；EV 高不保证 actor 有收益 |

Explained variance 常写为 $1-\mathrm{Var}(G-V)/\mathrm{Var}(G)$。return 方差接近零时它不稳定或无定义；EV≤0 是预测需要检查的线索，不是一个跨任务的万能判决。value clipping、return normalization 与计算 mask 都会影响解释。

### C. 更新：信号是否以合适的幅度进入参数

| 指标 | 用途 / 适用范围 | 需要避免的误读 |
| --- | --- | --- |
| Policy loss / KD loss 及各分项 | 对应优化路线；检查符号、reduction 和目标权重 | 不同 batch 的 loss 大小不等于能力大小 |
| Old/new ratio 的分位数 | ratio-based RL；识别尾部更新与旧数据复用 | 均值正常可能掩盖很大的尾部 |
| Approx KL / PPO KL | 对应 old/new policy 的局部变化诊断 | 必须注明方向与估计器，不能当成 teacher 或 reference KL |
| Clip fraction、上下界分项 | clipped surrogate；看目标的裁剪情况 | 不是“这么多参数/梯度被完全截掉” |
| Reference KL 与 KL coefficient | 使用 reference 正则的路线；同时看偏离和约束强度 | reference 不一定是最初 base model；KL 增长未必坏，低也未必好 |
| Grad norm、clipping norm、LR、NaN/Inf、skipped steps | 所有路线；查数值与优化异常 | norm 是否在裁剪前记录、分布式如何汇总会改变数值 |

PPO 的核心目标为：

$$
L^{\mathrm{clip}}=\mathbb E[\min(r_t\hat A_t,\operatorname{clip}(r_t,1-\epsilon,1+\epsilon)\hat A_t)],\quad r_t=\frac{\pi_\theta(a_t\mid s_t)}{\pi_{\rm old}(a_t\mid s_t)}.
$$

实现通常最小化其负值。只有结合 advantage 符号，才知道哪一侧的裁剪分支生效；有些日志统计 ratio 越界，有些统计裁剪分支被选中。裁剪可能让该项的局部梯度平坦，但其他 token、KL 或 entropy 项仍可贡献梯度。`clipfrac=0.6` 不能翻译成“60% 的学习完全没了”。

若 `approx_kl` 是样本上的 log-ratio 平均，它有限样本下可能出现负值；非负近似估计器又有不同口径。不能把日志标签当数学定义。[VERL PPO 文档](https://verl.readthedocs.io/en/latest/algo/ppo.html)还区分 KL reward penalty 和 actor KL loss，解读总 loss 时应确认是否重复或遗漏计入。

### D. 行为：模型具体变成了什么样

| 指标 | 用途 / 适用范围 | 需要避免的误读 |
| --- | --- | --- |
| Token entropy、分位置/任务 entropy | 所有生成训练；观察条件分布的确定性 | 低 entropy 可是正确答案更确定，不能单独判 collapse |
| Length P50/P95、正确/错误答案长度 | 所有路线；识别预算变化与冗长 | 平均长度稳定不代表没有尾部撞限 |
| EOS/stop rate、truncation rate | 所有路线；定位停止与截断 | 正常 stop string 可不生成 EOS，应分开记录停止原因 |
| 重复率、distinct outputs、格式/拒答率 | 所有路线；核对行为与任务要求 | 不同 tokenizer/温度不可横比；文本多样性不等于 token entropy |

$H(p)=-\sum_a p(a)\log p(a)$ 是给定前缀上的分布熵。如果记录的是采样 token 的 `−log p(a)`，它只有在采样分布匹配时才可作为熵的蒙特卡洛估计；temperature/top-p 后采样与原始模型分布可能不同。观察 entropy 与正确率、重复率、覆盖率及多样本评估，才有理由讨论探索不足或行为收缩。

### E. 蒸馏：student 到底学到了 teacher 的什么

| 指标 | 用途 / 适用范围 | 需要避免的误读 |
| --- | --- | --- |
| Forward KL：D(T ∥ S) | 采用该方向的 KD；强调 teacher 支持的模式 | 不要与 reverse KL 或有符号 sampled gap 混画 |
| Reverse KL：D(S ∥ T) | 采用该方向的 OPD；检查 student 分布与 teacher 一致性 | student 避开难前缀后，当前轨迹 KL 也可能下降 |
| Sampled logprob gap 的均值/分位数/正比例 | sampled teacher 反馈；看尾部、尺度与符号 | 单 token gap 不是真值标签，也不是全词表 KL |
| 固定前缀集上的 KL、held-out task score | 蒸馏；区分测量分布移动和能力迁移 | 训练轨迹 KL 下降不证明任务效果提高 |
| Teacher 请求成功率、覆盖率、延迟和成本 | 需要在线 teacher 的 OPD | teacher 失败或 top-k 截断可改变监督，而不只是减慢速度 |

在固定前缀 $s$，令 $p_S$、$p_T$ 是同一词表上的归一化条件分布：

$$
D_{\mathrm{KL}}(p_T\Vert p_S)=\sum_a p_T(a\mid s)\log\frac{p_T(a\mid s)}{p_S(a\mid s)},\quad
D_{\mathrm{KL}}(p_S\Vert p_T)=\sum_a p_S(a\mid s)\log\frac{p_S(a\mid s)}{p_T(a\mid s)}.
$$

对 sampled token 定义 $\Delta(a)=\log p_T(a\mid s)-\log p_S(a\mid s)$。则：

$$
\mathbb E_{a\sim p_S}[\Delta(a)]=-D_{\mathrm{KL}}(p_S\Vert p_T),\qquad
\mathbb E_{a\sim p_T}[\Delta(a)]=D_{\mathrm{KL}}(p_T\Vert p_S).
$$

所以 student 采样下 gap 的均值常为负，与“KL 应该非负”没有冲突。有限样本均值可能偏离期望；若真实采样是 temperature/top-p 改变后的 $q$，均值是 $\mathbb E_q[\Delta]$，不能自动等同上述 KL。前缀分布、teacher/student 温度、词表支持、top-k 尾部是否保留，也必须标注。

正 gap 只表示 teacher 相对 student 给这个 token 更高概率。它是否被当作 reward、如何 stop-gradient、是否经过 baseline，以及最终梯度的符号，需要读具体目标；不能直接说“teacher 认为 token 正确，因此一定提高它”。[MiniLLM](https://arxiv.org/abs/2306.08543)是 reverse-KL 蒸馏的一种具体方法，不是所有 OPD 的统一定义。

对使用工具的 agent，还应区分模型生成 token 与工具观察，分别记录解析、执行、结果有效和端到端成功率，以及 turn 数、超时和单位成功成本。HTTP 成功不等于任务完成。Teacher top-k mass、student mass 与 overlap 也是可新增的覆盖诊断，不是所有 trainer 默认字段。

### F. 系统：是不是训练根本没有有效运行

| 指标 | 用途 / 适用范围 | 需要避免的误读 |
| --- | --- | --- |
| Rollout / update / reward / teacher 各阶段时间 | 所有路线；确定瓶颈 | step 时间变长可能源于回答变长，不能直接归因于 GPU |
| 有效 tokens/s、GPU memory、OOM、重试率 | 所有路线；检查效率与丢样 | 高吞吐不证明优化有效 |
| Policy version lag、rollout/train logprob 差异、IS 权重尾部 | 异步或不同推理引擎训练；检验数据陈旧与分布失配 | logprob 差异也可能来自精度、模板、mask 或 tokenizer |

[VERL rollout correction](https://verl.readthedocs.io/en/latest/algo/rollout_corr.html)讨论训练与 rollout 分布的校正。遇到巨大 ratio/grad spike 时，应先确认权重同步与 logprob 一致性，再考虑调学习率。

## 4. 14 组联合诊断：现象 → 假设 → 验证 → 处置

下表是排查起点，不是自动报警规则。箭头表示**同口径下相对基线的变化**，没有固定阈值。每次尽量只改一个因素，保留对照 checkpoint 与评估预算。

| 指标组合 | 候选解释 | 下一步验证 | 验证后可采取的动作 |
| --- | --- | --- | --- |
| 1. Raw reward↑，held-out score↑ | 有效学习，也可能评估协议漂移 | 固定解码预算重评；检查分任务收益和置信区间 | 保留 checkpoint，继续监控回归与成本 |
| 2. Reward↑，held-out score→/↓ | 代理目标失配、过拟合或评分器漏洞 | 审计高分错答，独立 verifier/人工抽样，检查数据重叠 | 修评分与数据；优先选择 held-out 更好的 checkpoint |
| 3. Reward↑，length P95↑，truncation↑ | 有用推理变长或长度投机 | 按长度比较正确率；固定 token budget 重评 | 修停止规则或预算；仅在证实投机后调整长度奖励 |
| 4. Reward↑，entropy↓，pass@1↑ | 正确输出变得确定 | 查重复率、难题覆盖、pass@k 与通用回归 | 若无退化不必强行提高 entropy |
| 5. Entropy骤降，重复率↑，pass@k↓ | 行为收缩、探索不足或解码设置变化 | 核对采样配置，检查同题输出及更新前后 checkpoint | 恢复解码一致性；证实更新诱发后降低更新强度或调整探索 |
| 6. Batch reward std>0，组内 std≈0 | GRPO 同组无区分；题目全对或全错 | 分开统计全对/全错组，检查 reward 与采样是否失效 | 全对可增加难题；全错先查 verifier、难度和探索 |
| 7. Normalized adv std稳定，reward停滞 | 归一化隐藏原始信号、数据饱和或优化无效 | 原始组内方差、有效组数、grad 与参数变化 | 按已定位环节修数据/采样/更新，别仅按 adv std 调 LR |
| 8. Approx KL↑，clip↑，ratio 尾部↑ | 多 epoch/LR 过强，也可能 rollout 陈旧 | 查版本差、adv 尾部、mask、每 epoch ratio | 同步策略；再试减少 epoch/LR，重评局部退化 |
| 9. Grad spike，NaN/Inf 或 skipped step↑ | 数值、异常样本、分布失配 | 定位裁剪前 norm、精度、超长样本和 logprob 差异 | 修数值/数据问题；核对 clipping 后再调优化器 |
| 10. Reference KL↑，held-out score→ | 偏离没换来可见收益，也可能评估不敏感 | 查 KL coefficient、子任务与通用能力回归 | 对照不同正则强度，选择收益/回归更好的 checkpoint |
| 11. Value loss↓，EV↑，reward→ | critic 会预测当前失败，不代表 actor 会解决 | 检查 return 方差、adv、ratio 和新采样成功率 | 修 actor 信号或任务采样；无需仅为 reward 平台重训 critic |
| 12. Value loss↑，EV↓，actor KL↑ | return 尺度变化或 critic 跟不上 | 同尺度重算、检查 bootstrap、value clipping 与 critic LR | 修 return 定义；必要时调整 critic 更新节奏 |
| 13. Teacher KL↓，held-out score→/↓ | 模仿未迁移能力、teacher 失配或前缀分布移动 | 固定前缀 KL、teacher 自身表现、错误类型和尾部覆盖 | 调 teacher/目标/数据混合，以任务评估选模型 |
| 14. Teacher gap尾部异常，覆盖↓，延迟↑ | teacher 失败、tokenizer/mask 或 top-k 概率问题 | 查请求成功率、对齐、归一化及缺失反馈处理 | 修 teacher 服务与监督覆盖，再比较蒸馏目标 |

不要从一张曲线直接跳到“reward hacking”或“collapse”。先提出多个可能解释，再用固定条件评估、样本审计或小规模对照排除它们。一次偶发 spike 与持续趋势的处置也应不同。

## 5. 一个够用的最小 dashboard

不必给每个算法堆同样的十条曲线。可以按下面的面板模板开始：

| 面板 | 通用内容 | 算法附加内容 |
| --- | --- | --- |
| 效果 | 固定 held-out score、分任务表现、样本数/不确定性、相对初始 checkpoint 的差值 | 有 reward 时加 raw reward 与各分项；有 shaping 时独立画 penalized reward |
| 行为 | Length P50/P95、停止原因、截断率、重复率、entropy 定义 | reasoning 任务加正确/错误长度与固定预算 pass@k |
| 信号 | 有效 prompt/token 数、过滤比例 | PPO：adv 与 value/EV；GRPO：组内 std、全对/全错/有效组；OPD：gap 与 teacher 覆盖 |
| 更新 | LR、裁剪前/后 grad norm、非有限值/跳步、分项 loss | ratio-based：approx KL、ratio 尾部和 clip；reference 正则：KL 与 coefficient；OPD：明确方向的 KD KL |
| 系统 | 阶段耗时、tokens/s、显存、失败/重试 | 异步训练：版本 lag/IS 权重；在线 teacher：请求成本和延迟 |

在面板备注写上定义、代码 commit 与配置链接。参考 [VERL metrics 源码](https://github.com/verl-project/verl/blob/1876b06d0a3e4e71e06230be10af14492ca8a75b/verl/trainer/ppo/metric_utils.py)与[配置文档](https://verl.readthedocs.io/en/latest/examples/config.html)查字段，再沿具体 worker 的日志写入点确认。不应把本文的概念名复制后就默认已完成埋点。文档和 `main` 源码会更新，复现实验时应保存所用 commit 的永久链接。

### 同名指标读实现：VERL v0.9.1 的例子

以下特例限定于 [commit 1876b06](https://github.com/verl-project/verl/tree/1876b06d0a3e4e71e06230be10af14492ca8a75b)，不应直接推广到其他版本或 trainer：

- Vanilla PPO 的 `actor/pg_clipfrac` 统计 clipped surrogate 实际生效的 mask-token 比例，依赖 advantage 符号，不是单纯 ratio 越界率。
- `actor/distillation/loss` 在 direct GKD 路径是聚合 KD loss；在 `use_policy_gradient=true` 时则是以负 detached 蒸馏 loss 作为 advantage 的 PPO surrogate，不能当原始 KL。
- top-k forward-KL 路径截取 teacher top-k 概率而未重新归一化，计算值可能为负再 clamp 到零；不能当作精确全词表 KL。
- `compute_data_metrics` 的 score/reward 均值排除 response length 为零的 aborted 样本。联看 `response/aborted_ratio`，否则失败样本被排除可能让均值显得更好。

这正是为什么“一个指标名”还不够：还需要版本、执行路径、统计分母和变换。

## 6. 排障顺序：先确定证据，再动超参数

1. **确认没有“假异常”**：检查日志定义、横轴、采样配置、评估 checkpoint、reward 版本、样本数和 smoothing。
2. **确认训练在有效运行**：teacher/verifier 是否成功，mask 是否正确，是否跳步，rollout 与 actor 权重是否同步。
3. **先查任务收益与具体失败**：固定 held-out 协议，比较初始/当前/最佳 checkpoint，抽看高分失败与退化任务。
4. **再查信号**：GRPO 的同 prompt 组内区分、PPO 的 return/critic/adv、OPD 的 teacher 支持与 gap，而不是统看 adv std。
5. **查更新与行为变化是否同时出现**：ratio、KL、clip、grad 对齐到对应更新；结合 length、stop、entropy 和重复率定位假设。
6. **做一个小对照再下结论**：调一个因素，用相同题目和预算比较收益、回归与成本。若停训或回滚，依据独立评估和确认的异常，不靠单条曲线形状。

一个可复用的运行记录模板：

```text
算法 / 代码 commit / checkpoint：
训练与 held-out 数据版本 / reward 与 verifier 版本：
采样配置 / 每题样本数 / token budget：
KL 方向与 estimator / advantage normalization / loss reduction：
观察到的变化 / 有效样本数 / 不确定性：
候选解释 / 排除证据 / 待验证假设：
对照仅改变的因素 / 结果 / 下一步：
```

Tracking 的价值，是把“看起来在变好”变成可核对的证据：**评分信号是否可靠、更新是否有效、行为是否符合目标，以及独立评估中是否获得可复现的收益。**

## 参考资料

- [Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347)：PPO surrogate 与更新方法。
- [DeepSeekMath](https://arxiv.org/abs/2402.03300)：GRPO 与数学推理后训练。
- [On-Policy Distillation of Language Models / GKD](https://arxiv.org/abs/2306.13649)：student 自生成序列上的蒸馏与目标选择。
- [MiniLLM](https://arxiv.org/abs/2306.08543)：reverse-KL 蒸馏的具体方法。
- [VERL PPO](https://verl.readthedocs.io/en/latest/algo/ppo.html)、[GRPO](https://verl.readthedocs.io/en/latest/algo/grpo.html)、[rollout correction](https://verl.readthedocs.io/en/latest/algo/rollout_corr.html)：算法配置与分布校正。
- [VERL core_algos.py](https://github.com/verl-project/verl/blob/1876b06d0a3e4e71e06230be10af14492ca8a75b/verl/trainer/ppo/core_algos.py)、[metric_utils.py](https://github.com/verl-project/verl/blob/1876b06d0a3e4e71e06230be10af14492ca8a75b/verl/trainer/ppo/metric_utils.py)、[配置说明](https://verl.readthedocs.io/en/latest/examples/config.html)：核对估计器、统计口径与日志字段。
