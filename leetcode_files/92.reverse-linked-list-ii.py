#
# @lc app=leetcode.cn id=92 lang=python3
# @lcpr version=30204
#
# [92] 反转链表 II
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def reverseBetween(self, head: Optional[ListNode], left: int, right: int) -> Optional[ListNode]:
        if left == right or head.next == None:
            return head
        
        start, end = None, None
        before = None
        nex = None
        
        num = 1
        tm = head
        last = None
        while num <= right:
            if num == left:
                start = tm
                before = last
                
            if num == right:
                end = tm
                nex = tm.next
                break 
            num += 1
            last = tm
            tm = tm.next
        
        node = start
        header = None
        tail = None
        while node:
            if tail == None:
                tail = node
            node_next = node.next
            node.next = header
            header = node
            if node == end:
                break
            node = node_next
        
        tail.next = nex 
        if before == None:
            return header
        before.next = header
        return head
            
# @lc code=end



#
# @lcpr case=start
# [1,2,3,4,5]\n2\n4\n
# @lcpr case=end

# @lcpr case=start
# [5]\n1\n1\n
# @lcpr case=end

#

