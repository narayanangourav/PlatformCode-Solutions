def minion_game(string):
    # your code goes here 
    lent = len(string)
    v=['A','E','I','O','U']
    st, kt = 0, 0
    for i in range(lent):
        if string[i] not in v:
            st+=lent-i 
        else:
            kt+=lent-i
    if st>kt:
        print("Stuart", st)
    elif kt>st:
        print("Kevin", kt)
    else:
        print("Draw")
