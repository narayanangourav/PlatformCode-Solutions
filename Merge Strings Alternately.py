class Solution:
    def mergeAlternately(self, word1: str, word2: str) -> str:
        extt = ''
        ext = []
        for i in range(len(word1)):
            ext.append(word1[i])
            ext.append(str(0))
        for j in range(len(word2)):
            if '0' in ext:  
                for k in range(len(ext)):
                    if ext[k] == '0':
                        ext[k] = word2[j]
                        break
            else:
                ext.extend(word2[j])
        if '0' in ext:
            for i in ext:
                if i == '0':
                    continue
                else:
                    extt += i
        else:
            for i in ext:
                extt += i
        return(extt)
