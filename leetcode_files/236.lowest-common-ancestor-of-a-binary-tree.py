#
# @lc app=leetcode.cn id=236 lang=python3
# @lcpr version=30204
#
# [236] 二叉树的最近公共祖先
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start
# Definition for a binary tree node.
import math


class TreeNode:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None

class Solution:
    
    def lowestCommonAncestor(self, root: 'TreeNode', p: 'TreeNode', q: 'TreeNode') -> 'TreeNode':
        u = p.val
        v = q.val
        val_to_node = {}
        g = {}
        def build(root, fa):
            if not root:
                return
            val = root.val
            val_to_node[val] = root
            
            if val not in g:
                g[val] = set()                
            if fa:
                g[val].add(fa.val)
            if root.left:
                build(root.left, root)
                g[val].add(root.left.val)
            if root.right:
                build(root.right, root)
                g[val].add(root.right.val)
        
        build(root, None)   
        print(g)            
        
        n = len(g.keys())
        f = {}
        
        def tarjan(u):
            
        
        return val_to_node[tarjan(u)]
# @lc code=end



#
# @lcpr case=start
# [3,5,1,6,2,0,8,null,null,7,4]\n5\n1\n
# @lcpr case=end

# @lcpr case=start
# [3,5,1,6,2,0,8,null,null,7,4]\n5\n4\n
# @lcpr case=end

# @lcpr case=start
# [1,2]\n1\n2\n
# @lcpr case=end

#

