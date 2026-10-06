# 02 - Serve: load test + saturation reading

Host `Windows-AMD64` · llama.cpp `b10488` ·
`--parallel 4` · `ctx=2048` · `threads=2` ·
`ngl=99`

Load generation: 60 s per run · `LAB_LOAD_SHORT_TOKENS=8` ·
`LAB_LOAD_LONG_TOKENS=16`. These lower output caps were used consistently at both
user counts because the default 48/96-token workload produced too few completed
samples on this laptop.

| Users | Reqs | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|:--|--:|--:|--:|--:|--:|--:|--:|
| 10 | 16 | 0.34 | 26000 | 39000 | 39000 | 8.4 | 0.0% |
| 50 | 7 | 0.14 | 15000 | 49000 | 49000 | 4.0 | 0.0% |

*Estimated effective concurrency = completion RPS x average completed-request latency.
Little's Law is exact at steady state; this timed run ended with unfinished requests and
therefore underestimates it. A value above the slot count proves average queueing, but a
value below it does not rule out tail queueing. For true slot utilisation and queue depth,
use the server gauges from `make metrics`.*

## What these two runs say

| Going from 10 to 50 users | |
|:--|--:|
| Offered load | 5x |
| Throughput actually delivered | **0.41x** (8% of linear) |
| P95 latency | **1.26x** |
| Effective concurrency at 50 users | 4.0 vs `--parallel 4` slots (occupancy/slot ratio 1.00) |

**Saturated.** Throughput delivered only 0.41x for 5x the offered load, and estimated
occupancy (4.0) reaches the 4-slot capacity. The stronger corroborating evidence is
3.90/4 busy slots with 46 deferred requests.

Completion throughput **fell to 0.41x** while P95 grew 1.26x: overload made both
throughput and latency worse; it did not buy throughput with latency. At the chosen
40 s P95 SLO, the 10-user run passes and the 50-user run fails. Exact goodput cannot
be recovered from aggregate P95 alone without per-request counts at the threshold.

> **Small sample.** Only 7 requests completed in the
> shorter run, so these percentiles are indicative rather than solid. Note also that
> locust averages only *completed* requests: when the run ends with requests still
> queued, effective concurrency is an **under**-estimate. Trust the throughput-scaling
> row over the concurrency row here, and run longer (`-t 3m`) if you want firmer numbers.
> Only short requests completed before each 60 s cutoff; long-RAG requests still in
> flight are visible through the server's deferred-request gauge, not Locust's
> completed-request percentiles.

## Your reading

The server is saturated before 50 users: offered load rose 5x, but throughput fell
to 0.41x while P95 rose from 39 s to 49 s. The strongest evidence is 3.90/4 busy
decode slots plus 46 deferred requests; added latency is queueing, not extra per-request
compute. With a 40 s P95 SLO, the 10-user run is barely acceptable and the 50-user
run is not. I would test a higher `--parallel` first because the current four slots
are 98% occupied, then keep it only if goodput improves without memory pressure.
