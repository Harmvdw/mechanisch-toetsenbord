#!/usr/bin/env python3
"""Draaiknop (EC11) op de plek van SW25, gecombineerd met een gesoldeerde MX-switch.

Op deze plek past een hotswap-voet niet samen met een encoder (omkeerbare print: hotswap-pads
aan beide kanten precies waar de encoderpennen komen; doorgerekend 13 nov). Daarom:
  - SW25 wordt een MX-footprint om te solderen, omkeerbaar: 4 doorgemetalliseerde gaten ø1,5 / pad ø1,8
    (col5 op (-3.81,-2.54) en (-2.54,-5.08), D25-net op (2.54,-5.08) en (3.81,-2.54)).
    Hotswap-pads, Choc-gaten en de twee pootjesgaten (5-pins) vervallen; middengat ø4 blijft.
  - ENC1 (EC11, KiCad-maten Alps EC11E) op hetzelfde middelpunt, rotatie 0:
    A (-7,-2.5) -> F4 (U1 pen 20), C (-7,0) -> GND, B (-7,2.5) -> F5 (U1 pen 19),
    S1 (7.5,-2.5) -> D25-net, S2 (7.5,2.5) -> col5 (drukknop = matrixplek van SW25),
    lipjes: sleuven zonder koper 2,6 x 1,5 mm op (0,-5.6) en (0,5.6).
  - Oude sporen naar de verwijderde pads worden verwijderd, losse uiteinden opgeruimd en alles opnieuw gerouteerd.
Gebruik: python3 encoder_lily58.py <Lily58_Pro.kicad_pcb>   (bewerkt in place; maak vooraf een kopie)
Vereist route_lily58.py in dezelfde map (parser en router).
"""
import re, sys, math, uuid, os
HERE = os.path.dirname(os.path.abspath(__file__))
PCB = sys.argv[1]
t = open(PCB, 'rb').read().decode('utf-8', 'replace').replace('\r\n', '\n')
def U(): return str(uuid.uuid4())
log = []

# ---------- 1. SW25 ombouwen ----------
m = [m for m in re.finditer(r'\n\t\(footprint "([^"]+)"(.*?)\n\t\)', t, re.S) if '"Reference" "SW25"' in m.group(2)][0]
blk = m.group(0)
cx, cy = map(float, re.search(r'\n\t\t\(at ([0-9.\-]+) ([0-9.\-]+)', blk).groups())
pads = list(re.finditer(r'\n\t\t\(pad "([^"]*)" (\w+) \w+\n\t\t\t\(at ([^)]*)\)(.*?)\n\t\t\)', blk, re.S))
keep_npth = []
for p in pads:
    if p.group(2) == 'np_thru_hole':
        at = [float(v) for v in p.group(3).split()[:2]]
        if abs(at[0]) < 1e-3 and abs(at[1]) < 1e-3: keep_npth.append(p.group(0))   # middengat ø4
new_blk = blk
for p in pads: new_blk = new_blk.replace(p.group(0), '', 1)
def tht(num, x, y, net, size=1.8, drill=1.5, shape='circle'):
    return ('\n\t\t(pad "%s" thru_hole %s\n\t\t\t(at %g %g)\n\t\t\t(size %g %g)\n\t\t\t(drill %g)\n\t\t\t(layers "*.Cu" "*.Mask")\n'
            '\t\t\t(net "%s")\n\t\t\t(uuid "%s")\n\t\t)' % (num, shape, x, y, size, size, drill, net, U()))
MID = 'Net-(D25-Pad2)'
sw_pads = ''.join(keep_npth) + tht('1', -3.81, -2.54, 'col5') + tht('1', -2.54, -5.08, 'col5') + \
          tht('2', 2.54, -5.08, MID) + tht('2', 3.81, -2.54, MID)
new_blk = new_blk.replace('\n\t\t(embedded_fonts', sw_pads + '\n\t\t(embedded_fonts', 1) if '\n\t\t(embedded_fonts' in new_blk \
          else new_blk[:-len('\n\t)')] + sw_pads + '\n\t)'
new_blk = new_blk.replace('(footprint "Lily58-footprint:CherryMX_KailhLowProfile_Hotswap_edge"', '(footprint "Lily58-footprint:MX_solder_reversible_EC11"', 1)
new_blk = re.sub(r'\n\t\t\(attr [^)]*\)', '\n\t\t(attr through_hole)', new_blk, count=1)
t = t.replace(blk, new_blk, 1)
log.append('SW25 omgebouwd: %d pads -> 1 middengat + 4 soldeergaten' % len(pads))

