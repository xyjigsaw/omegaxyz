Reward rising, entropy falling, and KL shrinking are tempting signs of progress. None proves that a post-trained model became more useful. First establish what each metric measures, then check whether changes survive independent evaluation.

This guide covers PPO, GRPO and on-policy distillation (OPD), with metric tables and 14 joint diagnostics. Examples are illustrative, not measurements. There is no universal healthy threshold or mandatory curve shape.

![A reading workflow for post-training metrics](../../../../../assets/post-training-tracking.svg)

*Original workflow illustration; not an empirical curve or a causal diagram.*

## 1. Define the dashboard before reading it

Record these details for every run:

1. Algorithm and objective: PPO, GRPO, direct distillation, or a combination. OPD describes learning on student-generated trajectories; it does not imply a critic or PPO.
2. Versions: datasets, prompt templates, reward/verifier, teacher, reference, tokenizer, code commit and configuration.
3. Sampling: temperature, top-p/top-k, samples per prompt, length budget, EOS/stop rules. Record evaluation decoding separately.
4. Aggregation: token, response, prompt group or minibatch; response mask; average per sequence versus average over all tokens.
5. Transformations: reward shaping, advantage whitening, KL direction and estimator, loss reduction and coefficients.
6. Timing: rollout step versus optimizer step, checkpoint used for evaluation, and repeated updates over old rollouts.

Token averages give longer answers more weight. Keep unsmoothed spikes, tail quantiles and effective counts visible. Compare runs by processed tokens, GPU time or cost as well as steps.

## 2. PPO, GRPO and OPD require different panels

| Route | Signal and update | Useful specific metrics | Do not assume |
| --- | --- | --- | --- |
| PPO | Returns and a value baseline, commonly GAE; clipped old/new policy surrogate | Value loss, explained variance, ratio, approximate KL, clipping | Teacher KL |
| GRPO variants | Relative rewards within multiple responses to the same prompt; often PPO-style updates | Within-group reward std, all-correct/all-wrong groups, effective groups, ratio/clip | A separate critic or mandatory std normalization |
| OPD / GKD | Teacher feedback on student-generated prefixes; direct distribution matching or an RL combination | Direction-specific teacher KL/KD loss, gap distribution, coverage and cost | Critic, advantage, PPO ratio or clipping |

