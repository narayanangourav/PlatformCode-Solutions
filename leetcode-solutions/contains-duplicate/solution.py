class Solution:
    def containsDuplicate(self, nums: List[int]) -> bool:
        hp=set()
        for i in range(len(nums)):
            if nums[i] in hp:
                return True
            hp.add(nums[i])
        return False
