# Reflection — Day 20 Lab (Personal Report)

> **Đây là báo cáo cá nhân.** Số liệu của bạn **không** so sánh được với bạn cùng lớp
> — chỉ so **before vs after trên chính máy bạn**. Rubric chấm độ rõ ràng của setup,
> đo lường và **lập luận**, không chấm tốc độ tuyệt đối.
>
> `make verify` sẽ fail nếu còn placeholder chưa điền. Đó là cố ý.

**Họ Tên:** Dinh Ngoc Duc
**MSSV:** 2A202602935
**Cohort:** K4-L3
**Ngày submit:** 2026-10-06

---

## 1. Hardware & runtime  *(rubric 1, 2 — 10 điểm)*

> Từ `make probe`. Paste output hoặc điền tay.

- **OS:** Windows 10 AMD64
- **CPU:** Intel Core i7-6820HQ @ 2.70 GHz
- **Cores:** 4 physical / 8 logical
- **CPU extensions:** AVX2
- **RAM:** 15.9 GB
- **Accelerator:** Vulkan1 Quadro M1000M selected for benchmarks; Intel HD 530 also available
- **llama.cpp asset đã tải:** `llama-b10488-bin-win-vulkan-x64.zip`
- **Model đã dùng:** Gemma 4 E2B (`LAB_MODEL=gemma4-e2b`)
- **Quantization:** UD-Q4_K_XL + UD-Q2_K_XL (từ `models/active.json`)

**Chạy ở đâu:** laptop của tôi
_(Nếu dùng cloud fallback: nói rõ vì sao — RAM < 8 GB, setup fail, v.v. Không mất điểm.)_

**Setup story** (≤ 80 chữ): điều gì cần thay đổi để lab chạy trên máy bạn? Có bước
nào fail rồi phải workaround không?

Windows PowerShell 5.1 không parse được dấu em dash trong `lab.ps1`, và Python mặc
định dùng CP1252 nên probe lỗi khi in Unicode. Tôi đổi ba dấu em dash sang ASCII và
đặt `PYTHONUTF8=1` trong hai runner. Driver chỉ hỗ trợ CUDA 12.0 nên setup tự chọn
binary Vulkan; không cần compile hay cloud fallback.

---

## 2. Đo lường  *(rubric 3, 4, 5 — 20 điểm)*

> Paste bảng từ `benchmarks/01-quickstart-results.md` (`make bench` tự sinh).

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95/P99 (ms) | TPOT P50/P95/P99 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|---|--:|--:|--:|--:|--:|--:|
| UD-Q4_K_XL | 2.97 | 10704 | 3124 / 5044 / 5044 | 70.2 / 71.2 / 71.2 | 7558 / 9412 / 9412 | 14.2 |
| UD-Q2_K_XL | 2.24 | 11802 | 4438 / 6080 / 6080 | 94.5 / 107.5 / 107.5 | 10338 / 12853 / 12853 | 10.6 |

**Quan sát** (≤ 60 chữ): 2-bit nhanh hơn bao nhiêu, và **có đáng không**? Bạn đã thử
hỏi cùng một câu trên cả hai (`make serve` vs `.venv/bin/python labs/02-serve/serve.py --compare`)
chưa? Chất lượng khác nhau thế nào?

Cùng prompt (`temperature=0`, `max_tokens=120`), hai quant đều trả đúng ba bullet và
nêu đúng TTFT/throughput/queueing, nhưng cùng trả tiếng Anh thay vì tiếng Việt. Q4
ngắn gọn hơn (55 so với 90 output token); spot-check không thấy Q2 sai factual rõ ràng.
Q2 vẫn không đáng dùng: chỉ tiết kiệm 0.73 GB nhưng decode chậm hơn 1.34x.

---

## 3. Serving under load  *(rubric 8, 9, 10 — 20 điểm)*

> Từ `benchmarks/02-server-results.md` (`make load-report`).

| Users | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|--:|--:|--:|--:|--:|--:|--:|
| 10 | 0.34 | 26000 | 39000 | 39000 | 8.4 | 0.0% |
| 50 | 0.14 | 15000 | 49000 | 49000 | 4.0 | 0.0% |

- **Offered load tăng 5×, throughput thực tăng:** 0.41× (thực tế giảm)
- **P95 tăng:** 1.26×
- **Effective concurrency ở 50 users:** 4.0 so với `--parallel` = 4 slots

**Peak `llamacpp:n_busy_slots_per_decode`** (từ `make metrics` khi `make load-50` đang
chạy): 3.90 / 4 slots