# ---------- 2. ENC1 plaatsen ----------
def prop(name, val, x, y, layer, hide):
    return ('\t\t(property "%s" "%s"\n\t\t\t(at %g %g 0)\n\t\t\t(layer "%s")\n%s\t\t\t(uuid "%s")\n'
            '\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1 1)\n\t\t\t\t\t(thickness 0.15)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n'
            % (name, val, x, y, layer, '\t\t\t(hide yes)\n' if hide else '', U()))
def fp_line(x1, y1, x2, y2, layer, w=0.12):
    return ('\t\t(fp_line\n\t\t\t(start %g %g)\n\t\t\t(end %g %g)\n\t\t\t(stroke\n\t\t\t\t(width %g)\n\t\t\t\t(type solid)\n\t\t\t)\n'
            '\t\t\t(layer "%s")\n\t\t\t(uuid "%s")\n\t\t)\n' % (x1, y1, x2, y2, w, layer, U()))
enc = ('\t(footprint "Lily58-footprint:RotaryEncoder_EC11E_Switch_reversible"\n\t\t(layer "F.Cu")\n\t\t(uuid "%s")\n\t\t(at %g %g)\n' % (U(), cx, cy)
       + prop('Reference', 'ENC1', 0, -8.5, 'F.Fab', False) + prop('Value', 'EC11 (alternatief voor SW25)', 0, 8.5, 'F.Fab', True)
       + prop('Datasheet', '', 0, 0, 'F.Fab', True) + prop('Description', 'Alps EC11E met drukknop; S1/S2 = matrixplek SW25', 0, 0, 'F.Fab', True)
       + '\t\t(attr through_hole)\n')
for lay in ('F.Fab', 'B.Fab'):
    enc += fp_line(-6, -6, 6, -6, lay) + fp_line(6, -6, 6, 6, lay) + fp_line(6, 6, -6, 6, lay) + fp_line(-6, 6, -6, -6, lay)
enc += ('\t\t(fp_circle\n\t\t\t(center 0 0)\n\t\t\t(end 3 0)\n\t\t\t(stroke\n\t\t\t\t(width 0.1)\n\t\t\t\t(type solid)\n\t\t\t)\n\t\t\t(fill no)\n'
        '\t\t\t(layer "F.Fab")\n\t\t\t(uuid "%s")\n\t\t)\n' % U())
for num, x, y, net in (('A', -7, -2.5, 'Net-(U1-Pad20)'), ('C', -7, 0, 'GND'), ('B', -7, 2.5, 'Net-(U1-Pad19)'),
                       ('S1', 7.5, -2.5, MID), ('S2', 7.5, 2.5, 'col5')):
    enc += tht(num, x, y, net, size=2.0, drill=1.0, shape='rect' if num == 'A' else 'circle').lstrip('\n') + '\n'
for y in (-5.6, 5.6):
    enc += ('\t\t(pad "" np_thru_hole oval\n\t\t\t(at 0 %g)\n\t\t\t(size 2.6 1.5)\n\t\t\t(drill oval 2.6 1.5)\n'
            '\t\t\t(layers "*.Cu" "*.Mask")\n\t\t\t(uuid "%s")\n\t\t)\n' % (y, U()))
enc += '\t)\n'
i = t.index('\n\t(gr_line')
t = t[:i] + '\n' + enc.rstrip('\n') + t[i:]
log.append('ENC1 geplaatst op (%g, %g)' % (cx, cy))

# ---------- 3. oude sporen naar verwijderde pads weg, losse einden opruimen ----------
old_pad_pts = []
for p in pads:
    if p.group(1) in ('1', '2') and 'smd' in p.group(2):
        x, y = [float(v) for v in p.group(3).split()[:2]]
        old_pad_pts.append((cx + x, cy + y))
seg_re = re.compile(r'\n\t\(segment\n\t\t\(start ([0-9.\-]+) ([0-9.\-]+)\)\n\t\t\(end ([0-9.\-]+) ([0-9.\-]+)\)\n\t\t\(width ([0-9.]+)\)\n\t\t\(layer "([^"]+)"\)\n\t\t\(net "([^"]*)"\)\n\t\t\(uuid "[^"]+"\)\n\t\)')
def near_old(x, y): return any(math.hypot(x - a, y - b) < 1.6 for a, b in old_pad_pts)
removed = 0
def kill(mm):
    global removed
    if mm.group(7) in ('col5', MID):
        x1, y1, x2, y2 = map(float, mm.groups()[:4])
        if near_old(x1, y1) or near_old(x2, y2):
            removed += 1; return ''
    return mm.group(0)
