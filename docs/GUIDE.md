# GUIDE — Làm lab Day 20 từ đầu đến cuối

> **Bài cá nhân** — mỗi học viên tự làm và tự nộp repo riêng. Checkpoint tóm tắt:
> [docs/CHECKPOINTS.md](CHECKPOINTS.md) · Cách nộp: [docs/SUBMISSION.md](SUBMISSION.md) ·
> Quy định: [docs/RULES.md](RULES.md)

Làm lần lượt theo hướng dẫn này. Mỗi bước cho biết **lệnh cần chạy**, **kết quả bạn sẽ
thấy** và **file được sinh ra**. Các file đó là bằng chứng để chấm điểm.

**Tổng thời gian:** ~2.5 giờ cho base track · +1–2 giờ nếu làm bonus.

> ### 🪟 Windows: đọc phần này trước
> Windows không có `make`. Khi hướng dẫn ghi `make <target>`, hãy dùng
> **`.\lab.ps1 <target>`** với cùng tên target.
>
> ```powershell
> powershell -ExecutionPolicy Bypass -File labs/00-setup/bootstrap.ps1   # chỉ chạy 1 lần
> .\lab.ps1                 # xem toàn bộ target
> .\lab.ps1 bench           # tương đương make bench
> ```

> ### 🐍 Về các lệnh `python` trong tài liệu
> Lab **không** dùng `python` toàn cục — mọi thứ chạy trong virtualenv mà `make setup`
> tạo ra. Vì vậy tài liệu luôn ghi đường dẫn đầy đủ:
>
> | OS | Dùng |
> |---|---|
> | macOS / Linux | `.venv/bin/python labs/...` |
> | Windows | `.venv\Scripts\python labs\...` |
>
> Trên macOS/Linux, gõ `python` trần thường báo `command not found` (chỉ có `python3`),
> và kể cả `python3` cũng thiếu package của lab. Luôn dùng `.venv/bin/python`.

```
PHASE 0  Setup                 ~20 phút
PHASE 1  Base track (100 điểm)  ~2 giờ      ← bắt buộc
PHASE 2  Bonus track (≤10 điểm) ~1-2 giờ    ← optional, chỉ làm SAU khi xong base
PHASE 3  Submit                 ~5 phút
```

> **Quy tắc quan trọng:** mỗi file `benchmarks/*.md` do lab sinh ra đều có section
> **"required -- replace this line"**. Bạn **phải** thay section đó bằng nhận xét của
> mình. Nếu còn sót, `make verify` sẽ fail. Số liệu chỉ là đầu vào; phần nhận xét mới là
> nội dung được chấm.

---

# PHASE 0 — Setup

## Bước 0.1 — Kiểm tra máy

```bash
make probe
```

Bạn sẽ thấy thông tin về CPU, số core, RAM, accelerator và model dùng trong lab.

**Chọn cách chạy ngay ở bước này:**

| RAM | Cách làm |
|---|---|
| **≥ 8 GB** | Tiếp tục bước 0.2 và 0.3 trên laptop |
| **4–8 GB** | Vẫn chạy local, chỉ đổi model: `LAB_MODEL=qwen35-0.8b make setup` (xem bước 0.2). **Không mất điểm.** |
| **< 4 GB** | Mở [`docs/CLOUD.md`](CLOUD.md) và làm trên Colab/Kaggle. **Không mất điểm.** |

→ Sinh ra: **`hardware.json`** *(rubric 1)*

→ **Chụp screenshot ngay:** `submission/screenshots/01-hardware-probe.png`

## Bước 0.2 — Chọn model

Lab có **hai** option. Cả hai Apache-2.0, **không gated** (không token, không accept license).
Chọn một, làm hết lab với nó.

