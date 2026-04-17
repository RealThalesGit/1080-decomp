# 1080 Snowboarding n64 decompilation

In progress 1080 Snowboarding decompilation, mostly driven by Claude. Uses https://github.com/bigyoshi51/decomp for n64 common tooling, Claude skills, etc.

## Status

**Kernel only** — the libultra + USO loader + game init segment (~40 KB, 275 functions). USO overlays (bootup.uso, game.uso, character models, audio banks, etc.) are currently tracked as opaque binary blobs and are **not** counted toward progress: they use a custom relocatable overlay format that would require a bespoke USO linker to decompile byte-matching.

```
Kernel code:      6,156 / 40,464 bytes (15.21%)
Kernel functions:    63 / 275          (22.91%)
```

ROM-wide totals (for context — not currently tracked):
- Full ROM: ~2,014 functions, ~290 KB code
- True progress relative to full ROM: ~3.1% functions, ~2.1% code

## Building

Requires: `mips-linux-gnu` binutils, Python 3, and IDO 7.1.

```bash
# 1. Place your legally-obtained 1080 Snowboarding (USA) ROM as baserom.z64
#    (md5: f0a98b4b4a8f2b0f4d2e3c7b7d9e1a8c — N64 Z64 format, 16 MB).
# 2. Extract IDO 7.1:
#    https://github.com/decompals/ido-static-recomp/releases/latest
#    Extract `ido-7.1-recomp-linux.tar.gz` into tools/ido-static-recomp/build/7.1/out/
# 3. Extract asset bins from baserom via splat (one-time):
make setup
# 4. Build:
make
```

ROM-derived binary extracts (`assets/*.bin`) are not committed — they are
regenerated from your local baserom by `make setup`.

The build uses IDO 7.1 with two optimization levels:
- `kernel_o2.c` — game code compiled with `-O2`
- `kernel_o1.c` — libultra functions compiled with `-O1`

## References

- **[libreultra](https://github.com/n64decomp/libreultra)** — Complete decompilation of Nintendo's libultra SDK. We use libreultra source as reference for matching libultra functions in the kernel. Function names, struct layouts, and `register` keyword usage are adapted from this project.
- **[splat](https://github.com/ethteck/splat)** — ROM splitting tool
- **[asm-processor](https://github.com/simonlindholm/asm-processor)** — Enables mixing C decompilation with INCLUDE_ASM stubs
- **[spimdisasm](https://github.com/Decompollaborate/spimdisasm)** — MIPS disassembler (via splat)
- **[decomp.me](https://decomp.me)** / **[objdiff](https://github.com/encounter/objdiff)** — Function-level matching and progress tracking

## Game Structure

1080 Snowboarding uses a **USO (Universal Shared Objects)** overlay system:
- **Kernel** (43K): libultra, USO loader, audio — the part being decompiled
- **bootup.uso** (277K): Giles Goddard's libgdl game engine (C++, 302 functions)
- **game_libs** (480K): Support libraries (1,371 functions)
- **mainuso** (13.6MB): Data modules (models, audio, textures)

Total: ~1,781 functions across the full ROM.
