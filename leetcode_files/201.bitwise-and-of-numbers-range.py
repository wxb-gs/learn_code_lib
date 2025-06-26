#
# @lc app=leetcode.cn id=201 lang=python3
# @lcpr version=30204
#
# [201] 数字范围按位与
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start
class Solution:
    def rangeBitwiseAnd(self, left: int, right: int) -> int:
        # 101 110 111 1000
        # 1001 1010 1010 1011 1100
        m = (left ^ right).bit_length()
        return left & ~((1 << m) - 1)
            
        
        
        
# @lc code=end



#
# @lcpr case=start
# 5\n7\n
# @lcpr case=end

# @lcpr case=start
# 0\n0\n
# @lcpr case=end

# @lcpr case=start
# 1\n2147483647\n
# @lcpr case=end

#

