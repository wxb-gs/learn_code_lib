#
# @lc app=leetcode.cn id=123 lang=python3
# @lcpr version=30204
#
# [123] 买卖股票的最佳时机 III
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start
class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        n = len(prices)
        dp = [ [0] * 4 for _ in range(n + 1) ]
        # dp[i][0] 
        # dp[i][1]
        dp[1][0] = -prices[0]
        dp[1][2] = -prices[0]
        # dp[1][1] = 0
        
        for i in range(2, n + 1):
            dp[i][0] = max(dp[i - 1][0], -prices[i - 1])
            dp[i][1] = max(dp[i - 1][0] + prices[i - 1], dp[i - 1][1])
            dp[i][2] = max(dp[i - 1][1] - prices[i - 1], dp[i - 1][2])
            dp[i][3] = max(dp[i][2] + prices[i - 1], dp[i - 1][3])
            # print(dp)
        return dp[-1][-1]
        
# @lc code=end



#
# @lcpr case=start
# [3,3,5,0,0,3,1,4]\n
# @lcpr case=end

# @lcpr case=start
# [1,2,3,4,5]\n
# @lcpr case=end

# @lcpr case=start
# [7,6,4,3,1]\n
# @lcpr case=end

# @lcpr case=start
# [1]\n
# @lcpr case=end

#

