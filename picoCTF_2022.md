# **Table of Contents**
- [Binary Exploitation](./picoCTF_2022.md#binary-exploitation)
- [Cryptography](./picoCTF_2022.md#cryptography)
- [Web Exploitation](./picoCTF_2022.md#web-exploitation)

# **Binary Exploitation**
- [basic-file-exploit](./picoCTF_2022.md#basic-file-exploit)

## **basic-file-exploit**
-----

### ***Description***
The program provided allows you to write to a file and read what you wrote from it. Try playing around with it and see if you can break it! <br>
Connect to the program with netcat: <br>
`$ nc saturn.picoctf.net 50366` <br>
The program's source code with the flag redacted can be downloaded [here](https://artifacts.picoctf.net/c/538/program-redacted.c).
<details>
    <summary>Hint 1</summary>
    Try passing in things the program doesn't expect. Like a string instead of a number.
</details>
<br>

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

# **Cryptography**
- [basic-mod1](./picoCTF_2022.md#basic-mod1)
- [basic-mod2](./picoCTF_2022.md#basic-mod2)
- [substitution0](./picoCTF_2022.md#substitution0)
- [substitution1](./picoCTF_2022.md#substitution1)
- [substitution2](./picoCTF_2022.md#substitution2)

## **basic-mod1**
-----

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
<br>

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
-----

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
<br>

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

## **substitution0**
-----

### ***Description***
A message has come in but it seems to be all scrambled. Luckily it seems to have the key at the beginning. Can you crack this substitution cipher? <br>
Download the message [here](https://artifacts.picoctf.net/c/379/message.txt).
<details>
    <summary>Hint 1</summary>
    Try a frequency attack. An online tool might help.
</details>
<br>

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
└─$ python3 substitution1.py
CTFs (short for capture the flag) are a type of computer security competition. Contestants are presented with a set of challenges which test their creativity, technical (and googling) skills, and problem-solving ability. Challenges usually cover a number of categories, and when solved, each yields a string (called a flag) which is submitted to an online scoring service. CTFs are a great way to learn a wide array of computer security skills in a safe, legal environment, and are hosted and played by many security groups around the world for fun and practice. For this problem, the flag is: picoCTF{FR3QU3NCY_4774CK5_4R3_C001_4871E6FB}
```

Flag: `picoCTF{5UB5717U710N_3V0LU710N_59533A2E}`

## **substitution1**
-----

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
<br>

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
-----

### ***Description***
It seems that another encrypted message has been intercepted. The encryptor seems to have learned their lesson though and now there isn't any punctuation! Can you still crack the cipher? <br>
Download the message [here](https://artifacts.picoctf.net/c/107/message.txt).
<details>
    <summary>Hint 1</summary>
    Try refining your frequency attack, maybe analyzing groups of letters would improve your results?
</details>
<br>

### ***Writeup***
Make a [python script](./Cryptography/substitution2/substitution2.py) and slowly replace letters. It started with knowing that the last sentence should have the string `picoCTF{` to knowing that the sentence should include `theflagispicoCTF{`, and then guessing what some of the words might be using context clues. It was a lot of replacing letter by letter.

`message.txt`:
```└─$ cat message.txt
gvjwjjoeugujajwqxzgvjwkjxxjugqfxeuvjivecvumvzzxmzbpsgjwujmswegrmzbpjgegezhuehmxsiehcmrfjwpqgwezgqhisumrfjwmvqxxjhcjgvjujmzbpjgegezhunzmsupwebqwexrzhurugjbuqibeheugwqgezhnshiqbjhgqxukvemvqwjajwrsujnsxqhibqwdjgqfxjudexxuvzkjajwkjfjxejajgvjpwzpjwpswpzujznqvecvumvzzxmzbpsgjwujmswegrmzbpjgegezheuhzgzhxrgzgjqmvaqxsqfxjudexxufsgqxuzgzcjgugsijhguehgjwjugjiehqhijomegjiqfzsgmzbpsgjwumejhmjijnjhueajmzbpjgegezhuqwjzngjhxqfzwezsuqnnqewuqhimzbjizkhgzwshhehcmvjmdxeuguqhijojmsgehcmzhnecumwepguznnjhujzhgvjzgvjwvqhieuvjqaexrnzmsujizhjopxzwqgezhqhiebpwzaeuqgezhqhizngjhvqujxjbjhguznpxqrkjfjxejajqmzbpjgegezhgzsmvehczhgvjznnjhueajjxjbjhguznmzbpsgjwujmswegreugvjwjnzwjqfjggjwajvemxjnzwgjmvjaqhcjxeubgzugsijhguehqbjwemqhvecvumvzzxunswgvjwkjfjxejajgvqgqhshijwugqhiehcznznnjhueajgjmvhelsjueujuujhgeqxnzwbzshgehcqhjnnjmgeajijnjhujqhigvqggvjgzzxuqhimzhnecswqgezhnzmsujhmzshgjwjiehijnjhueajmzbpjgegezhuizjuhzgxjqiugsijhgugzdhzkgvjewjhjbrqujnnjmgeajxrqugjqmvehcgvjbgzqmgeajxrgvehdxedjqhqggqmdjwpemzmgneuqhznnjhueajxrzwejhgjivecvumvzzxmzbpsgjwujmswegrmzbpjgegezhgvqgujjdugzcjhjwqgjehgjwjugehmzbpsgjwumejhmjqbzhcvecvumvzzxjwugjqmvehcgvjbjhzscvqfzsgmzbpsgjwujmswegrgzpelsjgvjewmswezuegrbzgeaqgehcgvjbgzjopxzwjzhgvjewzkhqhijhqfxehcgvjbgzfjggjwijnjhigvjewbqmvehjugvjnxqceupemzMGN{H6W4B_4H41R515_15_73I10S5_8J1FN808}
```
output of `substitution2.py`:
```
└─$ python3 substitution2.py
thereexistseveralotherwellestablishedhighschoolcomputersecuritycompetitionsincludingcyberpatriotanduscyberchallengethesecompetitionsfocusprimarilyonsystemsadministrationfundamentalswhichareveryusefulandmarketableskillshoweverwebelievetheproperpurposeofahighschoolcomputersecuritycompetitionisnotonlytoteachvaluableskillsbutalsotogetstudentsinterestedinandexcitedaboutcomputersciencedefensivecompetitionsareoftenlaboriousaffairsandcomedowntorunningchecklistsandexecutingconfigscriptsoffenseontheotherhandisheavilyfocusedonexplorationandimprovisationandoftenhaselementsofplaywebelieveacompetitiontouchingontheoffensiveelementsofcomputersecurityisthereforeabettervehiclefortechevangelismtostudentsinamericanhighschoolsfurtherwebelievethatanunderstandingofoffensivetechnizuesisessentialformountinganeffectivedefenseandthatthetoolsandconfigurationfocusencounteredindefensivecompetitionsdoesnotleadstudentstoknowtheirenemyaseffectivelyasteachingthemtoactivelythinklikeanattackerpicoctfisanoffensivelyorientedhighschoolcomputersecuritycompetitionthatseekstogenerateinterestincomputerscienceamonghighschoolersteachingthemenoughaboutcomputersecuritytopizuetheircuriositymotivatingthemtoexploreontheirownandenablingthemtobetterdefendtheirmachinestheflagispicoCTF{N6R4M_4N41Y515_15_73D10U5_8E1BF808}
```

Flag: `picoCTF{N6R4M_4N41Y515_15_73D10U5_8E1BF808}`

# **Web Exploitation**
- [Includes](./picoCTF_2022.md#includes)
- [Inspect HTML](./picoCTF_2022.md#inspect-html)

## **Includes**
-----

### ***Description***
Can you get the flag? <br>
Go to this [website](http://saturn.picoctf.net:54634/) and see what you can discover.
<details>
    <summary>Hint 1</summary>
    Is there more code than what the inspector initially shows?
</details>
<br>

### ***Writeup***
Inspect `style.css` and `script.js` for parts of the flag

`http://saturn.picoctf.net:54634/style.css`:
```
body {
  background-color: lightblue;
}

/*  picoCTF{1nclu51v17y_1of2_  */
```
`http://saturn.picoctf.net:54634/script.js`:
```
function greetings()
{
  alert("This code is in a separate file!");
}

//  f7w_2of2_df589022}
```

Flag: `picoCTF{1nclu51v17y_1of2_f7w_2of2_df589022}`

## **Inspect HTML**
-----

### ***Description***
Can you get the flag? <br>
Go to this [website](http://saturn.picoctf.net:50920/) and see what you can discover.
<details>
    <summary>Hint 1</summary>
    What is the web inspector in web browsers?
</details>
<br>

### ***Writeup***
Inspect the HTML source code

`view-source:http://saturn.picoctf.net:50920/`:
```
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