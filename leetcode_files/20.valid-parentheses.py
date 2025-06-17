#
# @lc app=leetcode.cn id=20 lang=python3
# @lcpr version=30204
#
# [20] 有效的括号
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start
class Solution:

    def isValid(self, s: str) -> bool:
        stack = []
        m = {
            ')': '(',
            ']': '[',
            '}': '{'
        }
        for c in s:
            if c in m.values():
                stack.append(c)
            else:
                if len(stack) == 0 or stack[-1] != m[c]:
                    return False
                stack.pop()

        return len(stack) == 0
# @lc code=end



#
# @lcpr case=start
# "()"\n
# @lcpr case=end

# @lcpr case=start
# "()[]{}"\n
# @lcpr case=end

# @lcpr case=start
# "(]"\n
# @lcpr case=end

# @lcpr case=start
# "([])"\n
# @lcpr case=end

#
