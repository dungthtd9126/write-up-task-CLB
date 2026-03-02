# Task 5

## Document: ret2dl_resolve

- https://syst3mfailure.io/ret2dl_resolve/

## Technique: ret2dl_resolve

- I uses this techique because the challenge doesn't have any output functon despite PIE off

<img width="799" height="234" alt="image" src="https://github.com/user-attachments/assets/0d5b0fec-5991-4656-a132-bc8327dd447f" />

- This technique requires 3 me to fake 3 main parts: Rel struct, symtab (dynsym) struct, and strtab (dynstr)

  - Rel struct contains 2 main parts: r_offset, r_info
  
  <img width="1360" height="189" alt="image" src="https://github.com/user-attachments/assets/6e587dde-54d7-4e9b-9422-2186df008e90" />

  - Each part has 8 bytes length

- Symtab has 6 components:
  + st_name: It acts as a string table index. It will be used to locate the right string in the STRTAB section.
  + st_info: It contains symbol’s type and binding attributes.
  + st_other: It contains symbol’s visibility.
  + st_shndx: It contains the relevant section header table index.
  + st_value: It contains the value of the associated symbol.
  + st_size: It contains the symbol’s size. If the symbol has no size or the size is unknown, it contains 0.

<img width="1387" height="265" alt="image" src="https://github.com/user-attachments/assets/54f7aa81-3712-4fcc-bb30-c62abccf0ad7" />

- STRTAB (.dynstr): strings of symbol name stays here

<img width="640" height="249" alt="image" src="https://github.com/user-attachments/assets/7f219d3f-eb1d-4b98-9f61-c94846bf78d2" />

<details>
  
<summary> <b>  How to get JMP, STRTAB, SYMTAB base </b></summary>

- command on terminal: readelf -S ./chall_patched

<img width="741" height="854" alt="image" src="https://github.com/user-attachments/assets/aad02304-dd5d-429a-854d-57b3f7e67e19" />

- It will show a list of section headers with following atributes

- I'll get JMPREL, TRTAB, SYMTAB base in the following secton:
  + JMPREL: .rela.plt
  + SYMTAB: .dynsym
  + STRTAB: .dynstr

</details>

- Another important information is both JMPREL and SYMTAB are usually 0x18 in size

- So when fake JMPREL and SYMTAB, i should have 0x18 alignment

### How the program works

- This technique base on a mechanism of dynamic linking. When I first calls a libc function, it goes to a function stub stored as default inside the symbol's got.plt --> pushing <b>reloc_arg</b> then execute _dl_runtime_resolve() to find the true address in libc.

- After succesfully found the symbol with its libc address, it stores the real libc addr into that symbol's got.plt and execute that function

- Because PIE is off and saved rip can be overwrote, I can fake strtab, symtab, jmprel, reloc_arg and rop chain to force it call system(/bin/sh)

## Analyze libc

- I'll analyze only neccessary parts in my exploit so some parts may be skipped

<b> Source: https://codebrowser.dev/glibc/glibc/elf/dl-runtime.c.html#_dl_fixup </b>
```c
const PLTREL *const reloc = (const void *) (D_PTR(l, l_info[DT_JMPREL]) + reloc_offset);
const ElfW(Sym) *sym = &symtab[ELFW(R_SYM) (reloc->r_info)];
const ElfW(Sym) *refsym = sym;
void *const rel_addr = (void *)(l->l_addr + reloc->r_offset);
```
- Those parts above are in _dl_fixup function, 
