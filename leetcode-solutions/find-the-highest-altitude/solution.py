class Solution:
    def largestAltitude(self, gain: List[int]) -> int:
        #self made code
        nmax = 0
        for i in range(0,len(gain)):
            if i == 0:
                val = 0 + gain[0]
            else:
                val = val + gain[i]
            if max(nmax, val) > 0:
                nmax = max(nmax, val)
        if nmax > 0:
            return nmax
        else:
            return 0
