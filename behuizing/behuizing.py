#!/usr/bin/env python3
"""Parametrische behuizing voor één toetsenbordhelft (rechts) en het numpad.

Prototype v0.1 (12 nov 2026), gemaakt in CadQuery als tussenstap tot het Fusion-ontwerp.
Uitvoer: STEP (voor Fusion) en STL (3D-print) in behuizing/export/.

Assenstelsel (gelijk aan de Fusion master-schets en data/*.csv):
  oorsprong = midden bovenste toets van kolom 3, x naar rechts (pinkkant), y omhoog, z omhoog.
  z = 0 is de onderkant van de bak.

Opbouw per deel:
  bak   : bodem + wand, open bovenkant. Plaat rust op de wand en wordt met M3 vastgezet.
  plaat : 1,5 mm, 14 x 14 mm uitsparingen, volle buitenmaat (sandwich-look).
  kap   : alleen helft; dekt Pro Micro, OLED en TRRS af, met venster voor de OLED.
"""
import csv, math, os
import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(HERE, 'export')
os.makedirs(OUT, exist_ok=True)

# ---------------- parameters (mm) ----------------
P = dict(
    uitsparing=14.0,      # plaatuitsparing per switch (E8)
    duimhoek=30.0,        # gedraaide duimtoets
    plaat_dikte=1.5,      # W6
    pcb_dikte=1.6,
    pcb_plaat=5.0,        # MX: bovenkant print tot bovenkant plaat
    vrij_onder=3.5,       # ruimte onder de print (hotswap-voetjes 1,8 mm)
    bodem=4.0,            # bodemdikte (stevig, W11)
    spleet=1.0,           # print tot binnenwand
    wand=7.0,             # wanddikte (M3 in het midden van de wand)
    conn_diepte=9.0,      # pennenrij connector tot contactvlak. SCHATTING: opmeten na levering!
    r_buiten=3.0,         # afronding buitenhoeken (bovenaanzicht)
    r_binnen=1.5,         # minimale binnenradius (E22: >= 1 mm)
    kap_hoogte=10.0,      # kap boven plaat (OLED steekt ca. 11,5 mm boven de print uit)
    kap_wand=3.0,
    kap_dak=2.0,
    m3_gat=2.5,           # tapgat M3 in de wand
    m3_vrij=3.4,          # doorgaand gat M3 in plaat/kap
    m2_gat=1.6,           # tapgat M2 in steunbus
    bus_d=5.0,            # steunbus onder de print
    voet_d=10.0, voet_diepte=1.0,   # verdiepingen voor rubbervoetjes
)
Z_PCB_ONDER = P['bodem'] + P['vrij_onder']
Z_PCB_BOVEN = Z_PCB_ONDER + P['pcb_dikte']
Z_PLAAT_BOVEN = Z_PCB_BOVEN + P['pcb_plaat']
Z_WAND = Z_PLAAT_BOVEN - P['plaat_dikte']          # bovenkant wand = onderkant plaat

# ---------------- helpers ----------------
def poly(pts):
    return cq.Workplane('XY').polyline(pts).close()

def offset_face(pts, d, kind='arc'):
    w = cq.Workplane('XY').polyline(pts).close().val()
    return cq.Workplane('XY').add(w.offset2D(d, kind)[0])

def rounded(wp_wire, r_out, r_in):
    """rond bolle hoeken af met r_out en holle hoeken met r_in"""
    w = wp_wire.val()
    w = w.offset2D(-r_out, 'arc')[0].offset2D(r_out, 'arc')[0]
    w = w.offset2D(r_in, 'arc')[0].offset2D(-r_in, 'arc')[0]
    return cq.Workplane('XY').add(w)

def prism(wire_wp, z0, h):
    return wire_wp.toPending().extrude(h).translate((0, 0, z0))

def box(x0, y0, x1, y1, z0, z1):
    return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))

def cyl(x, y, d, z0, z1):
    return cq.Workplane('XY').circle(d / 2).extrude(z1 - z0).translate((x, y, z0))

