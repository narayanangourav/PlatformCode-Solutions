class Solution:
    def removeStars(self, s: str) -> str:
        string = s
        new_string = ""
        for i in range(len(string)):
            if string[i] == "*":
                new_string = new_string[:-1]
            else:
                new_string += string[i]
        return new_string
