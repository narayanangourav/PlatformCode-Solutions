class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        ms=nums[0]
        curr = 0
        for  i in nums:
            if curr < 0:
                curr = 0
            curr += i
            ms = max(ms, curr)
        return ms
