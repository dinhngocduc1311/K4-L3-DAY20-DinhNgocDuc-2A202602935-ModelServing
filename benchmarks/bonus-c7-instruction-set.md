# Bonus C7 - CPU instruction-set policy

Host `Windows-AMD64` · CPU `Intel i7-6820HQ` (AVX2) · llama.cpp `b10488`
(`9d77fa1`) · GCC/MinGW `14.2.0` · Release · CPU-only · `threads=4` ·
metric `tg128`, 3 repetitions.

| Build | Effective CPU flags | tg128 (tok/s) | Stddev | Relative |
|:--|:--|--:|--:|--:|
| `GGML_NATIVE=OFF` | SSE4.2, F16C, FMA, BMI2, AVX, AVX2 | 6.651 | 0.370 | 1.000x |
| `GGML_NATIVE=ON` | `-march=native` | 6.769 | 0.173 | 1.018x |

Raw outputs: `bonus-c7-generic.json` and `bonus-c7-native.json`.

## Finding

Native compilation improves the mean by only 1.8%, less than the run-to-run
variation. This CPU is Haswell-family, and llama.cpp's generic x86 configuration
already enables every relevant extension it exposes: through AVX2, FMA and BMI2.
`-march=native` therefore unlocks no wider vector ISA. Decode must also stream the
model weights for every token, so memory bandwidth limits the benefit of small
instruction-scheduling differences. The useful decision is to ship the explicit
AVX2 baseline for this hardware class; a host-specific binary adds deployment
complexity without a measurable win here.

## Reproduction

Both builds used the same source, model and Windows 10 target. The generic build
was configured with `-DGGML_NATIVE=OFF`; the native build with
`-DGGML_NATIVE=ON`. Both were built as Release and benchmarked with:

```text
llama-bench -m models/gemma-4-E2B-it-UD-Q4_K_XL.gguf \
  -t 4 -ngl 0 -p 0 -n 128 -r 3 -o json
```
