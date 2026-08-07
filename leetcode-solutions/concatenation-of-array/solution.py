class Solution:
    def getConcatenation(self, nums: List[int]) -> List[int]:
        out=0
        nums2=[]
        for i in nums:
            nums2.append(i)
        out=nums+nums2
        return(out)
