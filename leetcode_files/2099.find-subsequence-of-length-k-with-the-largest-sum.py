#
# @lc app=leetcode.cn id=2099 lang=python3
# @lcpr version=30204
#
# [2099] 找到和最大的长度为 K 的子序列
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start
import heapq


class Solution:
    def maxSubsequence(self, nums: List[int], k: int) -> List[int]:
        heap = []
        for i ,num in enumerate(nums):
            heapq.heappush(heap, (num, i))
            if len(heap) > k:
                heapq.heappop(heap)
        sorted_heap = sorted(heap, key = lambda x: x[1])
        ans =[x[0] for x in sorted_heap]
        # print(ans)
        return ans
                
        
        
# @lc code=end



#
# @lcpr case=start
# [2,1,3,3]\n2\n
# @lcpr case=end

# @lcpr case=start
# [-1,-2,3,4]\n3\n
# @lcpr case=end

# @lcpr case=start
# [3,4,3,3]\n2\n
# @lcpr case=end

#

