with open('message.txt') as f:
    contents = f.read()
    ret = ''
    for i in contents.split():
        n = pow(int(i)%41, -1, 41)
        if n <= 26:
            ret += chr(n+64)
        elif 27 <= n <= 36:
            ret += str(n-27)
        else:
            ret += '_'
    ret = 'picoCTF{'+ret+'}'
    print(ret)