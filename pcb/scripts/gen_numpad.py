#!/usr/bin/env python3
"""Genereert numpad/numpad.kicad_pcb (KiCad 10) op basis van footprints uit Lily58_Pro.kicad_pcb.
Gebruik: python3 gen_numpad.py <pad naar Lily58_Pro.kicad_pcb> <uitvoerbestand>
"""
import re, sys, uuid

SRC, OUT = sys.argv[1], sys.argv[2]
src = open(SRC, 'rb').read().decode('utf-8', 'replace').replace('\r\n', '\n')

def new_uuid(): return str(uuid.uuid4())

# ---------- sjablonen uit de Lily58-print ----------
blocks = re.findall(r'(\(footprint "([^"]+)".*?\n\t\))', src, re.S)
tpl = {}
for blk, name in blocks:
    ref = re.search(r'\(property "Reference" "([^"]+)"', blk).group(1)
    if ref in ('SW1', 'D1'):
        tpl[ref] = blk

def instantiate(block, ref, x, y, nets, value=None, layer=None):
    b = block
    b = re.sub(r'\(at [0-9.\-]+ [0-9.\-]+(?: [0-9.\-]+)?\)', '(at %g %g)' % (x, y), b, count=1)
    b = re.sub(r'\(property "Reference" "[^"]+"', '(property "Reference" "%s"' % ref, b, count=1)
    if value is not None:
        b = re.sub(r'\(property "Value" "[^"]*"', '(property "Value" "%s"' % value, b, count=1)
    if layer is not None:
        b = re.sub(r'\(layer "[^"]+"\)', '(layer "%s")' % layer, b, count=1)
    b = re.sub(r'\n\t\t\(path "[^"]*"\)', '', b)
    b = re.sub(r'\(uuid "[^"]+"\)', lambda m: '(uuid "%s")' % new_uuid(), b)
    # pads: netten opnieuw toekennen, 0,1 mm-gaatjes en dubbel 3 mm-gat weg
    seen = set()
    def fix_pad(m):
        pad = m.group(0)
        num = m.group(1)
        if '(size 0.1 0.1)' in pad:
            return ''
        at = re.search(r'\(at [^)]*\)', pad).group(0)
        key = (num, at, re.search(r'\(size [^)]*\)', pad).group(0))
        if num == '' and key in seen:
            return ''
        if num == '':
            # numpad is alleen MX, niet omkeerbaar: ongebruikte gaten (Choc + gespiegelde MX) weg
            a = [float(v) for v in re.findall(r'-?[0-9.]+', at)[:2]]
            sz = re.search(r'\(size ([0-9.]+)', pad).group(1)
            keep3 = [(-3.81, -2.54), (2.54, -5.08)]
            if sz == '1.9': return ''
            if sz == '3' and not any(abs(a[0]-x) < 0.01 and abs(a[1]-y) < 0.01 for x, y in keep3): return ''
        if num in ('1', '2') and 'smd' in pad:
            # numpad: alleen MX-hotswap aan de onderkant; voorkant- en Choc-pads weg
            if '"F.Cu"' in pad or ' 3.7' in at or ' 5.9' in at:
                return ''
        seen.add(key)
        pad = re.sub(r'\n\t\t\t\(net "[^"]*"\)', '', pad)
        if num in nets:
            pad = re.sub(r'(\n\t\t\t\(layers [^)]*\))', r'\1\n\t\t\t(net "%s")' % nets[num], pad, count=1)
        return pad
    b = re.sub(r'\n\t\t\(pad "([^"]*)".*?\n\t\t\)', fix_pad, b, flags=re.S)
    return b

# ---------- eigen footprints ----------
def prop(name, val, x, y, layer, hide):
    return ('\t\t(property "%s" "%s"\n\t\t\t(at %g %g 0)\n\t\t\t(layer "%s")\n%s\t\t\t(uuid "%s")\n'
            '\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1 1)\n\t\t\t\t\t(thickness 0.15)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n'
            % (name, val, x, y, layer, '\t\t\t(hide yes)\n' if hide else '', new_uuid()))

