# 03 — Integrate (Milestone 1)

Prove your serving endpoint speaks OpenAI-compatible HTTP well enough to slot into the
platform you have been building since N16. The goal is not an elaborate system — it is
a working seam, plus an honest account of where the time goes.

```bash
make serve       # terminal 1
make pipeline    # terminal 2
```

Windows uses the same targets: `.\lab.ps1 serve` and `.\lab.ps1 pipeline`.

Runs on toy data as shipped, so you can confirm the seam works before wiring anything
real.

## What to connect

| Day | Piece | Stub that is acceptable |
|---|---|---|
| N16 Cloud/IaC | k8s cluster, or a Compose stack | "localhost only" |
| N17 Data pipelines | Airflow DAG / batch job | in-memory list |
| N18 Lakehouse | Delta / Iceberg table | SQLite, or the toy dict |
| N19 Vector + features | vector index + Feast view | `TOY_DOCS` + keyword overlap |
| N20 Serving | your `llama-server` | — (this one must be real) |

**Stubbing is fine and costs no points — misrepresenting it does.** Rubric item 13
asks you to say which pieces are real and which are stubbed. An honest "SQLite
standing in for N18, because my Iceberg setup is not ready" scores full marks.

## What to replace

`pipeline.py` has two marked stubs:

- **STUB 1** `TOY_DOCS` — swap in your corpus
- **STUB 2** `retrieve()` — swap in your N19 vector search

`embed()` already calls a real embedding endpoint if you give it one:

```bash
make serve-embed &                                       # :8081
.venv/bin/python labs/03-integrate/pipeline.py --embed-url http://localhost:8081
```

On Windows, run `.\lab.ps1 serve-embed` in a separate terminal, then
`.\lab.ps1 pipeline --embed-url http://localhost:8081`. If an explicit embedding URL
fails, the pipeline stops instead of silently relabeling the run as keyword retrieval.

Without it, retrieval falls back to keyword overlap and reports `embed: 0.0 ms` —
which is itself a useful baseline for the latency question below.

## The deliverable

Three example queries running end to end, printing retrieved-context provenance and
the client-side stage breakdown plus server-side prefill/decode:

```
timings : {'embed': 41.2, 'retrieve': 0.3, 'llm': 1840.5, 'total': 1882.0}
Dominant stage: llm (98% of total)
Mean server timing (ms): prefill 1220.4, decode 510.2
```

Put those numbers in **REFLECTION §4** (rubric items 12 and 13).

Most students find the LLM dominates and are right. The interesting cases are the
ones where it does not — a slow embedder, or retrieval over a large index, can beat
decode on a small model. If your split surprised you, that is the observation worth
writing.

## Live demo checklist

1. `curl localhost:8080/v1/models` responds
2. `make pipeline` runs on a fresh query — show contexts *and* the answer
3. `/metrics` reflects the call (`tokens_predicted_total` went up)

## Common stumbling points

- **Prompt caching:** a byte-identical system prompt creates a reusable token prefix,
  but cumulative `prompt_tokens_total` alone does not prove a cache hit. For a clean
  A/B, use an otherwise idle one-slot server, repeat the exact prompt, then change one
  byte and compare server `prompt_ms` plus the LCP/cache log.
- **Token budgeting:** llama.cpp's tokenizer is not OpenAI's. Do not size retrieved
  context with `tiktoken` and expect it to match; ask the server via `/tokenize`.
- **Context budget:** default `--ctx-size` is 2048 and it is shared across `--parallel`
  slots (about 512 tokens per slot at the default width of four on this runtime).
  Prompt, template and output all consume that budget. Too many retrieved chunks can
  truncate; `make sweep-ctx` (bonus) shows what raising it costs in TTFT and memory.
- **OpenAI SDK:** the shipped code uses `httpx` and needs no extra dependency. If you
  prefer the SDK, `pip install "openai>=1.0"` and point `base_url` at
  `http://localhost:8080/v1`.

## Next

```bash
make verify
```
