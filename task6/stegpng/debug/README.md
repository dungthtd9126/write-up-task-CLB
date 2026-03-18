# Task 6

<h4> This challenge gives 2 binary <b> steghide (has bug)</b> and <b> steghide_patched (no bug)</b> and a dockerfile with some set up directories for docker build <h4>

## How the challenge works

This challenge is completely different with other challenges which I solved.

The challenge's name is steghide, it is a tool to extract hidden messages inside an image when enter correct passphrase.

You can see exactly how it works when you builds a docker. The server will act as a virtual web, taking our images then automatically run a subprocess with a command-line : 

```
steghide extract -sf 'our_image' -p 'our_passphrase' -xf outfile_name
```

--> So the bug definitely exist in this comamnd

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

<p>
