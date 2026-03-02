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
