#include "common.h"

extern s32 rmonbrk_bss_0000;
extern s32 D_8001FEF4;
extern s32 D_8001FEF0;
extern void func_800031F0(void*, s32);
extern void func_80005350(void*, s32);

/* __rmonSetBreak */
void func_800080D0(s32* arg0, s32* arg1) {
    *((s32*)((char*)&rmonbrk_bss_0000 + 4)) = *arg0;
    *arg0 = 0x40D;
    func_800031F0(arg0, 4);
    func_80005350(arg0, 4);
    *(s32*)&rmonbrk_bss_0000 = (s32)arg0;
    if (arg1 != 0) {
        D_8001FEF4 = *arg1;
        *arg1 = 0x40D;
        func_800031F0(arg1, 4);
        func_80005350(arg1, 4);
        D_8001FEF0 = (s32)arg1;
    }
}

INCLUDE_ASM("asm/nonmatchings/kernel", func_8000817C);
