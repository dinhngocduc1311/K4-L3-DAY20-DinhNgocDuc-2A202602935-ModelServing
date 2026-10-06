# Bonus C9 - Embedding serving regime

Gemma 4 E2B UD-Q4_K_XL · llama.cpp `b10488` · Intel HD Graphics 530
(`Vulkan0`) · `threads=4` · 4 server slots · `ctx=512` · `batch=ubatch=512` ·
mean pooling · 1536 dimensions. The initial corpus/query request warmed the server
before the timed sweep.

| Static batch | Batch latency (ms) | Throughput (texts/s) | vs batch 1 |
|--:|--:|--:|--:|
| 1 | 8167.9 | 0.122 | 1.00x |
| 2 | 7159.7 | 0.279 | 2.28x |
| 4 | 9337.8 | 0.428 | 3.50x |
| 8 | 28236.7 | 0.283 | 2.31x |
| 16 | 57820.8 | 0.277 | 2.26x |

The endpoint returned 1536-dimensional vectors. The expected document ranked
first for the query with cosine similarity 0.845.

## Finding

Batch 4 is the knee: it raises throughput 3.50x while batch latency rises only
1.14x versus batch 1. The server log shows four embedding tasks released together.
At batch 8 and 16, four slots execute two and four waves, so latency grows to 28.2
and 57.8 seconds and throughput falls back to about 0.28 text/s. Embedding has one
prefill-only forward pass and no decode/KV-cache loop, so static, length-sorted
batches are appropriate. Chat instead needs continuous batching so independent
requests can join and leave on each decode step. They should not share one
autoscaler: embedding scales on queued texts/batch fill, chat on active sequences,
TTFT and decode-token backlog.

This experiment reuses a chat GGUF only to avoid another download. Its high
similarities for unrelated documents show that it is not a production sentence
encoder; retrieval should use a dedicated model such as Qwen3-Embedding or BGE-M3.
