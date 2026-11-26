Show a model a photo of a workbench and ask it to draw a box around a particular part. Now ask how far a robot arm should reach to pick it up. The second question feels like a natural extension of the first. For a vision model, it is a different problem. That gap is why one story on [Scaling Low](https://scalinglow.com/) stuck with me: the picture stays the same, but a different question reveals a different limit.

## What is Scaling Low?

Scaling Low is a bilingual site tracking AI risks in English and Chinese. Its [news feed](https://scalinglow.com/#news) follows research and checks claims made about it, with entries that open onto the underlying evidence. The [risk map](https://scalinglow.com/#risks) offers another way in: follow reliability, misuse, governance or infrastructure instead of scrolling by date.

![Scaling Low's English homepage with its AI risk countdown and navigation](https://cdn.omegaxyz.com/2026/11/scaling-low-ai-risk-roundup/home-en.webp)

The first thing you notice is the countdown. **It is not a prediction of when an AI bubble will burst.** The site's [published method](https://scalinglow.com/bubble.json), as of November 26, gives equal weight to two dates: one to revisit inference costs, performance and supply after GTC, the other to check capital spending, cloud profits and cash flow after quarterly results. When the clock runs down, the useful question is what the new numbers say.

## Six stories from November 19–26

Dates below are when **Scaling Low listed each story**, not necessarily when a paper first appeared.

### November 26 | The right part, at the wrong distance

BOP-Refer tested 17 vision-language models on locating a described object in a single image. The strongest, Gemini 4 Carbon, scored 72.6% average precision in 2D but just 12.4% in 3D, even with more forgiving overlap thresholds. A predicted box could line up nicely on screen yet miss in depth by more than the size of the object. A convincing overlay is not enough to choose a vision system for that robot arm. [BOP-Refer paper](https://arxiv.org/abs/2611.34862)

### November 25 | A successful retry can leave an error behind

SecondChance restarts agents from states where an earlier attempt went wrong. On AppWorld, the researchers examined 84 continuations that ultimately succeeded; 40 left the earlier mistake in place. Those weren't 40 failed tasks. They are exactly what you miss when you look only at the successes column. [SecondChance paper](https://arxiv.org/abs/2611.31586)

### November 24 | What got 11.8 times cheaper?

Google DeepMind and Google Quantum AI used agents to propose changes to quantum algorithms and Lean to check them. For one circuit used to calculate a fusion-related property, the estimated computing cost fell by a factor of 11.8. That measure combines qubits and operations. It says nothing about energy output, and it isn't a stopwatch result from running the full simulation on existing hardware. [Research team's account](https://deepmind.google/blog/finding-faster-quantum-algorithms-with-agents-and-formal-verification/)

### November 24 | Can the research assistant point to the passage?

RDQA asks 1,350 questions whose answers depend on evidence in documents, recordings and videos. Under scoring that requires source evidence, the best of 12 general-purpose agent configurations scored 24.0%; RDQA-Skill, designed for this kind of retrieval, scored 41.1%. Try asking an assistant which part of a recorded interview supports its summary. That's a different test from asking whether the summary sounds plausible. [RDQA paper](https://aclanthology.org/2026.emnlp-main.1855/)

### November 20 | What doubles every 3.6 months?

Across two task suites, METR estimates that the length of task an agent can complete with 50% success has been doubling roughly every 3.6 months. The unit is **how long a human expert would need**, not how long the model runs. That matters when choosing longer R&D tasks to try with an agent; it is not a conversion factor for a team's productivity. [METR quarterly update](https://metr.org/blog/2026-11-20-q4-2026-capability-update/)

### November 19 | Data centers and the winter peak

The US Federal Energy Regulatory Commission cites a reliability forecast putting North America's winter peak demand growth at 245 gigawatts over the next decade. Large new loads, particularly data centers, are an important driver. The number measures power needed at peak, not annual energy use, and not all of it is attributable to AI. The same report expects adequate resources in the assessed US regions this winter under normal conditions. A ten-year projection and a one-winter assessment answer different questions. [FERC winter assessment, report p. 23](https://ferc.gov/news-events/news/2026-2027-winter-energy-market-electric-reliability-assessment)

I'd read BOP-Refer and SecondChance together. In one, the box looks right; in the other, the task is marked complete. Neither green check tells you the thing you most want to know. “What didn't this test?” is a good question to take back to the [latest entries on Scaling Low](https://scalinglow.com/#news).
