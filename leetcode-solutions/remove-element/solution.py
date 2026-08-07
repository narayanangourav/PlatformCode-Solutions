class Solution:
    def removeElement(self, nums: List[int], val: int) -> int:
        for i in range(len(nums)):
            if val>=0 and val in nums:
                nums.remove(val)
