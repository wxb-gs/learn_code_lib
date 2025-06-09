from ast import List


class Solution:
    def kSmallestPairs(self, nums1: List[int], nums2: List[int], k: int) -> List[List[int]]:
        # 1 4 11
        # 2 3 6
        n1 = len(nums1)
        n2 = len(nums2)
        f = [0] * n1
        f[0] = 1
        ans = []
        need = k
        ans.append([nums1[0], nums2[0]])
        need -= 1
        while need > 0:
            min_v = 10**9 + 1
            tm = []
            for i in range(n1):
                if f[i] < n2 and nums1[i] + nums2[f[i]] < min_v:
                    tm = [i, f[i]]
                    min_v = nums1[i] + nums2[f[i]]
            ans.append(tm)
            f[tm[0]] += 1
            need -= 1
        
        return ans 

