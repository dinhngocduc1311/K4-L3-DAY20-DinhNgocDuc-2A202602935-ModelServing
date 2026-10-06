# Bonus B1 - Prebuilt vs source build

Host `Windows-AMD64` · CPU `Intel(R) Core(TM) i7-6820HQ CPU @ 2.70GHz`
Vector extensions detected: AVX2
llama.cpp `b10488` both sides · `threads=4` ·
**both pinned to `ngl=0`** so this isolates the compiler ·
metric `tg128`, 3 repetitions

> **Backend mismatch, handled.** The prebuilt binary sees
> `['Vulkan0: Intel(R) HD Graphics 530 (8116 MiB, 7454 MiB free)', 'Vulkan1: Quadro M1000M (2222 MiB, 1920 MiB free)']` and your source build sees `(no devices)`.
> Left at `-ngl 99` this comparison would have measured the accelerator and printed
> it under a compiler headline, so both sides were pinned to `-ngl 0`.

| Binary | Built for | tg128 (tok/s) | Relative |
|:--|--:|--:|--:|
| prebuilt release | runtime CPU dispatch | 10.9 | 1.00x |
| your source build | this CPU (`-DGGML_NATIVE=ON`) | 6.8 | 0.62x |

On this machine, the prebuilt binary is **1.60x faster**.

before: 10.9 tok/s (prebuilt release)
after:  6.8 tok/s (source build, -DGGML_NATIVE=ON)
speedup: 0.62x

Same source revision, same model, same backend, same `-ngl` -- the only difference
is what the compiler was allowed to assume about the CPU.



## Explanation

The prebuilt binary wins even though this i7-6820HQ supports AVX2 and the source
build used `-march=native`. The release runtime selected its dedicated
`ggml-cpu-haswell.dll`, while my source binary was built with GCC/MinGW 14.2.
Native compilation therefore did not add an instruction set unavailable to the
prebuilt kernel; it changed the compiler/toolchain and produced a slower kernel.
Decode also streams weights repeatedly, so memory bandwidth limits how much
instruction tuning can help. Two runs were consistent (11.0 vs 6.9 and 10.9 vs
6.8 tok/s), making the 0.62x result unlikely to be measurement noise.