def cutouts(plate, keys, z0):
    u = P['uitsparing']
    for x, y, a in keys:
        c = cq.Workplane('XY').rect(u, u).extrude(P['plaat_dikte'] + 2).translate((0, 0, -1))
        if a: c = c.rotate((0, 0, 0), (0, 0, 1), a)
        plate = plate.cut(c.translate((x, y, z0)))
    return plate

def spread(wire, n, avoid, min_d=14.0):
    """n punten gelijk verdeeld over een draad; draai de verdeling tot ze uit de buurt van 'avoid' blijven"""
    best = None
    for k in range(40):
        ph = k / 40 / n
        pts = [wire.positionAt((ph + i / n) % 1.0) for i in range(n)]
        pts = [(p.x, p.y) for p in pts]
        dmin = min([math.hypot(px - ax, py - ay) for px, py in pts for ax, ay in avoid] or [99])
        if best is None or dmin > best[0]: best = (dmin, pts)
    return best[1], best[0]

def save(shape, name):
    cq.exporters.export(shape, os.path.join(OUT, name + '.step'))
    cq.exporters.export(shape, os.path.join(OUT, name + '.stl'), tolerance=0.05, angularTolerance=0.2)
    v = shape.val().Volume()
    print('%-22s volume %7.1f cm3  massa alu %5.0f g' % (name, v / 1000, v / 1000 * 2.70))
    return v

# =============================================================
# HELFT (rechts). Bronnen: data/*.csv en KiCad Lily58_Pro.kicad_pcb (12 nov)
# =============================================================
def kicad(xk, yk):  # KiCad-coördinaten (y omlaag) -> master
    return xk - 158.6, 46.21 - yk

