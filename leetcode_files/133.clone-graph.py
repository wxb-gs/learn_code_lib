#
# @lc app=leetcode.cn id=133 lang=python3
# @lcpr version=30204
#
# [133] 克隆图
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start

# Definition for a Node.
class Node:
    def __init__(self, val = 0, neighbors = None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []


from collections import deque
from typing import Optional
class Solution:
    def cloneGraph(self, node: Optional['Node']) -> Optional['Node']:
        if node == None:
            return None
        visited = dict()
        def dfs(node):
            if node.val in visited:
                return visited[node.val]
            
            new_node = Node(node.val)
            visited[node.val] = new_node
            for _node in node.neighbors:
                new_node.neighbors.append(dfs(_node))
            return new_node
        
        return dfs(node)
        
# @lc code=end



#
# @lcpr case=start
# [[2,4],[1,3],[2,4],[1,3]]\n
# @lcpr case=end

# @lcpr case=start
# [[]]\n
# @lcpr case=end

# @lcpr case=start
# []\n
# @lcpr case=end

#

