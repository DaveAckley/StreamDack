def make2D(x=0,y=0):
    return (x,y)

def add2D(a,b):
    return (a[0]+b[0],a[1]+b[1])

def neg2D(a):
    return (-a[0],-a[1])

def sub2D(a,b):
    return add2D(a,neg2D(b))

def mult2D(a,b):
    return (a[0]*b[0],a[1]*b[1])

def dot2D(a,b):
    c = mult2D(a,b)
    return c[0]+c[1]

def equal2D(a,b):
    return a[0] == b[0] and a[1] == b[1]

def eless2D(a,b):
    return a[0] < b[0] or a[1] < b[1]

def eneg2D(a):
    return eless2D(a,(0,0))

def indexFrom2D(pt,siz):
    return pt[1]*siz[0]+pt[0]

def indexTo2D(idx,siz):
    return (idx % siz[0], idx // siz[0])

def map2D(pos,siz,pt):
    #print("cn2D10",pos,siz,pt)
    p1 = sub2D(pt,pos)
    #print("cn2D11",p1)
    if eneg2D(p1):
        return None
    p2 = sub2D(siz,p1)
    #print("cn2D12",p2)
    if eless2D(p2,(1,1)):
        return None
    #print("cn2D13 true")
    return p1
