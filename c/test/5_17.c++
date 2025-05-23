#include <iostream>
#include <vector>
using namespace std;

class Solution
{
public:
    vector<int> productExceptSelf(vector<int> &nums)
    {
        int n = nums.size();
        vector<int> pre(n + 2, 1);
        vector<int> suf(n + 2, 1);
        pre[1] = nums[0];
        suf[n] = nums[n - 1];
        for (int i = 1; i < n; i++)
        {
            pre[i + 1] = pre[i] * nums[i];
            suf[n - i] = suf[n - i + 1] * nums[n - i - 1];
        }
        vector<int> ans;
        for (int i = 0; i < n; i++)
        {
            ans.push_back(pre[i] * suf[i]);
        }
        return ans;
    }
};

int main()
{
    vector<int> nums({1, 2, 3, 4});
    Solution s;
    vector<int> v = s.productExceptSelf(nums);
    for (int i = 0; i < v.size(); i++)
    {
        cout << v[i] << " ";
    }
    return 0;
}