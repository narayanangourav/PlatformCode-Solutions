class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        #self made code
        newnums = []
        for i in range(0, len(nums)):
            if nums[i] not in newnums:
                newnums.append(nums[i])
            else:
                continue
        nums[:len(newnums)] = newnums
        return len(newnums)
