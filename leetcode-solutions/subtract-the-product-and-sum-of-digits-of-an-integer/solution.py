class Solution:
    def subtractProductAndSum(self, n: int) -> int:
        n1=n
        pro=1
        ad=0
        while(n!=0):
            if n>0:
                pro*=(n%10)
                n=n//10
        while(n1!=0):
            if n1>0:
                ad+=(n1%10)
                n1=n1//10    
        return(pro-ad)
