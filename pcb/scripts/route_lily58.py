#!/usr/bin/env python3
"""Eenvoudige rasterrouter voor de Lily58-aanpassing (route 2).
- zoekt een vrije plek voor J_NP aan de buitenrand
- routeert VCC, SDA, SCL naar J_NP en BAT+ / RAW voor de batterij-aansluiting
Gebruik: python3 route_lily58.py <kicad_pcb>   (bewerkt in place; maak vooraf een kopie)
"""
import re, sys, math, heapq, uuid
import numpy as np

PCB = sys.argv[1]
t = open(PCB, 'rb').read().decode('utf-8', 'replace').replace('\r\n', '\n')

# ---------- buitenrand 6 mm verbreden (Edge.Cuts en GND-vlakken) ----------
SHIFT = 6.0
def shift_edge(m):
    blk = m.group(0)
    def sp(mm):
        x = float(mm.group(2))
        if x >= 223.0: x += SHIFT
        return '(%s %s %s)' % (mm.group(1), repr(round(x, 6)), mm.group(3))
    return re.sub(r'\((start|end) ([0-9.\-]+) ([0-9.\-]+)\)', sp, blk)
if '(xy 226 37)' in t:
    t = re.sub(r'\n\t\(gr_line\n(?:\t\t[^\n]*\n)*?\t\t\(layer "Edge\.Cuts"\)', shift_edge, t)
    t = t.replace('(xy 226 37) (xy 226 121)', '(xy %g 37) (xy %g 121)' % (226 + SHIFT, 226 + SHIFT))
    print('buitenrand verbreed met %g mm' % SHIFT)

G = 0.2                       # rastermaat mm
TW = 0.25                     # spoorbreedte
CL = 0.2                      # vrije afstand koper
K_TR = CL + TW / 2 + 0.05     # 0.375 hart spoor tot koperrand
K_HOLE = 0.25 + TW / 2 + 0.05 # hart spoor tot gatrand
VIA_D, VIA_DRILL = 0.6, 0.3
K_VIA = CL + VIA_D / 2 + 0.05 # 0.55 hart via tot koperrand
K_EDGE = 0.5 + TW / 2 + 0.05
LAYERS = ['F.Cu', 'B.Cu']

# ---------- inlezen ----------
items = []   # dict(kind, layers, net, geom...)
def add(kind, layers, net, **g):
    d = dict(kind=kind, layers=layers, net=net); d.update(g); items.append(d)

fps = list(re.finditer(r'\n\t\(footprint "([^"]+)"(.*?)\n\t\)', t, re.S))
fp_ref_span = {}
for m in fps:
    body = m.group(2)
    ref = re.search(r'\(property "Reference" "([^"]+)"', body).group(1)
    fp_ref_span[ref] = (m.start(), m.end())
    at = re.search(r'\n\t\t\(at ([0-9.\-]+) ([0-9.\-]+)(?: ([0-9.\-]+))?\)', body)
    fx, fy = float(at.group(1)), float(at.group(2))
    frot = float(at.group(3) or 0)
    th = math.radians(frot)
    for gm in re.finditer(r'\n\t\t\(fp_(?:poly|rect|circle|line|arc)\n(.*?)\n\t\t\)', body, re.S):
        gb = gm.group(1)
        lm = re.search(r'\(layer "([FB]\.Cu)"\)', gb)
        if not lm: continue
        pts = [(float(a), float(b)) for a, b in re.findall(r'\((?:xy|start|end|center|mid) ([0-9.\-]+) ([0-9.\-]+)\)', gb)]
        if not pts: continue
        gx = [fx + px * math.cos(th) + py * math.sin(th) for px, py in pts]
        gy = [fy - px * math.sin(th) + py * math.cos(th) for px, py in pts]
        add('rect', [lm.group(1)], None, x=(min(gx) + max(gx)) / 2, y=(min(gy) + max(gy)) / 2,
            hw=(max(gx) - min(gx)) / 2 + 0.1, hh=(max(gy) - min(gy)) / 2 + 0.1, ref=ref + '_art', num='')
    for pm in re.finditer(r'\n\t\t\(pad "([^"]*)" (\w+) (\w+)(.*?)\n\t\t\)', body, re.S):
        num, ptype, shape, pb = pm.groups()
        pa = re.search(r'\(at ([0-9.\-]+) ([0-9.\-]+)(?: ([0-9.\-]+))?\)', pb)
        px, py = float(pa.group(1)), float(pa.group(2))
        prot = float(pa.group(3) or 0)
        ax = fx + px * math.cos(th) + py * math.sin(th)
        ay = fy - px * math.sin(th) + py * math.cos(th)
        sz = re.search(r'\(size ([0-9.\-]+) ([0-9.\-]+)\)', pb)
        w, h = float(sz.group(1)), float(sz.group(2))
        lay = re.search(r'\(layers ([^)]*)\)', pb).group(1)
        if '*.Cu' in lay: layers = LAYERS
        else: layers = [l for l in LAYERS if '"%s"' % l in lay]
        net = re.search(r'\(net "([^"]*)"\)', pb)
        net = net.group(1) if net else None
        dr = re.search(r'\(drill (?:oval )?([0-9.]+)', pb)
        drill = float(dr.group(1)) if dr else 0
        if ptype == 'np_thru_hole':
            add('hole', LAYERS, None, x=ax, y=ay, r=max(w, drill) / 2, ref=ref)
            continue
        if not layers: continue
        a = prot % 180
        if shape == 'circle':
            add('circle', layers, net, x=ax, y=ay, r=w / 2, ref=ref, num=num)
        elif abs(a) < 1e-6 or abs(a - 90) < 1e-6:
            if abs(a - 90) < 1e-6: w, h = h, w
            add('rect', layers, net, x=ax, y=ay, hw=w / 2, hh=h / 2, ref=ref, num=num)
        else:
            add('circle', layers, net, x=ax, y=ay, r=math.hypot(w, h) / 2, ref=ref, num=num)
        if drill and ptype == 'thru_hole':
            add('hole', LAYERS, net, x=ax, y=ay, r=drill / 2, ref=ref)