| | **Gemma 4 E2B** *(mặc định)* | **Qwen3.5 0.8B** *(nhỏ, nhanh)* |
|---|---|---|
| Repo | [unsloth/gemma-4-E2B-it-GGUF](https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF) | [unsloth/Qwen3.5-0.8B-GGUF](https://huggingface.co/unsloth/Qwen3.5-0.8B-GGUF) |
| Tải về | ~5.2 GB | **~0.9 GB** |
| RAM tối thiểu | 8 GB | **4 GB** |
| Model load | ~6 s | **~3 s** |
| Decode (M1, Metal) | ~27 tok/s | **~42 tok/s** |
| Chất lượng câu trả lời | tốt hơn | thấp hơn (0.8B là 0.8B) |
| Bonus C1 (MTP spec-decode) | có MTP head | không có |

**Chọn thế nào:**

- **RAM ≥ 8 GB, muốn câu trả lời tử tế** → Gemma 4 E2B. Không cần làm gì, đây là mặc định.
- **RAM 4–8 GB, hoặc muốn chạy nhanh gấp 5 lần** → Qwen3.5 0.8B:

  ```bash
  export LAB_MODEL=qwen35-0.8b      # macOS / Linux
  $env:LAB_MODEL = 'qwen35-0.8b'    # Windows PowerShell
  ```

  Set **trước** khi chạy `make setup`. Sau đó `models/active.json` ghi lại lựa chọn, nên
  các bước sau tự dùng đúng model — bạn không cần export lại mỗi lần.

**Rubric không quan tâm bạn chọn model nào.** Cả hai đều cho đủ TTFT/TPOT/percentile,
load test, batching và tuning story. Model nhỏ thậm chí làm phần load test dễ đọc hơn vì
mỗi request xong nhanh hơn nên bạn thu được nhiều mẫu hơn trong 60 s.

### File sẽ được tải

| Vai trò | Gemma 4 E2B | Qwen3.5 0.8B |
|---|---|---|
| primary | `gemma-4-E2B-it-UD-Q4_K_XL.gguf` (2.97 GB) [tải](https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF/resolve/main/gemma-4-E2B-it-UD-Q4_K_XL.gguf) | `Qwen3.5-0.8B-Q4_K_M.gguf` (0.50 GB) [tải](https://huggingface.co/unsloth/Qwen3.5-0.8B-GGUF/resolve/main/Qwen3.5-0.8B-Q4_K_M.gguf) |
| compare | `gemma-4-E2B-it-UD-Q2_K_XL.gguf` (2.24 GB) [tải](https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF/resolve/main/gemma-4-E2B-it-UD-Q2_K_XL.gguf) | `Qwen3.5-0.8B-UD-Q2_K_XL.gguf` (0.39 GB) [tải](https://huggingface.co/unsloth/Qwen3.5-0.8B-GGUF/resolve/main/Qwen3.5-0.8B-UD-Q2_K_XL.gguf) |
| bonus C1 | `mtp-gemma-4-E2B-it.gguf` (0.09 GB) [tải](https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF/resolve/main/mtp-gemma-4-E2B-it.gguf) | — |

**Bước 0.3 (`make setup`) tự tải hai file đầu.** Bảng trên để bạn biết mình đang tải gì, và
để dùng khi mạng trường chặn Hugging Face. Nếu tải tự động fail, script in ra đúng lệnh
`curl` cần chạy — chi tiết trong
[`docs/MANUAL-DOWNLOAD.md`](MANUAL-DOWNLOAD.md).

---

## Bước 0.3 — Cài đặt

```bash
make setup
```

Bước này mất khoảng 5–15 phút và thực hiện ba việc:

- Tạo `.venv` và cài 4 package Python.
- Tải **llama.cpp prebuilt binary** (10–35 MB, **không compile**).
- Tải **Gemma 4 E2B** với 2 quantization (~5.2 GB).

Trên Windows, bạn có thể chạy target tương ứng:

```powershell
.\lab.ps1 setup
```

Hoặc chạy bootstrap trực tiếp:

```powershell
pwsh -ExecutionPolicy Bypass -File labs/00-setup/bootstrap.ps1
```

→ Sinh ra: **`models/active.json`** *(rubric 2)*, `runtime/`, `models/*.gguf`

Nếu tải model fail do mạng trường chặn Hugging Face, xem
[`docs/MANUAL-DOWNLOAD.md`](MANUAL-DOWNLOAD.md).

---

# PHASE 1 — Base track (100 điểm)

## Bước 1.1 — Đo baseline: TTFT / TPOT / percentiles

Baseline trả lời hai câu hỏi khác nhau:

- **TTFT** (*time to first token*) là thời gian phía client từ lúc gửi request đến token
  đầu tiên. Nó gồm overhead HTTP/queue và prefill; trong benchmark cô lập này, prefill
  thường chi phối. Prompt RAG dài làm TTFT tăng mạnh.
- **TPOT** (*time per output token*) là thời gian trung bình cho mỗi token sau token
  đầu. Decode thường bị giới hạn bởi memory bandwidth vì mỗi bước phải đọc lại weights.
  Quant nhỏ hơn di chuyển ít byte hơn, nhưng chỉ nhanh hơn nếu phần tiết kiệm bandwidth
  lớn hơn chi phí dequantization.

Đóng ứng dụng nặng trước khi đo, rồi chạy đúng lệnh của hệ điều hành:

```bash
# macOS / Linux
make bench
```

```powershell
# Windows PowerShell
.\lab.ps1 bench
```

Script dùng port riêng `8099`, tự bật `llama-server`, bỏ một request warm-up, stream
10 prompt qua `/v1/chat/completions`, rồi tắt server. Toàn bộ quy trình được lặp lại
với quantization thứ hai; bạn không cần tự quản lý server ở bước này.

→ Sinh ra **`benchmarks/01-quickstart-results.md`** với hai quantization và các cột:
Load, TTFT P50/P95/P99, TPOT P50/P95/P99, E2E P50/P95/P99, Decode tok/s.

TTFT đo phía client. Số output token lấy từ block `timings` của llama.cpp, nên TPOT
không được suy đoán từ số chunk SSE. Percentile dùng nearest-rank: với 10 mẫu, P50 là
mẫu nhỏ thứ 5; P95 và P99 đều là mẫu thứ 10. Vì vậy P99 đáp ứng rubric nhưng vẫn là
tail estimate mỏng — nếu cần kết luận chắc hơn, tăng số mẫu thay vì nội suy.

→ **Chụp screenshot:** `submission/screenshots/02-bench.png`

### So sánh chất lượng hai quantization

Hỏi cùng một câu với cùng tham số sampling. Tắt server cũ bằng Ctrl-C trước khi đổi
quantization, hoặc chạy bản 2-bit ở port `8090`:

```bash
# macOS / Linux
make serve                                              # Q4; stop with Ctrl-C
.venv/bin/python labs/02-serve/serve.py --compare --port 8090  # Q2
```

```powershell
# Windows PowerShell
.\lab.ps1 serve                                         # Q4; stop with Ctrl-C
.\lab.ps1 serve --compare --port 8090                   # Q2
```

Gửi cùng prompt bằng UI/API của server; nếu dùng `smoke-test.py` cho bản Q2, đặt
`LAB_SERVER_PORT=8090` trong terminal gọi client rồi xóa biến sau khi so sánh.

Cuối cùng, thay section **"Your observation"** trong report bằng ba kết luận có số:
2-bit nhanh/chậm hơn bao nhiêu, nhỏ hơn bao nhiêu GB, và có đáng dùng không sau khi
so chất lượng. Nếu 2-bit chậm hơn, giữ nguyên kết quả và giải thích compute/dequantization
so với memory bandwidth; không sửa tay số liệu.

> Lần chạy đầu có thể chậm hơn vì page cache hệ điều hành còn lạnh. Hãy ghi rõ bạn báo
> lần chạy nào và chỉ so hai quantization trong cùng điều kiện.

## Bước 1.2 — Tune thread count cho máy của bạn

Trên CPU, decode thường bị giới hạn bởi băng thông bộ nhớ: tăng thread chỉ giúp tới
**knee**, sau đó các thread cùng tranh memory channel, cache và thời gian scheduling.
Knee thường gần số core physical; hyperthread chia sẻ tài nguyên nên không mặc định
nhanh hơn. Tuy nhiên, nếu report ghi `ngl > 0`, nhiều layer đang chạy trên accelerator
và đường thread CPU có thể gần như phẳng — đó là kết quả hợp lệ, không phải lỗi.

Script chạy `llama-bench` với `tg128`, 2 lần cho mỗi điểm: 1, nửa số core physical,
số core physical, số core logical và gấp đôi logical (khi máy có ít nhất 8 logical
core). Các điểm trùng được bỏ tự động.

**macOS / Linux:**

```bash
make tune
```

**Windows:**

```powershell
.\lab.ps1 tune
```

Mở **`benchmarks/01-tuning-tg128.md`** và đọc `Best`, `Slowest tested`,
`Against the physical-core default` cùng cột `vs best`. Đây là nguồn cho
**REFLECTION §5** và rubric 11.

**Đo lại baseline với thread tốt nhất** (thay `<N>` bằng giá trị ở dòng `Best`):

```bash
# macOS / Linux
LAB_N_THREADS=<N> make bench
```

```powershell
# Windows
$env:LAB_N_THREADS = '<N>'
.\lab.ps1 bench
Remove-Item Env:LAB_N_THREADS
```

Muốn tune prefill thay vì decode:

```bash
# macOS / Linux
.venv/bin/python labs/01-measure/tune.py --metric pp512
```

```powershell
# Windows
.\lab.ps1 tune --metric pp512
```

→ Screenshot optional: `06-tune.png`

**Bạn cần làm:** xác định knee và giải thích bằng cơ chế đo được. Nếu curve phẳng, kiểm
tra `ngl` trước khi kết luận: có thể accelerator đang làm phần lớn công việc, hoặc CPU
đã chạm trần bandwidth từ ít thread. Nếu logical core vẫn tăng, báo đúng kết quả và
liên hệ backend/workload; nếu VM chỉ có 1 physical core, ghi rõ giới hạn của VM. Một
speedup nhỏ nhưng được giải thích bằng bandwidth, cache, vector width hoặc scheduling
có giá trị hơn một speedup lớn chỉ được mô tả là “nhanh hơn”.

## Bước 1.3 — Dựng server và chứng minh server hoạt động

> 📖 Đọc [`docs/labs/02-serve.md`](labs/02-serve.md) trước: continuous batching,
> cách đọc queue time vs compute time bằng Little's Law, và thí nghiệm đáng giá nhất của
> lab (`--parallel 1` so với `--parallel 4`). REFLECTION §3 chấm phần này.

`serve` chạy một `llama-server` lâu dài với API OpenAI-compatible, `--parallel 4`,
`--cont-batching`, `--metrics` và `--reasoning off`. Bốn slot cho phép tối đa bốn
request cùng được scheduler xử lý; continuous batching cho phép request vào hoặc rời
batch giữa các bước decode. Smoke chỉ chứng minh API và metrics hoạt động — bằng chứng
continuous batching cần `make metrics` chạy đồng thời với load ở bước sau.

Context mặc định `2048` là ngân sách tổng của server. Với 4 slot, log runtime b10488
ghi `n_ctx_slot = 512`; tăng `--parallel` mà giữ nguyên context sẽ làm context khả dụng
trên mỗi slot nhỏ đi. `--reasoning off` giúp Gemma 4 trả nội dung nhìn thấy được trong
ngân sách token ngắn thay vì dành hết token cho thinking.

| Endpoint | Dùng để |
|---|---|
| `POST /v1/chat/completions` | Gọi model theo chuẩn OpenAI |
| `GET /metrics` | Đọc counter và gauge Prometheus |
| `GET /slots` | Xem trạng thái từng slot |
| `GET /health` | Kiểm tra server sẵn sàng |

Bạn cần **2 terminal** và phải để terminal 1 chạy.

**Terminal 1** — giữ server chạy:

```bash
# macOS / Linux
make serve
```

```powershell
# Windows
.\lab.ps1 serve
```

**Terminal 2** — chạy smoke test:

```bash
# macOS / Linux
make smoke
```

```powershell
# Windows
.\lab.ps1 smoke
```

Smoke đọc metrics trước request, gửi một completion, in server timings, rồi đọc lại
metrics và in delta `(+N)`. Phần `prompt ...` là thời gian prefill phía server và
`decode ...` là thời gian sinh token phía server. Chúng giúp giải thích TTFT/TPOT nhưng
không bằng số client-side ở baseline vì không gồm network, queue và toàn bộ overhead
phía client.

| Metric | Ý nghĩa |
|---|---|
| `llamacpp:tokens_predicted_total` | Tổng token đã sinh; rubric 7 cần khác 0 |
| `llamacpp:prompt_tokens_total` | Tổng token prompt đã prefill |
| `llamacpp:n_decode_total` | Tổng số lần backend chạy decode |
| `llamacpp:requests_processing` | Request đang xử lý tại thời điểm scrape |

Kết quả đạt checkpoint khi kết thúc bằng:

```text
OK -- served a completion and tokens_predicted_total is ... (non-zero).
```

→ *(rubric 6, 7)*

→ **Chụp screenshot:** `03-serve-and-smoke.png`. Ảnh phải có **cả** server đang listen
và output của `make smoke`. Bạn có thể chia đôi terminal hoặc chụp hai file `03a-` /
`03b-`.

Nếu port 8080 bị chiếm, đặt cùng biến trong **cả hai terminal**:

```bash
# macOS / Linux
export LAB_SERVER_PORT=8090
```

```powershell
# Windows
$env:LAB_SERVER_PORT = '8090'
```

Mọi tham số sau `--` được chuyển thẳng cho `llama-server`, ví dụ:

```bash
# macOS / Linux
.venv/bin/python labs/02-serve/serve.py -- --ctx-size 4096
```

```powershell
# Windows
.\lab.ps1 serve -- --ctx-size 4096
```

Context lớn hơn làm KV cache và RAM/RSS tăng. Không cần đổi knob để lấy điểm base.

## Bước 1.4 — Load test

Locust phát request theo tỷ lệ 80% chat ngắn (`max_tokens=48`) và 20% RAG dài
(`max_tokens=96`), với 0,2–1,5 giây nghỉ giữa hai request của mỗi user ảo. Đây là tỷ lệ
request được **phát**, không nhất thiết là tỷ lệ request hoàn thành: tại cutoff 60 giây,
request dài còn chờ hoặc đang chạy sẽ chưa xuất hiện trong percentile hoàn thành.

Gauge chứng minh batching là `llamacpp:n_busy_slots_per_decode`: số slot bận trung bình
trên mỗi lần decode. Giá trị tăng rõ ràng trên 1 và tiến gần `--parallel 4` cho thấy
scheduler đang đưa nhiều request vào các bước decode chung. `requests_deferred > 0`
cho thấy request phải đợi slot. Continuous batching tạo khả năng tăng throughput khi
request chồng lấp; nó không bảo đảm throughput tiếp tục tăng sau điểm bão hòa.

Giữ server ở terminal 1. Tại terminal 2, chạy 10 user trong 60 giây:

```bash
# macOS / Linux
make load-10       # 10 users, 60s
```

```powershell
# Windows
.\lab.ps1 load-10
```

→ **Chụp screenshot:** `04-locust-10.png`. Ảnh phải thấy dòng có
`# reqs · Median · 95%ile · 99%ile`.

Tiếp theo cần **3 terminal chạy chồng thời gian**:

| Terminal | Vai trò | Lệnh |
|---|---|---|
| 1 | Server giữ nguyên | `serve` |
| 2 | Phát tải 50 user | `load-50` |
| 3 | Scrape `/metrics` mỗi 2 giây | `metrics` |

```bash
# macOS / Linux — terminal 2
make load-50

# terminal 3, chạy ngay khi load-50 đang chạy
make metrics
```

```powershell
# Windows — terminal 2
.\lab.ps1 load-50

# terminal 3, chạy ngay khi load-50 đang chạy
.\lab.ps1 metrics
```

> ⚠️ **Lỗi phổ biến nhất của lab:** chạy `make metrics` khi server đang rảnh. Khi đó,
> `n_busy_slots_per_decode` sẽ ≈ 1 và không chứng minh được continuous batching.
> `make metrics` **phải chạy chồng thời gian với `make load-50`**.

→ **Chụp screenshot:** `05-locust-50.png`

Hai load test sinh `benchmarks/locust-10_stats.csv` và `locust-50_stats.csv` (rubric 8).
Metrics sinh **`benchmarks/02-server-batching-u50.md`** và
`02-server-metrics-u50.csv` (rubric 9).

Report dùng peak của các mẫu trong 60 giây. `n_busy_slots_per_decode` bản thân là số
trung bình trên các bước decode, nên peak report là **giá trị trung bình cao nhất được
lấy mẫu**, không phải batch width tức thời lớn nhất. Peak gần 1 nghĩa là tải chưa đủ
chồng lấp; peak tiến gần 4 là bằng chứng nhiều slot được decode cùng nhau. Nếu
`kv_cache_usage_ratio` là `n/a`, build hiện tại không xuất metric đó — không đổi thành 0.

Nếu quá ít request hoàn thành, có thể đặt `LAB_LOAD_DURATION=3m` hoặc hạ output cap.
Phải dùng cùng duration và cap cho cả 10 và 50 user, rồi ghi rõ trong
report/Reflection. Ví dụ Windows:

```powershell
$env:LAB_LOAD_DURATION = '3m'       # tùy chọn; mặc định 1m
$env:LAB_LOAD_SHORT_TOKENS = '8'
$env:LAB_LOAD_LONG_TOKENS = '16'
.\lab.ps1 load-10
# giữ nguyên các biến trên khi chạy load-50
```

Sau khi chạy, mở `benchmarks/02-server-batching-u50.md` và thay phần
`Your observation`: nêu peak busy slots, so với effective concurrency, giải thích
`requests_deferred`, và nói metric nào đáng tin hơn khi số request hoàn thành còn ít.

## Bước 1.5 — Xác định điểm saturation của server

Little's Law viết `L = λ × W`: số request trung bình trong hệ thống bằng arrival rate
nhân thời gian trung bình trong hệ thống. Report ước lượng **effective concurrency**
bằng completion RPS × latency trung bình của request đã hoàn thành. Ước lượng này chính
xác khi hệ thống gần steady state; nếu test dừng khi còn request trong queue, nó sẽ thấp
hơn thực tế.

| Effective concurrency | Kết luận an toàn |
|---|---|
| `> slots` | Trung bình có request phải xếp hàng |
| `≤ slots` | Chưa chứng minh có queue trung bình; vẫn có thể có queue ở tail |

Đây là occupancy của toàn hệ thống, không phải slot utilisation. Đọc busy slots và
`requests_deferred` từ `/metrics` để xác nhận compute slots có kín và queue có tồn tại.

Sau khi có cả hai CSV, chạy:

```bash
# macOS / Linux
make load-report
```

```powershell
# Windows
.\lab.ps1 load-report
```

→ Sinh ra: **`benchmarks/02-server-results.md`** *(rubric 10)*

Script dùng hai tín hiệu: throughput đạt dưới 50% mức tuyến tính được xem là phẳng;
effective concurrency đạt ít nhất 85% số slot được xem là chạm capacity.

| Throughput phẳng? | Occupancy ≥ 85% slot? | Kết luận |
|---|---|---|
| Có | Có | **Saturated** — kiểm tra deferred để xác nhận queue |
| Có | Không | **Saturated** bởi bandwidth, KV/context hoặc tài nguyên khác |
| Không | Có | **At capacity, still scaling** — đang ở knee |
| Không | Không | **Not saturated** — tăng tải để tìm knee |

Mở report, đọc bảng `Going from 10 to 50 users` và cảnh báo `Small sample`. Nếu dưới
20 request hoàn thành, ưu tiên throughput scaling và gauge server hơn effective
concurrency. Không kết luận queue chỉ từ việc P95 tăng: bằng chứng queue trực tiếp là
`requests_deferred > 0`; P95 tăng cho biết tác động mà người dùng chịu.

**Throughput** đếm mọi completion mỗi giây. **Goodput@SLO** chỉ đếm completion đạt
ngưỡng latency đã chọn. P95 dưới SLO cho biết ít nhất khoảng 95% mẫu hoàn thành đạt
ngưỡng; P95 trên SLO chỉ cho biết mục tiêu 95% bị trượt, không cho biết chính xác bao
nhiêu request đạt. Muốn goodput chính xác cần count latency từng request, nên không suy
ra một con số giả từ một percentile tổng hợp.

Thay `Your reading`: nêu RPS ratio, P95 ratio, effective concurrency/slot, bằng chứng
busy/deferred, SLO tự chọn và knob thử đầu tiên. Thử `--parallel 1` so với 4 thì phải
restart server và đặt cùng `LAB_PARALLEL` trong terminal chạy `load-report`; nếu không,
report sẽ so với sai số slot.

## Bước 1.6 — Chạy RAG pipeline

Pipeline chạy ba câu hỏi theo luồng:

```text
query → optional embed → retrieve top-k → ghép prompt → llama-server → answer
```

Mặc định không có embedding server: `TOY_DOCS` là corpus trong RAM, `retrieve()` dùng
keyword overlap và embed báo `0.0 ms`. Đây là stub hợp lệ. Prompt assembly rất nhỏ và
nằm trong `total`, không được báo thành một stage riêng. N20 serving là thật vì request
đi qua `/v1/chat/completions`.

Giữ server chạy. Tại terminal 2:

```bash
# macOS / Linux
make pipeline
```

```powershell
# Windows
.\lab.ps1 pipeline
```

Mỗi query in `contexts`, `timings`, server prefill/decode và `answer`. Cuối cùng script
in mean theo stage, dominant stage và mean server timing. Server timing tách phần LLM
thành prefill/decode; còn `llm` phía client bao gồm queue, HTTP và server compute.

→ Sinh ra: **`benchmarks/03-integration-results.md`** và `.json` *(rubric 12, 13)*.
Screenshot `08-pipeline.png` là tùy chọn.

Thay phần `Which N16-N19 pieces are real`: khai báo riêng N16, N17, N18, N19 là real
hay stub, nêu dominant stage, rồi chọn stage cần xử lý nếu phải giảm latency 2×. Dùng
stub không mất điểm; khai sai mới mất điểm. Với kết quả hiện tại, N16 local, N17/N18
in-memory và N19 keyword overlap đều là stub; chỉ N20 `llama-server` là real.

Embedding thật là tùy chọn và cần server thứ hai:

```bash
# macOS / Linux — terminal riêng
make serve-embed
# terminal chạy pipeline
.venv/bin/python labs/03-integrate/pipeline.py --embed-url http://localhost:8081
```

```powershell
# Windows — terminal riêng
.\lab.ps1 serve-embed
# terminal chạy pipeline
.\lab.ps1 pipeline --embed-url http://localhost:8081
```

Khi đã truyền `--embed-url`, endpoint lỗi sẽ làm pipeline dừng thay vì âm thầm đổi về
keyword overlap. Điều này ngăn report vô tình khai retrieval thật khi embedder không chạy.

**Context budget:** `ctx=2048` được chia cho 4 slot thành khoảng 512 token/slot trên
runtime hiện tại. Prompt RAG, output và template phải cùng nằm trong ngân sách đó. Khi
nối corpus thật, dùng `POST /tokenize` của chính llama.cpp để đếm token; không dùng
`tiktoken` rồi giả định tokenizer giống OpenAI.

**Prompt caching:** system prompt giống hệt từng byte tạo prefix có thể tái sử dụng,
nhưng không tự nó chứng minh cache hit. `prompt_tokens_total` là counter tích lũy và
không đủ để kết luận. Muốn kiểm chứng, giữ server rảnh, tốt nhất dùng một slot, gọi lặp
đúng cùng prompt rồi đổi một byte; so `prompt_ms` và log LCP/cache giữa hai trường hợp.

Checkpoint: cả ba query có context và answer, report/JSON có mean embed/retrieve/llm,
dominant stage, server prefill/decode, và khai báo real/stub khớp code. Chép các mean
này sang REFLECTION §4.

## Bước 1.7 — Viết REFLECTION.md

Mở [`submission/REFLECTION.md`](../submission/REFLECTION.md) và điền đủ mọi section. Đây
là file grader đọc kỹ nhất.

| Section | Phải có | Nguồn |
|---|---|---|
| §1 Hardware & runtime | CPU/core/RAM/backend/model và workaround thật | `hardware.json`, `models/active.json` |
| §2 Đo lường | Bảng hai quant, TTFT/TPOT/P50–P99 và nhận xét chất lượng | `01-quickstart-results.*` |
| §3 Serving | 10/50 users, busy slots, deferred, saturation và SLO | `02-server-*`, Locust CSV |
| §4 Integration | N16–N19 real/stub và latency từng stage | `03-integration-results.*` |
| §5 Thay đổi chính | before/after thật và giải thích cơ chế | report đo tương ứng |

Phần quan trọng nhất là §5. Speedup nhỏ được giải thích bằng bandwidth, cache,
dequantization, backend hay scheduling có giá trị hơn một tỷ lệ lớn không có cơ chế.
Không tái sử dụng số bonus cho §5; §6 dành riêng cho bonus.

Đối chiếu từng số trong REFLECTION với JSON/CSV/Markdown. `verify` phát hiện placeholder
và ô trống nhưng không thể biết bạn chép nhầm 14.2 thành 12.4. Nếu dùng AI để debug,
chạy lệnh hoặc hỗ trợ diễn giải, khai báo ngắn và đúng phạm vi ở §9; không dùng AI tạo
số liệu hay screenshot.

## Bước 1.8 — Kiểm tra base track

Đặt đủ năm ảnh thật vào `submission/screenshots/`:

1. `01-hardware-probe.png`
2. `02-bench.png`
3. `03-serve-and-smoke.png`
4. `04-locust-10.png`
5. `05-locust-50.png`

Stage ảnh để verifier nhìn thấy chúng. **Stage không phải commit**; bạn vẫn có thể làm
bonus rồi commit một lần cuối.

```bash
git add submission/screenshots/
make verify
```

```powershell
git add submission/screenshots/
.\lab.ps1 verify
```

Lệnh phải exit 0. Nếu fail, output liệt kê file thiếu, file chưa được Git track hoặc
placeholder còn sót. Sau đó tự kiểm tra tên repo, public visibility, số liệu chéo và
khai báo AI — những việc script không thể xác minh.

Không commit/push nếu bạn còn làm bonus. Khi `verify` đã exit 0, chuyển sang PHASE 2;
chỉ commit và push ở PHASE 3 sau khi bonus và `verify` cuối cùng đều xong.

**Base track hoàn tất tại đây. Bạn đã có đủ bằng chứng cho 100 điểm base.**

---

# PHASE 2 — Bonus track (tối đa 10 điểm, optional)

> **Chỉ bắt đầu khi PHASE 1 đã hoàn tất và `make verify` đã exit 0.** Bonus không bù
> được phần base còn thiếu.

Chi tiết: [`docs/bonus/README.md`](bonus/README.md) ·
[`docs/bonus/CHALLENGES.md`](bonus/CHALLENGES.md)

Chọn **1–2 mục**, không cần làm hết. Có 5 tiêu chí, mỗi tiêu chí 2 điểm (tối đa 10 điểm):

| | Lệnh | Ghi chú |
|---|---|---|
| **B1** | `make build-llama && make compare-builds` | Compile cho CPU của bạn rồi so với prebuilt binary. **Máy yếu thường có mức cải thiện rõ nhất ở đây.** Cần `cmake`. |
| **B2** | `make sweep-quant` / `sweep-ctx` / `sweep-batch` / `sweep-gpu` | Chọn 1 sweep phù hợp với bottleneck của bạn |
| **B3** | — | Ghi before/after của B1 hoặc B2 vào REFLECTION §6 |
| **B4** | — | Chọn 1 challenge C1–C7 trong `docs/bonus/CHALLENGES.md` |
| **B5** | `make mlx-compare` (Mac) **hoặc** `make semantic-cache` (C8) **hoặc** `make serve-embed && make embed-demo` (C9) **hoặc** C6 | 4 lựa chọn; nền tảng nào cũng có lựa chọn phù hợp |

Gợi ý theo máy và mục tiêu:

- **CPU-only** → B1 (`compare-builds`). Đây thường là speedup lớn nhất trong lab.
- **RAM hạn chế** → `make sweep-quant`.
- **Có GPU** → `make sweep-gpu`.
- **Quan tâm RAG long-context** → `make sweep-ctx`.
- **Không muốn tải thêm** → C8 hoặc C9, có thể chạy với `--offline`.

Mỗi bonus script cũng sinh file `benchmarks/bonus-*.md` có section
*"required -- replace this line"*. Bạn vẫn phải điền section này.

---

# PHASE 3 — Submit

> Chi tiết đầy đủ (cấu trúc file, checklist): **[docs/SUBMISSION.md](SUBMISSION.md)**.
> **Deadline: 23:59 (UTC+7) ngày làm lab** — nộp muộn bị trừ điểm ([docs/RULES.md](RULES.md)).

1. Chạy `make verify` lần cuối. Kết quả phải **exit 0**.
2. Tạo repo **public** trên GitHub account của bạn, đặt tên đúng quy ước
   **`K4-L3-DAY20-HoVaTen-MSSV-ModelServing`** (không dấu, không khoảng trắng; ví dụ
   `K4-L3-DAY20-NguyenVanAn-20241234-ModelServing`). Fork rồi đổi tên cũng được.
3. Commit và push:

   ```bash
   git add -A && git commit -m "Day 20 lab submission" && git push
   ```

4. Paste public URL vào ô submission Day 20 trên VinUni LMS.

**Repo phải public cho đến khi điểm được công bố.** Nếu repo private, grader không thể
đọc bài và bạn nhận **0 điểm**.

Không commit `models/*.gguf` hoặc `runtime/`. Hai path này đã có trong `.gitignore`, và
`make verify` không yêu cầu chúng.

---

# Troubleshooting

| Triệu chứng | Cách xử lý |
|---|---|
| `unknown model architecture: 'gemma4'` | llama.cpp quá cũ. Chạy `make runtime` để tải lại bản đã pin. |
| `make probe` báo `GPU offload : OFF` dù máy có GPU | Bình thường, và **không mất điểm** — toàn bộ 100 điểm base chạy trên CPU. Upstream llama.cpp **không** phát hành bản CUDA cho Linux, nên máy Linux + NVIDIA nhận bản Vulkan; thiếu Vulkan ICD thì runtime không thấy device nào. Lab tự set `ngl=0` để report không ghi sai. Muốn dùng GPU: `LLAMA_CMAKE_FLAGS=-DGGML_CUDA=ON make build-llama` (bonus B1). |
| `make serve` báo không tìm thấy venv | Bạn chưa chạy `make setup`. |
| `couldn't bind HTTP server socket … port: 8080` | Có process khác đang giữ port 8080. Đổi port: `LAB_SERVER_PORT=8090 make serve` (và dùng cùng biến đó cho `make smoke`, `make load-10/50`, `make metrics`, `make pipeline`). Trên Colab notebook đã set sẵn. |
| `make bench` fail, câu trả lời rỗng | Gemma 4 là reasoning model; lab đã set `--reasoning off`. Nếu bạn tự bật `LAB_REASONING=on`, `content` sẽ rỗng cho đến khi model "nghĩ" xong. |
| `make metrics` báo scrape failed | Server chưa chạy. Chạy `make serve` trước. |
| `busy_slots ≈ 1` dù đã chạy metrics | Bạn chạy `make metrics` khi không có load. Phải chạy chồng với `make load-50`. |
| locust chỉ hoàn thành vài request | Bình thường trên máy yếu. Đặt `LAB_LOAD_DURATION=3m` hoặc giảm `LAB_LOAD_SHORT_TOKENS`; giữ cùng cấu hình cho cả 10/50 users. |
| Hugging Face bị chặn | Xem [`docs/MANUAL-DOWNLOAD.md`](MANUAL-DOWNLOAD.md). |
| Máy < 8 GB RAM | Dùng [`docs/CLOUD.md`](CLOUD.md). |
| `make verify` fail mà chưa rõ lý do | Output ghi đúng file còn thiếu và lệnh cần chạy. Đọc từng dòng lỗi. |
| Sau checklist có dòng `make: *** [verify] Error 1` | Bình thường. Đó chỉ là cách `make` báo rằng `verify` tìm thấy mục còn thiếu — không phải `make` bị lỗi. Đọc checklist ở trên nó. |

## Các knob có thể đổi

Trên Windows, `lab.ps1` tự đọc file `.env` local nếu có; biến đã export trong terminal
vẫn được ưu tiên. File này là optional và đã được `.gitignore`. Trên macOS/Linux,
Makefile không tự source `.env`, nên set inline:

```bash
LAB_N_THREADS=4 make bench       # dùng thread count tốt nhất từ make tune
LAB_N_CTX=4096 make serve        # context lớn hơn (tốn RAM hơn)
LAB_PARALLEL=8 make serve        # nhiều slot hơn
LAB_REASONING=on make bench      # bật thinking để đo chi phí
```

Danh sách đầy đủ: [`.env.example`](../.env.example)
