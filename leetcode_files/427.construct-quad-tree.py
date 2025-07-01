#
# @lc app=leetcode.cn id=427 lang=python3
# @lcpr version=30204
#
# [427] 建立四叉树
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start
"""
# Definition for a QuadTree node.
class Node:
    def __init__(self, val, isLeaf, topLeft, topRight, bottomLeft, bottomRight):
        self.val = val
        self.isLeaf = isLeaf
        self.topLeft = topLeft
        self.topRight = topRight
        self.bottomLeft = bottomLeft
        self.bottomRight = bottomRight
"""

class Solution:
    def construct(self, grid: List[List[int]]) -> 'Node':
        
# @lc code=end



#
# @lcpr case=start
# [[0,1],[1,0]]\n
# @lcpr case=end

# @lcpr case=start
# [[1,1,1,1,0,0,0,0],[1,1,1,1,0,0,0,0],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[1,1,1,1,0,0,0,0],[1,1,1,1,0,0,0,0],[1,1,1,1,0,0,0,0],[1,1,1,1,0,0,0,0]]\n
# @lcpr case=end

#

