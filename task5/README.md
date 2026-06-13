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
  
## How to get JMP, STRTAB, SYMTAB base

- command on terminal: readelf -d  ./chall_name 

<img width="922" height="718" alt="image" src="https://github.com/user-attachments/assets/3a3c1842-dcc1-4432-b8d7-555eafccc021" />

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

```
- Those parts above are in _dl_fixup function
- The first line:
  - <b>reloc_offset</b> corresponds to reloc_arg * sizeof(PLTREL) = reloc_arg * 0x18
  
  - D_PTR(l, l_info[DT_JMPREL]) = JMPREL address

- So the first line means: reloc = JMPREL + reloc_arg * 0x18. It stores our chosen REL struct to reloc

- The last line stores our chosen symtab into sym: *sym = &symtab[reloc->r_info >> 32];

- After that, there will be a check:
```c
assert (ELFW(R_TYPE)(reloc->r_info) == ELF_MACHINE_JMP_SLOT);
```
- Meaning: assert ((reloc->r_info & 0xffffffff) == 0x7); 

- It check if <b> (reloc->r_info & 0xffffffff) == 0x7 </b> to confirm if that is a valid JUMP_SLOT.

- From what we can see:
    ```
     *sym = &symtab[reloc->r_info >> 32];
     assert ((reloc->r_info & 0xffffffff) == 0x7);
    ```
- We can bypass these by set our fake r_info like below:

  + <b> r_info = (int((fake_symtab - SYMTAB) / 0x18)  << 32) | 0x7 </b>

- Not only that, I need to fake reloc_arg too:
  - <b> (fake_rel  - JMPREL) / 0x18 </b>

- Note that both fake_rel and fake_symtab should be 0x18 aligned to get integer type value

## Exploit

- Back to the challenge, I'll first write <b> /bin/sh </b> and <b> system </b> string in bss

--> rop chain, making rdi stores ptr to /bin/sh string -->  execute default function stub

<img width="961" height="728" alt="image" src="https://github.com/user-attachments/assets/93722abe-e503-4f60-9796-499c41ab9a12" />

- From the picture above, reloc_arg should be set up right after a libc address just gets pushed on the stack by the program

- Note that we need to align our fake symtab and jmprel with 0x18

<img width="913" height="192" alt="image" src="https://github.com/user-attachments/assets/ac28c029-f4e0-4577-b87c-f63c836c72ee" />

- In reality, jmprel struct only uses 0x10 bytes, 8 bytes left are padded

- So we can use 8 bytes left as our fake symtab too if it is a valid aligned address

<img width="913" height="192" alt="image" src="https://github.com/user-attachments/assets/051a72fa-e7bb-463a-9d47-5d8f1ece10ff" />

- With this action, we need much less bytes to write --> avoid not enough input num

- I uses this trick in the picture above so it was perfectly fit in this challenge

- Because the program executes that functon after resolved so I'll succesfully get shell in here without libc leak

- Last note that '/bin/sh' and 'system' string addresses should be bigger than rsp when the program starting to resolve the symbol

- If not, it value may be replaced by stack frames of _dl_runtime_resolve() and its sub function, leading to unexpectable scenarios

<img width="945" height="816" alt="image" src="https://github.com/user-attachments/assets/efceb656-2835-4df5-9193-c62ab8e936e8" />

