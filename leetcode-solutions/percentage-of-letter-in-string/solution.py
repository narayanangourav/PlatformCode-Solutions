class Solution:
    def percentageLetter(self, s: str, letter: str) -> int:
        dic={}
        val=1
        den=len(s)
        for i in range(0,len(s)):
            if s[i] not in dic:
                dic.update({s[i]: val})
            else:
                key=s[i]
                dic[key]=dic[key]+1
        for i in dic:
            if i==letter:
                v=dic[i]
                break
            else:
                v=0
        res=int(v/den*100)
        return(res)
