#
# @lc app=leetcode.cn id=399 lang=python3
# @lcpr version=30204
#
# [399] 除法求值
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start
class Solution:
    def calcEquation(self, equations: List[List[str]], values: List[float], queries: List[List[str]]) -> List[float]:
        m = {}
        for i, equ in enumerate(equations):
            [a, b] = equ
            if a not in m:
                m[a] = {}
            if b not in m:
                m[b] = {}
            m[a][b] = values[i] 
            m[b][a] = 1 / values[i]
        
        visited = None
        
        def dfs(a, end, num):
            if a not in m or end not in m:
                return -1.0
            
            if a == end:
                return num
            
            for key, val in  m[a].items():
                if key not in visited:
                    visited.add(key)
                    tm = dfs(key, end, num * val)
                    if tm + 1.0 > 0.0000001:
                        return tm
            
            return -1.0
            
        ans = []
        for q in queries:
            visited = set()
            [a, b] = q
            # 目前已经遍历到a
            visited.add(a)
            ans.append(dfs(a, b, 1))
            
        return ans
# @lc code=end



#
# @lcpr case=start
# [["a","b"],["b","c"]]\n[2.0,3.0]\n[["a","c"],["b","a"],["a","e"],["a","a"],["x","x"]]\n
# @lcpr case=end

# @lcpr case=start
# [["a","b"],["b","c"],["bc","cd"]]\n[1.5,2.5,5.0]\n[["a","c"],["c","b"],["bc","cd"],["cd","bc"]]\n
# @lcpr case=end

# @lcpr case=start
# [["a","b"]]\n[0.5]\n[["a","b"],["b","a"],["a","c"],["x","y"]]\n
# @lcpr case=end

#