def fp_header(libname, ref, value, x, y, attr, ref_dy=-6, layer='F.Cu'):
    return ('\t(footprint "%s"\n\t\t(layer "%s")\n\t\t(uuid "%s")\n\t\t(at %g %g)\n' % (libname, layer, new_uuid(), x, y)
            + prop('Reference', ref, 0, ref_dy, 'F.SilkS', False)
            + prop('Value', value, 0, -ref_dy, 'F.Fab', True)
            + prop('Datasheet', '', 0, 0, 'F.Fab', True)
            + prop('Description', '', 0, 0, 'F.Fab', True)
            + '\t\t(attr %s)\n' % attr)

def fp_line(x1, y1, x2, y2, layer, w=0.12):
    return ('\t\t(fp_line\n\t\t\t(start %g %g)\n\t\t\t(end %g %g)\n\t\t\t(stroke\n\t\t\t\t(width %g)\n\t\t\t\t(type solid)\n\t\t\t)\n'
            '\t\t\t(layer "%s")\n\t\t\t(uuid "%s")\n\t\t)\n' % (x1, y1, x2, y2, w, layer, new_uuid()))

def fp_rect(x1, y1, x2, y2, layer, w=0.12):
    return (fp_line(x1, y1, x2, y1, layer, w) + fp_line(x2, y1, x2, y2, layer, w)
            + fp_line(x2, y2, x1, y2, layer, w) + fp_line(x1, y2, x1, y1, layer, w))

def pad_smd(num, x, y, sx, sy, net=None):
    s = '\t\t(pad "%s" smd roundrect\n\t\t\t(at %g %g)\n\t\t\t(size %g %g)\n\t\t\t(layers "F.Cu" "F.Mask" "F.Paste")\n\t\t\t(roundrect_rratio 0.25)\n' % (num, x, y, sx, sy)
    if net: s += '\t\t\t(net "%s")\n' % net
    return s + '\t\t\t(uuid "%s")\n\t\t)\n' % new_uuid()

def pad_tht(num, x, y, size, drill, net=None, shape='circle'):
    s = '\t\t(pad "%s" thru_hole %s\n\t\t\t(at %g %g)\n\t\t\t(size %g %g)\n\t\t\t(drill %g)\n\t\t\t(layers "*.Cu" "*.Mask")\n' % (num, shape, x, y, size, size, drill)
    if net: s += '\t\t\t(net "%s")\n' % net
    return s + '\t\t\t(uuid "%s")\n\t\t)\n' % new_uuid()

def pad_npth(x, y, drill):
    return '\t\t(pad "" np_thru_hole circle\n\t\t\t(at %g %g)\n\t\t\t(size %g %g)\n\t\t\t(drill %g)\n\t\t\t(layers "*.Cu" "*.Mask")\n\t\t\t(uuid "%s")\n\t\t)\n' % (x, y, drill, drill, drill, new_uuid())

def soic28w(ref, x, y, nets):
    """SOIC-28W, 7,5 mm body, pitch 1,27. Pen 1 linksonder; 1-14 onderste rij (links->rechts), 15-28 bovenste rij (rechts->links)."""
    s = fp_header('Numpad:SOIC-28W_7.5x17.9mm_P1.27mm', ref, 'MCP23017-E/SO', x, y, 'smd', ref_dy=0)
    s += fp_rect(-8.95, -3.75, 8.95, 3.75, 'F.SilkS', 0.15)
    s += fp_line(-8.95, 3.75, -8.95, 2.5, 'F.SilkS', 0.3)  # pen-1 markering
    s += fp_rect(-9.5, -5.95, 9.5, 5.95, 'F.CrtYd', 0.05)
    for i in range(1, 15):
        px = -8.255 + (i - 1) * 1.27
        s += pad_smd(str(i), px, 4.7, 0.65, 2.0, nets.get(str(i)))
    for i in range(15, 29):
        px = 8.255 - (i - 15) * 1.27
        s += pad_smd(str(i), px, -4.7, 0.65, 2.0, nets.get(str(i)))
    return s + '\t)\n'

