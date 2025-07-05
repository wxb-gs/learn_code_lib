#
# @lc app=leetcode.cn id=918 lang=python3
# @lcpr version=30204
#
# [918] 环形子数组的最大和
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start
from cmath import inf
from collections import deque


class Solution:
    def maxSubarraySumCircular(self, nums: List[int]) -> int:
        n = len(nums)
        
        summary = sum(nums)
        min_ans = inf
        max_ans = -inf
        tm_min = inf
        tm_max = -inf
        for i in range(n):
            if tm_min < 0:
                tm_min += nums[i]
            else:
                tm_min = nums[i]
            min_ans = min(min_ans, tm_min)
            
            if tm_max > 0:
                tm_max += nums[i]
            else:
                tm_max = nums[i]
            max_ans = max(max_ans, tm_max)
        # 说明全负
        if max_ans < 0:
            return max_ans
        return max(max_ans, summary - min_ans)
      
        
# @lc code=end



#
# @lcpr case=start
# [1,-2,3,-2]\n
# @lcpr case=end

# @lcpr case=start
# [5,-3,5]\n
# @lcpr case=end

# @lcpr case=start
# [3,-2,2,-3]\n
# @lcpr case=end

#

