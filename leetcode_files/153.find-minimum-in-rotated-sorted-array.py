#
# @lc app=leetcode.cn id=153 lang=python3
# @lcpr version=30204
#
# [153] 寻找旋转排序数组中的最小值
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start
class Solution:
    def findMin(self, nums: List[int]) -> int:
        n = len(nums)
        left = nums[0]
        right = nums[-1]
        l, r = 0, n - 1
        ans = nums[0]        
        while l <= r:
            mid = (l + r) // 2
            if nums[mid] >= left:
                if nums[mid] <= right:
                    return ans
                else:
                    l = mid + 1
            elif nums[mid] < left:
                ans = nums[mid]
                r = mid - 1
        return ans

            
# @lc code=end



#
# @lcpr case=start
# [3,4,5,1,2]\n
# @lcpr case=end

# @lcpr case=start
# [4,5,6,7,0,1,2]\n
# @lcpr case=end

# @lcpr case=start
# [11,13,15,17]\n
# @lcpr case=end

#