def r_c_0805(ref, value, x, y, nets, lib):
    s = fp_header('Numpad:%s' % lib, ref, value, x, y, 'smd', ref_dy=-2)
    s += fp_rect(-1.0, -0.65, 1.0, 0.65, 'F.Fab', 0.1)
    s += fp_rect(-1.7, -1.0, 1.7, 1.0, 'F.CrtYd', 0.05)
    s += pad_smd('1', -0.95, 0, 1.0, 1.45, nets.get('1'))
    s += pad_smd('2', 0.95, 0, 1.0, 1.45, nets.get('2'))
    return s + '\t)\n'

def conn4(ref, x, y, nets, layer='F.Cu'):
    """1x4 doorlopend, pitch 2,54, verticaal (pen 1 bovenaan). Voor Adafruit 5358 (magnetisch, haaks)."""
    s = fp_header('Numpad:Magnetic_5358_1x4_P2.54_Vertical', ref, 'Adafruit 5358', x, y, 'through_hole', ref_dy=-6.5, layer=layer)
    s += fp_rect(-1.5, -5.1, 1.5, 5.1, 'F.SilkS', 0.15)
    s += fp_rect(-2.0, -5.6, 2.0, 5.6, 'F.CrtYd', 0.05)
    for i in range(4):
        s += pad_tht(str(i + 1), 0, -3.81 + i * 2.54, 1.7, 1.0, nets.get(str(i + 1)), 'rect' if i == 0 else 'circle')
    return s + '\t)\n'

def hole_m3(ref, x, y):
    s = fp_header('Numpad:MountingHole_3.2mm', ref, 'M3', x, y, 'exclude_from_pos_files exclude_from_bom', ref_dy=-3)
    s += pad_npth(0, 0, 3.2)
    s += '\t\t(fp_circle\n\t\t\t(center 0 0)\n\t\t\t(end 3.2 0)\n\t\t\t(stroke\n\t\t\t\t(width 0.05)\n\t\t\t\t(type solid)\n\t\t\t)\n\t\t\t(fill no)\n\t\t\t(layer "F.CrtYd")\n\t\t\t(uuid "%s")\n\t\t)\n' % new_uuid()
    return s + '\t)\n'

def gr_line(x1, y1, x2, y2, layer='Edge.Cuts', w=0.1):
    return ('\t(gr_line\n\t\t(start %g %g)\n\t\t(end %g %g)\n\t\t(stroke\n\t\t\t(width %g)\n\t\t\t(type solid)\n\t\t)\n\t\t(layer "%s")\n\t\t(uuid "%s")\n\t)\n'
            % (x1, y1, x2, y2, w, layer, new_uuid()))

def gr_text(txt, x, y, layer='F.SilkS', size=1.5):
    return ('\t(gr_text "%s"\n\t\t(at %g %g 0)\n\t\t(layer "%s")\n\t\t(uuid "%s")\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size %g %g)\n\t\t\t\t(thickness 0.2)\n\t\t\t)\n\t\t)\n\t)\n'
            % (txt, x, y, layer, new_uuid(), size, size))

def zone(net, layer, pts):
    return ('\t(zone\n\t\t(net "%s")\n\t\t(layer "%s")\n\t\t(uuid "%s")\n\t\t(hatch edge 0.5)\n\t\t(connect_pads\n\t\t\t(clearance 0.5)\n\t\t)\n'
            '\t\t(min_thickness 0.25)\n\t\t(fill yes\n\t\t\t(thermal_gap 0.5)\n\t\t\t(thermal_bridge_width 0.5)\n\t\t)\n\t\t(polygon\n\t\t\t(pts\n\t\t\t\t%s\n\t\t\t)\n\t\t)\n\t)\n'
            % (net, layer, new_uuid(), ' '.join('(xy %g %g)' % p for p in pts)))

