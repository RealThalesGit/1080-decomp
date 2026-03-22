extern int __osPiAccessQueue;
extern int osSendMesg(int*, int, int);

/* __osSiGetAccess */
void func_80005894(void) {
    osSendMesg(&__osPiAccessQueue, 0, 0);
}
