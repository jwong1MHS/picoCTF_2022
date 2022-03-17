with open('message.txt') as f:
    contents = f.read()
    ret = ''
    for i in contents.split():
        n = int(i) % 37
        if n <= 25:
            ret += chr(n+65)
        elif 26 <= n <= 35:
            ret += str(n-26)
        else:
            ret += '_'
    ret = 'picoCTF{'+ret+'}'
    print(ret)
    g = open('flag.txt', 'w')
    g.write(ret+'\n')
    g.close()