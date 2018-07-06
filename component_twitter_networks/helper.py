
def chunkFun(l, c, n):
    if c > len(l):
        c = len(l)
    csize = int(len(l)/c)
    if n >= c - 1:
        n = c - 1
        return l[n*csize:]
    else:
        return l[n*csize:(n+1)*csize]
