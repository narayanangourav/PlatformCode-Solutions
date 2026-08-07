# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def deleteMiddle(self, head: Optional[ListNode]) -> Optional[ListNode]:
        if not head or not head.next:
            return None
        
        curr = head
        count = 0
        while curr:
            count += 1
            curr = curr.next
        
        middle = count // 2
        curr = head
        prev = None
        for i in range(middle):
            prev = curr
            curr = curr.next
        if prev and curr:
            prev.next = curr.next
        
        return head
