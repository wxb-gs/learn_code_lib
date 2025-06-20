#
# @lc app=leetcode.cn id=117 lang=python3
# @lcpr version=30204
#
# [117] 填充每个节点的下一个右侧节点指针 II
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start
"""
# Definition for a Node.
class Node:
    def __init__(self, val: int = 0, left: 'Node' = None, right: 'Node' = None, next: 'Node' = None):
        self.val = val
        self.left = left
        self.right = right
        self.next = next
"""

import queue


class Solution:
    def connect(self, root: 'Node') -> 'Node':
        if root == None:
            return root
        q = queue.Queue()
        q.put_nowait(root)
        root.next = None
        while not q.empty():
            size = q.qsize()
            last = None
            # 从右往左遍历 
            for i in range(size):
                top = q.get_nowait()
                right = top.right
                left = top.left
                if right:
                    q.put_nowait(right)
                    right.next = last
                    last = right
                if left:
                    q.put_nowait(left)
                    left.next = last
                    last = left
        
        return root
# @lc code=end



#
# @lcpr case=start
# [1,2,3,4,5,null,7]\n
# @lcpr case=end

# @lcpr case=start
# []\n
# @lcpr case=end

#

