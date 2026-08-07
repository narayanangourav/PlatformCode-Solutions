class Solution:
    def reverse(self, x: int) -> int:
        xt = []
        cc = []
        y = str(x)
        for i in range(len(y)):
            if y[i].isdigit() and y[i]!= 0:
                xt.append(y[i])
            else:
                cc.append(y[i])
        u = "".join(cc)
        y = "".join(xt)
        z = int(u+y[::-1])
        if z.bit_length() <= 31:
            return z
        else:
            return 0
