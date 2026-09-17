# Spin-off extraction experiment

First completed comparison: [2026-09-17 results and manual evidence review](results/35189904752/REVIEW.md).
Strict field passes were rules 4/6, Qwen3.5 9B 3/6, Qwen3 14B 1/6. Neither model
was integrated into production spin-off facts.

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

Each model gets identical text, prompt, output schema, context 4096, temperature 0,
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
