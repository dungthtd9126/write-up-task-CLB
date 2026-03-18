# Task 6
## How the challenge works
- This challenge is completely different with other challenges which I solved
- The challenge's name is steghide, it is a tool to extract hidden messages inside an image when enter correct passphrase.
- You can see exactly how it works when you builds a docker. The server will act as a virtual web, taking our images then automatically run a subprocess: <b> steghide extract -sf 'our_image' -p 'our_passphrase' -xf outfile_name </b>
- 