class Solution:
    def smallestEvenMultiple(self, n: int) -> int:
        if n>0 and n%2==0 and n%n==0:
            o=n
        else:
            o=2*n
        if n==1 or n==0:
            o=n*2
        return o
