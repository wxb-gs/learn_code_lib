#
# @lc app=leetcode.cn id=138 lang=python3
# @lcpr version=30204
#
# [138] 随机链表的复制
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start

# Definition for a Node.
class Node:
    def __init__(self, x: int, next: 'Node' = None, random: 'Node' = None):
        self.val = int(x)
        self.next = next
        self.random = random


class Solution:
    def copyRandomList(self, head: 'Optional[Node]') -> 'Optional[Node]':
        # 使用map表示，node -> new_node的关系
        tm = head
        while tm:
            nex = tm.next
            node = Node(tm.val)
            tm.next = node
            node.next = nex 
            tm = nex
        
        tm = head
        while tm:
            old_random = tm.random
            new_node = tm.next
            if old_random: new_node.random = old_random.next
            tm = new_node.next
                  
        header = None
        tail = None 
        tm = head
        while tm:
            new_node = tm.next
            if header == None:
                header = new_node
            else:
                tail.next = new_node
            tail = new_node
            tm = new_node.next
        return header
            
# @lc code=end



#
# @lcpr case=start
# [[7,null],[13,0],[11,4],[10,2],[1,0]]\n
# @lcpr case=end

# @lcpr case=start
# [[1,1],[2,1]]\n
# @lcpr case=end

# @lcpr case=start
# [[3,null],[3,0],[3,null]]\n
# @lcpr case=end

#