# ---------- maten ----------
P = 19.05
X0, Y0 = 60.0, 60.0            # hart toets kolom 0, rij 0
NC, NR = 4, 5
SIDE = 10.0                    # extra zijrand voor connector, feeders en gaten
STRIP = 14.0                   # strook boven rij 0 voor MCP23017
BOT = 4.5                      # extra onderrand voor de I2C/VCC-lus
L = X0 - P / 2 - SIDE
R = X0 + (NC - 1) * P + P / 2 + SIDE
T = Y0 - P / 2 - STRIP
B = Y0 + (NR - 1) * P + P / 2 + BOT
TW = 0.25                      # spoorbreedte

def seg(x1, y1, x2, y2, layer, net, w=TW):
    return ('\t(segment\n\t\t(start %g %g)\n\t\t(end %g %g)\n\t\t(width %g)\n\t\t(layer "%s")\n\t\t(net "%s")\n\t\t(uuid "%s")\n\t)\n'
            % (round(x1, 4), round(y1, 4), round(x2, 4), round(y2, 4), w, layer, net, new_uuid()))

def path(pts, layer, net):
    return ''.join(seg(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], layer, net) for i in range(len(pts) - 1))

def via(x, y, net):
    return ('\t(via\n\t\t(at %g %g)\n\t\t(size 0.6)\n\t\t(drill 0.3)\n\t\t(layers "F.Cu" "B.Cu")\n\t\t(net "%s")\n\t\t(uuid "%s")\n\t)\n'
            % (round(x, 4), round(y, 4), net, new_uuid()))

out = []
out.append('(kicad_pcb\n\t(version 20260206)\n\t(generator "gen_numpad")\n\t(generator_version "10.0")\n'
           '\t(general\n\t\t(thickness 1.6)\n\t\t(legacy_teardrops no)\n\t)\n\t(paper "A4")\n')
# lagen + setup overnemen van de Lily58-print
m = re.search(r'\t\(layers\n.*?\n\t\)\n\t\(setup\n.*?\n\t\)\n', src, re.S)
out.append(m.group(0))

# toetsen en diodes
n = 0
for r in range(NR):
    for c in range(NC):
        n += 1
        sx, sy = X0 + c * P, Y0 + r * P
        col, row, mid = 'np_col%d' % c, 'np_row%d' % r, 'Net-(D%d-Pad2)' % n
        out.append(instantiate(tpl['SW1'], 'SW%d' % n, sx, sy, {'1': col, '2': mid}, value='MX_hotswap'))
        out.append(instantiate(tpl['D1'], 'D%d' % n, sx + 5.0, sy + 8.5, {'1': row, '2': mid}, value='1N4148W'))

# MCP23017: 1-5 GPB0-4 = rijen, 21-24 GPA0-3 = kolommen
u1 = {'5': 'np_row0', '4': 'np_row1', '3': 'np_row2', '2': 'np_row3', '1': 'np_row4',
      '21': 'np_col0', '22': 'np_col1', '23': 'np_col2', '24': 'np_col3',
      '9': 'VCC', '10': 'GND', '15': 'GND', '16': 'GND', '17': 'GND',
      '12': 'SCL', '13': 'SDA', '18': 'nRESET'}
UX, UY = X0 + 1.5 * P, T + STRIP / 2 - 0.5
out.append(soic28w('U1', UX, UY, u1))
CX, CY = UX + 13.5, UY + 3.0           # C1: pad1 VCC (links), pad2 GND
RX, RY = UX + 11.9, UY - 1.475       # R1: pad1 nRESET (links), pad2 VCC
out.append(r_c_0805('C1', '100nF', CX, CY, {'1': 'VCC', '2': 'GND'}, 'C_0805'))
out.append(r_c_0805('R1', '10k', RX, RY, {'1': 'nRESET', '2': 'VCC'}, 'R_0805'))

# connectoren (J2 later in KiCad omklappen naar de achterkant)
JY = Y0 + 2 * P
JX1, JX2 = L + 4.725, R - 4.725
jn = {'1': 'GND', '2': 'SDA', '3': 'SCL', '4': 'VCC'}
out.append(conn4('J1', JX1, JY, jn))
out.append(conn4('J2', JX2, JY, jn))

