class Solution:
    def fizzBuzz(self, n: int) -> List[str]:
        l=[]
        for i in range(1,n+1):
            l.append(str(i))
        for i in range(0,n):
            if int(l[i])%3==0 and int(l[i])%5==0:
                l[i]="FizzBuzz"
            elif int(l[i])%3==0:
                l[i]="Fizz"
            elif int(l[i])%5==0:
                l[i]="Buzz"
            else:
                pass
        return l
