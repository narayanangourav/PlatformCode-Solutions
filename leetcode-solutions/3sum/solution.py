class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        nums.sort()
        result = set()
        n = len(nums)
        for i, a in enumerate(nums):
            target = -a
            seen = {}
            for b in nums[i+1:]:
                c = target - b
                if c in seen:
                    result.add((a, b, c))
                else:
                    seen[b] = True
        return [list(triplet) for triplet in result]
