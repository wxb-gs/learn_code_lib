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
        nums = []
        if head == None:
            return None
        def get_len(head):
            tm = head
            size = 0
            while head:
                nums.append(head.val)
                size += 1
                head = head.next
            return size
        
        n = get_len(head)
        k %= n
        nums.reverse()
        reverse_1 = nums[:k]
        reverse_1.reverse()
        # print(nums)
        reverse_2 = nums[k : n]
        reverse_2.reverse()
        header = None
        tail = None
        reverse_1.extend(reverse_2)
        for num in reverse_1:
            node = ListNode(num)
            if header == None:
                header = node 
            else:
                tail.next = node
            tail = node
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

