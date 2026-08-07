class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        i,j = 0,1
        mp = 0
        while j < len(prices):
            if prices[i] < prices[j]:
                p = prices[j]-prices[i]
                mp = max(mp, p)
            else:
                i=j
            j+=1
        return mp
