#
# @lc app=leetcode.cn id=114 lang=python3
# @lcpr version=30204
#
# [114] 二叉树展开为链表
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right

class Solution:
    def flatten(self, root: Optional[TreeNode]) -> None:
        """
        Do not return anything, modify root in-place instead.
        """
        if root == None:
            return None
        s = []
        header = None
        tail = None
        tm = root
        s.append(tm)
        while s:
            top = s.pop()
            if header == None:
                header = top
            else:
                tail.right = top
            tail = top
            if tail.right: s.append(tail.right)
            if tail.left: s.append(tail.left)
            tail.left = None
            tail.right = None
            
        return header        
# @lc code=end



#
# @lcpr case=start
# [1,2,5,3,4,null,6]\n
# @lcpr case=end

# @lcpr case=start
# []\n
# @lcpr case=end

# @lcpr case=start
# [0]\n
# @lcpr case=end

#

