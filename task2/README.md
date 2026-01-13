# Write up task 2 CLB
## Document

- https://github.com/un1c0rn-the-pwnie/FSOPAgain
- https://pwn.college/software-exploitation/file-struct-exploits

## fsop to shell

- In task 1, i learnt that file structure is a part of larger struct named as file plus
![image](https://hackmd.io/_uploads/BJPRLAmS-e.png)
- File plus has a new ptr called vtable pointer
- From what i know, the program usually use vtable to set up internal to make IO logic almost the same with diffrent function. May be this part exist for efficiency reason
- Back to exploit, the program will call 'rax+0x38' at some  point
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
- First, we should carefull a bit about lock variable
![image](https://hackmd.io/_uploads/HyQ-py4Sbe.png)
- We should overwrite lock ptr to random address that far away our fake vtable as it may block us from writing into that area
- Then overwrite wide data of stdout to heap address that i can control data inside it
- At that moment, i can fake a vtable ptr without meeting vtable check
- Inside that heap address, ill write that exact heap address again at fake_wide_data.vtable
- It will then call 'heap_addr + 0x38'
- Ill use this gadget to call one gadget by writing the address of one gadget in 'heap_addr + 0x38' 
- After it call 'heap_addr + 0x38', ill get shell from here
- 
![image](https://hackmd.io/_uploads/Skp091VBZg.png)
