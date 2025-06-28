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
        
        def dfs(start, a, end, num):
            nonlocal m
            if a not in m or end not in m:
                return False
            
            if start == end:
                return True
            
            if a in m[end]:
                val = m[a][end]
                print(f"{start} : {end} val: {val}")
                m[start][end] = num * val
                m[end][start] = val * num 
                return True
            
            for key, val in  m[a].items():
                if dfs(start, key, end, num * val):
                    return True

            
        ans = []
        for q in queries:
            [a, b] = q
            if not dfs(a, a, b, 1):
                ans.append(-1.0)
            else:
                if a != b:
                    ans.append(m[a][b])
                else:
                    ans.append(1.0)
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

