if __name__ == '__main__':
    s = input()
    print(True in [True if l.isalnum() else False for l in s])
    print(True in [True if l.isalpha() else False for l in s])
    print(True in [True if l.isdigit() else False for l in s])
    print(True in [True if l.islower() else False for l in s])
    print(True in [True if l.isupper() else False for l in s])
