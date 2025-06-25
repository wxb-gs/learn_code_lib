#
# @lc app=leetcode.cn id=2040 lang=python3
# @lcpr version=30204
#
# [2040] 两个有序数组的第 K 小乘积
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start
from bisect import bisect_left, bisect_right


class Solution:
    def kthSmallestProduct(self, nums1: List[int], nums2: List[int], k: int) -> int:

        # mx = max(abs(nums1[0]), abs(nums1[-1])) * max(abs(nums2[0]), abs(nums2[-1]))
        MAXV = max(abs(nums1[0]), nums1[-1]) * max(abs(nums2[0]), abs(nums2[-1]))
        l = - MAXV
        r = MAXV + 1
        n1 = len(nums1)
        n2 = len(nums2)
        
        # 二分枚举可能的最大乘积，log C，对于每个乘积枚举nums1
        # bisect_right(nums2, v // x1)二分查找，计算nums2中与nums1乘积小于其的数目，判断对应乘积的数目
        # 二分查找第一个大于目标值的索引 
        
        # 计算小于等于v, 当num1取x1时，符合要求nums2的个数
       
        def f(v):
            count = 0
            for x1 in nums1:
                num = 0
                #1. x1为正数的话，那么全部都按照正数来，从左到右，二分查找
                #2. x1为负数的话，那么全部相反，从右到左，二分查找
                #3. x1为0的话，那么全部乘积都是0，计算小于mid的个数,len(nums2)或者0
                if x1 > 0:
                    num = bisect_right(nums2, v / x1)
                elif x1 < 0:
                    num = n2 - bisect_left(nums2, v / x1)
                else:
                    # 注意等于0的时候
                    num = n2 if v >= 0 else 0
                count += num
                
            return count
        
        #二分枚举可能最大的乘积
        ans = 0
        while l < r:
            mid = (l + r) // 2
            count = f(mid)
            
            ## 这里要取第一个mid，因为第一个满足的mid一定存在于结果中，比如8-12，8也满足但是小于8不能满足，所以要用bisect_left
            # 但是这里要注意
            if count >= k:
                r = mid
            else:
                l = mid + 1
        return r
        
        
# @lc code=end



#
# @lcpr case=start
# [2,5]\n[3,4]\n2\n
# @lcpr case=end

# @lcpr case=start
# [-4,-2,0,3]\n[2,4]\n6\n
# @lcpr case=end

# @lcpr case=start
# [-2,-1,0,1,2]\n[-3,-1,2,4,5]\n3\n
# @lcpr case=end

#

