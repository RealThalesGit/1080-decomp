#include "common.h"

extern void func_800073F8(void*, s32, s32);

typedef struct { s32 pad0; u8 type; char pad5; u16 flags; s32 pad8; s32 id; s32 count; } RmonHdr;
typedef struct { s32 pad0; u8 type; char pad5[4]; u8 domain; char padA[2]; s32 id; } RmonMsg;

/* __rmonWriteMem */
s32 func_80006D0C(RmonMsg* msg) {
    RmonMsg* p = msg;
    RmonHdr hdr;
    hdr.type = p->type;
    hdr.flags = 0;
    hdr.id = p->id;
    if (p->domain == 1) {
        hdr.count = 2;
    } else {
        hdr.count = 5;
    }
    func_800073F8(&hdr, 0x14, 1);
    return 0;
}

INCLUDE_ASM("asm/nonmatchings/kernel", func_80006D7C);
