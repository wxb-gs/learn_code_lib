#
# @lc app=leetcode.cn id=100 lang=python3
# @lcpr version=30204
#
# [100] 相同的树
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
    def isSameTree(self, p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
        def view(node_p, node_q):
            if node_p == None and node_q != None:
                return False
            if node_p != None and node_q == None:
                return False
            if node_p == None and node_q == None:
                return True
            
            if node_p.val != node_q.val:
                return False
            
            left= view(node_p.left, node_q.left)
            right = view(node_p.right, node_q.right)
            return left and right
        
        return view(p, q)
# @lc code=end



#
# @lcpr case=start
# [1,2,3]\n[1,2,3]\n
# @lcpr case=end

# @lcpr case=start
# [1,2]\n[1,null,2]\n
# @lcpr case=end

# @lcpr case=start
# [1,2,1]\n[1,1,2]\n
# @lcpr case=end

#

