class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        #self made code
        v = {}
        for num in nums:
            if num in v:
                if v[num] < 2:
                    v[num] += 1
            else:
                v[num] = 1
        nlist = []
        for key, count in v.items():
            nlist.extend([key] * count)
        nums[:len(nlist)] = nlist
        return len(nlist)
