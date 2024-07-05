class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        maxi = 0
        mini = prices [0]
        for i in range(1, len(prices)):
            if prices[i] >= maxi:
                maxi = prices[i]
                p =i
        for j in range(0, len(prices)):
            if prices[j] < mini:
                mini = prices[j]
                pos = i
        if mini < prices[pos]:
            return (maxi-mini)
        else: 
            return 0
