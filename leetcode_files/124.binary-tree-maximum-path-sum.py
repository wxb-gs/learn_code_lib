#
# @lc app=leetcode.cn id=124 lang=python3
# @lcpr version=30204
#
# [124] 二叉树中的最大路径和
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
    def maxPathSum(self, root: Optional[TreeNode]) -> int:
        ans = -1 * 10**8
        
        def getMax(node):
            nonlocal ans
            if node == None:
                return 0
            
            val_l = getMax(node.left)
            val_r = getMax(node.right)            
            # 当前几点为根的话
            ans = max(ans, val_l + val_r + node.val)
            # 不为根的话，作为一条支路
            # 不需要节点的话
            val = max(max(val_l, val_r) + node.val, node.val)
            ans = max(ans, val)
            return val
        
        getMax(root)
        
        return ans
        
# @lc code=end



#
# @lcpr case=start
# [1,2,3]\n
# @lcpr case=end

# @lcpr case=start
# [-10,9,20,null,null,15,7]\n
# @lcpr case=end

#

