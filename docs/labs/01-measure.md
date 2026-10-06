# 01 — Measure

Two commands. The first tells you where you stand; the second gives you something to
write about.

```bash
make bench      # TTFT / TPOT / P50-P95-P99, both quantizations
make tune       # thread sweep -> your before/after speedup
```

## `make bench` — the baseline

Starts `llama-server` on a scratch port (8099), streams 10 prompts through
`/v1/chat/completions`, tears the server down, then repeats for the second
quantization. You measure real over-the-wire latency without managing two terminals.

Writes **`benchmarks/01-quickstart-results.md`** — rubric items 3, 4 and 5.

```
TTFT P50/P95/P99  <- client wait until the first token
TPOT P50/P95/P99  <- decode cost per token after the first
Decode (tok/s)     <- 1000 / TPOT_p50
E2E P50/P95/P99   <- complete request latency
```

- **TTFT** is dominated by prefill compute. Short prompts hide it; long-context RAG
  does not. Bonus `make sweep-ctx` shows exactly how badly.
- **TPOT** is often dominated by memory bandwidth, not FLOPs. A smaller quantization
  moves fewer bytes per token, but can still be slower when dequantization compute or
  backend kernel efficiency dominates.

Percentiles use nearest-rank. With only 10 samples, P95 and P99 both select the
slowest sample, so report them as required but do not overstate tail precision.

Token counts come from llama.cpp's own `timings` block, so TPOT is not inferred from
counting SSE chunks.

**The first run is not the fast run.** Model load is excluded from the percentiles and
a warm-up request is discarded, but the OS page cache still matters: the second time
you run this, the weights are already in RAM. Know which number you are reporting.

## `make tune` — a measured thread-count before/after

Sweeps thread counts through `llama-bench` (no server or compiler required) and writes
**`benchmarks/01-tuning-tg128.md`** with a table, a winner, and a speedup ratio against
the physical-core default. It runs CPU-only when no accelerator is usable and otherwise
uses the configured `n_gpu_layers`; inspect the report header before interpreting the
curve.

This is enough for **rubric item 11** on its own. No bonus work required.

For a CPU-bound decode, the expected shape is a climb to roughly the *physical* core
count followed by a plateau or drop. Threads past that point compete for memory
channels, cache, and scheduling time. With `ngl > 0`, accelerator offload can make the
CPU-thread curve nearly flat. **If your curve does something else, that is the more
interesting report** — report it and explain the active backend instead of forcing the
expected story.

```bash
# macOS / Linux
make tune
LAB_N_THREADS=<winner> make bench
.venv/bin/python labs/01-measure/tune.py --metric pp512
```

```powershell
# Windows
.\lab.ps1 tune
$env:LAB_N_THREADS = '<winner>'
.\lab.ps1 bench
Remove-Item Env:LAB_N_THREADS
.\lab.ps1 tune --metric pp512
```

## Knobs

| Variable | Default | What it changes |
|---|---|---|
| `LAB_N_THREADS` | physical cores | Threads. More is not faster. |
| `LAB_N_CTX` | 2048 | Total server context, divided across slots → KV cache size |
| `LAB_N_GPU_LAYERS` | 99 if any accelerator, else 0 | Layers on the GPU |
| `LAB_MAX_TOKENS` | 64 | Tokens generated per request |
| `LAB_TEMPERATURE` | 0.7 | Sampling temperature |

## Before you benchmark

Close the browser, the IDE and Slack. They compete for exactly the resource decode is
bound by. A benchmark run next to 40 Chrome tabs measures Chrome.

## Next

```bash
make serve
```