t = seg_re.sub(kill, t)
log.append('sporen naar oude SW25-pads verwijderd: %d' % removed)

def anchors(net):
    pts = []
    for fm in re.finditer(r'\n\t\(footprint "[^"]+"(.*?)\n\t\)', t, re.S):
        b = fm.group(1)
        if '(net "%s")' % net not in b: continue
        a = re.search(r'\n\t\t\(at ([0-9.\-]+) ([0-9.\-]+)(?: ([0-9.\-]+))?\)', b)
        fx, fy, th = float(a.group(1)), float(a.group(2)), math.radians(float(a.group(3) or 0))
        for pm in re.finditer(r'\n\t\t\(pad "[^"]*" \w+ \w+\n\t\t\t\(at ([0-9.\-]+) ([0-9.\-]+)[^)]*\)\n\t\t\t\(size ([0-9.]+) ([0-9.]+)\)(.*?)\n\t\t\)', b, re.S):
            if '(net "%s")' % net not in pm.group(5): continue
            px, py = float(pm.group(1)), float(pm.group(2))
            pts.append((fx + px * math.cos(th) + py * math.sin(th), fy - px * math.sin(th) + py * math.cos(th), max(float(pm.group(3)), float(pm.group(4))) / 2))
    for vm in re.finditer(r'\n\t\(via\n\t\t\(at ([0-9.\-]+) ([0-9.\-]+)\)\n\t\t\(size ([0-9.]+)\)(?:\n\t\t[^\n]*)*?\n\t\t\(net "%s"\)' % re.escape(net), t):
        pts.append((float(vm.group(1)), float(vm.group(2)), float(vm.group(3)) / 2))
    return pts
def prune():
    global t
    pruned = 0
    for net in ('col5', MID):
        while True:
            segs = [(mm, tuple(map(float, mm.groups()[:4])), mm.group(6)) for mm in seg_re.finditer(t) if mm.group(7) == net]
            anc = anchors(net)
            def touches(x, y, me):
                if any(math.hypot(x - a, y - b) <= r + 0.01 for a, b, r in anc): return True
                for mm, (a1, b1, a2, b2), _ in segs:
                    if mm is me: continue
                    if math.hypot(x - a1, y - b1) < 0.01 or math.hypot(x - a2, y - b2) < 0.01: return True
                return False
            dead = [mm for mm, (x1, y1, x2, y2), _ in segs if not touches(x1, y1, mm) or not touches(x2, y2, mm)]
            if not dead: break
            for mm in sorted(dead, key=lambda q: -q.start()):
                t = t[:mm.start()] + t[mm.end():]; pruned += 1
    return pruned
pruned = prune()
log.append('losse spoorstukjes opgeruimd: %d' % pruned)

# via's opruimen: zonder spoor op beide lagen, of binnen een doorgemetalliseerde pad van SW25/ENC1 (dubbel geboord)
new_tht = [(cx + x, cy + y, r) for x, y, r in [(-3.81, -2.54, 0.9), (-2.54, -5.08, 0.9), (2.54, -5.08, 0.9), (3.81, -2.54, 0.9),
                                                (-7, -2.5, 1.0), (-7, 0, 1.0), (-7, 2.5, 1.0), (7.5, -2.5, 1.0), (7.5, 2.5, 1.0)]]
via_re = re.compile(r'\n\t\(via\n\t\t\(at ([0-9.\-]+) ([0-9.\-]+)\)\n(?:\t\t[^\n]*\n)*?\t\t\(net "([^"]*)"\)\n(?:\t\t[^\n]*\n)*?\t\)')
vk = 0
for vm in list(via_re.finditer(t))[::-1]:
    net = vm.group(3)
    if net not in ('col5', MID): continue
    vx, vy = float(vm.group(1)), float(vm.group(2))
    if math.hypot(vx - cx, vy - cy) > 15: continue
    lay = set(mm.group(6) for mm in seg_re.finditer(t) if mm.group(7) == net and
              any(math.hypot(float(a) - vx, float(b) - vy) < 0.01 for a, b in ((mm.group(1), mm.group(2)), (mm.group(3), mm.group(4)))))
    in_pad = any(math.hypot(vx - x, vy - y) < r for x, y, r in new_tht)
    if len(lay) < 2 or in_pad:
        t = t[:vm.start()] + t[vm.end():]; vk += 1
