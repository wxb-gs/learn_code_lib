#
# @lc app=leetcode.cn id=52 lang=python3
# @lcpr version=30204
#
# [52] N 皇后 II
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start
class Solution:
    def totalNQueens(self, n: int) -> int:
        # nums = [[0] * n for _ in range(n)]
        ans = 0
        # 遍历的时候保证横线上没有
        # rows = [0] * n 
        cols = [0] * n  
        # 对角线一共2*n条，所以中间那条特点是i == j, i - j = 0, 往左，往右分别是负数和正数 + n 保证都大于0
        # 反对角线一共2*n条， 中间那条 特点是 i + j == n
        line = [0] * (2 * n + 1)
        anti_line = [0]* (2 *n + 1)
        
        

        def backtrace(step):            
            nonlocal ans
            if step == n:
                # print(f"step:{step} ans:{ans}")
                ans = ans + 1
                return
            
            for p in range(n):
                if cols[p] or line[step - p + n] or anti_line[step + p]:
                    continue
                cols[p] = line[step - p + n] = anti_line[step + p] = 1
                backtrace(step + 1)
                cols[p] = line[step - p + n] = anti_line[step + p] = 0
        
        backtrace(0)
        return ans
# @lc code=end

if __name__ == "__main__":
    s = Solution()
    print( s.totalNQueens(4))
    

#
# @lcpr case=start
# 4\n
# @lcpr case=end

# @lcpr case=start
# 1\n
# @lcpr case=end

#

