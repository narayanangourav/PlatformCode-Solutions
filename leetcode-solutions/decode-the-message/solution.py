class Solution:
    def decodeMessage(self, key: str, message: str) -> str:
        lsl=["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
        res=[]
        dic={}
        st=""
        for ele in key:
            if ele.strip():
                res.append((ele))
        res=list(dict.fromkeys(res))

        for i in range(0,len(res)):
            dic.update({res[i]: lsl[i]})

        for i in range(0,len(message)):
            if message[i] in dic:
                val=dic[message[i]]
                st=st+str(val)
            if message[i]==" ":
                st=st+" "

        return (st)
