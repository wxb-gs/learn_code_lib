#
# @lc app=leetcode.cn id=61 lang=python3
# @lcpr version=30204
#
# [61] 旋转链表
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
    def rotateRight(self, head, k: int):
        if head == None:
            return head
        last = None
        tm = head
        n = 0
        while tm:
            last = tm
            n += 1
            tm = tm.next
        k %= n
        
        last.next = head
        
        tm = head
        last = None
        for i in range(n - k):
            last = tm
            tm = tm.next
        
        header = last.next
        last.next = None
        return header         
# @lc code=end



#
# @lcpr case=start
# [1,2,3,4,5]\n2\n
# @lcpr case=end

# @lcpr case=start
# [0,1,2]\n4\n
# @lcpr case=end

#

