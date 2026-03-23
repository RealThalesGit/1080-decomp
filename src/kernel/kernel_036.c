#include "common.h"

extern void* func_80009C30(void);

/* __rmonSendHeader — find free comm slot and configure it */
void __rmonSendHeader(void) {
    register s32* node = (s32*)func_80009C30();
    while (node[1] != -1) {
        if (node[1] == 0) {
            *(s32*)((char*)node + 0x118) = *(s32*)((char*)node + 0x118) & 0xFFFF00FE;
            *(s32*)((char*)node + 0x118) = *(s32*)((char*)node + 0x118) | 0x6C01;
            break;
        }
        node = (s32*)node[3];
    }
}

INCLUDE_ASM("asm/nonmatchings/kernel", func_800073DC);
