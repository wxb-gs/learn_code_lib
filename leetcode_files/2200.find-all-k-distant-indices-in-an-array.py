#
# @lc app=leetcode.cn id=2200 lang=python3
# @lcpr version=30204
#
# [2200] 找出数组中的所有 K 近邻下标
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start
class Solution:
    def findKDistantIndices(self, nums: List[int], key: int, k: int) -> List[int]:
        n = len(nums)
        l, r = 0, 0
        ans = []
        i = 0
        need_r = 0
        for i in range(n):
            if nums[i] == key:
                need_l = max(i - k, 0)
                #必须大于上一次的need_r
                need_l = max(need_r, need_l)
                
                need_r = min(i + k, n - 1) + 1
                for j in range(need_l, need_r):
                    ans.append(j) 
            
        return ans
# @lc code=end



#
# @lcpr case=start
# [3,4,9,1,3,9,5]\n9\n1\n
# @lcpr case=end

# @lcpr case=start
# [2,2,2,2,2]\n2\n2\n
# @lcpr case=end

#

