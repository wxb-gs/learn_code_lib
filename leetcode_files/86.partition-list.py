#
# @lc app=leetcode.cn id=86 lang=python3
# @lcpr version=30204
#
# [86] 分隔链表
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
    def partition(self, head: Optional[ListNode], x: int) -> Optional[ListNode]:
        if head == None:
            return None
        head1 = None
        tail1 = None
        head2 = None
        tail2 = None
        tm = head
        while tm:
            nex = tm.next
            # print(f"now val:{tm.val}")
            if tm.val >= x:
                # print(f"now val:{tm.val}")
                if head2 == None:
                    head2 = tm
                else:
                    tail2.next = tm
                tail2 = tm
                tail2.next = None
            else:
                if head1 == None:
                    head1 = tm
                else:
                    tail1.next = tm
                tail1 = tm
                tail1.next = None
            tm = nex
        if head1 == None:
            return head2
        if head2 == None:
            return head1
        
        tail1.next = head2
        return head1
        
# @lc code=end



#
# @lcpr case=start
# [1,4,3,2,5,2]\n3\n
# @lcpr case=end

# @lcpr case=start
# [2,1]\n2\n
# @lcpr case=end

#

