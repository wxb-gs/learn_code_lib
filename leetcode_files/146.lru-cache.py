#
# @lc app=leetcode.cn id=146 lang=python3
# @lcpr version=30204
#
# [146] LRU 缓存
#


# @lcpr-template-start

# @lcpr-template-end
# @lc code=start
from collections import deque

class LinkedNode:
    val = None
    pre = None
    next = None    
    def __init__(self, val) -> None:
        self.val = val

class LRUCache:

    def __init__(self, capacity: int):
        self.m = dict() # key -> node
        self.header = None
        self.tail = None
        self.capacity = capacity
        self.num = 0
    
    def _move_to_end(self, key):
        node = self.m[key]
        if self.num == 1 or node == self.tail:
            return
        
        pre = node.pre
        nex = node.next

        if node == self.header:
            self.header = node.next
        
        if pre: pre.next = nex
        if nex: nex.pre = pre            
        
        self.tail.next = node
        node.next = None
        node.pre = self.tail
        self.tail = node
    
        
        
    def get(self, key: int) -> int:
        if key not in self.m:
            return -1
        
        # 尽量的往尾挪动
        self._move_to_end(key)
        node = self.m[key]
        return node.val[1]

    def _pop_LRU(self):
        if self.num == self.capacity:
            #出头
            key = self.header.val[0]
            self.m.pop(key)
            head = self.header.next
            
            if head: head.pre = None
            self.header.next = None
            
            self.header = head
            self.num -= 1
    
    def put(self, key: int, value: int) -> None:
        if key in self.m:
            node = self.m[key]
            node.val = (key, value)
            self._move_to_end(key)
            return
        
        self._pop_LRU()
            
        node = LinkedNode((key, value))
        
        if self.header == None:
            self.header = node
        else:
            self.tail.next = node
            node.pre = self.tail
        
        self.tail = node
        self.m[key] = node
        self.num += 1
# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
# @lc code=end



