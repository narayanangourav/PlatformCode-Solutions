class Solution:
    def maxProduct(self, nums: List[int]) -> int:
        prefix =1
        suffix=1
        maxx=0
        for i in range(len(nums)):
            if prefix==0:
                prefix=1
            if suffix==0:
                suffix=1
            if len(nums)==1:
                maxx = nums[0]
            prefix *= nums[i]
            suffix *= nums[len(nums)-i-1]
            maxx=max(maxx, max(prefix, suffix))
        return maxx
