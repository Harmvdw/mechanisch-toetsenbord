#!/usr/bin/env python3
"""Route-2-voorbereiding Lily58 Pro: J_NP, batterij-pads, 0,1 mm-gaatjes weg, stompjes weg.
Gebruik: python3 mod_lily58.py <Lily58_Pro.kicad_pcb> <MX_Choc_Hotswap.kicad_mod>
Bewerkt beide bestanden in place (maak vooraf een kopie)."""
import re, sys, uuid

PCB, MOD = sys.argv[1], sys.argv[2]
t = open(PCB, 'rb').read().decode('utf-8', 'replace').replace('\r\n', '\n')
n0 = len(t)

def new_uuid(): return str(uuid.uuid4())
log = []

# 1. 0,1 mm NPTH-pads weg (instanties)
t, k = re.subn(r'\n\t\t\(pad "" np_thru_hole circle\n\t\t\t\(at [^)]*\)\n\t\t\t\(size 0\.1 0\.1\)\n\t\t\t\(drill 0\.1\)\n(?:\t\t\t[^\n]*\n)*?\t\t\)', '', t)
log.append('0,1 mm-pads verwijderd uit print: %d' % k)

# 2. nul-spoor en stompjes weg (exacte segmenten uit het DRC-rapport)
def del_seg(sx, sy, net, layer, maxlen):
    global t
    pat = re.compile(r'\n\t\(segment\n\t\t\(start ([0-9.\-]+) ([0-9.\-]+)\)\n\t\t\(end ([0-9.\-]+) ([0-9.\-]+)\)\n\t\t\(width [0-9.]+\)\n\t\t\(layer "%s"\)\n\t\t\(net "%s"\)\n\t\t\(uuid "[^"]+"\)\n\t\)' % (layer, re.escape(net)))
    removed = 0
    def f(m):
        nonlocal removed
        x1, y1, x2, y2 = map(float, m.groups())
        L = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        near = min(abs(x1 - sx) + abs(y1 - sy), abs(x2 - sx) + abs(y2 - sy)) < 0.02
        if near and L <= maxlen + 1e-6:
            removed += 1
            return ''
        return m.group(0)
    t = pat.sub(f, t)
    log.append('segment %s %s bij (%g, %g): %d verwijderd' % (net, layer, sx, sy, removed))

del_seg(105.3, 67.1, 'row4', 'F.Cu', 0.001)
del_seg(110.825, 88.9, 'row4', 'F.Cu', 0.0751)
del_seg(132.6, 61.9, 'col4', 'B.Cu', 2.2601)
del_seg(94.7, 43.77, 'DATA', 'F.Cu', 0.2701)

# 3. nieuwe footprints
def prop(name, val, x, y, layer, hide):
    return ('\t\t(property "%s" "%s"\n\t\t\t(at %g %g 0)\n\t\t\t(layer "%s")\n%s\t\t\t(uuid "%s")\n'
            '\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1 1)\n\t\t\t\t\t(thickness 0.15)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n'
            % (name, val, x, y, layer, '\t\t\t(hide yes)\n' if hide else '', new_uuid()))

def fp_header(libname, ref, value, x, y, ref_dx, ref_dy):
    return ('\t(footprint "%s"\n\t\t(layer "F.Cu")\n\t\t(uuid "%s")\n\t\t(at %g %g)\n' % (libname, new_uuid(), x, y)
            + prop('Reference', ref, ref_dx, ref_dy, 'F.SilkS', False)
            + prop('Value', value, 0, -ref_dy, 'F.Fab', True)
            + prop('Datasheet', '', 0, 0, 'F.Fab', True)
            + prop('Description', '', 0, 0, 'F.Fab', True)
            + '\t\t(attr through_hole)\n')

def fp_line(x1, y1, x2, y2, layer, w=0.12):
    return ('\t\t(fp_line\n\t\t\t(start %g %g)\n\t\t\t(end %g %g)\n\t\t\t(stroke\n\t\t\t\t(width %g)\n\t\t\t\t(type solid)\n\t\t\t)\n'
            '\t\t\t(layer "%s")\n\t\t\t(uuid "%s")\n\t\t)\n' % (x1, y1, x2, y2, w, layer, new_uuid()))

