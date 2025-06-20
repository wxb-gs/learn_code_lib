#
# @lc app=leetcode.cn id=210 lang=python3
# @lcpr version=30204
#
# [210] 课程表 II
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start


class Node:
    num = None
    pre_order = []

class Solution:
    def findOrder(self, numCourses: int, prerequisites: List[List[int]]) -> List[int]:
        m = dict([])
        for prerq in prerequisites:
            [a, b] = prerq
            if a not in m:
                m[a] = []
            m[a].append(b)
        
        visited = [0] * 2001
        ans = []
        
        def dfs(i):
            nonlocal ans, visited
            if visited[i] == 1:
                return
            
            if i not in m:
                ans.append(i)
                visited[i] = 1
                return
            
            for num in m[i]:
                if visited[num] == 1:
                    continue
                else:
                    dfs(num)
                    
            ans.append(i)
            visited[i] = 1
        
        
        for i in range(numCourses): 
            dfs(i)
        
        return ans
# @lc code=end



#
# @lcpr case=start
# 2\n[[1,0]]\n
# @lcpr case=end

# @lcpr case=start
# 4\n[[1,0],[2,0],[3,1],[3,2]]\n
# @lcpr case=end

# @lcpr case=start
# 1\n[]\n
# @lcpr case=end

#

