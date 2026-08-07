class Solution:
    def lengthOfLastWord(self, s: str) -> int:
        for i in range(len(s)):
            l=s.split()
        if len(s)==1:
            return len(l[0])
        else:
            return len(l[-1])