log.append('via\'s verwijderd (los of binnen een pad): %d; daarna opgeruimd: %d' % (vk, prune()))

# ---------- 4. routeren met de router uit route_lily58.py ----------
src = open(os.path.join(HERE, 'route_lily58.py'), encoding='utf-8').read()
lib = src[src.index('# ---------- inlezen ----------'):src.index('# ---------- J_NP verplaatsen')]
G_ = dict(t=t, re=re, sys=sys, math=math, uuid=uuid, __name__='lib')
exec('import numpy as np, heapq\nG = 0.2\nTW = 0.25\nCL = 0.2\nK_TR = CL + TW / 2 + 0.05\nK_HOLE = 0.25 + TW / 2 + 0.05\n'
     'VIA_D, VIA_DRILL = 0.6, 0.3\nK_VIA = CL + VIA_D / 2 + 0.05\nK_EDGE = 0.5 + TW / 2 + 0.05\nLAYERS = ["F.Cu", "B.Cu"]\n' + lib, G_)
items = G_['items']
def island_groups(net):
    """verbonden groepen van koper van één net (pads, vias, sporen), via aanraking"""
    its = [it for it in items if it['net'] == net and it['kind'] in ('circle', 'rect', 'seg')]
    n = len(its); par = list(range(n))
    def f(a):
        while par[a] != a: par[a] = par[par[a]]; a = par[a]
        return a
    np_ = G_['np']
    def pts(it):
        if it['kind'] == 'seg': return [(it['x1'], it['y1']), (it['x2'], it['y2'])]
        return [(it['x'], it['y'])]
    for a in range(n):
        for b in range(a + 1, n):
            A, B = its[a], its[b]
            if not set(A['layers']) & set(B['layers']): continue
            hit = any(float(G_['dist_item'](B, np_.array(x), np_.array(y))) <= 0.01 for x, y in pts(A)) or \
                  any(float(G_['dist_item'](A, np_.array(x), np_.array(y))) <= 0.01 for x, y in pts(B))
            if hit: par[f(a)] = f(b)
    groups = {}
    for k in range(n): groups.setdefault(f(k), []).append(its[k])
    return sorted(groups.values(), key=len, reverse=True)

new_txt = []
for net in ('col5', MID, 'Net-(U1-Pad20)', 'Net-(U1-Pad19)'):
    for rnd in range(6):
        gr = island_groups(net)
        if len(gr) <= 1: break
        tgt_items = [it for it in gr[-1] if it['kind'] in ('circle', 'rect')] or gr[-1]
        own = [it for g in gr[:-1] for it in g if it['kind'] in ('circle', 'rect')]
        tr, vb = G_['blocked_for'](net)
        srcc, tgtc = G_['cells_of'](own), G_['cells_of'](tgt_items)
        txy = (tgt_items[0].get('x', tgt_items[0].get('x1')), tgt_items[0].get('y', tgt_items[0].get('y1')))
        path, nn = G_['astar'](tr, vb, srcc, tgtc, txy)
        if not path:
            log.append('%s: GEEN route voor eiland %d' % (net, rnd)); break
        li, j, i_ = path[0][:3]
        sx, sy = G_['X0'] + i_ * G_['G'], G_['Y0'] + j * G_['G']
        sp = min(own, key=lambda it: math.hypot(it['x'] - sx, it['y'] - sy))
        start = (sp['x'], sp['y']) if float(G_['dist_item'](sp, G_['np'].array(sx), G_['np'].array(sy))) < 0 else None
        end = txy if tgt_items[0]['kind'] in ('circle', 'rect') else None
        txt, nv = G_['path_to_copper'](path, net, start, end)
        new_txt += txt
        log.append('%s: eiland %d verbonden, %d stukken, %d via(s)' % (net, rnd + 1, len(txt) - nv, nv))
    log.append('%s: %d eiland(en) over' % (net, len(island_groups(net))))
t = G_['t']
i = t.index('\n\t(segment')
t = t[:i] + ''.join(new_txt) + t[i:]
open(PCB, 'wb').write(t.replace('\n', '\r\n').encode('utf-8'))
print('\n'.join(log)); print('haakjes', t.count('('), t.count(')'))
