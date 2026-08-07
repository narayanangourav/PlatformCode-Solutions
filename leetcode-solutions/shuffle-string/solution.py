class Solution:
    def restoreString(self, s: str, indices: List[int]) -> str:
        st=""
        a=[]
        for i in range(0,len(s)):
            for j in range(0,len(indices)):
                if i==indices[j] and j not in a:
                    a.append(j)
        for i in range(0,len(a)):
            val=a[i]
            st=st+s[val]
        return (st)
