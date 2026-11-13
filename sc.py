with open('channels.txt', mode='r') as file:
    data = file.readlines()
    data = list(map(lambda x: x[:-1], data))
    print(*data, sep=', ')