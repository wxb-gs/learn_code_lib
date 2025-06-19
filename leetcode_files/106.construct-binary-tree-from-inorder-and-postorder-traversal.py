#
# @lc app=leetcode.cn id=106 lang=python3
# @lcpr version=30204
#
# [106] 从中序与后序遍历序列构造二叉树
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
    def buildTree(self, inorder: List[int], postorder: List[int]) -> Optional[TreeNode]:
        n = len(postorder)
        
        sure = n - 1
        def build(start, end):
            nonlocal sure
            
            if sure < 0 or start > end or start < 0 or  end >= n:
                return None
            
            # print(f"==={sure}===")
            val = postorder[sure]
            index = start
            for i in range(start, end + 1):
                if inorder[i] == val:
                    index = i
                    break
            # print(f"index:{index}")
            node = TreeNode(val)
            sure -= 1
            node.right = build(index + 1, end)
            node.left = build(start, index - 1)
            # print(node,node.left, node.right)
            
            return node

        return build(0, n - 1)
# @lc code=end



#
# @lcpr case=start
# [9,3,15,20,7]\n[9,15,7,20,3]\n
# @lcpr case=end

# @lcpr case=start
# [-1]\n[-1]\n
# @lcpr case=end

#

