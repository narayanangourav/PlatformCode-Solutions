class Solution:
    def checkIfExist(self, arr: List[int]) -> bool:
        #self made code
        flag = 0
        z = len(arr)
        for i in range(0, z):
            if arr[i] != 0:
                x = arr[i]*2
                if (x in arr) and (x%2 == 0):
                    flag = 1
                    break
            elif arr[i] == 0:
                c = arr.copy()
                c.pop(i)
                x = arr[i]*2
                if (x in c) and (x%2 == 0):
                    flag = 1
                    break
            else:
                flag = 0
        if flag == 1:
            return True
        else:
            return False
