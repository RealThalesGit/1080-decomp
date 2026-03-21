#!/usr/bin/env python3
"""Extract and analyze USO (Universal Shared Objects) modules from 1080 Snowboarding ROM."""

import struct
import json
import os
import sys
from pathlib import Path

MAGIC = 0x12345678

SECTION_NAMES = {
    0: "Info", 1: "Sym", 2: "TextReloc", 3: "DataReloc", 4: "RoDataReloc",
    5: "Text", 6: "Data", 7: "RoData", 8: "Bss", 9: "EntrySym",
    10: "EndOfFile", 11: "End", 12: "BinaryData", 13: "DiskInfo",
}


def read_u32(data: bytes, offset: int) -> int:
    return struct.unpack_from(">I", data, offset)[0]


def read_string(data: bytes, offset: int, max_len: int = 256) -> str:
    """Read null-terminated string from data."""
    end = offset
    while end < len(data) and end < offset + max_len and data[end] != 0:
        end += 1
    return data[offset:end].decode("ascii", errors="replace")


def find_filesystem_entries(data: bytes) -> list[dict]:
    """Find all filesystem entries marked with magic 0x12345678."""
    entries = []
    for i in range(0x1000, len(data) - 4, 4):
        if read_u32(data, i) == MAGIC:
            entry = {
                "magic_offset": i,
                "field1": read_u32(data, i + 4),
                "field2": read_u32(data, i + 8),
            }
            # Try to find filename at offset +12 or nearby
            for name_off in [12, 8]:
                s = read_string(data, i + name_off, 40)
                if s and (s.endswith(".uso") or s.endswith(".bin") or s == "<null>"):
                    entry["name"] = s
                    break
            entries.append(entry)
    return entries


def extract_strings(data: bytes, start: int, end: int, min_len: int = 4) -> list[dict]:
    """Extract ASCII strings from a byte range."""
    strings = []
    i = start
    while i < end:
        run = 0
        j = i
        while j < end and 32 <= data[j] < 127:
            run += 1
            j += 1
        if run >= min_len and j < len(data) and data[j] == 0:
            s = data[i : i + run].decode("ascii")
            strings.append({"offset": i - start, "value": s})
        i = j + 1
    return strings


def analyze_uso_module(data: bytes, rom_offset: int, name: str) -> dict:
    """Analyze a USO module and extract its sections."""
    magic = read_u32(data, rom_offset)
    if magic != MAGIC:
        return {"name": name, "error": f"Bad magic at 0x{rom_offset:X}: 0x{magic:08X}"}

    section_count = read_u32(data, rom_offset + 4)
    total_size = read_u32(data, rom_offset + 8)

    module = {
        "name": name,
        "rom_offset": rom_offset,
        "section_count": section_count,
        "total_size": total_size,
    }

    uso_data = data[rom_offset : rom_offset + total_size + 12]

    # Find code (.text) by scanning for MIPS function prologues
    prologues = []
    jr_locations = []
    for i in range(0, len(uso_data), 4):
        w = read_u32(uso_data, i)
        if (w >> 16) == 0x27BD and (w & 0x8000):
            prologues.append(i)
        if w == 0x03E00008:
            jr_locations.append(i)

    if prologues:
        # .text starts at the first prologue (or the jr $ra just before it)
        text_start = prologues[0]
        # Check if there's a jr $ra right before (trivial return function)
        if text_start >= 8:
            prev = read_u32(uso_data, text_start - 4)
            prev2 = read_u32(uso_data, text_start - 8)
            if prev == 0 and prev2 == 0x03E00008:
                text_start -= 8

        text_end = jr_locations[-1] + 8 if jr_locations else prologues[-1] + 4
        # Align to 16
        text_end = (text_end + 0xF) & ~0xF

        module["text"] = {
            "offset": text_start,
            "size": text_end - text_start,
            "functions": len(prologues),
            "returns": len(jr_locations),
        }

    # Everything before .text is data/rodata/metadata
    if prologues:
        # Find where string data transitions to non-string data
        pre_text = uso_data[12 : prologues[0]]
        strings = extract_strings(uso_data, 12, text_start)
        module["pre_text_size"] = text_start - 12
        module["strings_count"] = len(strings)

        # Check for section-type markers (small integers 0-13 followed by sizes)
        markers = []
        for i in range(12, text_start, 4):
            w = read_u32(uso_data, i)
            if 0 <= w <= 13:
                next_w = read_u32(uso_data, i + 4) if i + 4 < len(uso_data) else 0
                if next_w > 0x100 and next_w < total_size:
                    markers.append(
                        {
                            "offset": i,
                            "type": w,
                            "type_name": SECTION_NAMES.get(w, "?"),
                            "value": next_w,
                        }
                    )
        module["section_markers"] = markers

    # Everything after .text might be relocation data or more rodata
    if jr_locations:
        post_text = uso_data[text_end:]
        if len(post_text) > 0:
            module["post_text"] = {
                "offset": text_end,
                "size": len(post_text),
            }

    return module


