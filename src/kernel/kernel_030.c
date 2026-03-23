#include "common.h"

extern void func_800073F8(void*, s32, s32);

typedef struct { s32 pad0; u8 type; char pad5; u16 flags; s32 pad8; s32 id; } RmonHdr16;
typedef struct { s32 pad0; u8 type; char pad5[7]; s32 id; } RmonMsg;

/* __rmonListProcesses */
s32 func_80007EA0(RmonMsg* msg) {
    RmonMsg* p = msg;
    RmonHdr16 hdr;
    hdr.type = p->type;
    hdr.flags = 0;
    hdr.id = p->id;
    func_800073F8(&hdr, 0x10, 1);
    return 0;
}

INCLUDE_ASM("asm/nonmatchings/kernel", func_80007EEC);
