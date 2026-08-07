class Solution:
    def runningSum(self, nums: List[int]) -> List[int]:
        a=[]
        for i in range(0,len(nums)):
            add=0
            val=i+1
            for j in range(0,val):
                add=add+nums[j]
            a.append(add)
            val+=1
        return a
