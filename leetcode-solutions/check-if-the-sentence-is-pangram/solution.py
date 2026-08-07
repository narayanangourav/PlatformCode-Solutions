class Solution:
    def checkIfPangram(self, sentence: str) -> bool:
        a=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        s=sentence
        s=s.lower()
        t=list(set(s))
        for j in range(0,len(t)-1):
            if t[j]==" ":
                t.pop(j)    
        for i in a:
            if i in t and len(t)==26:
                return True
            return False