def helft():
    rand = [(float(r['x_mm']), float(r['y_mm'])) for r in csv.DictReader(open(os.path.join(REPO, 'data/lily58-pro-printrand.csv')))]
    # route 2: pinkkant 6 mm breder (alle punten met KiCad x >= 223 mm)
    rand = [(x + 6.0 if x >= 223.0 - 158.6 else x, y) for x, y in rand]
    sw = [(float(r['x_mm']) - 158.6, float(r['y_mm']) + 46.21) for r in csv.DictReader(open(os.path.join(REPO, 'data/lily58-pro-switchposities.csv')))]
    keys = [(x, y, P['duimhoek'] if abs(x - (105.0 - 158.6)) < 0.01 and abs(y - (46.21 - 127.0)) < 0.01 else 0.0) for x, y in sw]

    j_np = kicad(229.4, 81.75)          # magnetische connector (pennenrij)
    usb = kicad(101.0, 37.0)            # Pro Micro USB-C (bovenrand)
    trrs = kicad(87.9, 37.0)            # TRRS-jack (bovenrand)
    reset = kicad(85.0, 67.7)           # resetknop (linkerrand)
    oled_hdr = kicad(100.5, 74.6)       # midden OLED-header
    m2 = [kicad(*p) for p in [(129.6, 59.6), (205.8, 61.8), (129.6, 97.6), (205.8, 100.0), (105.0, 114.8), (86.0, 85.0), (108.0, 85.0)]]

    pcb_xmax = max(x for x, y in rand)
    pcb_xmin = min(x for x, y in rand)
    pcb_ymax = max(y for x, y in rand)

    # buitenomtrek: print + spleet + wand; pinkkant zo dat het contactvlak van de connector gelijk ligt met de wand
    out_wire = offset_face(rand, P['spleet'] + P['wand'])
    x_rechts = j_np[0] + P['conn_diepte']
    outer_face = out_wire.toPending().extrude(1).intersect(box(-200, -200, x_rechts, 200, -1, 2)).faces('<Z').wires()
    outer = rounded(outer_face, P['r_buiten'], P['r_binnen'])
    inner = rounded(offset_face(rand, P['spleet']), 0.01, P['r_binnen'])
    wand_rechts = x_rechts - (pcb_xmax + P['spleet'])

    # ---- bak ----
    bak = prism(outer, 0, Z_WAND)
    bak = bak.cut(prism(inner, P['bodem'], Z_WAND))
    for x, y in m2:
        bak = bak.union(cyl(x, y, P['bus_d'], P['bodem'] - 0.1, Z_PCB_ONDER)).cut(cyl(x, y, P['m2_gat'], P['bodem'] - 2.0, Z_PCB_ONDER + 0.1))

    # uitsparingen in de wand
    zu = Z_PCB_BOVEN
    cut_usb = box(usb[0] - 6.0, pcb_ymax - 1, usb[0] + 6.0, pcb_ymax + 20, zu + 0.5, zu + 12.0)   # ruim; Pro Micro-hoogte nog onbekend
    cut_trrs = box(trrs[0] - 4.0, pcb_ymax - 1, trrs[0] + 4.0, pcb_ymax + 20, zu - 1.0, zu + 7.0)
    cut_reset = cyl(0, 0, 3.5, 0, 30).rotate((0, 0, 0), (0, 1, 0), 90).translate((pcb_xmin - 15, reset[1], zu + 1.5))
    cut_conn = box(pcb_xmax, j_np[1] - 12.5, x_rechts + 5, j_np[1] + 12.5, zu - 0.5, zu + 7.5)
    for c in (cut_usb, cut_trrs, cut_reset, cut_conn): bak = bak.cut(c)

    # ---- kap-gebied (Pro Micro, OLED, TRRS) ----
    # Dak met wanden alleen aan de buitenkant (links en boven). Rechts zit de keycap van kolom 1 op 1,4 mm
    # van de Pro Micro, dus daar geen wand: het dak eindigt 0,5 mm voor de keycap (zoals de Lily58-OLED-kap).
    # Onderkant: 1 mm voor de keycap van de bovenste duimtoets. Steun binnenin: 2 afstandsbussen M2 op TH1/TH2.
    kx1 = (120.5 - 158.6) - 18.0 / 2 - 0.5           # keycap kolom 1 (18 mm) min 0,5 mm
    ky0 = (46.21 - 97.5) + 18.0 / 2 + 1.0             # keycap duimtoets SW25 plus 1 mm
    kap_box = box(-200, ky0, kx1, 200, -1, 99)
    pm_x1 = kicad(110.1, 0)[0]                         # rechterrand Pro Micro (18 mm breed rond x=101,1)
    th12 = [kicad(86.0, 85.0), kicad(108.0, 85.0)]
    # schroeven M3 in de wand (8 stuks), midden van de wand
    mid = offset_face(rand, P['spleet'] + P['wand'] / 2).val()
    avoid = [usb, trrs, (reset[0] - 8, reset[1]), (x_rechts - wand_rechts / 2, j_np[1])]
    m3, dmin = spread(mid, 8, avoid)
    m3 = [(min(x, x_rechts - wand_rechts / 2), y) for x, y in m3]
    for x, y in m3:
        bak = bak.cut(cyl(x, y, P['m3_gat'], Z_WAND - 8.0, Z_WAND + 0.1))

    # rubbervoetjes
    bb = outer.val().BoundingBox()
    feet = [(bb.xmin + 14, bb.ymax - 14), (bb.xmax - 14, bb.ymax - 14), (bb.xmax - 14, bb.ymin + 30), (-40, bb.ymin + 18)]
    for x, y in feet:
        bak = bak.cut(cyl(x, y, P['voet_d'], -0.1, P['voet_diepte']))

    # ---- plaat ----
    plaat = prism(outer, Z_WAND, P['plaat_dikte'])
    plaat = cutouts(plaat, keys, Z_WAND)
    kap_open = box(pcb_xmin, kicad(0, 77.2)[1], pm_x1 + 0.5, pcb_ymax, Z_WAND - 1, Z_WAND + 5)   # Pro Micro + OLED steken door het plaatniveau
    plaat = plaat.cut(kap_open)
    for x, y in th12:
        plaat = plaat.cut(cyl(x, y, 4.5, Z_WAND - 1, Z_WAND + 5))                  # doorvoer afstandsbus
    for x, y in m3:
        plaat = plaat.cut(cyl(x, y, P['m3_vrij'], Z_WAND - 1, Z_WAND + 5))
    for c in (cut_usb, cut_trrs, cut_conn):
        plaat = plaat.cut(c)

    # ---- kap ----
    kz0, kz1 = Z_PLAAT_BOVEN, Z_PLAAT_BOVEN + P['kap_hoogte']
    kap = prism(outer, kz0, P['kap_hoogte']).intersect(kap_box)
    holte = prism(inner, kz0 - 1, P['kap_hoogte'] - P['kap_dak'] + 1).intersect(box(-200, ky0 - 1, kx1 + 1, 200, -1, 99))
    kap = kap.cut(holte)
    # OLED-venster: actief vlak ca. 22,4 x 5,6 mm; module staand boven de Pro Micro, header onderaan
    ox, oy = oled_hdr[0], oled_hdr[1] + 1.5 + 38.0 / 2
    kap = kap.cut(box(ox - 4.5, oy - 13.0, ox + 4.5, oy + 13.0, kz1 - P['kap_dak'] - 1, kz1 + 1))
    kap = kap.cut(cut_usb).cut(cut_trrs)
    for x, y in th12:                                   # M2 door het dak naar de afstandsbus, verzonken kop
        kap = kap.cut(cyl(x, y, 2.4, kz0, kz1 + 1)).cut(cyl(x, y, 4.4, kz1 - 1.2, kz1 + 1))
    in_kap = [(x, y) for x, y in m3 if x < kx1 and y > ky0]
    for x, y in in_kap:
        kap = kap.cut(cyl(x, y, P['m3_vrij'], kz0 - 1, kz1 + 1)).cut(cyl(x, y, 6.0, kz1 - 3.2, kz1 + 1))
    try:
        kap = kap.faces('>Z').edges().fillet(0.8)
    except Exception as e:
        print('kap: afronding overgeslagen', e)
    afstandsbus = Z_PLAAT_BOVEN + P['kap_hoogte'] - P['kap_dak'] - Z_PCB_BOVEN

    info = dict(m3=m3, m3_dmin=dmin, wand_rechts=wand_rechts, x_rechts=x_rechts, in_kap=in_kap, ky0=ky0, kx1=kx1,
                speling_pm=kx1 - pm_x1, afstandsbus=afstandsbus)
    return bak, plaat, kap, keys, info