for m in re.finditer(r'\n\t\(segment\n\t\t\(start ([0-9.\-]+) ([0-9.\-]+)\)\n\t\t\(end ([0-9.\-]+) ([0-9.\-]+)\)\n\t\t\(width ([0-9.]+)\)\n\t\t\(layer "([^"]+)"\)\n\t\t\(net "([^"]*)"\)', t):
    x1, y1, x2, y2, w = map(float, m.groups()[:5])
    add('seg', [m.group(6)], m.group(7), x1=x1, y1=y1, x2=x2, y2=y2, hw=w / 2)
for m in re.finditer(r'\n\t\(via\n\t\t\(at ([0-9.\-]+) ([0-9.\-]+)\)\n\t\t\(size ([0-9.]+)\)\n\t\t\(drill ([0-9.]+)\)\n(?:\t\t[^\n]*\n)*?\t\t\(net "([^"]*)"\)', t):
    x, y, s, d = map(float, m.groups()[:4])
    add('circle', LAYERS, m.group(5), x=x, y=y, r=s / 2, ref='via', num='')
    add('hole', LAYERS, m.group(5), x=x, y=y, r=d / 2, ref='via')

edges = []
for m in re.finditer(r'\n\t\(gr_line\n\t\t\(start ([0-9.\-]+) ([0-9.\-]+)\)\n\t\t\(end ([0-9.\-]+) ([0-9.\-]+)\)\n(?:\t\t[^\n]*\n)*?\t\t\(layer "Edge\.Cuts"\)', t):
    edges.append(tuple(map(float, m.groups())))
zone = re.search(r'\(zone\n\t\t\(net "GND"\)\n\t\t\(layer "F.Cu"\).*?\(polygon\n\t\t\t\(pts\n\t\t\t\t(.*?)\n\t\t\t\)', t, re.S).group(1)
zpts = [(float(a), float(b)) for a, b in re.findall(r'\(xy ([0-9.\-]+) ([0-9.\-]+)\)', zone)]

X0, Y0 = 80.0, 34.0
NX, NY = int((234 - X0) / G) + 1, int((147 - Y0) / G) + 1
xs = X0 + np.arange(NX) * G
ys = Y0 + np.arange(NY) * G
XX, YY = np.meshgrid(xs, ys)          # [iy, ix]

def inside_poly(px, py, poly):
    res = np.zeros(px.shape, bool)
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        cond = ((y1 > py) != (y2 > py))
        xint = (x2 - x1) * (py - y1) / ((y2 - y1) if y2 != y1 else 1e-9) + x1
        res ^= cond & (px < xint)
    return res
INSIDE = inside_poly(XX, YY, zpts)

