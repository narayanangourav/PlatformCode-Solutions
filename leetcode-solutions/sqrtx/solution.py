class Solution:
    def mySqrt(self, x: int) -> int:
        #self made code
        res = 1
        i = 1
        while res<=x:
            i+=1
            res = i*i
        return i-1
