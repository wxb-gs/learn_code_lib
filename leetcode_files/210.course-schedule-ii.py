#
# @lc app=leetcode.cn id=210 lang=python3
# @lcpr version=30204
#
# [210] 课程表 II
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start



class Solution:
    def findOrder(self, numCourses: int, prerequisites: List[List[int]]) -> List[int]:
        out = dict()
        visited = [0] * 2001
        in_nums = [0] * 2001 
        for prerq in prerequisites:
            [a, b] = prerq
            if b not in out:
                out[b] = []
            out[b].append(a)
            in_nums[a] += 1
            
        ans = []
        
        def dfs(i):
            nonlocal ans, visited
            if visited[i] == 1:
                return
            
            ans.append(i)
            visited[i] = 1
            
            if i not in out:
                return
            
            for num in out[i]:
                in_nums[num] -= 1
                
                if visited[num] == 1:
                    continue
                else:
                    # 对应的入度减1
                    if in_nums[num] <=0: dfs(num)
                    
        
        
        for i in range(numCourses): 
            if in_nums[i] == 0: dfs(i)
        
        return ans if len(ans) == numCourses else []
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

