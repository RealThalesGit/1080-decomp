#include "common.h"

extern s32 func_80006A98(s32);
extern void func_80006A50(s32, s32);
extern void func_80007A98(s32, s32, void*);
extern void func_80008D0C(void*);
extern void func_800073F8(void*, s32, s32);
extern u8 __rmonRcpAtBreak;

/* __rmonHitSpBreak */
void func_80008A38(void) {
    s32 buf[19];
    register s32 val = func_80006A98(0x04080000);
    func_80006A50(0x04080000, val - 4);
    func_80007A98(1, 0x3E8, buf);
    func_80008D0C(buf);
    func_800073F8(buf, 0x4C, 2);
    __rmonRcpAtBreak = 1;
}

/* __rmonHitCpuBreak — walk thread list checking for breakpoints */
extern s32 func_80009C30(void);
extern void func_80008D4C(s32, s32);
extern void func_800054C0(void*);

void func_80008AD0(void) {
    register s32* t = (s32*)func_80009C30();

    while (*(s32*)((char*)t + 4) != -1) {
        if (*(s32*)((char*)t + 4) > 0 && *(s32*)((char*)t + 4) < 0x80) {
            if (*(u16*)((char*)t + 0x12) & 1) {
                s32 instr = **(s32**)((char*)t + 0x11C);
                if ((instr & (s32)0xFC00003F) == 0xD) {
                    func_80008D4C(*(s32*)((char*)t + 0x14), instr >> 6);
                } else {
                    func_80008D4C(*(s32*)((char*)t + 0x14), 0);
                }
            }
            if (*(u16*)((char*)t + 0x12) & 2) {
                func_800054C0(t);
                func_80008D4C(*(s32*)((char*)t + 0x14), 0xF);
            }
        }
        t = *(s32**)((char*)t + 0x0C);
    }
}
