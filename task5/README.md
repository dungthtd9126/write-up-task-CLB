# Task 5

## Document: ret2dl_resolve

- https://syst3mfailure.io/ret2dl_resolve/

## Technique: ret2dl_resolve

- I uses this techique because the challenge doesn't have any output functon despite PIE off

<img width="799" height="234" alt="image" src="https://github.com/user-attachments/assets/0d5b0fec-5991-4656-a132-bc8327dd447f" />

- This technique requires 3 me to fake 3 main parts: Rel struct, symtab (dynsym) struct, and strtab (dynstr)

  - Rel struct has 2 main parts: r_offset, r_info
 
  <img width="1360" height="189" alt="image" src="https://github.com/user-attachments/assets/6e587dde-54d7-4e9b-9422-2186df008e90" />
