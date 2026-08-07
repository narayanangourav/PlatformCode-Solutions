class Solution:
    def sortColors(self, nums: List[int]) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """
        #self did code
        k=0
        while(k<len(nums)):
            for i in range(0, len(nums)-1):
                if nums[i] <= nums[i+1]:
                    continue 
                else:
                    nums[i], nums[i+1] = nums[i+1], nums[i]
            k+=1
