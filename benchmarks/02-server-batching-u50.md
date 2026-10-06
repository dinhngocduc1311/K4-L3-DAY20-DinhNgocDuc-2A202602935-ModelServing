# 02 - Continuous batching under load (u50)

Host `Windows-AMD64` · `--parallel 4` · 13 samples over
60s at 2.0s intervals · raw CSV: `02-server-metrics-u50.csv`

| Gauge | Peak observed |
|:--|--:|
| `n_busy_slots_per_decode` (avg/decode) | 3.90 of 4 slots (98%) |
| `requests_processing` | 4 |
| `requests_deferred` | 46 |
| `kv_cache_usage_ratio` | n/a — not exported by llama.cpp `b10488` |
| `tokens_predicted_total` (final) | 56 |

Highest sampled value was **3.90 of 4** slots. Note this gauge is llama.cpp's *average* busy slots per decode step, so the number below is the highest average we sampled, not an instantaneous maximum batch width. A peak near 1 means
requests were served one at a time -- either the load was too light to overlap, or
they arrived too far apart. A peak approaching `--parallel` means the scheduler was
genuinely packing concurrent requests into shared decode steps.
`requests_deferred` went above zero: more requests arrived than there were slots, so some waited. That wait is the queue time in your P95.

## Your observation

Peak `n_busy_slots_per_decode` was 3.90/4 (98%), matching the 50-user Little's Law
estimate of 4.0 active requests. I trust the server gauge for slot utilisation
because it measures decode directly; Little's Law includes queue time and, with
only 7 completed requests, undercounts work still queued when the test stopped.
The peak of 46 deferred requests is direct evidence that continuous batching was
full and excess load waited.
