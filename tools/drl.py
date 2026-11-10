import re, sys, math
from collections import defaultdict, Counter
base=sys.argv[1]
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
        if m and cur:
            pts[cur].append((float(m.group(1)),float(m.group(2))))
    f=25.4 if inch else 1
    return {k:(round(tools[k]*f,3),[(x*f,y*f) for x,y in v]) for k,v in pts.items()}
for name in ('NPTH','PTH'):
    d=drl(f'{base}/Lily58_Pro-{name}.drl')
    print(name,{k:(v[0],len(v[1])) for k,v in d.items()})
n=drl(f'{base}/Lily58_Pro-NPTH.drl')
# MX-middengat 4.0 mm
sw=[p for k,v in n.items() if abs(v[0]-4.0)<0.01 for p in v[1]]
print('gaten 4.0 mm (NPTH):',len(sw))
if not sw:
    p=drl(f'{base}/Lily58_Pro-PTH.drl'); sw=[q for k,v in p.items() if abs(v[0]-4.0)<0.01 for q in v[1]]
    print('gaten 4.0 mm (PTH):',len(sw))
sw=sorted(set((round(x,2),round(y,2)) for x,y in sw))
print('uniek',len(sw))
for x,y in sw: print(x,y)
# buurafstanden
ds=[]
for i,a in enumerate(sw):
    best=min(math.dist(a,b) for j,b in enumerate(sw) if j!=i)
    ds.append(round(best,2))
print('dichtstbijzijnde buur (afstand: aantal):',sorted(Counter(ds).items()))
# Edge cuts
xs=[];ys=[]
for l in open(f'{base}/Lily58_Pro-Edge_Cuts.gbr'):
    m=re.match(r'X(-?\d+)Y(-?\d+)D0[12]',l.strip())
    if m: xs.append(int(m.group(1))/1e6); ys.append(int(m.group(2))/1e6)
print('printrand bbox mm: x',round(min(xs),2),round(max(xs),2),'=',round(max(xs)-min(xs),2),' y',round(min(ys),2),round(max(ys),2),'=',round(max(ys)-min(ys),2))
