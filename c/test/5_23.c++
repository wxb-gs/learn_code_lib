#include <iostream>
#include <vector>
#include <unordered_map>
using namespace std;

class Solution
{
public:
    unordered_map<int, string> m;
    vector<int> v1{1, 5, 10, 50, 100, 500, 1000};
    vector<string> v1_str{"I", "V", "X", "L", "C", "D", "M"};
    vector<int> v2{4, 9, 40, 90, 400, 900};
    vector<string> v2_str{"IV", "IX", "XL", "XC", "CD", "CM"};
    string intToRoman(int num)
    {
        string ans = "";
        while (num > 0)
        {
            int tm = num;
            while (tm / 10 > 0)
            {
                tm /= 10;
            }
            int first = tm;

            int index = 0;

            vector<int> *v;
            vector<string> *v_str;
            if (first == 4 || first == 9)
            {
                v = &v1;
                v_str = &v1_str;
            }
            else
            {
                v = &v2;
                v_str = &v2_str;
            }
            index = v->size() - 1;
            while (num < v->at(index))
            {
                index--;
            }
            num -= v_str->at(index);
            ans += v_str->at(index);
        }
        return ans;
    }
};