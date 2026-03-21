SECTIONS
{
    __romPos = 0;
    header_ROM_START = __romPos;
    header_VRAM = ADDR(.header);
    .header : AT(header_ROM_START)
    {
        FILL(0x00000000);
        header_DATA_START = .;
        build/assets/header.bin.o(.data);
        header_DATA_END = .;
        header_DATA_SIZE = ABSOLUTE(header_DATA_END - header_DATA_START);
    }
    __romPos += SIZEOF(.header);
    header_ROM_END = __romPos;
    header_VRAM_END = .;

    ipl3_ROM_START = __romPos;
    ipl3_VRAM = ADDR(.ipl3);
    .ipl3 : AT(ipl3_ROM_START)
    {
        FILL(0x00000000);
        ipl3_DATA_START = .;
        build/assets/ipl3.bin.o(.data);
        ipl3_DATA_END = .;
        ipl3_DATA_SIZE = ABSOLUTE(ipl3_DATA_END - ipl3_DATA_START);
    }
    __romPos += SIZEOF(.ipl3);
    ipl3_ROM_END = __romPos;
    ipl3_VRAM_END = .;

    kernel_ROM_START = __romPos;
    kernel_VRAM = ADDR(.kernel);
    .kernel 0x80000000 : AT(kernel_ROM_START)
    {
        FILL(0x00000000);
        kernel_TEXT_START = .;
        build/asm/kernel.s.o(.text);
        kernel_TEXT_END = .;
        kernel_TEXT_SIZE = ABSOLUTE(kernel_TEXT_END - kernel_TEXT_START);
        kernel_RODATA_START = .;
        build/asm/kernel.s.o(.rodata);
        kernel_RODATA_END = .;
        kernel_RODATA_SIZE = ABSOLUTE(kernel_RODATA_END - kernel_RODATA_START);
        kernel_DATA_START = .;
        build/asm/kernel.s.o(.data);
        kernel_DATA_END = .;
        kernel_DATA_SIZE = ABSOLUTE(kernel_DATA_END - kernel_DATA_START);
    }
    kernel_bss_VRAM = ADDR(.kernel_bss);
    .kernel_bss (NOLOAD) :
    {
        FILL(0x00000000);
        kernel_BSS_START = .;
        build/asm/kernel.s.o(.bss);
        kernel_BSS_END = .;
        kernel_BSS_SIZE = ABSOLUTE(kernel_BSS_END - kernel_BSS_START);
    }
    __romPos += SIZEOF(.kernel);
    __romPos = ALIGN(__romPos, 16);
    kernel_ROM_END = __romPos;
    kernel_VRAM_END = .;

    uso_data_ROM_START = __romPos;
    uso_data_VRAM = ADDR(.uso_data);
    .uso_data : AT(uso_data_ROM_START)
    {
        FILL(0x00000000);
        uso_data_DATA_START = .;
        build/assets/uso_data.bin.o(.data);
        uso_data_DATA_END = .;
        uso_data_DATA_SIZE = ABSOLUTE(uso_data_DATA_END - uso_data_DATA_START);
    }
    __romPos += SIZEOF(.uso_data);
    uso_data_ROM_END = __romPos;
    uso_data_VRAM_END = .;

    /DISCARD/ :
    {
        *(*);
    }
}
