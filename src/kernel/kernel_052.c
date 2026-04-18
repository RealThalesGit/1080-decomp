#include "common.h"

extern s32 func_800066F0(void*, s32, s32);

/* Receive 4 bytes from host I/O into the caller's arg0 stack slot. */
void func_80005184(s32 arg0) {
    s32 totalRecv;
    char* p;
    totalRecv = 0;
    p = (char*)&arg0;
    do {
        register s32 recv = func_800066F0(p + totalRecv, 4 - totalRecv, 8);
        totalRecv += recv;
    } while (totalRecv < 4);
}
