#
# @lc app=leetcode.cn id=129 lang=python3
# @lcpr version=30204
#
# [129] 求根节点到叶节点数字之和
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
    def sumNumbers(self, root: Optional[TreeNode]) -> int:
        ans = 0    
        def dfs(node, tm):
            nonlocal ans
            if node == None:
                return
            tm = tm * 10 + node.val
            
            if not node.left and not node.right:
                ans += tm
                return 
            dfs(node.left, tm)
            dfs(node.right, tm)
            
        dfs(root, 0)             
        return ans
# @lc code=end



#
# @lcpr case=start
# [1,2,3]\n
# @lcpr case=end

# @lcpr case=start
# [4,9,0,5,1]\n
# @lcpr case=end

#

