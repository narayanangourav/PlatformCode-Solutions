class Solution:
    def reverseWords(self, s: str) -> str:
        s = s.split()  
        res = ""
        for i in reversed(range(len(s))):
            if s[i] != "":
                res += s[i] + " "  
        res = res.strip()  
        return (res)
