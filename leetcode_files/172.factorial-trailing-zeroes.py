#
# @lc app=leetcode.cn id=172 lang=python3
# @lcpr version=30204
#
# [172] 阶乘后的零
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start
class Solution:
    def trailingZeroes(self, n: int) -> int:
        ans = 0
        while n:
            n //= 5
            ans += n
        return ans
# @lc code=end



#
# @lcpr case=start
# 3\n
# @lcpr case=end

# @lcpr case=start
# 5\n
# @lcpr case=end

# @lcpr case=start
# 0\n
# @lcpr case=end

#

