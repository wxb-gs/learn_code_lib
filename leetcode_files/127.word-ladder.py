#
# @lc app=leetcode.cn id=127 lang=python3
# @lcpr version=30204
#
# [127] 单词接龙
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start
from collections import deque


class Solution:
    def ladderLength(self, beginWord: str, endWord: str, wordList: List[str]) -> int:
        if endWord not in wordList:
            return 0
        m = dict()
        def get_change(s):
            nonlocal m
            # 遍历整个数组建立联系为O(n), 遍历字符串长度最多10中可能
            if s not in m:
                m[s] = []
            chars = list(s)
            for i in range(len(s)):
                c = chars[i]
                chars[i] = '*'
                tm_s = "".join(chars)
                m[s].append(tm_s)
                if tm_s not in m:
                    m[tm_s] = []
                m[tm_s].append(s)
                chars[i] = c

        get_change(beginWord)
        for word in wordList:
            get_change(word)
        # print(m)
        
        dq = deque()
        dq2 = deque()
        dq.append(beginWord)
        dq2.append(endWord)
        visited = set()
        visited.add(beginWord)
        visited2 = set()
        visited2.add(endWord)

        step = 0
        ## begin != end
        while dq or dq2:
            if dq:
                step += 1
                size = len(dq)
                for i in range(size): 
                    node = dq.popleft()
                    for w in m[node]:
                        if w not in visited:
                            if w in visited2:
                                return step // 2 + 1
                            dq.append(w)
                            visited.add(w)
            if dq2:
                step += 1
                size2 = len(dq2)
                for j in range(size2):
                    end_node = dq2.popleft()
                    for w in m[end_node]:
                        if w not in visited2:
                            if w in visited:
                                return step // 2 + 1
                            dq2.append(w)
                            visited2.add(w)

        return 0
        
# @lc code=end



#
# @lcpr case=start
# "hit"\n"cog"\n["hot","dot","dog","lot","log","cog"]\n
# @lcpr case=end

# @lcpr case=start
# "hit"\n"cog"\n["hot","dot","dog","lot","log"]\n
# @lcpr case=end

#

