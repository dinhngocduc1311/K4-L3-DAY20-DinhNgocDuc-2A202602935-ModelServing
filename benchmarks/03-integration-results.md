# 03 - Integrate: RAG pipeline run

Host `Windows-AMD64` · llama.cpp `b10488` ·
retrieval backend: **keyword overlap** · 3 queries

| Query | Contexts retrieved | embed (ms) | retrieve (ms) | llm (ms) | total (ms) |
|:--|--:|--:|--:|--:|--:|
| Why is goodput more useful than raw throughp... | goodput, paged, radix | 0.0 | 0.2 | 16396.9 | 16397.1 |
| What problem does PagedAttention actually so... | paged, radix, disagg | 0.0 | 0.2 | 13794.5 | 13794.9 |
| When does splitting prefill and decode help?... | disagg, radix, batching | 0.0 | 0.2 | 13856.9 | 13857.2 |

## Retrieved contexts

**Why is goodput more useful than raw throughput?**

- `[goodput]` score=1.0000: Goodput@SLO counts only the requests per second that met the TTFT and TPOT targets. Throughput at saturation ignores SLOs.
- `[paged]` score=0.0000: PagedAttention stores the KV cache in non-contiguous pages, removing the internal fragmentation that wasted most GPU memory.
- `[radix]` score=0.0000: RadixAttention keys cached KV by token prefix in a trie, so a shared prefix lets the engine skip prefill entirely.

**What problem does PagedAttention actually solve?**

- `[paged]` score=1.0000: PagedAttention stores the KV cache in non-contiguous pages, removing the internal fragmentation that wasted most GPU memory.
- `[radix]` score=0.0000: RadixAttention keys cached KV by token prefix in a trie, so a shared prefix lets the engine skip prefill entirely.
- `[disagg]` score=0.0000: Disaggregated serving splits prefill and decode onto separate pools because prefill is compute-bound and decode is memory-bandwidth-bound.

**When does splitting prefill and decode help?**

- `[disagg]` score=2.0000: Disaggregated serving splits prefill and decode onto separate pools because prefill is compute-bound and decode is memory-bandwidth-bound.
- `[radix]` score=1.0000: RadixAttention keys cached KV by token prefix in a trie, so a shared prefix lets the engine skip prefill entirely.
- `[batching]` score=1.0000: Continuous batching lets requests join and leave the running batch each decode step instead of waiting for a full batch.

Mean per stage (ms): embed **0.0** · retrieve **0.2** ·
llm **14682.8** · total **14683.1**
Dominant stage: **llm** (100% of total)
Mean server timing (ms): prefill **10245.1** · decode **1761.4**

## Answers returned

**Why is goodput more useful than raw throughput?**

> Goodput@SLO counts only the requests per second that met the TTFT and TPOT targets. Throughput at saturation ignores SLOs.

**What problem does PagedAttention actually solve?**

> PagedAttention stores the KV cache in non-contiguous pages, removing the internal fragmentation that wasted most GPU memory.

**When does splitting prefill and decode help?**

> Splitting prefill and decode helps because prefill is compute-bound and decode is memory-bandwidth-bound.


## Which N16-N19 pieces are real

- N16 Cloud/IaC: stubbed; this run is local and has no cloud provisioning.
- N17 Data pipeline: stubbed; the six documents are an in-memory constant.
- N18 Lakehouse: stubbed; there is no persisted lakehouse in this demo.
- N19 Vector + features: stubbed; retrieval uses keyword overlap, not embeddings.
- N20 Serving: real `llama-server` through `/v1/chat/completions`.

The LLM stage dominates at 14,682.8 ms, essentially 100% of the 14,683.1 ms total;
embed is 0 ms and retrieval averages 0.2 ms. Within the server timing, prefill averages
10,245.1 ms versus 1,761.4 ms for decode. To halve end-to-end latency I would reduce
prompt/prefill cost first; optimizing the 0.2 ms retriever cannot materially help.
