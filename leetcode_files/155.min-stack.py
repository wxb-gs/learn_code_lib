#
# @lc app=leetcode.cn id=155 lang=python3
# @lcpr version=30204
#
# [155] 最小栈
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start
class MinStack:

    def __init__(self):
        self.min_stack =  []
        self.elems = []

    def push(self, val: int) -> None:
        elems = self.elems
        min_stack = self.min_stack
        elems.append(val)
        index = len(elems) - 1
        if not min_stack or val < elems[min_stack[-1]]:
                min_stack.append(index)
            
    def pop(self) -> None:
        self.elems.pop()
        top_index = len(self.elems) - 1
        while self.min_stack and self.min_stack[-1] > top_index:
            self.min_stack.pop()

    def top(self) -> int:
        return self.elems[-1]

    def getMin(self) -> int:
        return self.elems[self.min_stack[-1]]


# Your MinStack object will be instantiated and called as such:
# obj = MinStack()
# obj.push(val)
# obj.pop()
# param_3 = obj.top()
# param_4 = obj.getMin()
# @lc code=end



#
# @lcpr case=start
# ["MinStack","push","push","push","getMin","pop","top","getMin"][[],[-2],[0],[-3],[],[],[],[]]\n
# @lcpr case=end

#