# montagegaten M3
holes = [(JX1, T + 5.5), (JX2, T + 5.5), (JX1, B - 6.0), (JX2, B - 6.0),
         (X0 + 0.2625 * P, T + 10.425), (X0 + 2.78 * P, T + 10.425)]
for i, (hx, hy) in enumerate(holes, 1):
    out.append(hole_m3('H%d' % i, hx, hy))

# ---------- routering ----------
def ux(pin):  # x van U1-pen
    return UX - 8.255 + (pin - 1) * 1.27 if pin <= 14 else UX + 8.255 - (pin - 15) * 1.27
UYB, UYT = UY + 4.7 + 1.0, UY - 4.7 - 1.0   # onderrand onderste pads / bovenrand bovenste pads (y)
UYB_PAD, UYT_PAD = UY + 4.7, UY - 4.7

rt = []
for r in range(NR):
    for c in range(NC):
        n = r * NC + c + 1
        sx, sy = X0 + c * P, Y0 + r * P
        col, row, mid = 'np_col%d' % c, 'np_row%d' % r, 'Net-(D%d-Pad2)' % n
        # diode pad2 (sx+6.7, sy+8.5) -> hotswap pad2 (sx+7.2, sy-5.1) op B.Cu
        rt.append(path([(sx + 6.7, sy + 8.5), (sx + 7.6, sy + 7.6), (sx + 7.6, sy - 5.1), (sx + 7.2, sy - 5.1)], 'B.Cu', mid))
        # diode pad1 (sx+3.3, sy+8.5) -> rijlijn y=sy+10 op F.Cu
        rt.append(path([(sx + 3.3, sy + 8.5), (sx + 3.3, sy + 10.0)], 'F.Cu', row))
        # kolom: hotswap pad1 (sx-6.9, sy-2.54) -> (sx-8.5,-2.5) -> bypass x=sx-9.6, B.Cu
        rt.append(path([(sx - 6.9, sy - 2.54), (sx - 8.5, sy - 2.5), (sx - 9.6, sy - 2.5)], 'B.Cu', col))
        if r < NR - 1:
            rt.append(path([(sx - 9.6, sy - 2.5), (sx - 9.6, sy + P - 2.5)], 'B.Cu', col))
# rijlijnen F.Cu y=sy+10 van feeder tot kolom 3, en feeders + pinstubs
for r in range(NR):
    sy = Y0 + r * P
    yl = sy + 10.0
    xf = L + 0.625 + 0.5 * (NR - 1 - r)            # feeder x (F.Cu)
    yh = T + 14.525 + 0.5 * (NR - 1 - r)           # horizontale lijn onder U1 (F.Cu): 51.0 + 0.5r
    xp = ux(NR - r)                      # pen 1..5
    row = 'np_row%d' % r
    rt.append(path([(xf, yl), (X0 + 3 * P + 3.3, yl)], 'F.Cu', row))
    rt.append(path([(xf, yl), (xf, yh), (xp, yh), (xp, UYB_PAD)], 'F.Cu', row))
# kolommen -> U1 pennen 21..24 (bovenste rij) via B.Cu lijn + via onder de chip + F.Cu stub
col_y = {0: UY - 1.975, 1: UY - 1.075, 2: UY + 0.725, 3: UY - 0.175}   # 41.0, 41.9, 43.7, 42.8
for c in range(NC):
    sx = X0 + c * P
    xb = sx - 9.6
    xp = ux(21 + c)
    y = col_y[c]
    net = 'np_col%d' % c
    rt.append(path([(xb, Y0 - 2.5), (xb, y), (xp, y)], 'B.Cu', net))
    rt.append(via(xp, y, net))
    rt.append(path([(xp, y), (xp, UYT_PAD)], 'F.Cu', net))
