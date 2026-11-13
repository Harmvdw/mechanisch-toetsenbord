"""Eenvoudige afstandscontrole koper, als snelle controle zonder KiCad (geen vervanging van de DRC).
Pads als capsule/cirkel, sporen als lijnstuk, via's als cirkel; ook afstand tot de printrand.
Gebruik: python3 afstand_controle.py <bord.kicad_pcb> <net1,net2,...>   (toont de kleinste afstanden van die netten)
"""
import re, sys, math
t = open(sys.argv[1], encoding='utf-8', errors='replace').read().replace('\r\n', '\n')
focus = set(sys.argv[2].split(','))           # netten om te controleren
items = []   # (layerset, net, kind, geom)
for m in re.finditer(r"\(footprint \"([^\"]+)\"(.*?)\n\t\)", t, re.S):
    b = m.group(2)
    fx, fy = map(float, re.search(r'\n\t\t\(at ([0-9.\-]+) ([0-9.\-]+)', b).groups())
    ref = re.search(r'"Reference" "([^"]+)"', b).group(1)
    for p in re.finditer(r'\n\t\t\(pad "([^"]*)" (\w+) (\w+)(.*?)\n\t\t\)', b, re.S):
        body = p.group(4)
        at = [float(v) for v in re.search(r'\(at ([^)]*)\)', body).group(1).split()[:2]]
        sz = [float(v) for v in re.search(r'\(size ([^)]*)\)', body).group(1).split()]
        lay = re.search(r'\(layers ([^)]*)\)', body).group(1)
        net = re.search(r'\(net "([^"]*)"\)', body); net = net.group(1) if net else ''
        layers = {'F.Cu', 'B.Cu'} if '*.Cu' in lay else ({'F.Cu'} if 'F.Cu' in lay else ({'B.Cu'} if 'B.Cu' in lay else set()))
        if p.group(2) == 'np_thru_hole': net = '#NPTH'; layers = {'F.Cu', 'B.Cu'}
        shape = 'circle' if p.group(3) == 'circle' else 'rect'
        items.append((layers, net, ('pad', ref, p.group(1)), ('rect', fx + at[0], fy + at[1], sz[0], sz[1]) if shape == 'rect' or sz[0] != sz[1] else ('circ', fx + at[0], fy + at[1], sz[0] / 2)))
for m in re.finditer(r'\(segment\s*\(start ([^)]*)\)\s*\(end ([^)]*)\)\s*\(width ([^)]*)\)\s*\(layer "([^"]+)"\)\s*\(net "?([^")]*)"?\)', t):
    a = list(map(float, m.group(1).split())); b2 = list(map(float, m.group(2).split()))
    items.append(({m.group(4)}, m.group(5), ('seg',), ('seg', a[0], a[1], b2[0], b2[1], float(m.group(3)) / 2)))
for m in re.finditer(r'\(via\s*\(at ([^)]*)\)\s*\(size ([^)]*)\)\s*\(drill [^)]*\)\s*\(layers [^)]*\)\s*\(net "?([^")]*)"?\)', t):
    a = list(map(float, m.group(1).split()))
    items.append(({'F.Cu', 'B.Cu'}, m.group(3), ('via',), ('circ', a[0], a[1], float(m.group(2)) / 2)))
def samples(g, n=40):
    if g[0] == 'circ': return [(g[1], g[2], g[3])]
    if g[0] == 'seg':
        return [(g[1] + (g[3] - g[1]) * i / n, g[2] + (g[4] - g[2]) * i / n, g[5]) for i in range(n + 1)]
    _, x, y, w, h = g; r = min(w, h) / 2
    if w >= h: return [(x - w / 2 + r + (w - 2 * r) * i / n, y, r) for i in range(n + 1)]
    return [(x, y - h / 2 + r + (h - 2 * r) * i / n, r) for i in range(n + 1)]
def dist(g1, g2):
    best = 1e9
    for x1, y1, r1 in samples(g1):
        for x2, y2, r2 in samples(g2):
            # rechthoekige pads benaderd als capsule (bovengrens voor de afstand)
            best = min(best, math.hypot(x1 - x2, y1 - y2) - r1 - r2)
    return best
edges = [tuple(map(float, (m.group(1) + ' ' + m.group(2)).split())) for m in re.finditer(r'\(gr_line\s*\(start ([^)]*)\)\s*\(end ([^)]*)\)\s*\(stroke\s*\(width [^)]*\)\s*\(type \w+\)\s*\)\s*\(layer "Edge.Cuts"\)', t)]
worst = []
for i, (l1, n1, k1, g1) in enumerate(items):
    if n1 not in focus: continue
    for j, (l2, n2, k2, g2) in enumerate(items):
        if i == j or n1 == n2 or not (l1 & l2): continue
        # snelle voorselectie
        c1 = samples(g1, 1)[0]; c2 = samples(g2, 1)[0]
        if math.hypot(c1[0] - c2[0], c1[1] - c2[1]) > 25: continue
        d = dist(g1, g2)
        worst.append((round(d, 3), n1, k1, n2, k2))
    de = min(dist(g1, ('seg', e[0], e[1], e[2], e[3], 0)) for e in edges)
    worst.append((round(de, 3), n1, k1, 'RAND', ''))
worst.sort()
for w in worst[:12]: print(w)
print('kleinste afstand', worst[0][0], 'mm; items gecontroleerd', len([1 for it in items if it[1] in focus]))
