class Solution:
    def longestOnes(self, nums: List[int], k: int) -> int:
        maxw = 0
        maxz = 0
        n=len(nums)
        l=0
        for r in range(n):
            if nums[r] == 0:
                maxz+=1
            while maxz > k:
                if nums[l] == 0:
                    maxz-=1
                l+=1
            w=r-l+1
            maxw=max(maxw, w)
        return maxw