def dist_item(it, X, Y):
    k = it['kind']
    if k in ('circle', 'hole'):
        return np.hypot(X - it['x'], Y - it['y']) - it['r']
    if k == 'rect':
        qx = np.abs(X - it['x']) - it['hw']
        qy = np.abs(Y - it['y']) - it['hh']
        return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0)
    if k == 'seg':
        x1, y1, x2, y2 = it['x1'], it['y1'], it['x2'], it['y2']
        vx, vy = x2 - x1, y2 - y1
        L2 = vx * vx + vy * vy
        if L2 == 0: tt = 0
        else: tt = np.clip(((X - x1) * vx + (Y - y1) * vy) / L2, 0, 1)
        return np.hypot(X - (x1 + tt * vx), Y - (y1 + tt * vy)) - it['hw']

def bbox(it, m):
    k = it['kind']
    if k in ('circle', 'hole'): r = it['r'] + m; return it['x'] - r, it['y'] - r, it['x'] + r, it['y'] + r
    if k == 'rect': return it['x'] - it['hw'] - m, it['y'] - it['hh'] - m, it['x'] + it['hw'] + m, it['y'] + it['hh'] + m
    hw = it['hw'] + m
    return min(it['x1'], it['x2']) - hw, min(it['y1'], it['y2']) - hw, max(it['x1'], it['x2']) + hw, max(it['y1'], it['y2']) + hw

def window(b):
    i0 = max(int((b[0] - X0) / G) - 1, 0); i1 = min(int((b[2] - X0) / G) + 2, NX)
    j0 = max(int((b[1] - Y0) / G) - 1, 0); j1 = min(int((b[3] - Y0) / G) + 2, NY)
    return j0, j1, i0, i1

def stamp(arr, it, margin):
    j0, j1, i0, i1 = window(bbox(it, margin))
    if j0 >= j1 or i0 >= i1: return
    d = dist_item(it, XX[j0:j1, i0:i1], YY[j0:j1, i0:i1])
    arr[j0:j1, i0:i1] |= d < margin

def blocked_for(net):
    """per laag: verboden voor spoorhart; plus verboden voor via."""
    tr = {l: ~INSIDE.copy() for l in LAYERS}
    vb = ~INSIDE.copy()
    for e in edges:
        it = dict(kind='seg', x1=e[0], y1=e[1], x2=e[2], y2=e[3], hw=0)
        for l in LAYERS: stamp(tr[l], it, K_EDGE)
        stamp(vb, it, K_EDGE + 0.2)
    for it in items:
        if it['kind'] == 'hole':
            for l in LAYERS: stamp(tr[l], it, K_HOLE if it['net'] != net else 0)
            stamp(vb, it, 0.25 + VIA_DRILL / 2 + 0.05 if it['net'] != net else VIA_D / 2)
            continue
        if it['net'] == net: continue
        for l in it['layers']:
            stamp(tr[l], it, K_TR)
        stamp(vb, it, K_VIA)
    return tr, vb

def cells_of(net_items):
    """rastercellen binnen pads/vias van het eigen net (per laag)."""
    src = {l: np.zeros((NY, NX), bool) for l in LAYERS}
    for it in net_items:
        for l in it['layers']:
            j0, j1, i0, i1 = window(bbox(it, 0))
            if j0 >= j1 or i0 >= i1: continue
            d = dist_item(it, XX[j0:j1, i0:i1], YY[j0:j1, i0:i1])
            src[l][j0:j1, i0:i1] |= d < -0.05
    return src

def astar(tr, vb, src, tgt_cells, tgt_xy):
    INF = 1e18
    tx, ty = tgt_xy
    ti, tj = (tx - X0) / G, (ty - Y0) / G
    def h0(i, j):
        dx, dy = abs(i - ti), abs(j - tj)
        return 1.15 * (max(dx, dy) + 0.4142 * min(dx, dy))
    dist, prev, pq = {}, {}, []
    for li, l in enumerate(LAYERS):
        js, is_ = np.nonzero(src[l])
        for j, i in zip(js, is_):
            s = (li, int(j), int(i), 8)
            dist[s] = 0.0
            heapq.heappush(pq, (h0(i, j), 0.0, s))
    nb = [(1, 0, 1), (1, 1, 1.4142), (0, 1, 1), (-1, 1, 1.4142), (-1, 0, 1), (-1, -1, 1.4142), (0, -1, 1), (1, -1, 1.4142)]
    TURN = {0: 0.0, 1: 2.0, 2: 6.0, 3: 30.0, 4: 60.0}
    VIA_COST = 15.0
    n = 0
    while pq:
        f, g, s = heapq.heappop(pq)
        if g > dist.get(s, INF): continue
        li, j, i, d = s
        n += 1
        if tgt_cells[LAYERS[li]][j, i]:
            path = [s]
            while path[-1] in prev: path.append(prev[path[-1]])
            return path[::-1], n
        L = LAYERS[li]
        tl, sl, gl = tr[L], src[L], tgt_cells[L]
        for k, (di, dj, c) in enumerate(nb):
            ii, jj = i + di, j + dj
            if not (0 <= ii < NX and 0 <= jj < NY): continue
            if tl[jj, ii] and not gl[jj, ii] and not sl[jj, ii]: continue
            if di and dj and (tl[j, ii] or tl[jj, i]) and not (sl[j, ii] or sl[jj, i]): continue
            if d != 8 and not sl[j, i]:
                dd = abs(d - k); dd = min(dd, 8 - dd)
                c = c + TURN[dd]
            ns = (li, jj, ii, k); ng = g + c
            if ng < dist.get(ns, INF):
                dist[ns] = ng; prev[ns] = s
                heapq.heappush(pq, (ng + h0(ii, jj), ng, ns))
        if not vb[j, i] and not tr[LAYERS[1 - li]][j, i]:
            ns = (1 - li, j, i, 8); ng = g + VIA_COST
            if ng < dist.get(ns, INF):
                dist[ns] = ng; prev[ns] = s
                heapq.heappush(pq, (ng + h0(i, j), ng, ns))
    return None, n

