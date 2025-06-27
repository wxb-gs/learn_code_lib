#
# @lc app=leetcode.cn id=222 lang=python3
# @lcpr version=30204
#
# [222] 完全二叉树的节点个数
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
    def countNodes(self, root: Optional[TreeNode]) -> int:
        if root == None:
            return 0
        
        def count_h(node):
            h = 0
            while node:
                h += 1
                node = node.left
            return h

        l_h = count_h(root.left)
        r_h = count_h(root.right)
        if l_h == r_h:
            return 2** l_h - 1 + self.countNodes(root.right) + 1
        else:
            return 2** r_h - 1 + self.countNodes(root.left) + 1
        
        
# @lc code=end



#
# @lcpr case=start
# [1,2,3,4,5,6]\n
# @lcpr case=end

# @lcpr case=start
# []\n
# @lcpr case=end

# @lcpr case=start
# [1]\n
# @lcpr case=end

#

