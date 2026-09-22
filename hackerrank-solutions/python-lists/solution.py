if __name__ == '__main__':
    N = int(input())
    listWeWant = []
    for _ in range(N) :
        action = input().split()
        if action[0].lower() == "insert" :
            listWeWant.insert(int(action[1]), int(action[2]))
        elif action[0].lower() == "append" :
            listWeWant.append(int(action[1]))
        elif action[0].lower() == "pop" :
            listWeWant.pop()
        elif action[0].lower() == "remove" :
            listWeWant.remove(int(action[1]))
        elif action[0].lower() == "reverse" :
            listWeWant.reverse()
        elif action[0].lower() == "sort" :
            listWeWant.sort()
        elif action[0].lower() == "print" :
            print(listWeWant)
        else :
            print("Something went wrong")
