#
# @lc app=leetcode.cn id=199 lang=python3
# @lcpr version=30204
#
# [199] 二叉树的右视图
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
from collections import deque


class Solution:
    def rightSideView(self, root: Optional[TreeNode]) -> List[int]:
        if not root:
            return []
        dq = deque()
        dq.append(root)
        ans = []
        while dq:
            # print(dq[0].val)
            ans.append(dq[0].val)
            size = len(dq)
            for i in range(size):
                node = dq.popleft()
                if node.right: dq.append(node.right)
                if node.left: dq.append(node.left)
        return ans
# @lc code=end



#
# @lcpr case=start
# [1,2,3,null,5,null,4]\n
# @lcpr case=end

# @lcpr case=start
# [1,2,3,4,null,null,null,5]\n
# @lcpr case=end

# @lcpr case=start
# [1,null,3]\n
# @lcpr case=end

# @lcpr case=start
# []\n
# @lcpr case=end

#

