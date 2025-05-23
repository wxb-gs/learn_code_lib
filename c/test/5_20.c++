#include <iostream>
#include <unordered_map>
#include <set>
using namespace std;

class Solution
{
public:
    unordered_map<char, int> m;
    unordered_map<string, int> v_m;
    set<char> left_s{'I', 'X', 'C'};
    Solution()
    {
        m['I'] = 1;
        m['V'] = 5;
        m['X'] = 10;
        m['L'] = 50;
        m['C'] = 100;
        m['D'] = 500;
        m['M'] = 1000;
        v_m["IV"] = 4;
        v_m["IX"] = 9;
        v_m["XL"] = 40;
        v_m["XC"] = 90;
        v_m["CD"] = 400;
        v_m["CM"] = 900;
    }
    int romanToInt(string s)
    {
        int i = 0;
        int sum = 0;
        int n = s.size();
        while (i < s.size())
        {
            if (i < n - 1 && left_s.count(s[i]))
            {
                // 看右边的
                string str = "";
                str.push_back(s[i]);
                str.push_back(s[i + 1]);
                cout << str << " ";
                if (v_m.count(str))
                {
                    sum += v_m[str];
                    i++;
                }
                else
                    sum += m[s[i]];
            }
            else
            {
                sum += m[s[i]];
            }
            i++;
        }
        return sum;
    }
};

int main(void)
{
    Solution s;
    cout << s.romanToInt("MCMXCIV");
    return 0;
}