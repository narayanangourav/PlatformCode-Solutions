class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        hp = {}
        for i, n in enumerate(nums):
            diff = target - n
            if diff in hp:
                return (hp[diff], i)
            hp[n] = i
