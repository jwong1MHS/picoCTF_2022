with open('message.txt') as f:
    letter_key = f.readline()
    contents = f.read()
    ret = ''
    letter_val = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    letter_map = {}

    for i in range(26):
        letter_map[letter_key[i]] = letter_val[i]

    for i in contents:
        if i.islower():
            ret += letter_map.get(i.upper()).lower()
        else:  
            if i in letter_map:
                ret += letter_map.get(i)
            else:
                ret += i
    print(letter_key + ret)