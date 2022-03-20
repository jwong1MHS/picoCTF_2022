# **Table of Contents**
- [Binary Exploitation](./picoCTF_2022.md#Binary-Exploitation)
- [Cryptography](./picoCTF_2022.md#Cryptography)
- [Forensics](./picoCTF_2022.md#Forensics)
- [Reverse Engineering](./picoCTF_2022.md#Reverse-Engineering)
- [Web Exploitation](./picoCTF_2022.md#Web-Exploitation)

# **Binary Exploitation**
- [basic-file-exploit](./picoCTF_2022.md#basic-file-exploit)
- [buffer-overflow-0](./picoCTF_2022.md#buffer-overflow-0)
- [CVE-XXXX-XXXX](./picoCTF_2022.md#CVE-XXXX-XXXX)
- [RPS](./picoCTF_2022.md#RPS)

## **basic-file-exploit**

### ***Description***
The program provided allows you to write to a file and read what you wrote from it. Try playing around with it and see if you can break it! <br>
Connect to the program with netcat: <br>
`$ nc saturn.picoctf.net 50366` <br>
The program's source code with the flag redacted can be downloaded [here](https://artifacts.picoctf.net/c/538/program-redacted.c).
<details>
    <summary>Hint 1</summary>
    Try passing in things the program doesn't expect. Like a string instead of a number.
</details>

### ***Writeup***
Look through the soruce code and find where the flag might be.
There is a flag char*, but it is redacted, so let's see where it is used.
The pointer is outputted if `entry_number==0`, or if `strtol` errors.
The value of entry needs to be a letter for `strtol` to error.
The `data_read` function is called when option 2 is selected. Therefore, to trigger the flag, choose option 2 and pass in any string.

```
└─$ nc saturn.picoctf.net 50366
Hi, welcome to my echo chamber!
Type '1' to enter a phrase into our database
Type '2' to echo a phrase in our database
Type '3' to exit the program
1
1
Please enter your data:
a
a
Please enter the length of your data:
1
1
Your entry number is: 1
Write successful, would you like to do anything else?
2
2
Please enter the entry number of your data:
c
c
picoCTF{M4K3_5UR3_70_CH3CK_Y0UR_1NPU75_25D6CDDB}
```

Flag: `picoCTF{M4K3_5UR3_70_CH3CK_Y0UR_1NPU75_25D6CDDB}`

## **buffer overflow 0**

### ***Description***
Smash the stack <br>
Let's start off simple, can you overflow the correct buffer? The program is available here. You can view source here. And connect with it using: <br>
`nc saturn.picoctf.net 64712`
<details>
    <summary>Hint 1</summary>
    How can you trigger the flag to print?
</details>
<details>
    <summary>Hint 2</summary>
    If you try to do the math by hand, maybe try and add a few more characters. Sometimes there are things you aren't expecting.
</details>
<details>
    <summary>Hint 3</summary>
    Run `man gets` and read the BUGS section. How many characters can the program really read?
</details>

### ***Writeup***
If you cannot run the vuln executable, it might be because your OS does not support 32-bit programs. I recommend either [installing gcc-multilib](https://superuser.com/a/1603878) to install libc6 to run a 32-bit ELF on a 64-bit architecture (`sudo apt install gcc-multilib`), or use the gcc compiler and compile the C code (`gcc vuln.c -o vuln`).

Looking at the vuln code, I can see that it first takes the contents of `flag.txt` and copies it to the global buffer `flag` using `fgets`. It then takes user input and writes it to `buf1` which is of size 100. Then, it calls the `vuln` void function which will use `strcpy` and copy the contents of `buf1` to `buf2` which is of size 16 using `gets`.

The error here is the vulnerable `strcpy` function, because it will write all the bytes from the input buffer to the destination buffer, and it can even write past the buffer (which is called a buffer overflow).

Attempting to execute vuln shows that it needs a `flag.txt`, so I created a new `flag.txt` file with some random string. This will be used later to test whether the contents of flag are printed out onto the console.

```
└─$ cat flag.txt
picoCTF{random_string}
```

I am going to write 16 A's into `input.txt` and feed it into the vuln program to see what happens.

```
└─$ python3 -c "print('A'*16)" > input.txt && ./vuln < input.txt
Input: The program will exit now
```

As expected, nothing much and the program exits nicely. Time to use GDB! Reason why I am using multiple A's is because since A is 0x41, I just have to look multiple occurences of 0x41 in the stack. Run `gdb vuln` and then `layout asm` to get the assembly as well as the debugger console. If you are using `layout asm`, the memory addresses displayed may not be correct (not sure why). For example, it might say main starts at address 0x1382, which is incorrect. I recommend running the program once to display the correct addresses, so main should start at 0x56556382.

Correct memory addresses:
![after_layout_asm](Binary_Exploitation/buffer_overflow_0/after_layout_asm.png)

Since `strcpy` is in the vuln function, I am going to analyze the assembly at that section by doing `disas vuln`. The `strcpy` function is called at address  0x56556374, so I will set a breakpoint at the address right after the call by doing `b *0x56556379` so I can analyze the stack. Time to run the program once with `input.txt` by doing `r < input.txt` and see what the stack looks like.

The first 64 bytes of sp register:
![sp_with_16A](Binary_Exploitation/buffer_overflow_0/sp_with_16A.png)

I can see that `buf2` starts at address 0xffffd048 because that's where the 0x41 starts to appear. I also notice that at 0xffffd054 there is something stored there. Running `info frame` shows that `ebx` is stored there, which currently has the contents of `eax` as shown from the instruction at address 0x56556372.

Frame info at the breakpoint after strcpy:
![ebx_register_location](Binary_Exploitation/buffer_overflow_0/ebx_register_location.png)

I am going to try and corrupt ebx register and possibly create a segmentation fault, I will write 20 A's into `input.txt` now and see what happens.

```
└─$ python3 -c "print('A'*20)" > input.txt && ./vuln < input.txt
Input: picoCTF{random_string}
```

As expected, something was corrupt which outputted the contents of `flag`. Let's see what happened on the assembly scale.

![corrupt_sp](Binary_Exploitation/buffer_overflow_0/corrupt_sp.png)

Notice that at 0xffffd054 it changed from 0xac to 0x00, but 0xffffd055 remains unchanged and is still 0x8f. This is because when writing the 20 A's into input.txt, the `gets` function reads it as 20 A's as well as the null-terminating character, so in reality 21 characters are written to buf2. 

If you look at memory address 0x5655635b, the program allocates 0x14, or in decimal 20 bytes for buf2. Even though buf2 was created on the stack with a size of 16, it needs the null-terminating charaters, so in reality buf2 needs 17 bytes of storage. Since this is a 32-bit program, memory is stored in units of 4 bytes, and the smallest multiple of 4 greater than 17 is 20.

Any input greater than 19 characters will segfault the program, which then the signal handler will capture and call `sigsegv_handler` and will print the flag and fully exit. I took `input.txt` which already has 20 A's and fed the contents to the netcat connection.

```
└─$ python3 -c "print('A'*20)" > input.txt && nc saturn.picoctf.net 64712 < input.txt
Input: picoCTF{ov3rfl0ws_ar3nt_that_bad_81929e72}
```

Flag: `picoCTF{M4K3_5UR3_70_CH3CK_Y0UR_1NPU75_25D6CDDB}`

## **CVE-XXXX-XXXX**

### ***Description***
Enter the CVE of the vulnerability as the flag with the correct flag format:
`picoCTF{CVE-XXXX-XXXXX}` replacing XXXX-XXXXX with the numbers for the matching vulnerability. <br>
The CVE we're looking for is the first recorded remote code execution (RCE) vulnerability in 2021 in the Windows Print Spooler Service, which is available across desktop and server versions of Windows operating systems. The service is used to manage printers and print servers.
<details>
    <summary>Hint 1</summary>
    We're not looking for the Local Spooler vulnerability in 2021...
</details>

### ***Writeup***
A quick Google search of "first recorded remote code execution (RCE) vulnerability in 2021 in the Windows Print Spooler Service" gives this [result](https://msrc.microsoft.com/update-guide/vulnerability/cve-2021-34527). Make sure that the Attack Vector is Network and not Local.

Flag: `picoCTF{CVE-2021-34527}`

## **RPS**

### ***Description***
Here's a program that plays rock, paper, scissors against you. I hear something good happens if you win 5 times in a row. <br>
Connect to the program with netcat: <br>
`$ nc saturn.picoctf.net 50305` <br>
The program's source code with the flag redacted can be downloaded [here](https://artifacts.picoctf.net/c/445/game-redacted.c).
<details>
    <summary>Hint 1</summary>
    How does the program check if you won?
</details>

### ***Writeup***
Looking at the source code, I need `wins` to be greater than 5 for the program to print the flag to the console. The `wins` variable is accumulated if `play()` returns true, which is if `strstr(player_turn, loses[computer_turn])` also returns a non-zero result. Looking at the man pages for `strstr` shows that it is in the form of `char *strstr(const char *haystack, const char *needle)`, where `strstr()` finds the first occurrence of the substring `needle` in the string `haystack`. It then returns a pointer to the beginning of the located substring. Therefore, the program tries to find the specific string of `loses[computer_turn]` in the `player_turn` string that we provided to the program, where `char* loses[3] = {"paper", "scissors", "rock"};`. Essentially, create a string where if `strstr` tries to find the substring match it succeeds on all occurences, so such a string that does that is `rockpaperscissors` because each choice is a substring in that input string.

```
─$ nc saturn.picoctf.net 50305
Welcome challenger to the game of Rock, Paper, Scissors
For anyone that beats me 5 times in a row, I will offer up a flag I found
Are you ready?
Type '1' to play a game
Type '2' to exit the program
1
1


Please make your selection (rock/paper/scissors):
rockpaperscissors
rockpaperscissors
You played: rockpaperscissor
The computer played: paper
You win! Play again?
Type '1' to play a game
Type '2' to exit the program
1
1

...

Please make your selection (rock/paper/scissors):
rockpaperscissors
rockpaperscissors
You played: rockpaperscissors
The computer played: scissors
You win! Play again?
Congrats, here's the flag!
picoCTF{50M3_3X7R3M3_1UCK_D80B11AA}
Type '1' to play a game
Type '2' to exit the program
2
2
```

Flag: `picoCTF{50M3_3X7R3M3_1UCK_D80B11AA}`

# **Cryptography**
- [basic-mod1](./picoCTF_2022.md#basic-mod1)
- [basic-mod2](./picoCTF_2022.md#basic-mod2)
- [credstuff](./picoCTF_2022.md#credstuff)
- [morse-code](./picoCTF_2022.md#morse-code)
- [rail-fence](./picoCTF_2022.md#rail-fence)
- [substitution0](./picoCTF_2022.md#substitution0)
- [substitution1](./picoCTF_2022.md#substitution1)
- [substitution2](./picoCTF_2022.md#substitution2)
- [transposition-trial](./picoCTF_2022.md#transposition-trial)
- [Vigenere](./picoCTF_2022.md#vigenere)

## **basic-mod1**

### ***Description***
We found this weird message being passed around on the servers, we think we have a working decrpytion scheme. <br>
Download the message [here](https://artifacts.picoctf.net/c/393/message.txt). <br>
Take each number mod 37 and map it to the following character set: 0-25 is the alphabet (uppercase), 26-35 are the decimal digits, and 36 is an underscore. <br>
Wrap your decrypted message in the picoCTF flag format (i.e. `picoCTF{decrypted_message}`)
<details>
    <summary>Hint 1</summary>
    Do you know what <code>mod 37</code> means?
</details>
<details>
    <summary>Hint 2</summary>
    <code>mod 37</code> means modulo 37. It gives the remainder of a number after being divided by 37.
</details>

### ***Writeup***
Make a [python script](./Cryptography/basic-mod1/basic_mod1.py) that will parse the text file and mod every number.

`message.txt`:
```
└─$ cat message.txt
54 396 131 198 225 258 87 258 128 211 57 235 114 258 144 220 39 175 330 338 297 288
```
output of `basic_mod1.py`:
```
└─$ python3 basic_mod1.py
picoCTF{R0UND_N_R0UND_79C18FB3}
```

Flag: `picoCTF{R0UND_N_R0UND_79C18FB3}`

## **basic-mod2**

### ***Description***
A new modular challenge! <br>
Download the message [here](https://artifacts.picoctf.net/c/499/message.txt). <br>
Take each number mod 41 and find the modular inverse for the result. Then map to the following character set: 1-26 are the alphabet, 27-36 are the decimal digits, and 37 is an underscore. <br>
Wrap your decrypted message in the picoCTF flag format (i.e. `picoCTF{decrypted_message}`)
<details>
    <summary>Hint 1</summary>
    Do you know what the modular inverse is?
</details>
<details>
    <summary>Hint 2</summary>
    The inverse modulo <em>z</em> of <em>x</em> is the number, <em>y</em> that when multiplied by <em>x</em> is 1 modulo <em>z</em>
</details>
<details>
    <summary>Hint 3</summary>
    It's recommended to use a tool to find the modular inverses
</details>

### ***Writeup***
Make a [python script](./Cryptography/basic-mod2/basic_mod2.py) that will parse the text file and mod every number and then find the modular inverse using `pow(a,-1,x)`.

`message.txt`:
```
└─$ cat message.txt
268 413 110 190 426 419 108 229 310 379 323 373 385 236 92 96 169 321 284 185 154 137 186
```
output of `basic_mod2.py`:
```
└─$ python3 basic_mod2.py
picoCTF{1NV3R53LY_H4RD_C680BDC1}
```

Flag: `picoCTF{1NV3R53LY_H4RD_C680BDC1}`

## **credstuff**

### ***Description***
We found a leak of a blackmarket website's login credentials. Can you find the password of the user `cultiris` and successfully decrypt it? <br>
Download the leak [here](https://artifacts.picoctf.net/c/534/leak.tar). <br>
The first user in `usernames.txt` corresponds to the first password in `passwords.txt`. The second user corresponds to the second password, and so on.
<details>
    <summary>Hint 1</summary>
    Maybe other passwords will have hints about the leak?
</details>

### ***Writeup***

First thing to do is extract the tar file using `tar -xvf leak.tar` and then change directory into the extracted folder.

```
└─$ tar -xvf leak.tar
leak/
leak/passwords.txt
leak/usernames.txt
```

Use `grep -n` to not only find the user `cultiris` in `usernames.txt`, but also the line number of that user in the text file (this only works if the first user and the first password is on line 1 of their respective files).

```
└─$ grep -n cultiris usernames.txt
378:cultiris
```

Then, use `sed -n NUMp`, where NUM is the line number, and `p` to print the contents at that line number.

```
└─$ sed -n '378p' < passwords.txt
cvpbPGS{P7e1S_54I35_71Z3}
```

This looks like the flag, but isn't the flag since it does not start with picoCTF. It is actually encrypted in ROT13, so the last step is to transform the password.

```
└─$ sed -n '378p' < passwords.txt | tr 'A-Za-z' 'N-ZA-Mn-za-m'
picoCTF{C7r1F_54V35_71M3}
```

Flag: `picoCTF{1NV3R53LY_H4RD_C680BDC1}`

## **morse-code**

### ***Description***
Morse code is well known. Can you decrypt this? <br>
Download the file [here](https://artifacts.picoctf.net/c/235/morse_chal.wav). <br>
Wrap your answer with picoCTF{}, put underscores in place of pauses, and use all lowercase.
<details>
    <summary>Hint 1</summary>
    Audacity is a really good program to analyze morse code audio.
</details>

### ***Writeup***
After analyzing the wav file using Audacity, I can see that the waveform is split by either short or long waves. The short ones are dots and the long ones are dashes. After writing down the morse code, I used an [online morse code translator](https://morsecode.world/international/translator.html) to convert the message.

```
└─$ audacity morse_chal.wav
```

![morse_code](./Cryptography/morse-code/morse_code.png)

```
.-- .... ....- --... / .... ....- --... .... / ----. ----- -.. / .-- ..--- ----- ..- ----. .... --...
```
morse code: `WH47 H47H 90D W20U9H7`

```
└─$ python3
Python 3.9.10 (main, Feb 22 2022, 13:54:07)
[GCC 11.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> "picoCTF{" + "WH47 H47H 90D W20U9H7".lower().replace(" ", "_") + "}"
'picoCTF{wh47_h47h_90d_w20u9h7}'
>>>
```

Flag: `picoCTF{wh47_h47h_90d_w20u9h7}`

## **rail-fence**

### ***Description***
A type of transposition cipher is the rail fence cipher, which is described [here](https://en.wikipedia.org/wiki/Rail_fence_cipher). Here is one such cipher encrypted using the rail fence with 4 rails. Can you decrypt it? <br>
Download the message [here](https://artifacts.picoctf.net/c/275/message.txt). <br>
Put the decoded message in the picoCTF flag format, `picoCTF{decoded_message}`.
<details>
    <summary>Hint 1</summary>
    Once you've understood how the cipher works, it's best to draw it out yourself on paper
</details>

### ***Writeup***
It is really tedious to do by hand since you have to take into account of padding the plaintext, so it is better to use an online cracking tool such as the one [here](https://www.boxentriq.com/code-breaking/rail-fence-cipher). Giving 4 rails should give a result.

```
T     a           _     7     N     6     D     E     7
 h   l g   : W   3 D   _ H   3 C   3 1   N _   _ B   D 4
  e f     s   H R   0 5   3 F   3 8   N 4   3 D   4 7
         i     3     3     _     _     _     N     C
```

Flag: `picoCTF{WH3R3_D035_7H3_F3NC3_8361N_4ND_3ND_EB4C7D74}`

## **substitution0**

### ***Description***
A message has come in but it seems to be all scrambled. Luckily it seems to have the key at the beginning. Can you crack this substitution cipher? <br>
Download the message [here](https://artifacts.picoctf.net/c/379/message.txt).
<details>
    <summary>Hint 1</summary>
    Try a frequency attack. An online tool might help.
</details>

### ***Writeup***
Make a [python script](./Cryptography/substitution0/substitution0.py) that will take the first line of the message and use it as the substitution key.

`message.txt`:
```
└─$ cat message.txt
EKSZJTCMXOQUDYLFABGPHNRVIW

Mjbjhfly Ujcbeyz eblgj, rxpm e cbenj eyz gpepjui exb, eyz kblhcmp dj pmj kjjpuj
tbld e cuegg segj xy rmxsm xp reg jysulgjz. Xp reg e kjehpxthu gsebekejhg, eyz, ep
pmep pxdj, hyqylry pl yephbeuxgpg—lt slhbgj e cbjep fbxwj xy e gsxjypxtxs flxyp
lt nxjr. Pmjbj rjbj prl blhyz kuesq gflpg yjeb lyj jvpbjdxpi lt pmj kesq, eyz e
ulyc lyj yjeb pmj lpmjb. Pmj gseujg rjbj jvsjjzxycui mebz eyz culggi, rxpm euu pmj
effjebeysj lt khbyxgmjz cluz. Pmj rjxcmp lt pmj xygjsp reg njbi bjdebqekuj, eyz,
peqxyc euu pmxycg xypl slygxzjbepxly, X slhuz mebzui kuedj Ohfxpjb tlb mxg lfxyxly
bjgfjspxyc xp.

Pmj tuec xg: fxslSPT{5HK5717H710Y_3N0UH710Y_59533E2J}
```
output of `substitution0.py`:
```
└─$ python3 substitution0.py
EKSZJTCMXOQUDYLFABGPHNRVIW

Hereupon Legrand arose, with a grave and stately air, and brought me the beetle
from a glass case in which it was enclosed. It was a beautiful scarabaeus, and, at
that time, unknown to naturalists—of course a great prize in a scientific point
of view. There were two round black spots near one extremity of the back, and a
long one near the other. The scales were exceedingly hard and glossy, with all the
appearance of burnished gold. The weight of the insect was very remarkable, and,
taking all things into consideration, I could hardly blame Jupiter for his opinion
respecting it.

The flag is: picoCTF{5UB5717U710N_3V0LU710N_59533A2E}
```

Flag: `picoCTF{5UB5717U710N_3V0LU710N_59533A2E}`

## **substitution1**

### ***Description***
A second message has come in the mail, and it seems almost identical to the first one. Maybe the same thing will work again.
Download the message [here](https://artifacts.picoctf.net/c/414/message.txt).
<details>
    <summary>Hint 1</summary>
    Try a frequency attack
</details>
<details>
    <summary>Hint 2</summary>
    Do the punctuation and the individual words help you make any substitutions?
</details>

### ***Writeup***
Make a [python script](./Cryptography/substitution1/substitution1.py) and slowly replace letters. It started with knowing that the last sentence should have the string `picoCTF{` to knowing that the sentence should include `the flag is: picoCTF{`, and then figuring out that the message has to do with talking about CTFs. It was a lot of replacing letter by letter.

Quick note: since it's a substitution cipher which means each letter maps to another letter, it's better to use a hashmap (in this case a dictionary for python) since it has a lookup time of O(1), and it's better than having 26 if statements.

`message.txt`:
```
└─$ cat message.txt
IECj (jqfue cfu ixzelus eqs coxa) xus x emzs fc ifrzlesu jsiludem ifrzsededfy. Ifyesjexyej xus zusjsyesk hdeq x jse fc iqxoosyasj hqdiq esje eqsdu iusxedgdem, esiqydixo (xyk affaodya) jpdooj, xyk zuftosr-jfogdya xtdodem. Iqxoosyasj ljlxoom ifgsu x ylrtsu fc ixesafudsj, xyk hqsy jfogsk, sxiq mdsokj x jeudya (ixoosk x coxa) hqdiq dj jltrdeesk ef xy fyodys jifudya jsugdis. IECj xus x ausxe hxm ef osxuy x hdks xuuxm fc ifrzlesu jsiludem jpdooj dy x jxcs, osaxo sygdufyrsye, xyk xus qfjesk xyk zoxmsk tm rxym jsiludem auflzj xuflyk eqs hfuok cfu cly xyk zuxiedis. Cfu eqdj zuftosr, eqs coxa dj: zdifIEC{CU3NL3YIM_4774IP5_4U3_I001_4871S6CT}
```
output of `substitution1.py`:
```
└─$ python3 substitution1.py
CTFs (short for capture the flag) are a type of computer security competition. Contestants are presented with a set of challenges which test their creativity, technical (and googling) skills, and problem-solving ability. Challenges usually cover a number of categories, and when solved, each yields a string (called a flag) which is submitted to an online scoring service. CTFs are a great way to learn a wide array of computer security skills in a safe, legal environment, and are hosted and played by many security groups around the world for fun and practice. For this problem, the flag is: picoCTF{FR3QU3NCY_4774CK5_4R3_C001_4871E6FB}
```

Flag: `picoCTF{FR3QU3NCY_4774CK5_4R3_C001_4871E6FB}`

## **substitution2**

### ***Description***
It seems that another encrypted message has been intercepted. The encryptor seems to have learned their lesson though and now there isn't any punctuation! Can you still crack the cipher? <br>
Download the message [here](https://artifacts.picoctf.net/c/107/message.txt).
<details>
    <summary>Hint 1</summary>
    Try refining your frequency attack, maybe analyzing groups of letters would improve your results?
</details>

### ***Writeup***
Make a [python script](./Cryptography/substitution2/substitution2.py) and slowly replace letters. It started with knowing that the last sentence should have the string `picoCTF{` to knowing that the sentence should include `theflagispicoCTF{`, and then guessing what some of the words might be using context clues. It was a lot of replacing letter by letter.

`message.txt`:
```
└─$ cat message.txt
gvjwjjoeugujajwqxzgvjwkjxxjugqfxeuvjivecvumvzzxmzbpsgjwujmswegrmzbpjgegezhuehmxsiehcmrfjwpqgwezgqhisumrfjwmvqxxjhcjgvjujmzbpjgegezhunzmsupwebqwexrzhurugjbuqibeheugwqgezhnshiqbjhgqxukvemvqwjajwrsujnsxqhibqwdjgqfxjudexxuvzkjajwkjfjxejajgvjpwzpjwpswpzujznqvecvumvzzxmzbpsgjwujmswegrmzbpjgegezheuhzgzhxrgzgjqmvaqxsqfxjudexxufsgqxuzgzcjgugsijhguehgjwjugjiehqhijomegjiqfzsgmzbpsgjwumejhmjijnjhueajmzbpjgegezhuqwjzngjhxqfzwezsuqnnqewuqhimzbjizkhgzwshhehcmvjmdxeuguqhijojmsgehcmzhnecumwepguznnjhujzhgvjzgvjwvqhieuvjqaexrnzmsujizhjopxzwqgezhqhiebpwzaeuqgezhqhizngjhvqujxjbjhguznpxqrkjfjxejajqmzbpjgegezhgzsmvehczhgvjznnjhueajjxjbjhguznmzbpsgjwujmswegreugvjwjnzwjqfjggjwajvemxjnzwgjmvjaqhcjxeubgzugsijhguehqbjwemqhvecvumvzzxunswgvjwkjfjxejajgvqgqhshijwugqhiehcznznnjhueajgjmvhelsjueujuujhgeqxnzwbzshgehcqhjnnjmgeajijnjhujqhigvqggvjgzzxuqhimzhnecswqgezhnzmsujhmzshgjwjiehijnjhueajmzbpjgegezhuizjuhzgxjqiugsijhgugzdhzkgvjewjhjbrqujnnjmgeajxrqugjqmvehcgvjbgzqmgeajxrgvehdxedjqhqggqmdjwpemzmgneuqhznnjhueajxrzwejhgjivecvumvzzxmzbpsgjwujmswegrmzbpjgegezhgvqgujjdugzcjhjwqgjehgjwjugehmzbpsgjwumejhmjqbzhcvecvumvzzxjwugjqmvehcgvjbjhzscvqfzsgmzbpsgjwujmswegrgzpelsjgvjewmswezuegrbzgeaqgehcgvjbgzjopxzwjzhgvjewzkhqhijhqfxehcgvjbgzfjggjwijnjhigvjewbqmvehjugvjnxqceupemzMGN{H6W4B_4H41R515_15_73I10S5_8J1FN808}
```
output of `substitution2.py`:
```
└─$ python3 substitution2.py
thereexistseveralotherwellestablishedhighschoolcomputersecuritycompetitionsincludingcyberpatriotanduscyberchallengethesecompetitionsfocusprimarilyonsystemsadministrationfundamentalswhichareveryusefulandmarketableskillshoweverwebelievetheproperpurposeofahighschoolcomputersecuritycompetitionisnotonlytoteachvaluableskillsbutalsotogetstudentsinterestedinandexcitedaboutcomputersciencedefensivecompetitionsareoftenlaboriousaffairsandcomedowntorunningchecklistsandexecutingconfigscriptsoffenseontheotherhandisheavilyfocusedonexplorationandimprovisationandoftenhaselementsofplaywebelieveacompetitiontouchingontheoffensiveelementsofcomputersecurityisthereforeabettervehiclefortechevangelismtostudentsinamericanhighschoolsfurtherwebelievethatanunderstandingofoffensivetechnizuesisessentialformountinganeffectivedefenseandthatthetoolsandconfigurationfocusencounteredindefensivecompetitionsdoesnotleadstudentstoknowtheirenemyaseffectivelyasteachingthemtoactivelythinklikeanattackerpicoctfisanoffensivelyorientedhighschoolcomputersecuritycompetitionthatseekstogenerateinterestincomputerscienceamonghighschoolersteachingthemenoughaboutcomputersecuritytopizuetheircuriositymotivatingthemtoexploreontheirownandenablingthemtobetterdefendtheirmachinestheflagispicoCTF{N6R4M_4N41Y515_15_73D10U5_8E1BF808}
```

Flag: `picoCTF{N6R4M_4N41Y515_15_73D10U5_8E1BF808}`

## **transposition-trial**

### ***Description***
Our data got corrupted on the way here. Luckily, nothing got replaced, but every block of 3 got scrambled around! The first word seems to be three letters long, maybe you can use that to recover the rest of the message. <br>
Download the corrupted message [here](https://artifacts.picoctf.net/c/459/message.txt).
<details>
    <summary>Hint 1</summary>
    Split the message up into blocks of 3 and see how the first block is scrambled
</details>

### ***Writeup***
Analyzing the corrupted message it seems that for every block of three characters, the first characters is moved to the end (so instead of 1 2 3 it got corrupted to 2 3 1). Make a [python script](./Cryptography/transposition-trial/transposition-trial.py) that will check every third character and move it two places back.

```
└─$ python3 transposition-trial.py
The flag is picoCTF{7R4N5P051N6_15_3XP3N51V3_5C82A0E0}
```

Flag: `picoCTF{7R4N5P051N6_15_3XP3N51V3_5C82A0E0}`

## **Vigenere**

### ***Description***
Can you decrypt this message?
Decrypt this [message](https://artifacts.picoctf.net/c/527/cipher.txt) using this key "CYLAB".
<details>
    <summary>Hint 1</summary>
    https://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher
</details>

### ***Writeup***
Make a [python script](./Cryptography/Vigenere/vigenere.py) that will do the Vigenere Cipher. Used the [geeksforgeeks](https://www.geeksforgeeks.org/vigenere-cipher/) page for code reference and [dcode.fr](https://www.dcode.fr/vigenere-cipher) to verify.

`message.txt`:
```
└─$ cat cipher.txt
rgnoDVD{O0NU_WQ3_G1G3O3T3_A1AH3S_a23a13a5}
```
output of `vigenere.py`:
```
└─$ python3 vigenere.py cipher.txt CYLAB
picoCTF{D0NT_US3_V1G3N3R3_C1PH3R_y23c13p5}
```

# **Forensics**
- [Enhance!](./picoCTF_2022.md#Enhance)
- [File types](./picoCTF_2022.md#File-types)
- [Lookey here](./picoCTF_2022.md#Lookey-here)
- [Packets Primer](./picoCTF_2022.md#Packets-Primer)
- [Redaction gone wrong](./picoCTF_2022.md#Redaction-gone-wrong)
- [Sleuthkit Intro](./picoCTF_2022.md#Sleuthkit-Intro)

## **Enhance!**

### ***Description***
Download this image file and find the flag. <br>
- [Download image file](https://artifacts.picoctf.net/c/139/drawing.flag.svg)

### ***Writeup***
First I tried viewing the SVG using eog (Eye of Gnome), but sadly even after viewing the image under 2000x magnification I was unable to find anything at the center. Therefore, I tried another tool called InkScape, and viewed it under 25600x magnification. I was able to see something within the very tiny black dot at the center of the image, but I am unable to figure out what it is. I then opened the Document Properties menu (<kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>D</kbd>) and changed the scale of the document from 1.0 to 0.1, which allowed me to see the flag.

The alternative to getting the string is to cat the SVG and analyze every text and try to piece it together.

Starting InkScape on `drawing.flag.svg`:
```
└─$ inkscape drawing.flag.svg
```

![enhance](./Forensics/Enhance!/enhance.png)

Flag: `picoCTF{3nh4nc3d_6783cc46}`

## **File types**

### ***Description***
This file was found among some files marked confidential but my pdf reader cannot read it, maybe yours can. <br>
You can download the file from [here](https://artifacts.picoctf.net/c/326/Flag.pdf).
<details>
    <summary>Hint 1</summary>
    Remember that some file types can contain and nest other files
</details>

### ***Writeup***
Downloading and then running `file Flag.pdf` shows that it's a shell archive text, and reading the comments at the top of the file shows that to run a shell archive (shar) file you do `sh FILE`.

```
└─$ file Flag.pdf
Flag.pdf: shell archive text
```

```
└─$ cat Flag.pdf
#!/bin/sh
# This is a shell archive (produced by GNU sharutils 4.15.2).
# To extract the files from this archive, save it to some FILE, remove
# everything before the '#!/bin/sh' line above, then type 'sh FILE'.
#
...
```

Running `sh Flag.pdf` will extract a file to the current directory called `flag`. If extracting errors and says `uudecode: not found`, install `sharutils` package using `sudo apt install sharutils`.

```
└─$ sh Flag.pdf
x - created lock directory _sh00048.
x - extracting flag (text)
x - removed lock directory _sh00048.
```

```
└─$ file *
flag:     current ar archive
Flag.pdf: shell archive text
```

The rest of this is really tedious and extracting nested files.

```
└─$ ar -xv flag && file *
x - flag
flag:     cpio archive
Flag.pdf: shell archive text
```

```
└─$ cpio -iuv < flag && file *
flag
2 blocks
flag:     bzip2 compressed data, block size = 900k
Flag.pdf: shell archive text
```

```
└─$ bzip2 -dv flag && file *
bzip2: Can't guess original name for flag -- using flag.out
  flag:    done
flag.out: gzip compressed data, was "flag", last modified: Tue Mar 15 06:50:44 2022, from Unix, original size modulo 2^32 327
Flag.pdf: shell archive text
```

```
└─$ gunzip -vS .out flag.out && file *
flag.out:        -1.5% -- replaced with flag
flag:     lzip compressed data, version: 1
Flag.pdf: shell archive text
```

Have to install using `sudo apt install lzip`:
```
└─$ lzip -dv flag && file *
lzip: Can't guess original name for 'flag' -- using 'flag.out'
  flag: done
flag.out: LZ4 compressed data (v1.4+)
Flag.pdf: shell archive text
```

Have to install using `sudo apt install lz4`
```
└─$ unlz4 -v flag.out flag && mv flag flag.out && file *
*** LZ4 command line interface 64-bits v1.9.3, by Yann Collet ***
flag.out             : decoded 264 bytes
flag.out: LZMA compressed data, non-streamed, size 253
Flag.pdf: shell archive text
```

```
└─$ unlzma -vS .out flag.out && file *
flag.out (1/1)
  100 %               264 B / 253 B = 1.043
flag:     lzop compressed data - version 1.040, LZO1X-1, os: Unix
Flag.pdf: shell archive text
```

Have to install using `sudo apt install lzop`
```
└─$ lzop -dvff flag && file *
decompressing flag into flag.raw
flag:     lzop compressed data - version 1.040, LZO1X-1, os: Unix
Flag.pdf: shell archive text
flag.raw: lzip compressed data, version: 1
```

```
└─$ lzip -dv flag.raw && file *
lzip: Can't guess original name for 'flag.raw' -- using 'flag.raw.out'
  flag.raw: done
flag:         lzop compressed data - version 1.040, LZO1X-1, os: Unix
Flag.pdf:     shell archive text
flag.raw.out: XZ compressed data, checksum CRC64
```

```
└─$ unxz -vS .out flag.raw.out && file *
flag.raw.out (1/1)
  100 %               152 B / 110 B = 1.382
flag:     lzop compressed data - version 1.040, LZO1X-1, os: Unix
Flag.pdf: shell archive text
flag.raw: ASCII text
```

Finally reached the end after 10 decompressions (I hate this). Printing teh contents of the flag.raw ASCII text file shows this:
```
└─# cat flag.raw
7069636f4354467b66316c656e406d335f6d406e3170756c407431306e5f
6630725f3062326375723137795f33343765616536357d0a
```

All of that and it's still not the flag?? Looking at the string carefully though, every character is from 0-f, so it's most likely in hex. Converting from hex to ASCII should give the correct flag.

```
└─$ cat flag.raw | xxd -r -p
picoCTF{f1len@m3_m@n1pul@t10n_f0r_0b2cur17y_347eae65}
```

Flag: `picoCTF{f1len@m3_m@n1pul@t10n_f0r_0b2cur17y_347eae65}`

## **Lookey here**

### ***Description***
Attackers have hidden information in a very large mass of data in the past, maybe they are still doing it. <br>
Download the data [here](https://artifacts.picoctf.net/c/297/anthem.flag.txt).
<details>
    <summary>Hint 1</summary>
    Download the file and search for the flag based on the known prefix.
</details>

### ***Writeup***
Run `grep picoCTF{ anthem.flag.txt` in the terminal.

```
└─$ grep picoCTF{ anthem.flag.txt
      we think that the men of picoCTF{gr3p_15_@w3s0m3_4554f5f5}
```

Flag: `picoCTF{gr3p_15_@w3s0m3_4554f5f5}`

## **Packets Primer**

### ***Description***
Download the packet capture file and use packet analysis software to find the flag.
- [Download packet capture](https://artifacts.picoctf.net/c/202/network-dump.flag.pcap)
<details>
    <summary>Hint 1</summary>
    Wireshark, if you can install and use it, is probably the most beginner friendly packet analysis software product.
</details>

### ***Writeup***
Opening up the .pcap file using Wireshark and analyzing all the packets, the 4th packet has bytes that when converted to ASCII gives the flag.

Starting Wireshark on `network-dump.flag.pcap`:
```
└─$ wireshark network-dump.flag.pcap
```

![packets_primer](./Forensics/Packets_Primer/packets_primer.png)

Flag: `picoCTF{p4ck37_5h4rk_d0565941}`

## **Redaction gone wrong**

### ***Description***
Now you DON’T see me. <br>
This [report](https://artifacts.picoctf.net/c/264/Financial_Report_for_ABC_Labs.pdf) has some critical data in it, some of which have been redacted correctly, while some were not. Can you find an important key that was not redacted properly?
<details>
    <summary>Hint 1</summary>
    How can you be sure of the redaction?
</details>

### ***Writeup***
I recommend using a tool called `pdftotext` which can be found in `poppler-utils`, so go ahead and install that using `sudo apt install poppler-utils`.

```
└─$ pdftotext -v Financial_Report_for_ABC_Labs.pdf
pdftotext version 20.09.0
Copyright 2005-2020 The Poppler Developers - http://poppler.freedesktop.org
Copyright 1996-2011 Glyph & Cog, LLC
```

Running `pdftotext` will copy the contents in the pdf to a separate text file, so printing the text file should display everything, including all the text that was "redacted" in the PDF.

```
└─$ cat Financial_Report_for_ABC_Labs.txt
Financial Report for ABC Labs, Kigali, Rwanda for the year 2021.
Breakdown - Just painted over in MS word.

Cost Benefit Analysis
Credit Debit
This is not the flag, keep looking
Expenses from the
picoCTF{C4n_Y0u_S33_m3_fully}
Redacted document.
```

Flag: `picoCTF{C4n_Y0u_S33_m3_fully}`

## **Sleuthkit Intro**

### ***Description***
Download the disk image and use `mmls` on it to find the size of the Linux partition. Connect to the remote checker service to check your answer and get the flag. <br>
Note: if you are using the webshell, download and extract the disk image into `/tmp` not your home directory. <br>
- [Download disk image](https://artifacts.picoctf.net/c/114/disk.img.gz)
- Access checker program: `nc saturn.picoctf.net 52279`

### ***Writeup***

Not much to this challenge. Just extract the file and run `mmls` on it.
```
└─$ gunzip -v disk.img.gz
disk.img.gz:     71.7% -- replaced with disk.img
```

```
└─$ mmls disk.img
DOS Partition Table
Offset Sector: 0
Units are in 512-byte sectors

      Slot      Start        End          Length       Description
000:  Meta      0000000000   0000000000   0000000001   Primary Table (#0)
001:  -------   0000000000   0000002047   0000002048   Unallocated
002:  000:000   0000002048   0000204799   0000202752   Linux (0x83)
```

```
└─$ nc saturn.picoctf.net 52279
What is the size of the Linux partition in the given disk image?
Length in sectors: 202752
202752
Great work!
picoCTF{mm15_f7w!}
```

Flag: `picoCTF{mm15_f7w!}`

# **Reverse Engineering**
- [file-run1](./picoCTF_2022.md#file-run1)
- [file-run2](./picoCTF_2022.md#file-run2)
- [GDB Test Drive](./picoCTF_2022.md#GDB-Test-Drive)
- [patchme.py](./picoCTF_2022.md#patchme.py)

## **file-run1**

### ***Description***
A program has been provided to you, what happens if you try to run it on the command line? <br>
Download the program [here](https://artifacts.picoctf.net/c/311/run).
<details>
    <summary>Hint 1</summary>
    To run the program at all, you must make it executable (i.e. `$ chmod +x run`)
</details>
<details>
    <summary>Hint 2</summary>
    Try running it by adding a '.' in front of the path to the file (i.e. `$ ./run`)
</details>

### ***Writeup***
Give permission to execute `run` (you might not need to do this):
```
└─$ chmod +x run
```
Execute the `run` program in the current directory:
```
└─$ ./run
The flag is: picoCTF{U51N6_Y0Ur_F1r57_F113_102c30db}
```

Flag: `picoCTF{U51N6_Y0Ur_F1r57_F113_102c30db}`

## **file-run2**

### ***Description***
Another program, but this time, it seems to want some input. What happens if you try to run it on the command line with input "Hello!"?
Download the program [here](https://artifacts.picoctf.net/c/354/run).
<details>
    <summary>Hint 1</summary>
    Try running it and add the phrase "Hello!" with a space in front (i.e. "./run Hello!")
</details>

### ***Writeup***
Give permission to execute `run` and run the program with the argument "Hello!":
```
└─$ ./run Hello!
The flag is: picoCTF{F1r57_4rgum3n7_4653b5f6}
```

Flag: `picoCTF{F1r57_4rgum3n7_4653b5f6}`

## **GDB Test Drive**

### ***Description***
Can you get the flag? <br>
Download this binary. <br>
Here's the test drive instructions:
- `$ chmod +x gdbme`
- `$ gdb gdbme`
- `(gdb) layout asm`
- `(gdb) break *(main+99)`
- `(gdb) run`
- `(gdb) jump *(main+104)`

### ***Writeup***
Give permission to execute `gdbme` and run gdb on `gdbme`. Bring out the assembly code layout, set a breakpoint at the sleep call in the main function at address `(main+99)`, run the program which will stop at the sleep call, and the jump to the next instruction. What the gdb instructions are doing is it's jumping over the infinite sleep, whereas running the program normally will just have it be stuck on the sleep.

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│   0x5555555552c7 <main>           endbr64                                                                                         │
│   0x5555555552cb <main+4>         push   %rbp                                                                                     │
│   0x5555555552cc <main+5>         mov    %rsp,%rbp                                                                                │
│   0x5555555552cf <main+8>         sub    $0x50,%rsp                                                                               │
│   0x5555555552d3 <main+12>        mov    %edi,-0x44(%rbp)                                                                         │
│   0x5555555552d6 <main+15>        mov    %rsi,-0x50(%rbp)                                                                         │
│   0x5555555552da <main+19>        mov    %fs:0x28,%rax                                                                            │
│   0x5555555552e3 <main+28>        mov    %rax,-0x8(%rbp)                                                                          │
│   0x5555555552e7 <main+32>        xor    %eax,%eax                                                                                │
│   0x5555555552e9 <main+34>        movabs $0x4c75257240343a41,%rax                                                                 │
│   0x5555555552f3 <main+44>        movabs $0x4362383846336235,%rdx                                                                 │
│   0x5555555552fd <main+54>        mov    %rax,-0x30(%rbp)                                                                         │
│   0x555555555301 <main+58>        mov    %rdx,-0x28(%rbp)                                                                         │
│   0x555555555305 <main+62>        movabs $0x6430624760433530,%rax                                                                 │
│   0x55555555530f <main+72>        movabs $0x4e3432656065365f,%rdx                                                                 │
│   0x555555555319 <main+82>        mov    %rax,-0x20(%rbp)                                                                         │
│   0x55555555531d <main+86>        mov    %rdx,-0x18(%rbp)                                                                         │
│   0x555555555321 <main+90>        movb   $0x0,-0x10(%rbp)                                                                         │
│   0x555555555325 <main+94>        mov    $0x186a0,%edi                                                                            │
│B+ 0x55555555532a <main+99>        call   0x555555555110 <sleep@plt>                                                               │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
native No process In:                                                                                                   L??   PC: ?? 
(gdb) break *(main+99)
Breakpoint 1 at 0x132a
(gdb) run
Starting program: /mnt/c/Users/jason/Documents/GitHub/picoCTF_2022/Reverse_Engineering/GDB_Test_Drive/gdbme

Breakpoint 1, 0x000055555555532a in main ()
(gdb) jump *(main+104)
Continuing at 0x55555555532f.
picoCTF{d3bugg3r_dr1v3_50e616ac}
(gdb) ior 1 (process 16883) exited normally]
```

Flag: `picoCTF{d3bugg3r_dr1v3_50e616ac}`

## **patchme.py**

### ***Description***
Can you get the flag? <br>
Run this [Python program](https://artifacts.picoctf.net/c/389/patchme.flag.py) in the same directory as this [encrypted flag](https://artifacts.picoctf.net/c/389/flag.txt.enc).

### ***Writeup***
Running `patchme.flag.py` will prompt the user for a password, which we do not have at the moment. After inspecting the python code however, lines 18-22 checks that the input that is written to `user_pw` matches a series of split strings. Piecing together the strings produces `ak98-=90adfjhgj321sleuth9000`, which is the password. Running `patchme.flag.py` again with the password gives the flag.

```
└─$ python3 patchme.flag.py
Please enter correct password for flag: ak98-=90adfjhgj321sleuth9000
Welcome back... your flag, user:
picoCTF{p47ch1ng_l1f3_h4ck_c3daefb9}
```

Flag: `picoCTF{p47ch1ng_l1f3_h4ck_c3daefb9}`

## **Safe Opener**

### ***Description***
Can you open this safe? <br>
I forgot the key to my safe but this [program](https://artifacts.picoctf.net/c/463/SafeOpener.java) is supposed to help me with retrieving the lost key. Can you help me unlock my safe? <br>
Put the password you recover into the picoCTF flag format like:
`picoCTF{password}`

### ***Writeup***
First, if running `java SafeOpener` does not work because the JDK is not installed, I recommend doing `sudo apt install default-jdk` which should install openjdk 11.0 (you can verify this by doing `java --vesion`).

After looking at the java code, I notice that the input we pass into the program is stored as `key`, and then is converted to Base64 (because `encoder` is a Base64 encoder) and stored as `encodedkey`. Finally, it checks if `encodedkey` equals `cGwzYXMzX2wzdF9tM18xbnQwX3RoM19zYWYz` in the openSafe method. In other words, the string that we pass into the program when encoded in Base64 must be equal to `cGwzYXMzX2wzdF9tM18xbnQwX3RoM19zYWYz`. The easiest way to approach this is to decode the above string from Base64 to ASCII. The following python command should do the trick.

```
└─$ python3
Python 3.9.10 (main, Feb 22 2022, 13:54:07)
[GCC 11.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import base64
>>> encodedkey = "cGwzYXMzX2wzdF9tM18xbnQwX3RoM19zYWYz"
>>> base64.b64decode(encodedkey.encode('ascii')).decode('ascii')
'pl3as3_l3t_m3_1nt0_th3_saf3'
```
After getting the password, pass it back into the program to verify it's correct:
```
└─$ java SafeOpener.java
Enter password for the safe: pl3as3_l3t_m3_1nt0_th3_saf3
cGwzYXMzX2wzdF9tM18xbnQwX3RoM19zYWYz
Sesame open
```

Flag: `picoCTF{pl3as3_l3t_m3_1nt0_th3_saf3}`

# **Web Exploitation**
- [Includes](./picoCTF_2022.md#Includes)
- [Inspect HTML](./picoCTF_2022.md#Inspect-html)
- [Local Authority](./picoCTF_2022.md#Local-Authority)
- [Search source](./picoCTF_2022.md#Search-source)
- [Forbidden Paths](./picoCTF_2022.md#Forbidden-Paths)

## **Includes**

### ***Description***
Can you get the flag? <br>
Go to this [website](http://saturn.picoctf.net:54634/) and see what you can discover.
<details>
    <summary>Hint 1</summary>
    Is there more code than what the inspector initially shows?
</details>

### ***Writeup***
Inspect `style.css` and `script.js` for parts of the flag

`style.css`:
```css
body {
  background-color: lightblue;
}

/*  picoCTF{1nclu51v17y_1of2_  */
```
`script.js`:
```js
function greetings()
{
  alert("This code is in a separate file!");
}

//  f7w_2of2_df589022}
```

Flag: `picoCTF{1nclu51v17y_1of2_f7w_2of2_df589022}`

## **Inspect HTML**

### ***Description***
Can you get the flag? <br>
Go to this [website](http://saturn.picoctf.net:50920/) and see what you can discover.
<details>
    <summary>Hint 1</summary>
    What is the web inspector in web browsers?
</details>

### ***Writeup***
Inspect the HTML source code

`index.html`:
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>On Histiaeus</title>
  </head>
  <body>
    <h1>On Histiaeus</h1>
    <p>However, according to Herodotus, Histiaeus was unhappy having to stay in
       Susa, and made plans to return to his position as King of Miletus by 
       instigating a revolt in Ionia. In 499 BC, he shaved the head of his 
       most trusted slave, tattooed a message on his head, and then waited for 
       his hair to grow back. The slave was then sent to Aristagoras, who was 
       instructed to shave the slave's head again and read the message, which 
       told him to revolt against the Persians.</p>
    <br>
    <p> Source: Wikipedia on Histiaeus </p>
	<!--picoCTF{1n5p3t0r_0f_h7ml_1fd8425b}-->
  </body>
</html>
```

Flag: `picoCTF{1n5p3t0r_0f_h7ml_1fd8425b}`

## **Local Authority**

### ***Description***
Can you get the flag? <br>
Go to this [website](http://saturn.picoctf.net:65317/) and see what you can discover.
<details>
    <summary>Hint 1</summary>
    How is the password checked on this website?
</details>

### ***Writeup***
Inspect the HTML source code. Notice that the form is processed in login.php, so there are two ways of getting to login.php. Either give incorrect credentials or go to `http://saturn.picoctf.net:65317/login.php`. After inspecting the php, notice that `checkPassword` will return true if the username is `admin` and the password is `strongPassword098765`. Going back to the login site and giving the correct username and password will give the flag.

`login.php`:
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <link rel="stylesheet" href="style.css">
    <title>Secure Customer Portal</title>
  </head>
  <body>

    <h1>Secure Customer Portal</h1>
    
   <p>Only letters and numbers allowed for username and password.</p>
    
    <form role="form" action="login.php" method="post">
      <input type="text" name="username" placeholder="Username" required 
       autofocus></br>
      <input type="password" name="password" placeholder="Password" required>
      <button type="submit" name="login">Login</button>
    </form>
  </body>
</html>
```
`index.html`:
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <link rel="stylesheet" href="style.css">
    <title>Login Page</title>
  </head>
  <body>
    <script src="secure.js"></script>
    
    <p id='msg'></p>
    
    <form hidden action="admin.php" method="post" id="hiddenAdminForm">
      <input type="text" name="hash" required id="adminFormHash">
    </form>
    ...
```
`secure.js`:
```js
function checkPassword(username, password)
{
  if( username === 'admin' && password === 'strongPassword098765' )
  {
    return true;
  }
  else
  {
    return false;
  }
}
```
`admin.php`:
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <link rel="stylesheet" href="style.css">
    <title>Secure Customer Portal</title>
  </head>
  <body>
    picoCTF{j5_15_7r4n5p4r3n7_8086bcb1}  </body>
</html>
```
Flag: `picoCTF{j5_15_7r4n5p4r3n7_8086bcb1}`

## **Search source**

### ***Description***
The developer of this website mistakenly left an important artifact in the website source, can you find it? <br>
The website is [here](http://saturn.picoctf.net:58519/)
<details>
    <summary>Hint 1</summary>
    How could you mirror the website on your local machine so you could use more powerful tools for searching?
</details>

### ***Writeup***
Download the website as well as the dependencies using `wget -r`, which will recursively download all the files. After running `wget -r http://saturn.picoctf.net:58519/`, running `grep -r picoCTF{ saturn.picoctf.net\:58519/` to recursively search in the cloned directory showed a match in the `css/styles.css` file.

```
└─$ wget -r http://saturn.picoctf.net:58519/
```

```
└─$ grep -r picoCTF{ saturn.picoctf.net\:58519/
saturn.picoctf.net:58519/css/style.css:/** banner_main picoCTF{1nsp3ti0n_0f_w3bpag3s_869d23af} **/
```


Flag: `picoCTF{1nsp3ti0n_0f_w3bpag3s_869d23af}`

## **Forbidden Paths**

### ***Description***
Can you get the flag? <br>
Here's the [website](http://saturn.picoctf.net:52523/). <br>
We know that the website files live in `/usr/share/nginx/html/` and the flag is at `/flag.txt` but the website is filtering absolute file paths. Can you get past the filter to read the flag?

### ***Writeup***
On the webpage, notice that giving any of the filenames on the site (`divine-comedy.txt`, `oliver-twist.txt`, and `the-happy-prince.txt`) will print the contents of that file. For example, putting in `divine-comedy.txt` most likely will do `cat /usr/share/nginx/html/divine-comedy.txt`. Also notice that the first "file" on the list is `..`, and putting that in gives a blank page. This is a good thing, as it's trying to print the contents of `/usr/share/nginx/html/..`, which is just a directory.

Giving the input `..` will go back one directory, so the webpage will print `/usr/share/nginx/`. Giving the input `../..` will print `/usr/share/`, `../../..` will print `/usr/`, `../../../..` will print `/`, and finally `../../../../flag.txt` will print the contents of `/flag.txt`. This type of attack is called a [path traversal attack](https://en.wikipedia.org/wiki/Directory_traversal_attack).

Flag: `picoCTF{7h3_p47h_70_5ucc355_e73ad00d}`