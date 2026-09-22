if __name__ == '__main__':
    mark_list={}
    for _ in range(int(input())):
        name = input()
        score = float(input())
        mark_list.update({name: score})

    b = sorted(set(mark_list.values()))[1]
    for i in sorted(mark_list):
        if mark_list[i] == b:
            print(i)