**Saturation reading** (≤ 80 chữ): server của bạn bão hoà ở đâu, và **bằng chứng nào**
thuyết phục bạn? Nếu P95 tăng nhanh hơn RPS thì phần latency thêm đó là queue time hay
compute time — bạn biết bằng cách nào? Nếu bạn phải nâng goodput@SLO, bạn sẽ đổi knob
nào **trước**, và vì sao knob đó?

Server bão hòa trước 50 users: offered load tăng 5x nhưng RPS giảm 0.34→0.14
(còn 0.41x), P95 tăng 39→49 s. Busy slots đạt 3.90/4 và 46 request deferred, chứng
minh queueing; Little's Law 4.0 còn bị thấp do request chưa xong. Với SLO P95 40 s,
10 users đạt còn 50 users trượt. Tôi sẽ thử tăng `--parallel`, chỉ giữ nếu goodput
tăng mà không gây áp lực KV/RAM.

Cả hai lượt chạy 60 s dùng cùng output cap 8/16 token để có thêm mẫu. Chỉ short
request hoàn tất trước cutoff; vì vậy tôi xem percentile là chỉ dấu, và ưu tiên gauge
server/deferred queue khi kết luận saturation.

---

## 4. Integration  *(rubric 12, 13 — 15 điểm)*

> Từ `make pipeline`. Nói thật cái nào real, cái nào stub — stub **không** mất điểm.

| Day | Piece | Real hay stub? |
|---|---|---|
| N16 Cloud/IaC | local only, no IaC | stub |
| N17 Data pipeline | in-memory `TOY_DOCS` | stub |
| N18 Lakehouse | no persisted lakehouse | stub |
| N19 Vector + features | keyword overlap, no vector index | stub |
| N20 Serving | `llama-server` | real |

**Latency split** (mean của 3 query, từ output của `pipeline.py`):

- embed: 0.0 ms
- retrieve: 0.2 ms
- llm: 14682.8 ms
- **stage chiếm nhiều nhất:** llm (100% của total)
- server breakdown: prefill 10245.1 ms; decode 1761.4 ms

**Reflection** (≤ 60 chữ): bottleneck ở đâu? Có khớp với kỳ vọng của bạn không? Nếu
phải giảm latency của pipeline này 2×, bạn sẽ tấn công vào đâu?

Bottleneck là LLM, gần 100% tổng latency; trong server, prefill 10.25 s lớn hơn decode
1.76 s. Điều này đúng kỳ vọng vì retrieval chỉ quét sáu document trong RAM. Muốn giảm
latency 2x, tôi sẽ rút prompt/context và tối ưu prefill trước; 0.2 ms retrieval không
thể thay đổi đáng kể tổng 14.68 s.

---

## 5. The single change that mattered most  *(rubric 11 — 10 điểm)*

> **Phần quan trọng nhất của report.** Không cần bonus track: `make tune` đã cho bạn
> một before/after thật (`benchmarks/01-tuning-tg128.md`). Đổi quantization,
> `LAB_N_CTX`, hay `--parallel` rồi đo lại cũng được.

**Change:** đổi quantization từ UD-Q2_K_XL sang UD-Q4_K_XL

```
before:  10.6 tok/s (UD-Q2_K_XL)
after:   14.2 tok/s (UD-Q4_K_XL)
speedup: 1.34×
```

**Tại sao nó work** (1–2 đoạn — đây là phần grader đọc kỹ nhất):

Kết quả này ngược với trực giác “ít bit hơn thì nhanh hơn”. Cả hai lượt chạy dùng cùng
10 prompt, `threads=4`, `ngl=99`, `ctx=2048` và Vulkan, nên khác biệt chính là format
quantization. Q2 giảm lượng byte phải đọc, nhưng kernel phải giải mã format nén mạnh
và xử lý scale/metadata phức tạp hơn. Trên backend Vulkan của Quadro M1000M, phần
dequantization/compute đó lớn hơn lợi ích giảm memory traffic, nên Q2 đạt 10.6 tok/s
trong khi Q4 đạt 14.2 tok/s.

Thread sweep củng cố cách đọc này: 1-8 CPU threads gần như phẳng 14.1-14.4 tok/s vì
`ngl=99` đã offload model sang Vulkan; 16 threads còn giảm xuống 13.0 tok/s do
oversubscription. Vì vậy đổi 4 xuống 2 thread chỉ khoảng 1.01x và không phải speedup
đáng kể; chọn đúng quantization mới là thay đổi có tác động thật trên máy này.