# =============================================================
# NUMPAD. Bron: numpad/numpad.kicad_pcb (12 nov). KiCad: toets (0,0) op (60; 60), steek 19,05.
# Master voor het numpad: oorsprong midden toets kolom 0 / rij 0, y omhoog.
# =============================================================
def numpad():
    S = 19.05
    def kc(xk, yk): return xk - 60.0, 60.0 - yk
    L, T, R, B = 40.475, 17.475, 136.675, 150.225      # v0.4: bovenstrook 19 mm langer voor de draaiknop
    pcb = [kc(L, T), kc(R, T), kc(R, B), kc(L, B)]
    keys = [(c * S, -r * S, 0.0) for r in range(5) for c in range(4)]
    enc = kc(88.575, 27.475)                         # draaiknop EC11 (ENC1); plaatuitsparing 14 x 14 zoals een toets
    keys.append((enc[0], enc[1], 0.0))
    j1 = kc(45.2, 98.1); j2 = kc(131.95, 98.1)
    h = [kc(*p) for p in [(45.2, 22.975), (131.95, 22.975), (45.2, 144.225), (131.95, 144.225), (65.0, 46.9), (112.96, 46.9)]]
    xl, xr = j1[0] - P['conn_diepte'], j2[0] + P['conn_diepte']
    pymax, pymin = kc(0, T)[1], kc(0, B)[1]
    yb, yo = pymax + P['spleet'] + P['wand'], pymin - P['spleet'] - P['wand']
    outer = rounded(poly([(xl, yo), (xr, yo), (xr, yb), (xl, yb)]), P['r_buiten'], P['r_binnen'])
    inner = rounded(offset_face(pcb, P['spleet'], 'intersection'), 0.01, P['r_binnen'])
    bak = prism(outer, 0, Z_WAND).cut(prism(inner, P['bodem'], Z_WAND))
    for x, y in h:
        bak = bak.union(cyl(x, y, 6.0, P['bodem'] - 0.1, Z_PCB_ONDER)).cut(cyl(x, y, P['m3_gat'], P['bodem'] - 2.0, Z_PCB_ONDER + 0.1))
    zu = Z_PCB_BOVEN
    for jx, jy, s in ((j1[0], j1[1], -1), (j2[0], j2[1], 1)):
        x0, x1 = (xl - 5, kc(L, 0)[0]) if s < 0 else (kc(R, 0)[0], xr + 5)
        bak = bak.cut(box(x0, jy - 12.5, x1, jy + 12.5, zu - 0.5, zu + 7.5))
    # 8 x M3 alleen in voor- en achterwand (zijwanden zijn dun door de connector)
    yw_b, yw_o = pymax + P['spleet'] + P['wand'] / 2, pymin - P['spleet'] - P['wand'] / 2
    xs = [xl + 12, xl + 12 + (xr - xl - 24) / 3, xl + 12 + 2 * (xr - xl - 24) / 3, xr - 12]
    m3 = [(x, yw_b) for x in xs] + [(x, yw_o) for x in xs]
    for x, y in m3:
        bak = bak.cut(cyl(x, y, P['m3_gat'], Z_WAND - 8.0, Z_WAND + 0.1))
    for x, y in [(xl + 12, yb - 20), (xr - 12, yb - 20), (xl + 12, yo + 14), (xr - 12, yo + 14)]:
        bak = bak.cut(cyl(x, y, P['voet_d'], -0.1, P['voet_diepte']))
    plaat = prism(outer, Z_WAND, P['plaat_dikte'])
    plaat = cutouts(plaat, keys, Z_WAND)
    for x, y in m3:
        plaat = plaat.cut(cyl(x, y, P['m3_vrij'], Z_WAND - 1, Z_WAND + 5))
    info = dict(m3=m3, wand_zij=kc(L, 0)[0] - P['spleet'] - xl, maat=(xr - xl, yb - yo), enc=enc)
    return bak, plaat, keys, info

