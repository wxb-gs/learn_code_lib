#include <iostream>
#include <vector>
#include <unordered_map>
using namespace std;

class Solution
{
public:
    vector<string> fullJustify(vector<string> &words, int maxWidth)
    {
        vector<string> ans;
        int i = 0;
        vector<string> line;
        int now = 0;
        while (i < words.size())
        {
            if (now + words[i].size() <= maxWidth)
            {
                line.push_back(words[i]);
                now = now + words[i].size() + 1;
            }
            if (i == words.size() - 1 || now + words[i + 1].size() > maxWidth)
            {
                int size = line.size();
                int char_len = 0;
                for (int j = 0; j < size; j++)
                {
                    char_len += line[j].size();
                }

                int blank = maxWidth - char_len;
                int every_blank_num = blank / (size - 1);
                int rest = blank % (size - 1);
                string tm = "" + line[0];
                for (int j = 1; j < size; j++)
                {
                    for (int k = 0; k < every_blank_num; k++)
                        tm += " ";
                    if (rest)
                    {
                        tm += " ";
                        rest--;
                    }
                    tm += line[j];
                }
                ans.push_back(tm);
                now = 0;
                line.clear();
            }
            i++;
        }
        return ans;
    }
};
int main(void)
{
    Solution s;
    vector<string> v{"This", "is", "an", "example", "of", "text", "justification."};
    bool ans = s.fullJustify(v, 16);
    cout << ans;
    return 0;
}