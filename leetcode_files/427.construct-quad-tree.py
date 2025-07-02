#
# @lc app=leetcode.cn id=427 lang=python3
# @lcpr version=30204
#
# [427] 建立四叉树
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start

# Definition for a QuadTree node.
class Node:
    def __init__(self, val, isLeaf, topLeft, topRight, bottomLeft, bottomRight):
        self.val = val
        self.isLeaf = isLeaf
        self.topLeft = topLeft
        self.topRight = topRight
        self.bottomLeft = bottomLeft
        self.bottomRight = bottomRight


class Solution:
    def construct(self, grid: List[List[int]]) -> 'Node':
        n = len(grid)
        
        # 每一块的size, 右下角i, j
        def dfs(size, i, j):
            if size == 1:
                return Node(grid[i][j], True, None, None, None, None)
            size //= 2
            tleft = dfs(size, i - size, j - size)
            tright = dfs(size, i - size, j)
            bleft = dfs(size, i, j - size)
            bright = dfs(size, i, j)
            # print(i , j)
            if tleft.isLeaf and tright.isLeaf and bleft.isLeaf and bright.isLeaf:
                if tleft.val == tright.val and tleft.val == bleft.val and bleft.val == bright.val:
                    return Node(grid[i][j], True, None, None, None, None)
            
            return Node(1, False, tleft, tright, bleft, bright)
        
        return dfs(n, n - 1, n - 1)

# @lc code=end



#
# @lcpr case=start
# [[0,1],[1,0]]\n
# @lcpr case=end

# @lcpr case=start
# [[1,1,1,1,0,0,0,0],[1,1,1,1,0,0,0,0],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[1,1,1,1,0,0,0,0],[1,1,1,1,0,0,0,0],[1,1,1,1,0,0,0,0],[1,1,1,1,0,0,0,0]]\n
# @lcpr case=end

#

