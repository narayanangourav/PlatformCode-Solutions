class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        char_index = {}
        start = 0
        longest_substr = ""

        for i in range(len(s)):
            char = s[i]
            if char in char_index and char_index[char] >= start:
                start = char_index[char] + 1
            char_index[char] = i
            if i - start + 1 > len(longest_substr):
                longest_substr = s[start:i + 1]

        return len(longest_substr)
