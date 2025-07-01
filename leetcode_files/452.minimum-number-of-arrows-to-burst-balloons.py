#
# @lc app=leetcode.cn id=452 lang=python3
# @lcpr version=30204
#
# [452] 用最少数量的箭引爆气球
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start
from math import inf


class Solution:
    def findMinArrowShots(self, points: List[List[int]]) -> int:
        points.sort(key = lambda x : x[1])
        ans = 0
        pre_point = -inf
        for [a, b] in points:
            if a > pre_point:
                ans += 1
                pre_point = b
        return ans
                
 # @lc code=end



#
# @lcpr case=start
# [[10,16],[2,8],[1,6],[7,12]]\n
# @lcpr case=end

# @lcpr case=start
# [[1,2],[3,4],[5,6],[7,8]]\n
# @lcpr case=end

# @lcpr case=start
# [[1,2],[2,3],[3,4],[4,5]]\n
# @lcpr case=end

#

