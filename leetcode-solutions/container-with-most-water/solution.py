class Solution:
    def maxArea(self, height: List[int]) -> int:
        n=len(height)
        a=0
        b=n-1
        maxar=0
        while(a<b):
            l=min(height[a], height[b]) #formula for length
            w=int(b-a) #formula for width
            ar=l*w #area formula
            maxar=max(maxar, ar)
            if height[a] <= height[b]:
                a+=1
            else:
                b-=1
        return maxar
