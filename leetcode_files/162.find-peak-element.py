#
# @lc app=leetcode.cn id=162 lang=python3
# @lcpr version=30204
#
# [162] 寻找峰值
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start
class Solution:
    def findPeakElement(self, nums: List[int]) -> int:
        n = len(nums)
        if n == 1:
            return 0
        
        if nums[-1] > nums[-2]:
            return len(nums) - 1
        
        l, r = 0, n - 1
        ans = l
        while l <= r:
            mid = (l + r) >> 1
            if mid < n - 1 and nums[mid] > nums[mid + 1]:
                ans = mid
                r = mid - 1
            else:
                l = mid + 1
        return ans
# @lc code=end



#
# @lcpr case=start
# [1,2,3,1]\n
# @lcpr case=end

# @lcpr case=start
# [1,2,1,3,5,6,4]\n
# @lcpr case=end

#

