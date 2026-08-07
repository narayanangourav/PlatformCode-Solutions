class Solution:
    def merge(self, nums1: List[int], m: int, nums2: List[int], n: int) -> None:
        """
        Do not return anything, modify nums1 in-place instead.
        """
        # Start filling the nums1 from the end
        last = m + n - 1
        # Pointers for nums1 and nums2
        i = m - 1
        j = n - 1
        # While there are still elements to compare
        while i >= 0 and j >= 0:
            if nums1[i] > nums2[j]:
                nums1[last] = nums1[i]
                i -= 1
            else:
                nums1[last] = nums2[j]
                j -= 1
            last -= 1
        # Fill nums1 with leftover elements from nums2 if any
        while j >= 0:
            nums1[last] = nums2[j]
            j -= 1
            last -= 1
