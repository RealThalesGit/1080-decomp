#include "common.h"

extern s32 func_8000898C(s32, s32, s32);
extern void func_800084D0(s32, s32);
extern s32 func_80008BB4(s32);

/* __rmonStepBreak */
s32 func_80008848(s32 arg0, s32* arg1) {
    s32 result = func_8000898C(0, arg0, (s32)arg1);
    if (result & 3) {
        func_800084D0((s32)arg1 + 4, 0);
    } else {
        if ((s32)arg1 == result) {
            return 0;
        }
        if (func_80008BB4(*arg1) != 0 || (s32)arg1 + 8 == result) {
            func_800084D0(result, 0);
        } else {
            func_800084D0(result, (s32)arg1 + 8);
        }
    }
    return 1;
}

INCLUDE_ASM("asm/nonmatchings/kernel", func_8000890C);
