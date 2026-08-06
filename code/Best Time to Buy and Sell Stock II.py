class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        profit = 0
        for i in range(1, len(prices)):
            # If the price increases, add the difference to the total profit
            if prices[i] > prices[i - 1]:
                profit += prices[i] - prices[i - 1]
        return profit