def fp_rect(x1, y1, x2, y2, layer, w=0.12):
    return (fp_line(x1, y1, x2, y1, layer, w) + fp_line(x2, y1, x2, y2, layer, w)
            + fp_line(x2, y2, x1, y2, layer, w) + fp_line(x1, y2, x1, y1, layer, w))

def pad_tht(num, x, y, size, drill, net, shape='circle'):
    return ('\t\t(pad "%s" thru_hole %s\n\t\t\t(at %g %g)\n\t\t\t(size %g %g)\n\t\t\t(drill %g)\n\t\t\t(layers "*.Cu" "*.Mask")\n\t\t\t(net "%s")\n\t\t\t(uuid "%s")\n\t\t)\n'
            % (num, shape, x, y, size, size, drill, net, new_uuid()))

def conn4(ref, x, y, nets):
    s = fp_header('Numpad:Magnetic_5358_1x4_P2.54_Vertical', ref, 'Adafruit 5358 (contactvlak)', x, y, -3.5, 0)
    s += fp_rect(-1.5, -5.1, 1.5, 5.1, 'F.SilkS', 0.15) + fp_rect(-1.5, -5.1, 1.5, 5.1, 'B.SilkS', 0.15)
    s += fp_rect(-2.0, -5.6, 2.0, 5.6, 'F.CrtYd', 0.05)
    for i in range(4):
        s += pad_tht(str(i + 1), 0, -3.81 + i * 2.54, 1.7, 1.0, nets[str(i + 1)], 'rect' if i == 0 else 'circle')
    return s + '\t)\n'

def jst_ph2(ref, x, y, nets):
    s = fp_header('Numpad:JST_PH_1x02_P2.00mm_Vertical', ref, 'BAT (onbestukt)', x, y, 0, -3.5)
    s += fp_rect(-2.95, -1.7, 2.95, 2.8, 'F.SilkS', 0.15) + fp_rect(-2.95, -1.7, 2.95, 2.8, 'B.SilkS', 0.15)
    s += fp_rect(-3.45, -2.2, 3.45, 3.3, 'F.CrtYd', 0.05)
    s += pad_tht('1', -1.0, 0, 1.6, 0.8, nets['1'], 'rect') + pad_tht('2', 1.0, 0, 1.6, 0.8, nets['2'])
    return s + '\t)\n'

def sw2(ref, x, y, nets):
    s = fp_header('Numpad:Switch_pads_1x02_P2.54mm', ref, 'SW_BAT (onbestukt)', x, y, 0, -3.0)
    s += fp_rect(-2.5, -1.3, 2.5, 1.3, 'F.SilkS', 0.15) + fp_rect(-2.5, -1.3, 2.5, 1.3, 'B.SilkS', 0.15)
    s += fp_rect(-3.0, -1.8, 3.0, 1.8, 'F.CrtYd', 0.05)
    s += pad_tht('1', -1.27, 0, 1.7, 1.0, nets['1'], 'rect') + pad_tht('2', 1.27, 0, 1.7, 1.0, nets['2'])
    return s + '\t)\n'

new = ''
new += conn4('J_NP', 222.3, 81.7, {'1': 'GND', '2': 'SDA', '3': 'SCL', '4': 'VCC'})
new += jst_ph2('J_BAT', 87.0, 78.5, {'1': 'BAT+', '2': 'GND'})
new += sw2('SW_BAT', 87.0, 93.0, {'1': 'BAT+', '2': 'Net-(U1-Pad24)'})
# invoegen vóór het eerste gr_line
i = t.index('\n\t(gr_line')
t = t[:i] + '\n' + new.rstrip('\n') + t[i:]
log.append('footprints toegevoegd: J_NP (222.3, 81.7), J_BAT (87, 78.5), SW_BAT (87, 93)')

open(PCB, 'wb').write(t.replace('\n', '\r\n').encode('utf-8'))

# 4. footprint-bibliotheek: 0,1 mm-gaatjes weg
m = open(MOD, 'rb').read().decode('utf-8', 'replace')
m2, k = re.subn(r'\n[^\n]*np_thru_hole circle \(at [^)]*\) \(size 0\.1 0\.1\) \(drill 0\.1\)[^\n]*', '', m)
open(MOD, 'wb').write(m2.encode('utf-8'))
log.append('0,1 mm-pads verwijderd uit %s: %d' % (MOD.split('/')[-1], k))
print('\n'.join(log))
print('haakjes:', t.count('('), t.count(')'))