---

## 6. Bonus  *(optional — tối đa 10 điểm)*

> Bỏ trống nếu không làm. Xem `docs/bonus/README.md`. Đừng làm hết — **một** finding sâu
> ăn điểm hơn năm bảng nông.

**Đã làm:** B1 source-build comparison; B2 GPU offload sweep; B3 before/after;
B4 challenge C7 (instruction sets); B5 challenge C9 (embedding serving).

**Numbers:**

```
before:  11.2 tok/s (-ngl 0, CPU-only)
after:   14.3 tok/s (-ngl 99, 36/36 layers on Vulkan1)
speedup: 1.28×
```

**Điều này nói lên gì mà deck chưa nói:**

Full offload is best, but partial offload is much worse than both endpoints:
`-ngl 8..32` reaches only 4.4--6.6 tok/s. Partial placement splits each decode
step across CPU and Quadro, adding synchronization and PCIe hand-off overhead.
At `-ngl 99`, all 36 transformer layers use Vulkan1 (1481.9 MiB device buffer),
while 1804.0 MiB of tensors remain CPU-mapped. The boundary between transformer
layers disappears even though the whole GGUF does not fit in VRAM. Offload is
therefore a placement threshold on this machine, not a smooth per-layer speedup.

Hai finding phụ củng cố kết luận. Ở B1, prebuilt chọn đúng
`ggml-cpu-haswell.dll` và đạt 10.9 tok/s, còn GCC/MinGW `-march=native` chỉ đạt
6.8 tok/s: native build không mặc nhiên tốt hơn runtime dispatch. Ở C7,
`GGML_NATIVE=ON` chỉ hơn baseline AVX2 1.8% (6.769 so với 6.651 tok/s), nằm trong
độ lệch giữa các lần chạy vì cả hai đã dùng cùng ISA của CPU Haswell.

Ở C9, embedding batch 4 là knee: 0.428 text/s, nhanh hơn batch 1 3.50x trong khi
batch latency chỉ tăng 1.14x. Batch 8/16 giảm còn khoảng 0.28 text/s do 4 slot
phải xử lý thành nhiều wave. Embedding cần static batching theo độ dài; chat cần
continuous batching theo decode step, nên hai workload không nên dùng chung một
autoscaler. Demo dùng chat GGUF, không đại diện chất lượng của embedding model
chuyên dụng.

---

## 7. Điều làm bạn ngạc nhiên nhất  *(optional)*

Điều bất ngờ nhất là cả partial GPU offload lẫn native CPU build đều có thể chậm
hơn cấu hình tưởng như “kém tối ưu”. Tên knob không đảm bảo speedup; placement,
kernel/runtime dispatch và điểm bão hòa của scheduler mới quyết định kết quả.

---

## 8. Self-check trước khi push

- [x] `hardware.json` và `models/active.json` đã được stage cho final commit
- [x] Toàn bộ report base trong `benchmarks/` đã được stage
- [x] Hai CSV Locust 10/50 users và bằng chứng metrics/batching đã được stage
- [x] Mọi section **"required — replace this line"** trong `benchmarks/*.md` đã được thay
- [x] Đủ 5 screenshot trong `submission/screenshots/`, mỗi ảnh dưới 2 MB
- [x] `make verify` → **exit 0**
- [x] Repo đúng tên `K4-L3-DAY20-DinhNgocDuc-2A202602935-ModelServing`
- [x] Repo GitHub đang ở chế độ **public**
- [x] `models/*.gguf`, `runtime/`, `.venv/` và `.env` không nằm trong staging
- [x] Tạo final commit và push lên `origin/main`
- [ ] Paste public URL vào VinUni LMS trước deadline

**Quan trọng:** repo phải **public** đến khi điểm được công bố. Private → grader không
xem được → 0 điểm.

---

## 9. Khai báo sử dụng AI  *(xem `docs/RULES.md` §3)*

Tôi dùng OpenAI Codex để đọc rubric/code, chẩn đoán lỗi PowerShell 5.1 và UTF-8,
chạy lệnh benchmark, đối chiếu số liệu, và hỗ trợ soạn bản nháp diễn giải. Codex cũng
tự động capture/crop terminal thật và render nguyên hàng `Aggregated` từ CSV Locust
gốc thành screenshot dễ đọc. Mọi số liệu và nội dung ảnh đều đến từ output local hoặc
artifact gốc trên máy này; không dùng AI để bịa số liệu hay sinh ảnh giả.
