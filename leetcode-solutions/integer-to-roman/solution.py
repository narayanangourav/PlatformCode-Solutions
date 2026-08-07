class Solution:
    def intToRoman(self, num: int) -> str:
        arr={
            "I":1,
            "IV":4,
            "V":5,
            "IX":9,
            "X":10,
            "XL":40,
            "L":50,
            "XC":90,
            "C":100,
            "CD":400,
            "D":500,
            "CM":900,
            "M":1000,
        }
        out=[]
        for x,y in reversed(arr.items()):
            while num>0:
                if y<=num:
                    out.append(x)
                    num-=y
                else:
                    break
        return "".join(out)