See the [PPO paper](https://arxiv.org/abs/1707.06347), [DeepSeekMath](https://arxiv.org/abs/2402.03300) and [GKD](https://arxiv.org/abs/2306.13649). Always inspect the implementation behind the algorithm name.

Reward is feedback from a scorer. Return aggregates future rewards. Advantage compares an action against a baseline. A common PPO estimator is:

$$
\delta_t=r_t+\gamma V(s_{t+1})-V(s_t),\qquad \hat A_t=\sum_{l\ge0}(\gamma\lambda)^l\delta_{t+l}.
$$

The sum ends at the trajectory boundary; terminal, truncation and bootstrap handling matter. The simple expression $A=R-V$ is intuition, not a replacement for token-level GAE. A critic predicts return, rather than independently judging correctness. Centered sequence advantages can have nonzero token-weighted means when lengths differ; zero average advantage or loss does not imply zero gradient. Zero-variance groups remove the centered outcome-PG signal, not necessarily gradients from other loss terms.

A common outcome-reward GRPO definition is:

$$
\hat A_i=\frac{R_i-\bar R_g}{\sigma_g+\epsilon}.
$$

The group contains responses to **the same prompt**. Some variants omit std scaling; inspect [VERL GRPO](https://verl.readthedocs.io/en/latest/algo/grpo.html) and its advantage implementation.

Two illustrative groups `[1,1,1,1]` and `[0,0,0,0]` have nonzero batch reward variation but zero within-group variation. Neither supplies relative reward discrimination under this definition. An all-correct group and an all-wrong group need different remedies. Normalized advantage std can stay near a fixed scale by construction; inspect raw signal, nonzero/effective fractions, masks and gradients instead of treating it as learning strength.

## 3. Six groups of metrics

Names below are concepts, not a guaranteed mapping to any trainer. A `critic/` prefix does not by itself prove that a metric requires a critic.

### A. Outcomes

| Metric | Purpose and applicability | Common misreading |
| --- | --- | --- |
| Raw reward mean, quantiles and components | Reward-based runs: inspect scorer outcomes and tails | A proxy score is not evidence of generalization |
| Shaped reward / return | RL with KL penalties or other shaping | A coefficient change can move the mean without better answers |
| Held-out accuracy, pass@1, pass@k | All routes: task gains under a fixed budget | Different k, temperature, length or verifier makes comparison unreliable |
| Task/difficulty/length slices and general regressions | All routes: detect hidden losses | Small evaluation sets or leakage can create apparent gains |

Use identical prompts and evaluation protocols, report counts and uncertainty, and consider paired analysis or prompt-level bootstrap. Multiple answers to one prompt are not independent evaluation questions. Re-evaluate the baseline when the protocol changes.

### B. Learning signal

| Metric | Purpose and applicability | Common misreading |
| --- | --- | --- |
| Batch reward std and within-prompt std | Reward training; the latter is critical for GRPO | Batch variation may only reflect prompt difficulty |
| All-correct, all-wrong and nonzero-variance group fractions | GRPO: separate saturation from exploration failure | Low std alone does not imply convergence |
| Advantage mean/std, positive and zero fractions | Advantage-based RL: inspect baseline and normalization | Centering explains mean≈0; positive fraction need not be 50%; normalized std is not strength |
| Effective prompts/responses/tokens and filtering | All routes: actual coverage | A large nominal batch may have little usable data |
| Value loss and explained variance | Critic-based methods: return prediction | Scale affects loss; good predictions do not prove actor improvement |

Explained variance commonly equals $1-\mathrm{Var}(G-V)/\mathrm{Var}(G)$. Near-zero return variance makes it unstable or undefined. Value clipping, return normalization and masks affect interpretation.

### C. Parameter updates

| Metric | Purpose and applicability | Common misreading |
| --- | --- | --- |
| Policy/KD loss and weighted components | Corresponding objectives: inspect signs and reduction | Loss magnitudes across batches are not capability scores |
| Old/new ratio quantiles | Ratio-based RL: inspect update tails and data reuse | A normal mean can hide extreme tails |
| Approximate/PPO KL | Local old/new policy change | It is not teacher or reference KL; specify direction and estimator |
| Clip fraction and upper/lower components | Clipped objectives: monitor active clipping | It is not the proportion of parameters or gradients completely removed |
| Reference KL and coefficient | Reference regularization: drift and constraint strength | The reference may differ from the original base model; low KL need not be good |
| Grad norm before/after clipping, LR, NaN/Inf, skipped steps | All routes: numeric and optimizer issues | Logging stage and distributed reduction change the value |

The PPO surrogate is:

$$
L^{\mathrm{clip}}=\mathbb E[\min(r_t\hat A_t,\operatorname{clip}(r_t,1-\epsilon,1+\epsilon)\hat A_t)],\quad r_t=\frac{\pi_\theta(a_t\mid s_t)}{\pi_{\rm old}(a_t\mid s_t)}.
$$

Implementations commonly minimize its negative. Active clipping depends on advantage sign. Some logs count ratio violations; others count selection of the clipped branch. A locally flat clipped term does not remove gradients from other tokens, KL or entropy terms.

A sampled average log-ratio estimator may be negative in finite samples, whereas other KL approximations are nonnegative. Read the estimator. [VERL PPO](https://verl.readthedocs.io/en/latest/algo/ppo.html) also separates reward-side KL penalties and actor-side KL loss.

### D. Generated behavior

| Metric | Purpose and applicability | Common misreading |
| --- | --- | --- |
| Token entropy by task/position | All generation training: conditional certainty | Low entropy can reflect confident correct answers; it alone does not prove collapse |
| Length P50/P95, correct/incorrect lengths | All routes: reasoning and budget changes | A stable mean can hide truncating tails |
| EOS, stop and truncation rates | All routes: completion behavior | A valid stop string can end a response without EOS |
| Repetition, distinct outputs, formatting/refusal | All routes: behavioral checks | Text diversity is not token entropy; decoding and tokenizer must match |

$H(p)=-\sum_a p(a)\log p(a)$. Sampled-token surprisal estimates this only when sampling matches the distribution being measured. Temperature/top-p sampling may differ from raw model probabilities. Combine entropy with accuracy, repetition, coverage and multi-sample evaluation before diagnosing exploration failure.

### E. Distillation

| Metric | Purpose and applicability | Common misreading |
| --- | --- | --- |
| Forward KL: D(T ∥ S) | KD using this direction: teacher-supported modes | Not interchangeable with reverse KL or signed sampled gaps |
| Reverse KL: D(S ∥ T) | OPD using this direction: student/teacher alignment | Avoiding difficult prefixes can lower current-trajectory KL |
| Sampled logprob gap mean, quantiles and positive fraction | Sampled teacher feedback: tails and scale | A token gap is neither a correctness label nor full-vocabulary KL |
| Fixed-prefix KL and held-out task score | Distillation: distribution shift versus useful transfer | Training KL alone does not prove task gains |
| Teacher coverage, request success, latency and cost | Online-teacher OPD | Failure and truncated distributions change supervision, not only speed |

At a fixed prefix $s$, let $p_S$ and $p_T$ be normalized conditional distributions on the same vocabulary:

$$
D_{\mathrm{KL}}(p_T\Vert p_S)=\sum_a p_T(a\mid s)\log\frac{p_T(a\mid s)}{p_S(a\mid s)},\quad D_{\mathrm{KL}}(p_S\Vert p_T)=\sum_a p_S(a\mid s)\log\frac{p_S(a\mid s)}{p_T(a\mid s)}.
$$

For $\Delta(a)=\log p_T(a\mid s)-\log p_S(a\mid s)$:

$$
\mathbb E_{a\sim p_S}[\Delta(a)]=-D_{\mathrm{KL}}(p_S\Vert p_T),\qquad \mathbb E_{a\sim p_T}[\Delta(a)]=D_{\mathrm{KL}}(p_T\Vert p_S).
$$

The student-sampled mean can therefore be negative without contradicting KL nonnegativity. Finite samples vary. If actual sampling uses a transformed distribution $q$, its expectation is $\mathbb E_q[\Delta]$, not automatically either expression above. Record prefix distribution, temperature, vocabulary support and top-k tail handling.

A positive gap says only that the teacher assigns relatively greater token probability. Gradient effects depend on the objective, baseline and stop-gradient handling. [MiniLLM](https://arxiv.org/abs/2306.08543) is a particular reverse-KL method, not a universal OPD definition.

For tool-using agents, separate generated tokens from tool observations; report parse, execution, semantic and end-to-end success, turns, timeouts and cost per successful session. API success alone is not task success. Teacher top-k mass, student mass and overlap are useful additional diagnostics, not universal default logs.

### F. Systems

| Metric | Purpose and applicability | Common misreading |
| --- | --- | --- |
| Rollout/update/reward/teacher stage times | All routes: locate bottlenecks | Longer answers can increase step time without a hardware fault |
| Effective tokens/s, memory, OOM and retries | All routes: efficiency and lost samples | High throughput does not prove useful optimization |
| Policy version lag, rollout/train logprob differences, IS-weight tails | Asynchronous or separate-engine training: stale/mismatched data | Precision, templates, masks and tokenizers also cause differences |

See [VERL rollout correction](https://verl.readthedocs.io/en/latest/algo/rollout_corr.html). Check weight synchronization and logprob consistency before responding to a ratio or gradient spike by changing LR.

## 4. Fourteen joint diagnostics

Arrows mean changes relative to a comparable baseline, with identical definitions. These are hypotheses, not automatic causal conclusions or universal alarms.

| Combination | Possible explanation | Verify next | Action after verification |
| --- | --- | --- | --- |
| 1. Reward↑, held-out score↑ | Useful learning or evaluation drift | Fixed decoding, slices and uncertainty | Keep checkpoint; monitor regressions and cost |
| 2. Reward↑, held-out score flat/down | Proxy mismatch, overfit or scoring loophole | High-score failures, independent judging, overlap | Fix reward/data; select by held-out outcomes |
| 3. Reward↑, length P95↑, truncation↑ | Useful reasoning or length exploitation | Accuracy by length and fixed-budget evaluation | Fix stopping/budget; change length rewards only with evidence |
| 4. Entropy↓, reward↑, pass@1↑ | More confident correct answers | Repetition, coverage, pass@k and regressions | No need to force higher entropy if behavior remains good |
| 5. Entropy drops, repetition↑, pass@k↓ | Narrower behavior, exploration failure or decoding change | Same-prompt samples and checkpoint comparison | Restore decoding consistency; then test gentler updates/exploration |
| 6. Batch std positive, group std≈0 | GRPO lacks relative signal | Separate all-correct/all-wrong; check scorer/sampling | Harder tasks for saturation; inspect verifier/difficulty/exploration for failure |
| 7. Normalized adv std stable, reward flat | Hidden raw-signal loss, saturation or ineffective optimization | Raw variance, effective groups, gradients and parameter change | Repair the identified stage rather than tune from normalized std |
| 8. Approx KL↑, clip↑, ratio tails↑ | Aggressive updates or stale rollouts | Version lag, adv tails, masks and epoch-level ratios | Synchronize; test fewer epochs/lower LR and re-evaluate |
| 9. Grad spike with NaN/skipped steps↑ | Numeric, sample or distribution mismatch | Pre-clip norms, precision, long samples and logprobs | Fix numeric/data issues before tuning optimizer |
| 10. Reference KL↑, held-out flat | Drift without measured benefit or insensitive evaluation | Coefficient, task slices and general regressions | Compare regularization and select by benefit/regression |
| 11. Value loss↓, EV↑, reward flat | Critic predicts failure accurately | Return variance, adv, ratio and new-rollout success | Repair actor signal/task sampling |
| 12. Value loss↑, EV↓, actor KL↑ | Return-scale change or lagging critic | Same-scale metrics, bootstrap, clipping and critic LR | Fix return definition; then adjust critic updates |
| 13. Teacher KL↓, held-out flat/down | Imitation without transfer, teacher mismatch or moving prefixes | Fixed-prefix KL, teacher performance and error slices | Adjust teacher/objective/data; select by task evaluation |
| 14. Gap tails abnormal, coverage↓, latency↑ | Teacher failure, alignment or probability truncation | Request success, tokenizer/masks, normalization, missing feedback | Repair teacher supervision before comparing objectives |

Audit samples and run controlled comparisons before naming reward hacking or collapse. Treat isolated spikes differently from sustained changes. Change one factor at a time and preserve baseline checkpoints and evaluation budgets.

## 5. A minimal dashboard

| Panel | Shared metrics | Route-specific additions |
| --- | --- | --- |
| Outcomes | Fixed held-out score, slices, counts/uncertainty, baseline difference | Raw reward/components; shaped reward separately |
| Behavior | Length quantiles, stopping reasons, truncation, repetition, defined entropy | Correct/incorrect lengths and fixed-budget pass@k |
| Signal | Effective prompts/tokens and filtering | PPO: adv/value/EV; GRPO: group std and saturation/failure fractions; OPD: gap/teacher coverage |
| Updates | LR, pre/post-clip norm, nonfinite/skipped steps, loss components | Ratio/approx KL/clip where applicable; reference KL/coefficient; direction-specific KD |
| Systems | Stage times, throughput, memory and retries | Version lag/IS tails; teacher latency/cost |

Attach definitions, code commit and configuration to panel notes. Inspect [VERL metric_utils.py](https://github.com/verl-project/verl/blob/1876b06d0a3e4e71e06230be10af14492ca8a75b/verl/trainer/ppo/metric_utils.py), [core_algos.py](https://github.com/verl-project/verl/blob/1876b06d0a3e4e71e06230be10af14492ca8a75b/verl/trainer/ppo/core_algos.py) and [configuration](https://verl.readthedocs.io/en/latest/examples/config.html), then find the actual worker logging location. Documentation and `main` change; preserve commit-pinned links for reproducibility.

### Same name, different implementation: VERL v0.9.1

These examples apply to [commit 1876b06](https://github.com/verl-project/verl/tree/1876b06d0a3e4e71e06230be10af14492ca8a75b), not every trainer or release:

- Vanilla PPO `actor/pg_clipfrac` counts mask tokens where the clipped surrogate is active; advantage sign matters.
- `actor/distillation/loss` is aggregated KD loss for direct GKD, but with `use_policy_gradient=true` it is a PPO surrogate using negative detached distillation loss as advantage, rather than raw KL.
- The top-k forward-KL path keeps unnormalized teacher top-k probabilities. Its intermediate result can be negative and is clamped to zero; it is not exact full-vocabulary KL.
- `compute_data_metrics` excludes zero-response-length aborted samples from score/reward averages. Inspect `response/aborted_ratio` alongside these means.

Record the version, execution path, denominator and transformations behind each name.

## 6. Debug before changing hyperparameters

1. Exclude measurement artifacts: definitions, axes, sampling, evaluation checkpoints, reward versions, counts and smoothing.
2. Verify effective execution: teacher/verifier success, masks, skipped updates and synchronized weights.
3. Establish task outcomes: fixed held-out protocol, initial/current/best checkpoints, high-score failures and regressing slices.
4. Inspect route-specific signal: GRPO group discrimination, PPO returns/critic/adv, OPD teacher support/gaps.
5. Align updates and behavior in time: ratio/KL/clip/grad together with length/stop/entropy/repetition.
6. Run a small single-factor comparison with identical questions and budgets; decide continuation or rollback from validated outcomes and confirmed failures.

```text
Algorithm / code commit / checkpoint:
Training and held-out versions / reward and verifier versions:
Sampling / responses per prompt / token budget:
KL direction and estimator / advantage normalization / loss reduction:
Observed change / effective count / uncertainty:
Hypotheses / excluded explanations / remaining checks:
Single changed factor / comparison result / next action:
```

Tracking is useful when it produces inspectable evidence: reliable supervision, effective updates, appropriate behavior and reproducible gains in independent evaluation.

## References

- [PPO](https://arxiv.org/abs/1707.06347) and [DeepSeekMath / GRPO](https://arxiv.org/abs/2402.03300).
- [GKD](https://arxiv.org/abs/2306.13649) and [MiniLLM](https://arxiv.org/abs/2306.08543).
- [VERL PPO](https://verl.readthedocs.io/en/latest/algo/ppo.html), [GRPO](https://verl.readthedocs.io/en/latest/algo/grpo.html), [rollout correction](https://verl.readthedocs.io/en/latest/algo/rollout_corr.html) and [configuration](https://verl.readthedocs.io/en/latest/examples/config.html).
- [VERL core_algos.py](https://github.com/verl-project/verl/blob/1876b06d0a3e4e71e06230be10af14492ca8a75b/verl/trainer/ppo/core_algos.py) and [metric_utils.py](https://github.com/verl-project/verl/blob/1876b06d0a3e4e71e06230be10af14492ca8a75b/verl/trainer/ppo/metric_utils.py).
