# 01 - Measure: latency baseline

Model `Gemma 4 E2B` · host `Windows-AMD64` · llama.cpp `b10488`
Settings: `threads=4` `ngl=99` `ctx=2048`
`max_tokens=64` · warm-up discarded
Completed requests: `UD-Q4_K_XL` 10/10 · `UD-Q2_K_XL` 10/10

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95/P99 (ms) | TPOT P50/P95/P99 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:--|--:|--:|--:|--:|--:|--:|
| UD-Q4_K_XL | 2.97 | 10704 | 3124 / 5044 / 5044 | 70.2 / 71.2 / 71.2 | 7558 / 9412 / 9412 | 14.2 |
| UD-Q2_K_XL | 2.24 | 11802 | 4438 / 6080 / 6080 | 94.5 / 107.5 / 107.5 | 10338 / 12853 / 12853 | 10.6 |

- **TTFT** = prefill. Short prompts keep it small; long-context RAG is where it explodes.
- **TPOT** = per-output-token decode cost, bounded by memory bandwidth. `decode tok/s = 1000 / TPOT_p50`.
- `UD-Q2_K_XL` decodes **1.34x SLOWER** than `UD-Q4_K_XL` here, despite being 0.73 GB smaller. That is a real result, not a mistake: fewer bits only buys speed when decode is limited by memory bandwidth. On a machine that is compute-limited instead — few cores, no GPU offload — the extra dequantization work of a heavily-quantized format can cost more than the bytes it saves. Say which case yours is.

## Your observation

With the same prompt, `temperature=0`, and `max_tokens=120`, both quants returned
exactly three bullets and correctly covered TTFT, throughput, and queueing, but both
answered in English instead of the requested Vietnamese. Q4 was more concise (55 vs
90 output tokens); this spot-check found no clear factual degradation in Q2. Q2 is
still not worth using here: it saves 0.73 GB but decodes 1.34x slower.