# I2C en VCC: lus onder langs, risers links (B.Cu) en rechts (F.Cu)
Y_SCL, Y_SDA, Y_VCC = B - 2.925, B - 2.225, B - 1.525
XL = {'SCL': L + 8.425, 'SDA': L + 7.625, 'VCC': L + 6.825}  # 48.9 / 48.1 / 47.3  (B.Cu)
XR = {'SCL': R - 9.675, 'SDA': R - 8.875, 'VCC': R - 8.075}  # 127.0 / 127.8 / 128.6 (F.Cu)
JYP = {'GND': JY - 3.81, 'SDA': JY - 1.27, 'SCL': JY + 1.27, 'VCC': JY + 3.81}
YL = {'SCL': Y_SCL, 'SDA': Y_SDA, 'VCC': Y_VCC}
for net in ('SCL', 'SDA', 'VCC'):
    # links: riser B.Cu van connector-y naar lus, via + F.Cu stub naar J1-pad
    rt.append(path([(XL[net], JYP[net]), (XL[net], YL[net]), (XR[net], YL[net])], 'B.Cu', net))
    rt.append(via(XL[net], JYP[net], net))
    rt.append(path([(XL[net], JYP[net]), (JX1, JYP[net])], 'F.Cu', net))
    # rechts: via op de lus, riser F.Cu omhoog, B.Cu stub naar J2-pad via via
    rt.append(via(XR[net], YL[net], net))
    rt.append(via(XR[net], JYP[net], net))
    rt.append(path([(XR[net], JYP[net]), (JX2, JYP[net])], 'B.Cu', net))
Y_SDA_T, Y_SCL_T, Y_VCC_T = T + 12.825, T + 13.525, T + 8.025   # 49.3 / 50.0 / 44.5
rt.append(path([(XR['SDA'], Y_SDA), (XR['SDA'], Y_SDA_T), (ux(13), Y_SDA_T), (ux(13), UYB_PAD)], 'F.Cu', 'SDA'))
rt.append(path([(XR['SCL'], Y_SCL), (XR['SCL'], Y_SCL_T), (ux(12), Y_SCL_T), (ux(12), UYB_PAD)], 'F.Cu', 'SCL'))
rt.append(path([(XR['VCC'], Y_VCC), (XR['VCC'], Y_VCC_T), (ux(9), Y_VCC_T), (ux(9), UYB_PAD)], 'F.Cu', 'VCC'))
rt.append(path([(RX + 0.95, RY), (RX + 0.95, Y_VCC_T)], 'F.Cu', 'VCC'))          # R1.2 -> VCC-lijn
rt.append(path([(CX - 0.95, CY), (CX - 0.95, Y_VCC_T)], 'F.Cu', 'VCC'))          # C1.1 -> VCC-lijn
rt.append(path([(ux(18), UYT_PAD), (ux(18), RY - 0.9), (RX - 0.95, RY - 0.9), (RX - 0.95, RY)], 'F.Cu', 'nRESET'))
rt.append(path([(ux(15), UYT_PAD), (ux(17), UYT_PAD)], 'F.Cu', 'GND'))   # A0-A2 aan elkaar
out.extend(rt)

# omtrek
out.append(gr_line(L, T, R, T) + gr_line(R, T, R, B) + gr_line(R, B, L, B) + gr_line(L, B, L, T))
out.append(gr_text('NUMPAD v0.3', X0 + 3.2 * P, T + 3.0, 'F.SilkS', 1.2))
out.append(gr_text('J1 boven / J2 onder', X0 + 3.2 * P, T + 5.0, 'F.Fab', 1.0))

# GND-vlakken
pts = [(L, T), (R, T), (R, B), (L, B)]
out.append(zone('GND', 'F.Cu', pts))
out.append(zone('GND', 'B.Cu', pts))
out.append(')\n')

text = ''.join(out)
open(OUT, 'wb').write(text.replace('\n', '\r\n').encode('utf-8'))
print('geschreven:', OUT, 'omtrek %.2f x %.2f mm (L=%g T=%g R=%g B=%g)' % (R - L, B - T, L, T, R, B))
print('footprints:', len(re.findall(r'\n\t\(footprint ', text)), ' pads met net:', len(re.findall(r'\(net "', text)))
