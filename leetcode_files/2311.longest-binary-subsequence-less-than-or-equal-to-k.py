#
# @lc app=leetcode.cn id=2311 lang=python
# @lcpr version=30204
#
# [2311] 小于等于 K 的最长二进制子序列
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start
class Solution(object):
    def longestSubsequence(self, s, k):
        """
        :type s: str
        :type k: int
        :rtype: int
        """
        n = len(s)
        ans = 0
        indexes = []
        for i ,c in enumerate(s):
            if c == "1":
                indexes.append(i)
            else:
                ans += 1
        
        tm = 0
        for index in reversed(indexes):
            bit = n - 1 - index
            tm += (1 << bit)
            # print(tm)
            if tm > k:
                break
            else:
                ans += 1
        
        return ans
# @lc code=end



#
# @lcpr case=start
# "1001010"\n5\n
# @lcpr case=end

# @lcpr case=start
# "00101001"\n1\n
# @lcpr case=end

#

