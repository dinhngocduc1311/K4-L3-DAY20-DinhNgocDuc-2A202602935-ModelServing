# 02 — Serve

Step up from "measure a model" to "run a serving stack". Same shape as the vLLM and
SGLang setups in the deck — OpenAI-compatible HTTP, continuous batching, Prometheus
metrics — on a model small enough to fit your laptop.

There is **one** server. The prebuilt native binary gives you `/metrics`,
`--parallel` and `--cont-batching` out of the box, so nothing here needs a build.

The default command uses `--parallel 4 --cont-batching --metrics --reasoning off`.
`LAB_N_CTX=2048` is the server's total context budget: with four slots the runtime
reports `n_ctx_slot = 512`. Raising parallelism without raising the total context
therefore reduces the context available to each request.

## Load profile

Locust offers an intentional mix: 80% short chat requests with 48 output tokens and
20% RAG-shaped requests with 96 output tokens. Each virtual user waits 0.2–1.5 seconds
between requests. The 80/20 ratio describes requests started, not necessarily requests
completed before the 60-second cutoff; slow long requests can still be queued when
Locust prints its percentiles.

On a slow machine, lower `LAB_LOAD_SHORT_TOKENS` and `LAB_LOAD_LONG_TOKENS` or set
`LAB_LOAD_DURATION=3m`. Use identical duration and caps for the 10- and 50-user runs,
and record the overrides in the report so the comparison remains reproducible.

## The run, in order

```bash
# terminal 1 — leave it running
make serve

# terminal 2
make smoke          # rubric items 6 + 7 in one screenshot
make load-10        # 10 users, 60s  -> benchmarks/locust-10_stats.csv
make load-50        # 50 users, 60s  -> benchmarks/locust-50_stats.csv

# terminal 3, WHILE load-50 is running
make metrics        # samples /metrics for 60s

# after both load runs
make load-report    # -> benchmarks/02-server-results.md
```

Windows uses the same targets:

```powershell
# terminal 1 — leave it running
.\lab.ps1 serve

# terminal 2
.\lab.ps1 smoke
.\lab.ps1 load-10
.\lab.ps1 load-50

# terminal 3, while load-50 is running
.\lab.ps1 metrics

# after both load runs
.\lab.ps1 load-report
```

If port 8080 is occupied, set `LAB_SERVER_PORT=8090` in **every terminal** used by
the server, smoke test, load generator, metrics recorder, and pipeline. In PowerShell:
`$env:LAB_SERVER_PORT = '8090'`.

`make metrics` must overlap with load, or it records an idle server and the batching
gauges all read ~1. That is the single most common mistake in this track.

## What you get

| Command | Artifact | Rubric |
|---|---|---|
| `make smoke` | screenshot: a completion **and** non-zero `tokens_predicted_total` | 6, 7 |
| `make load-10` / `load-50` | locust summary screenshots + CSVs | 8 |
| `make load-report` | `benchmarks/02-server-results.md` | 10 |
| `make metrics` | `benchmarks/02-server-batching-u50.md` + CSV | 9 |

The smoke test reads `/metrics` before and after one completion. A successful run ends
with `OK -- served a completion and tokens_predicted_total is ... (non-zero).` Its
`prompt` and `decode` timings are server-side compute timings; unlike client-side TTFT
and TPOT, they exclude network and client overhead and do not expose queue time.

## Reading the load report

`load-report.py` estimates **effective concurrency** with Little's Law — `L = λ × W`.
It uses completion RPS and completed-request latency, so it is exact only near steady
state. A timed run that ends with queued requests underestimates concurrency.

- **Effective concurrency > slots** → requests queued on average.
- **Effective concurrency ≤ slots** → average occupancy did not exceed capacity; this
  does not rule out queueing in the tail. Check `requests_deferred`.

This is system occupancy, not slot utilisation; use `n_busy_slots_per_decode` for the
latter. Throughput counts every completion, while goodput@SLO counts only completions
within a chosen latency threshold. Aggregate P95 can establish whether the 95% target
passes, but exact goodput needs per-request counts at that threshold.

## Reading the batching metrics

`llamacpp:n_busy_slots_per_decode` is the average number of slots doing useful work
per decode step:

- near **1** under load → requests did not overlap enough, or were effectively serialized
- climbing toward **`--parallel`** → the scheduler is packing concurrent requests into
  shared decode steps. That is direct evidence of continuous batching; whether it
  improves goodput still depends on saturation and the latency SLO.
- `requests_deferred` above 0 → more requests arrived than there were slots

The report takes the highest sampled value over 60 seconds. Because the busy-slots
metric is itself an average per decode step, this peak is the highest average sampled,
not an instantaneous maximum batch width. If `kv_cache_usage_ratio` is `n/a`, the
current llama.cpp build did not export it; do not rewrite it as zero.

## Knobs worth trying

Anything after `--` goes straight to `llama-server`:

```bash
.venv/bin/python labs/02-serve/serve.py -- --parallel 1          # batching off, for contrast
.venv/bin/python labs/02-serve/serve.py -- --parallel 8
.venv/bin/python labs/02-serve/serve.py -- --ctx-size 4096       # watch process RSS grow
.venv/bin/python labs/02-serve/serve.py -- --cache-type-k q8_0 --cache-type-v q8_0   # bonus C2
.venv/bin/python labs/02-serve/serve.py --compare                # serve the 2-bit quantization
```

On Windows, use the same flags through the wrapper, for example
`.\lab.ps1 serve -- --ctx-size 4096`.

| Flag | Measure this |
|---|---|
| `--parallel N` | P95 at `-u 50` for N = 1, 2, 4, 8 |
| `--ctx-size` | Total context, per-slot context, and RAM/RSS as KV cache grows |
| `--cache-type-k/v` | RAM saved vs quality lost |

The most instructive experiment in this track: run `make load-50` at `--parallel 1`
and again at `--parallel 4`, and compare both RPS *and* P95. One of them improves a
lot more than the other. Restart the server between runs and set the same
`LAB_PARALLEL` value when running `load-report`, or the report will compare occupancy
against the wrong slot count.

## Endpoints

| Path | Use |
|---|---|
| `POST /v1/chat/completions` | OpenAI-compatible; works with the `openai` SDK pointed at `http://localhost:8080/v1` |
| `GET /metrics` | Prometheus text |
| `GET /slots` | per-slot state — useful for seeing batching directly |
| `GET /health` | readiness (this is what `serve_bg` polls) |
| `GET /props` | the server's active configuration |

## Next

```bash
make pipeline
```
