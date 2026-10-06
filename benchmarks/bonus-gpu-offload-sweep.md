# Bonus - GPU offload sweep

Host `Windows-AMD64` · selected device `Vulkan1: Quadro M1000M` ·
llama.cpp `b10488` · `threads=4` · metric `tg128`

| -ngl | tg128 (tok/s) | vs -ngl 0 | vs best |
|:--|--:|--:|--:|
| 0 | 11.2 | 1.00x | 78% |
| 8 | 6.6 | 0.59x | 46% |
| 16 | 5.5 | 0.49x | 38% |
| 24 | 4.8 | 0.43x | 33% |
| 32 | 4.4 | 0.39x | 31% |
| 99 | 14.3 | 1.28x | 100% |

Best: `-ngl 99` at 14.3 tok/s
-- 1.28x faster than CPU-only.

Where the curve flattens tells you the model ran out of layers to move. Where it
*peaks below* full offload tells you something did not fit and the accelerator
started paying to fetch weights it could not hold.

## Finding

Full layer offload is best: `-ngl 99` reaches 14.3 tok/s, 1.28x the CPU-only
11.2 tok/s. A verbose check confirms llama.cpp selected the Quadro M1000M,
offloaded 36/36 transformer layers into a 1481.9 MiB Vulkan buffer, and retained
1804.0 MiB of CPU-mapped tensors. The 8--32 layer points are only 4.4--6.6 tok/s:
each decode token crosses the CPU/GPU placement boundary, so synchronization and
PCIe hand-off cost more than partial acceleration saves. At 36 layers that
per-layer boundary disappears even though the entire GGUF does not fit in VRAM.
