import struct, sys
from collections import Counter
def load(p):
    d=open(p,'rb').read()
    n=struct.unpack('<I',d[80:84])[0]
    assert 84+50*n==len(d),(84+50*n,len(d))
    tris=[]
    for i in range(n):
        v=struct.unpack('<12fH',d[84+50*i:134+50*i])
        tris.append((v[3:6],v[6:9],v[9:12]))
    return tris
for p in sys.argv[1:]:
    t=load(p)
    pts=[v for tr in t for v in tr]
    mn=[min(v[i] for v in pts) for i in range(3)]
    mx=[max(v[i] for v in pts) for i in range(3)]
    print(p,'driehoeken',len(t))
    print(' min',[round(x,3) for x in mn],'max',[round(x,3) for x in mx])
    print(' afmeting',[round(mx[i]-mn[i],3) for i in range(3)])
    zs=Counter(round(v[2],3) for v in pts)
    print(' z-niveaus (aantal hoekpunten):',sorted(zs.items())[:20])