def new_uuid(): return str(uuid.uuid4())
def seg_txt(x1, y1, x2, y2, layer, net):
    return '\n\t(segment\n\t\t(start %g %g)\n\t\t(end %g %g)\n\t\t(width %g)\n\t\t(layer "%s")\n\t\t(net "%s")\n\t\t(uuid "%s")\n\t)' % (
        round(x1, 4), round(y1, 4), round(x2, 4), round(y2, 4), TW, layer, net, new_uuid())
def via_txt(x, y, net):
    return '\n\t(via\n\t\t(at %g %g)\n\t\t(size %g)\n\t\t(drill %g)\n\t\t(layers "F.Cu" "B.Cu")\n\t\t(net "%s")\n\t\t(uuid "%s")\n\t)' % (
        round(x, 4), round(y, 4), VIA_D, VIA_DRILL, net, new_uuid())

def path_to_copper(path, net, start_xy, end_xy):
    pts = [(LAYERS[p[0]], X0 + p[2] * G, Y0 + p[1] * G) for p in path]
    # knooppunten: laagwissel = via; richting gelijk = samenvoegen
    out_txt, vias, segs = [], [], []
    cur_layer = pts[0][0]
    poly = [(start_xy[0], start_xy[1])] if start_xy else []
    poly.append((pts[0][1], pts[0][2]))
    for k in range(1, len(pts)):
        l, x, y = pts[k]
        if l != cur_layer:
            segs.append((cur_layer, poly)); vias.append((x, y))
            cur_layer, poly = l, [(x, y)]
        else:
            poly.append((x, y))
    if end_xy: poly.append(end_xy)
    segs.append((cur_layer, poly))
    for l, poly in segs:
        # samenvoegen van collineaire punten
        simp = [poly[0]]
        for p in poly[1:]:
            if len(simp) >= 2:
                (ax, ay), (bx, by) = simp[-2], simp[-1]
                if abs((bx - ax) * (p[1] - by) - (by - ay) * (p[0] - bx)) < 1e-6:
                    simp[-1] = p; continue
            if abs(p[0] - simp[-1][0]) < 1e-9 and abs(p[1] - simp[-1][1]) < 1e-9: continue
            simp.append(p)
        for a, b in zip(simp, simp[1:]):
            out_txt.append(seg_txt(a[0], a[1], b[0], b[1], l, net))
            items.append(dict(kind='seg', layers=[l], net=net, x1=a[0], y1=a[1], x2=b[0], y2=b[1], hw=TW / 2))
    for x, y in vias:
        out_txt.append(via_txt(x, y, net))
        items.append(dict(kind='circle', layers=LAYERS, net=net, x=x, y=y, r=VIA_D / 2, ref='via', num=''))
        items.append(dict(kind='hole', layers=LAYERS, net=net, x=x, y=y, r=VIA_DRILL / 2, ref='via'))
    return out_txt, len(vias)