def extract_module_files(data: bytes, module: dict, outdir: Path):
    """Extract module sections to files."""
    outdir.mkdir(parents=True, exist_ok=True)

    rom = module["rom_offset"]
    total = module["total_size"] + 12  # include header

    # Raw module dump
    (outdir / "raw.bin").write_bytes(data[rom : rom + total])

    # .text section
    if "text" in module:
        t = module["text"]
        text_data = data[rom + t["offset"] : rom + t["offset"] + t["size"]]
        (outdir / "text.bin").write_bytes(text_data)

    # Pre-text data (data + rodata + metadata)
    if "pre_text_size" in module:
        pre = data[rom + 12 : rom + module["text"]["offset"]]
        (outdir / "data_rodata.bin").write_bytes(pre)

    # Extract strings
    strings = extract_strings(data, rom + 12, rom + total)
    with open(outdir / "strings.txt", "w") as f:
        for s in strings:
            f.write(f"+0x{s['offset']:05X}: {s['value']}\n")

    # Module info
    with open(outdir / "info.json", "w") as f:
        # Remove non-serializable data
        info = {k: v for k, v in module.items() if k != "raw"}
        json.dump(info, f, indent=2)


def main():
    rom_path = sys.argv[1] if len(sys.argv) > 1 else "baserom.z64"
    outdir = Path(sys.argv[2] if len(sys.argv) > 2 else "uso_extract")

    with open(rom_path, "rb") as f:
        data = f.read()

    print(f"ROM: {rom_path} ({len(data)} bytes)")

    # Find filesystem entries
    entries = find_filesystem_entries(data)
    print(f"Found {len(entries)} filesystem magic entries")

    # Build file table from named entries
    named = [e for e in entries if "name" in e]
    print(f"Named entries: {len(named)}")
    for e in named:
        print(f"  ROM 0x{e['magic_offset']:06X}: {e['name']}")

    # Analyze known uncompressed modules
    # bootup.uso is in the 'rom' filesystem (uncompressed)
    bootup_entries = [e for e in named if e["name"] == "bootup.uso"]
    if bootup_entries:
        # The actual USO data follows the second magic (data header)
        # Find the data magic that follows the name entry
        bootup_name = bootup_entries[0]
        # Look for the next magic after this one
        for e in entries:
            if e["magic_offset"] > bootup_name["magic_offset"]:
                bootup_data = e
                break

        print(f"\n=== Analyzing bootup.uso ===")
        print(f"  Data magic at ROM 0x{bootup_data['magic_offset']:06X}")
        module = analyze_uso_module(data, bootup_data["magic_offset"], "bootup.uso")

        for k, v in module.items():
            if k not in ("section_markers",):
                print(f"  {k}: {v}")

        if module.get("section_markers"):
            print(f"  Section markers:")
            for m in module["section_markers"]:
                print(
                    f"    +0x{m['offset']:05X}: type={m['type']} ({m['type_name']}) value=0x{m['value']:X}"
                )

        # Extract files
        print(f"\n  Extracting to {outdir / 'bootup.uso'}...")
        extract_module_files(data, module, outdir / "bootup.uso")
        print("  Done!")

    # Save manifest
    manifest = {
        "rom": rom_path,
        "entries": [
            {
                "name": e.get("name", "(unnamed)"),
                "rom_offset": f"0x{e['magic_offset']:06X}",
                "field1": e["field1"],
                "field2": e["field2"],
            }
            for e in named
        ],
    }
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest written to {outdir / 'manifest.json'}")


if __name__ == "__main__":
    main()
