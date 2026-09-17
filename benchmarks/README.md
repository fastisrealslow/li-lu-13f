# Spin-off extraction experiment

First completed comparison: [2026-09-17 results and manual evidence review](results/35189904752/REVIEW.md).
Strict field passes were rules 4/6, Qwen3.5 9B 3/6, Qwen3 14B 1/6. Neither model
was integrated into production spin-off facts.

Completed Q8 comparison: [Q4 versus Q8 results and memory observations](results/35203275342/REVIEW.md).
Both scored 3/6 strict field passes; Q8 took 12m39s versus Q4's 9m15s. Q8 corrected
one missing name but regressed on one lifecycle stage. Production remains unchanged.

The latest bounded rerun uses the official general-task thinking sampling profile
(temperature 1, top_p .95, top_k 20, min_p 0, presence penalty 1.5, repeat penalty 1),
8192 context, 4096 output tokens and 1800 seconds per case. Both thinking ON and OFF
use identical settings except the think flag. This follows observed repetitive
self-checking and token exhaustion in the temperature-0 / 2048-token pair (run
35215827052). It is a new experimental condition, not a silent replacement of that
run. This single-seed, six-case test remains below the official suggested 32K output
budget; any remaining truncation is a budget failure, not a completed wrong answer.
Source: https://huggingface.co/Qwen/Qwen3.5-9B#best-practices

The earlier isolated workflow tested **Qwen3.5 9B Q8_0 with thinking on and off**.
A first direct-switch probe (run 35215503163) exposed empty final responses with
JSON appearing inside the thinking field when native schema grammar was enabled.
Those integration failures are preserved separately, not treated as a reasoning
quality comparison. The paired rerun uses the same schema in the system prompt
and omits native `format` in BOTH arms. Only the `think` flag differs between arms.
The scorer still requires strict JSON and does not recover answers from thinking.
This new pair is the direct comparison; old native-grammar Q8 is historical context.
The six frozen cases in each arm run in separate CPU jobs, with the same source text, extraction instructions,
schema, scorer, runtime, temperature 0, seed 42 and context 4096 as before.
Output budget increases from 800 to 2048 tokens and per-case timeout from 360 to
1200 seconds to accommodate thinking. This is a bounded reasoning trial, not a
maximum-capability claim. Truncation remains an explicit error; no repair retries.
The raw thinking field is retained separately and only the final answer is scored.
A nonempty thinking field is required to establish that thinking actually ran.
Each report identifies its selected case; `complete` covers selected cases only,
while `fullSuite` states whether one report contains all six. Aggregate all six
unique cases before comparing with the previous non-thinking Q8 run.

A wrapper samples Linux memory every five seconds and prints complete reports into
job logs. Sampled process RSS may double-count shared pages; system available RAM
and swap include other runner processes. These are observations, not exact peaks.
CPU identity is retained; parallel hosted runners may use different CPU models.
Compare summed inference seconds separately from parallel job wall-clock duration.

Run `python scripts/benchmark_spinoff_llm.py --model rules --output /tmp/rules.json`
or use the isolated **Spin-off LLM Benchmark** GitHub Action. This workflow has
read-only repository permission, no schedule, and no dependency on data updates.
Outputs are Actions artifacts and logs; it cannot publish model output to the site.

The first comparison is Qwen3.5 9B Q4_K_M versus Qwen3 14B Q4_K_M, both on standard
Ubuntu CPU runners. The latter is an **older generation**, included to measure
whether increasing parameter count helps this task. It is not assumed superior.
Qwen3.8 27B Q4_K_M is approximately 18GB of weights, exceeding the current runner's
16GB RAM before context/runtime memory; it is not included. No paid API is used.

## Frozen inputs and scoring

`tests/fixtures/spinoff_benchmark.json` contains six manually reviewed official
HKEX/SEC filings (two normalized full short filings and four contiguous excerpts),
source URLs, original download hashes, exact input hashes, and gold annotations.
Original documents were downloaded and read on 2026-09-17. HTML tags and repeated
whitespace/PDF Chinese spacing are normalized. Excerpt selection is manual: this
tests extraction given relevant text, **not document discovery or long-PDF recall**.
The existing Sihuan completion regression sample is deliberately included, so this
is not a wholly unseen holdout. The small, selected sample is not a general accuracy
estimate. Gold was frozen before model inference and never enters model requests.

In the original non-thinking comparison, each model got identical text, prompt, output schema, context 4096, temperature 0,
seed 42, thinking disabled, four CPU threads, and at most 800 output tokens and
360 seconds per case. This tests the production CPU budget, not maximum reasoning
capability. Model digest, runtime version, token counts, elapsed time, errors, and
raw output are retained. A timeout stops that model's run and leaves it explicitly
incomplete. There are no retries with hints and no rule fallback counted as success.

Target identity accepts only predeclared source aliases (case, whitespace and light
punctuation normalized). Status must match. Dates require the exact set of requested
fields, normalized values, and actual/scheduled classifications. `fieldsExact` needs
all three. `grounded` only checks verbatim source presence and the 240-character
quote limit; it does **not** prove the quote supports the claim. Human review of
entailment is required separately. Rules' existing joined/long evidence strings can
fail this stricter quote contract; field scores remain comparable.

Evaluation emphasizes dangerous errors: invented/wrong target and false completion.
An all-field pass with supporting evidence on all six cases is a prerequisite for
a larger shadow evaluation, **not authorization to replace production facts**.
Any false completion blocks automatic integration. Six good results alone do not
establish reliable automation. Review raw failure examples before deciding whether
more model capacity, a narrower prompt, or deterministic extraction is appropriate.

The cases cover achieved HK listing, published prospectus, deferred plan with unnamed
child, declared US record date plus future distribution/trading dates, a planned US
spin-off with similarly named acquired companies, and an irrelevant convertible-note
filing. The negative example does not contain a spin-off clause; a larger follow-up
needs harder compensation/boilerplate negatives and multi-event filings.