# ---------- J_NP verplaatsen naar vrije plek ----------
jnp = [it for it in items if it.get('ref') == 'J_NP' and it['kind'] != 'hole']
jnp_holes = [it for it in items if it.get('ref') == 'J_NP' and it['kind'] == 'hole']
cur = re.search(r'\(property "Reference" "J_NP"', t)
s0, s1 = fp_ref_span['J_NP']
jbody = t[s0:s1]
jx, jy = map(float, re.search(r'\n\t\t\(at ([0-9.\-]+) ([0-9.\-]+)\)', jbody).groups())
offs = [(it['x'] - jx, it['y'] - jy, it['net'], it) for it in jnp]
def prad(it): return it['r'] if 'r' in it else math.hypot(it['hw'], it['hh'])
near = [it for it in items if it.get('ref') != 'J_NP' and bbox(it, 0)[2] > 214]

def min_clear(cx, cy):
    worst = 99
    for dx, dy, net, pit in offs:
        px, py = cx + dx, cy + dy
        for it in near:
            if it['kind'] == 'hole':
                d = dist_item(it, np.array(px), np.array(py)) - prad(pit) - 0.25
            else:
                if it['net'] == net and net is not None: continue
                if not set(it['layers']) & set(pit['layers']): continue
                d = dist_item(it, np.array(px), np.array(py)) - prad(pit) - CL
            worst = min(worst, float(d))
        for e in edges:
            if max(e[0], e[2]) < 214: continue
            it = dict(kind='seg', x1=e[0], y1=e[1], x2=e[2], y2=e[3], hw=0)
            worst = min(worst, float(dist_item(it, np.array(px), np.array(py))) - prad(pit) - 0.5)
    return worst

best = None
for cx in np.arange(229.4, 225.0, -0.2):
    for cy in np.arange(62.0, 112.0, 0.25):
        c = min_clear(cx, cy)
        if c > 0.1:
            score = abs(cy - 81.7) + (229.4 - cx) * 2
            if best is None or score < best[0]:
                best = (score, cx, cy, c)
    if best: break
print('J_NP: oude plek (%.2f, %.2f) speling %.3f' % (jx, jy, min_clear(jx, jy)))
if best:
    _, nx_, ny_, c = best
    print('J_NP: nieuwe plek (%.2f, %.2f) speling %.3f' % (nx_, ny_, c))
    new_body = jbody.replace('\n\t\t(at %g %g)' % (jx, jy), '\n\t\t(at %g %g)' % (round(nx_, 3), round(ny_, 3)), 1)
    assert new_body != jbody
    t = t[:s0] + new_body + t[s1:]
    for it in items:
        if it.get('ref') == 'J_NP':
            it['x'] += nx_ - jx; it['y'] += ny_ - jy
else:
    print('GEEN vrije plek voor J_NP gevonden'); sys.exit(1)

# ---------- routeren ----------
def pads_of(ref, num):
    return [it for it in items if it.get('ref') == ref and it.get('num') == num and it['kind'] != 'hole']

jobs = [  # (net, doel-ref, doel-pen)
    ('VCC', 'J_NP', '4'), ('SDA', 'J_NP', '2'), ('SCL', 'J_NP', '3'),
    ('BAT+', 'SW_BAT', '1'), ('Net-(U1-Pad24)', 'SW_BAT', '2'),
]
new_txt = []
for net, tref, tnum in jobs:
    tp = pads_of(tref, tnum)
    own = [it for it in items if it['net'] == net and it['kind'] in ('circle', 'rect') and it not in tp]
    if not own:
        print(net, ': geen bron'); continue
    tr, vb = blocked_for(net)
    src = cells_of(own)
    tgt = cells_of(tp)
    txy = (tp[0]['x'], tp[0]['y'])
    path, n = astar(tr, vb, src, tgt, txy)
    if not path:
        print('%s: GEEN route gevonden (%d knopen)' % (net, n)); continue
    li, j, i = path[0][:3]
    sx, sy = X0 + i * G, Y0 + j * G
    # bron-pad/via waar het pad start, voor nette aansluiting
    sp = min(own, key=lambda it: math.hypot(it['x'] - sx, it['y'] - sy))
    start = (sp['x'], sp['y']) if float(dist_item(sp, np.array(sx), np.array(sy))) < 0 else None
    txt, nv = path_to_copper(path, net, start, txy)
    new_txt += txt
    L = sum(math.hypot(path[k][2] - path[k - 1][2], path[k][1] - path[k - 1][1]) for k in range(1, len(path))) * G
    print('%s -> %s.%s: %.1f mm, %d via(s), %d segmenten, %d knopen' % (net, tref, tnum, L, nv, len(txt) - nv, n))

i = t.index('\n\t(segment')
t = t[:i] + ''.join(new_txt) + t[i:]
open(PCB, 'wb').write(t.replace('\n', '\r\n').encode('utf-8'))
print('haakjes', t.count('('), t.count(')'))
