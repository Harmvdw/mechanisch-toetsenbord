import re, sys, math, csv
base=sys.argv[1]; out=sys.argv[2]
OX,OY=158.6,-46.21
segs=[]; cur=None
for l in open(f'{base}/Lily58_Pro-Edge_Cuts.gbr'):
    m=re.match(r'X(-?\d+)Y(-?\d+)D0([12])\*',l.strip())
    if not m: continue
    p=(int(m.group(1))/1e6,int(m.group(2))/1e6)
    if m.group(3)=='2': cur=p
    else: segs.append((cur,p)); cur=p
# ketenen met tolerantie (0,005 mm)
TOL=0.005
import math as _m
rest=list(segs); first=rest.pop(0); poly=[first[0],first[1]]; p=first[1]
while rest:
    best=None
    for i,(a,b) in enumerate(rest):
        d=_m.hypot(a[0]-p[0],a[1]-p[1])
        if d<TOL and (best is None or d<best[0]): best=(d,i,False)
        d2=_m.hypot(b[0]-p[0],b[1]-p[1])
        if d2<TOL and (best is None or d2<best[0]): best=(d2,i,True)
    if best is None: break
    a,b=rest.pop(best[1])
    p=a if best[2] else b
    poly.append(p)
used=set(range(len(segs)-len(rest)))
closed=_m.hypot(poly[0][0]-poly[-1][0],poly[0][1]-poly[-1][1])<TOL
poly=poly[:-1] if closed else poly
area=0.5*sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))
xs=[p[0] for p in poly]; ys=[p[1] for p in poly]
print('punten',len(poly),'gesloten',closed,'segmenten gebruikt',len(used),'van',len(segs))
print('oppervlak mm2',round(abs(area),1),'bbox',round(max(xs)-min(xs),2),'x',round(max(ys)-min(ys),2))
def inside(pt):
    x,y=pt; c=False
    for i in range(len(poly)):
        x1,y1=poly[i]; x2,y2=poly[(i+1)%len(poly)]
        if (y1>y)!=(y2>y) and x < (x2-x1)*(y-y1)/(y2-y1)+x1: c=not c
    return c
keys=[tuple(map(float,r)) for r in [l.split() for l in open(sys.argv[3])]]
def dseg(pt):
    best=1e9
    for i in range(len(poly)):
        a=poly[i]; b=poly[(i+1)%len(poly)]
        dx,dy=b[0]-a[0],b[1]-a[1]; L=dx*dx+dy*dy
        t=0 if L==0 else max(0,min(1,((pt[0]-a[0])*dx+(pt[1]-a[1])*dy)/L))
        best=min(best,math.hypot(pt[0]-a[0]-t*dx,pt[1]-a[1]-t*dy))
    return best
print('toetsen binnen rand:',sum(inside(k) for k in keys),'van',len(keys))
print('kleinste afstand toetsmidden-rand mm:',round(min(dseg(k) for k in keys),2),'(celrand 9,525)')
with open(out,'w',newline='') as f:
    w=csv.writer(f); w.writerow(['nr','x_mm','y_mm'])
    for i,p in enumerate(poly,1): w.writerow([i,round(p[0]-OX,3),round(p[1]-OY,3)])
