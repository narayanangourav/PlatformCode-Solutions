class Solution:
    def isPalindrome(self, x: int) -> bool:
        if x>=0:
            st=str(x)
            ch=st[::-1]
            if st==ch:
                return True
            return False
