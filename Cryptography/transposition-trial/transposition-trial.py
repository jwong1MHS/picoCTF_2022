with open('message.txt') as f:
    contents = f.read()
    ret = ''

    for i in range(len(contents)):
        if i % 3 == 2:
            ret = ret[:i-2] + contents[i] + ret[i-2:]
        else:
            ret += contents[i]
    print(ret)
