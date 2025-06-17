#
# @lc app=leetcode.cn id=25 lang=python3
# @lcpr version=30204
#
# [25] K 个一组翻转链表
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start
# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def get_len(self, head):
        if head == None:
            return 0
        
        tm = head
        size = 1
        while tm.next:
            tm = tm.next
            size += 1
        return size

    def reverseKGroup(self, head, k: int):
        size = self.get_len(head)
        # print(f"size:{size}")
        header = None
        tailer = None
        tm_node = head
        # print(f"num:{num}")
        n = size
        last_t = None
        ans_header = None
        while n >= k:
            # print(f"node:{tm_node.val}")
            for _ in range(k):
                next_list = tm_node.next
                if tailer == None:
                    tailer = tm_node
                # 前插
                tm_node.next = header
                header = tm_node
                tm_node = next_list
            if last_t:
                last_t.next = header
            # 赋值第一个header
            if ans_header == None:
                ans_header = header
            last_t = tailer
            
            header = None
            tailer = None
            n -= k
            
        if tm_node:
            if last_t:
                last_t.next = tm_node
        
        fin_tm = ans_header
        # while fin_tm:
        #     # print(f"_node:{fin_tm.val}")
        #     fin_tm = fin_tm.next
        return ans_header
    ## how to do?
# @lc code=end

if __name__ == "__main__":
    list = [1,2,3,4,5]
    head = ListNode(1)
    tail = head
    for i in range(1, len(list)):
        tail.next = ListNode(list[i])
        tail = tail.next

    s = Solution()
    s.reverseKGroup(head, 2)

#
# @lcpr case=start
# [1,2,3,4,5]\n2\n
# @lcpr case=end

# @lcpr case=start
# [1,2,3,4,5]\n3\n
# @lcpr case=end

#

