import re, sys, math
sys.path.insert(0,'/home/claude/scripts')
base=sys.argv[1]
from collections import defaultdict
def drl(p):
    tools={}; cur=None; pts=defaultdict(list); inch=False
    for l in open(p):
        l=l.strip()
        if l.startswith('INCH'): inch=True
        m=re.match(r'T(\d+)C([\d.]+)',l)
        if m: tools[m.group(1)]=float(m.group(2)); continue
        m=re.match(r'T(\d+)$',l)
        if m: cur=m.group(1); continue
        m=re.match(r'X(-?[\d.]+)Y(-?[\d.]+)',l)
        if m and cur: pts[cur].append((float(m.group(1)),float(m.group(2))))
    f=25.4 if inch else 1
    return {round(tools[k]*f,2):[(x*f,y*f) for x,y in v] for k,v in pts.items()}
n=drl(f'{base}/Lily58_Pro-NPTH.drl')
centers=n[4.0]
for diam,nom in ((1.7,5.08),(1.9,5.5)):
    holes=n[diam]
    print('gat',diam,'nominaal',nom)
    for c in sorted(centers):
        near=[h for h in holes if abs(math.dist(c,h)-nom)<0.4]
        angs=[round(math.degrees(math.atan2(h[1]-c[1],h[0]-c[0]))%180,2) for h in near]
        print(' ',tuple(round(v,2) for v in c),len(near),angs)
