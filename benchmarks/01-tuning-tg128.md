# 01 - Tune: thread-count sweep

Model `gemma-4-E2B-it-UD-Q4_K_XL.gguf` · host `Windows-AMD64` · llama.cpp `b10488`
CPU: **4 physical · 8 logical** cores · `ngl=99` · metric `tg128`

| threads (-t) | tg128 (tok/s) | vs best |
|:--|--:|--:|
| 1 | 14.1 | 98% |
| 2 | 14.4 | 100% |
| 4 | 14.3 | 100% |
| 8 | 14.2 | 99% |
| 16 | 13.0 | 90% |

**Best**: `-t 2` at 14.4 tok/s
**Slowest tested**: `-t 16` at 13.0 tok/s (1.11x spread)
**Against the physical-core default** (`-t 4`, 14.3 tok/s): 1.00x

Use this in your run:

```bash
LAB_N_THREADS=2 make bench
```

## Your explanation

The knee is at 2 threads, but 1-8 threads are effectively flat (14.1-14.4 tok/s).
This run used `ngl=99`, so Vulkan performs the model layers and CPU thread count is
not the main decode limiter. At 16 threads throughput drops to 13.0 tok/s: excess
CPU workers add scheduling and memory contention without adding GPU work. I use
2 threads because it is the measured peak, while treating its 1% gain over the
4-core default as noise-sized rather than a meaningful speedup.
