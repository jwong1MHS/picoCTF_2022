import sys

usage_msg = "Usage: "+ sys.argv[0] +" [file] [key]"

def generateKey(string, key):
    key = list(key)
    if len(string) == len(key):
        return(key)
    else:
        for i in range(len(string) -
                       len(key)):
            key.append(key[i % len(key)])
    return("" . join(key))

def originalText(cipher_text, key):
    orig_text = []
    key_counter = 0
    for i in range(len(cipher_text)):
        if cipher_text[i].isupper():
            x = (ord(cipher_text[i]) -
                ord(key[key_counter]) + 26) % 26
            x += ord('A')
            key_counter += 1
            orig_text.append(chr(x))
        elif cipher_text[i].islower():
            x = (ord(cipher_text[i].upper()) -
                ord(key[key_counter]) + 26) % 26
            x += ord('A')
            key_counter += 1
            orig_text.append(chr(x).lower())
        else:
            orig_text.append(cipher_text[i])
    return("" . join(orig_text))

if len(sys.argv) != 3:
    print(usage_msg)
    sys.exit(1)

with open('cipher.txt') as f:
    cipher_text = f.read()

key = generateKey(cipher_text, sys.argv[2])
print(originalText(cipher_text, key))