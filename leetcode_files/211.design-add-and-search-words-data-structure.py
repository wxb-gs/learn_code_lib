#
# @lc app=leetcode.cn id=211 lang=python3
# @lcpr version=30204
#
# [211] 添加与搜索单词 - 数据结构设计
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start
class Node:
    def __init__(self) -> None:
        self.end = False
        self.children = [None] * 26
    
    
class WordDictionary:
    head = None 
    def __init__(self):
        self.head = Node()

    def addWord(self, word: str) -> None:
        tm = self.head
        for i, c in enumerate(word):
            index = ord(c) - ord('a')
            node = tm.children[index]
            if node == None:
                node = Node()                
            if i == len(word) - 1:
                node.end = True
            tm.children[index] = node            
            tm = node
        
    def search(self, word: str) -> bool:
        def dfs(i, head):
            if i == len(word): 
                return head.end
                
            c = word[i]
            if c == ".":
                for node in head.children:
                    if node != None and dfs(i + 1, node):
                        return True
                return False
                
            index = ord(c) - ord('a')
            node = head.children[index] 
            if node == None:
                return False  
            return dfs(i + 1, node)
                
        tm = self.head
        return dfs(0, tm)
        
# if __name__ == "__main__":
#     obj = WordDictionary()
#     # obj.addWord("a")
#     param_2 = obj.search("a")
#     print(param_2)

# Your WordDictionary object will be instantiated and called as such:
# obj = WordDictionary()
# obj.addWord(word)
# param_2 = obj.search(word)
# @lc code=end



#
# @lcpr case=start
# ["WordDictionary","addWord","addWord","addWord","search","search","search","search"][[],["bad"],["dad"],["mad"],["pad"],["bad"],[".ad"],["b.."]]\n
# @lcpr case=end

#

