# Write up task 2 CLB

## How fsop with wfile_overflow jump

```
rax is wide data
<_IO_wdoallocbuf+45>    mov    rax, qword ptr [rax + 0xe0]     RAX, [0x55555555b4b0] => 0
<_IO_wdoallocbuf+52>    call   qword ptr [rax + 0x68]
```

## Document

- https://github.com/un1c0rn-the-pwnie/FSOPAgain
- https://pwn.college/software-exploitation/file-struct-exploits
- https://repository.root-me.org/Exploitation%20-%20Syst%C3%A8me/EN%20-%20Play%20with%20FILE%20Structure%20-%20Yet%20Another%20Binary%20Exploit%20Technique%20-%20An-Jie%20Yang.pdf

## fsop to shell

- In task 1, i learnt that file structure is a part of larger struct named as file plus

![image](https://hackmd.io/_uploads/BJPRLAmS-e.png)

- File plus has a new ptr called vtable pointer

- From what i know, the program usually use vtable to set up internal to make IO logic almost the same with diffrent function. May be this part exist for efficiency reason

- Back to exploit, the program will call 'r15+0x38' at some  point

![image](https://hackmd.io/_uploads/ryuS7k4BZe.png)
- In this case, im analyzing fwrite function

- So it will call xsputn at this part

- And if we notice the name of the function

- We can see the name 'put' in it

- Thats is the machinism of vtable, make the I/O of the program have basic I/O logic, not too complex --> So it may use the same vtable at different fucntion

- And from what pwn college taught me, we can overwrite vtable ptr to control program flow and get shell

- But in morden libc, there is a function called '_IO_vtable_check'

- This function will check if the vtable is in a specific libc area

- So when we have to use functions in that area as middle part to get shell

- Here is the method i use to get shell

![image](https://hackmd.io/_uploads/SyagOJVHZl.png)
- Inside wide_data, there is no vtable check

- So i just need to overwrite 'file.vtable' to make it call IO_wfile_overflow

- Then it call do_allocbuf --> call wide_data vtable without check

## Challenge
- So in my poc, its pretty simple

- First leak libc and heap address, i used the same method in task 1 so ill skip this part

- Lets ret2shell with fsop from here

- First of all, we should carefull a bit about lock variable

![image](https://hackmd.io/_uploads/HyQ-py4Sbe.png)
- We should overwrite lock ptr to random address that far away our fake vtable as it may block us from writing into that area

- After that, we should set flag to 0 as in IO_wfile_overflow will have some conditional check. And it will compare our fake flag with some value, we have to make sure it will these conditions result in false

<img width="1651" height="410" alt="image" src="https://github.com/user-attachments/assets/1be3e0e4-97d8-400c-8b63-d7c3f255a65d" />

- As we can see in the picture above, there is also a check at 'fake_wdata + 0x18', rdx is storing our fake vtable addr. But we dont need to bother it. I just need to set all data except our one gadget and 'fake wide data --> vtable' as 'NULL'

- The next step is overwriting wide data of stdout to heap address that i can control data inside it

- At that moment, i can fake a vtable ptr without meeting vtable check

- Inside that heap address, ill write that exact heap address again at fake_wide_data.vtable

- It will then call 'heap_addr + 0x38'

- Ill use this gadget to call one gadget by writing the address of one gadget in 'heap_addr + 0x38'

- After it call 'heap_addr + 0x38', ill get shell from here


![image](https://hackmd.io/_uploads/Skp091VBZg.png)

## Bonus

- I just changed from ubuntu to arch and just see that NOASLR in arch may result in a differ of the 4 bit in NOASLR mode

- For example:
          - Arch: 0xb0c0
          - Ubuntu: 0xa0c0

- As you can see, i brute force the 4 bit '0xb' or '0xa' in this chall, so it doesnt matter if in NOASLR mode on arch that give different bit. It still ok as im brute forcing, not a absolute address so it still true, we just cant use NOASLR on arch to auto get shell for test like on ubuntu

## Bonus 2

- From what i researched, i learnt that fsop is a technique base on controlling the flow of program.

- And we can use that for different purpose, arbitrary read/write or even get shell!!

### Get shell

- There are multiple ways to get shell by fsop even with vtable check

- We can use some popular techinque like overwrite IO_list_all variable and call shell

<img width="1526" height="898" alt="image" src="https://github.com/user-attachments/assets/29e85ed1-df77-4615-a501-4e3c61b776c8" />

- We can use the chain area to execute ropchain or get system('/bin/sh') when the program abort or end

<img width="1599" height="873" alt="image" src="https://github.com/user-attachments/assets/09d34a46-e2c4-406f-b128-ef57df110078" />

- Also, we can use this tecnique with fcloseall as it call IO_clean_up with has _IO_flush_all_lockp in it
<img width="477" height="320" alt="image" src="https://github.com/user-attachments/assets/78c11968-5bc5-43b9-a01c-ebc7e13ab4b1" />

<img width="919" height="425" alt="image" src="https://github.com/user-attachments/assets/79718705-b003-44e7-9efb-3f1304f2ddb9" />

- And as we can see, IO_flush_all  will call IO_overflow if the condition is meet

<img width="1449" height="846" alt="image" src="https://github.com/user-attachments/assets/46db00bc-97b0-4b82-80eb-03f1d261553d" />

- We can abuse this to call system('sh') when it checks each IO file connected by chain section in abort progress
  <img width="1493" height="903" alt="image" src="https://github.com/user-attachments/assets/34eb85ca-1004-49d6-9ecc-d45a8d1303e1" />