if __name__ == '__main__':
    print('z: bodem 0-%.1f, print %.1f-%.1f, wand tot %.1f, plaat tot %.1f' % (P['bodem'], Z_PCB_ONDER, Z_PCB_BOVEN, Z_WAND, Z_PLAAT_BOVEN))
    bak, plaat, kap, keys, info = helft()
    tot = save(bak, 'helft_rechts_bak') + save(plaat, 'helft_rechts_plaat') + save(kap, 'helft_rechts_kap')
    print('helft totaal alu %.0f g; wand pinkkant %.2f mm; M3 min. afstand tot uitsparing %.1f mm; M3 in kap: %d'
          % (tot / 1000 * 2.7, info['wand_rechts'], info['m3_dmin'], len(info['in_kap'])))
    print('kap: rand %.2f, onderrand %.2f; dak voorbij Pro Micro %.2f mm; afstandsbus M2 print-dak %.1f mm'
          % (info['kx1'], info['ky0'], info['speling_pm'], info['afstandsbus']))
    bb = bak.val().BoundingBox(); print('helft buitenmaat %.1f x %.1f x %.1f mm (zonder kap)' % (bb.xlen, bb.ylen, Z_PLAAT_BOVEN))
    nb, npl, nkeys, ninfo = numpad()
    tot = save(nb, 'numpad_bak') + save(npl, 'numpad_plaat')
    print('numpad totaal alu %.0f g; zijwand %.2f mm; buitenmaat %.1f x %.1f mm' % (tot / 1000 * 2.7, ninfo['wand_zij'], *ninfo['maat']))
