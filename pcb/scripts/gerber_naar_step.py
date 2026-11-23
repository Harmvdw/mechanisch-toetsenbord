#!/usr/bin/env python3
"""Maakt een STEP-model van een print, alleen uit de Gerber- en boorbestanden.

Het model laat zien wat de fabrikant (PCBWay) uit de bestanden haalt:
  - print   : printrand (Edge_Cuts) x dikte, met alle gaten en sleuven (PTH + NPTH)
  - koper   : optioneel (--koper), bovenste en onderste koperlaag als dunne lagen (0,035 mm), gaten eruit
  - opdruk  : optioneel (--opdruk), bovenste en onderste silkscreen (0,02 mm)
Koper en opdruk maken het bestand erg groot (Lily58 met koper: ca. 140 MB); voor passen in de
behuizing is alleen de print met gaten nodig.

Gebruik:
  python3 gerber_naar_step.py <gerbers.zip | map> <uitvoer.step> [opties]

Opties:
  --dx, --dy   verschuiving in mm (Gerber-coördinaten -> eigen assenstelsel)
  --z0         hoogte onderkant print in mm (standaard 0)
  --dikte      printdikte in mm (standaard 1,6)
  --koper      koperlagen meenemen (groot bestand)
  --opdruk     silkscreen meenemen

Lily58-helft in het master-assenstelsel van de behuizing (behuizing/behuizing.py):
  --dx -158.6 --dy 46.21 --z0 7.5
(Gerber-y = -KiCad-y; master = (x - 158,6; 46,21 - KiCad-y); print ligt op z 7,5-9,1.)

Benodigd: pip install gerbonara shapely cadquery
"""
import argparse, math, os, sys, tempfile, warnings, zipfile
warnings.filterwarnings('ignore')

import shapely
from shapely.geometry import Point, LineString, Polygon, box as sbox
from shapely import affinity
import cadquery as cq
from gerbonara import LayerStack, graphic_primitives as gp
from gerbonara.utils import MM

KOPER = 0.035
OPDRUK = 0.02
QS = 4            # boogsegmenten per kwartcirkel bij het omzetten naar vlakken


def laad(pad):
    if os.path.isdir(pad):
        return LayerStack.open_dir(pad)
    tmp = tempfile.mkdtemp(prefix='gerbers_')
    with zipfile.ZipFile(pad) as z:
        z.extractall(tmp)
    return LayerStack.open_dir(tmp)


# ---------- Gerber-primitieven -> shapely ----------
def prim_naar_geom(p):
    if isinstance(p, gp.Circle):
        return Point(p.x, p.y).buffer(p.r, quad_segs=QS)
    if isinstance(p, gp.Line):
        if p.width <= 0:
            return None
        if (p.x1, p.y1) == (p.x2, p.y2):
            return Point(p.x1, p.y1).buffer(p.width / 2, quad_segs=QS)
        return LineString([(p.x1, p.y1), (p.x2, p.y2)]).buffer(p.width / 2, quad_segs=QS)
    if isinstance(p, gp.Arc):
        pts = gp.approximate_arc(p.cx, p.cy, p.x1, p.y1, p.x2, p.y2, p.clockwise, max_error=0.002)
        pts = [(x, y) for x, y in pts]
        return LineString(pts).buffer(p.width / 2, quad_segs=QS) if len(pts) > 1 else None
    if isinstance(p, gp.Rectangle):
        r = sbox(p.x - p.w / 2, p.y - p.h / 2, p.x + p.w / 2, p.y + p.h / 2)
        return affinity.rotate(r, p.rotation, origin=(p.x, p.y), use_radians=True) if p.rotation else r
    if isinstance(p, gp.ArcPoly):
        pts = [tuple(q) for q in p.approximate_arcs(max_error=0.002)] if p.arc_centers and any(c for c in p.arc_centers) else [tuple(q) for q in p.outline]
        if len(pts) < 3:
            return None
        return shapely.make_valid(Polygon(pts))
    raise TypeError(type(p).__name__)


def laag_naar_geom(layer):
    """Belicht een Gerber-laag in volgorde (donker = erbij, helder = eraf)."""
    geom = shapely.Polygon()
    blok = []
    huidig = True
    def flush():
        nonlocal geom, blok
        if blok:
            u = shapely.union_all(blok)
            geom = geom.union(u) if huidig else geom.difference(u)
            blok = []
    for obj in layer.objects:
        for p in obj.to_primitives(unit=MM):
            g = prim_naar_geom(p)
            if g is None or g.is_empty:
                continue
            if p.polarity_dark != huidig:
                flush()
                huidig = p.polarity_dark
            blok.append(g)
    flush()
    return shapely.make_valid(geom)


# ---------- printrand ----------
def printrand(stack, tol=0.01):
    segs = []
    for obj in stack.outline.objects:
        for p in obj.to_primitives(unit=MM):
            if isinstance(p, gp.Line):
                segs.append([(p.x1, p.y1), (p.x2, p.y2)])
            elif isinstance(p, gp.Arc):
                segs.append([tuple(q) for q in gp.approximate_arc(p.cx, p.cy, p.x1, p.y1, p.x2, p.y2, p.clockwise, max_error=0.002)])
    # segmenten aan elkaar rijgen; kleine gaatjes (afronding) dichten
    ketting = segs.pop(0)
    gaten = []
    while segs:
        eind = ketting[-1]
        best = min(range(len(segs)), key=lambda i: min(math.dist(eind, segs[i][0]), math.dist(eind, segs[i][-1])))
        s = segs.pop(best)
        if math.dist(eind, s[-1]) < math.dist(eind, s[0]):
            s = s[::-1]
        afst = math.dist(eind, s[0])
        if afst > tol:
            raise SystemExit(f'Printrand niet gesloten: gat van {afst:.4f} mm bij {eind}')
        if afst > 1e-6:
            gaten.append(afst)
        ketting += s[1:]
    sluit = math.dist(ketting[0], ketting[-1])
    if sluit > tol:
        raise SystemExit(f'Printrand niet gesloten: begin en eind {sluit:.4f} mm uit elkaar')
    if sluit > 1e-6:
        gaten.append(sluit)
    ketting = ketting[:-1]
    # dubbele punten weg
    pts = [ketting[0]]
    for q in ketting[1:]:
        if math.dist(q, pts[-1]) > 1e-4:
            pts.append(q)
    poly = Polygon(pts)
    if not poly.is_valid:
        poly = shapely.make_valid(poly)
    return poly, gaten


# ---------- boorgaten ----------
def gaten(stack):
    rond, sleuf = [], []
    for laag in stack.drill_layers:
        plated = 'NPTH' not in laag.original_path.name.upper()
        for o in laag.objects:
            d = o.tool.diameter
            if type(o).__name__ == 'Flash':
                rond.append((o.x, o.y, d, plated))
            elif type(o).__name__ == 'Line':
                sleuf.append((o.x1, o.y1, o.x2, o.y2, d, plated))
            else:
                raise TypeError(type(o).__name__)
    return rond, sleuf


def gaten_geom(rond, sleuf):
    g = [Point(x, y).buffer(d / 2, quad_segs=QS) for x, y, d, _ in rond]
    g += [LineString([(a, b), (c, e)]).buffer(d / 2, quad_segs=QS) for a, b, c, e, d, _ in sleuf]
    return shapely.union_all(g)


# ---------- shapely -> CadQuery ----------
def T(x, y, a):
    return (x + a.dx, y + a.dy)


def wire(coords, a, z):
    pts = [cq.Vector(*T(x, y, a), z) for x, y in list(coords)[:-1]]
    return cq.Wire.makePolygon(pts, close=True)


def vlak_naar_solid(poly, a, z, h):
    face = cq.Face.makeFromWires(wire(poly.exterior.coords, a, z), [wire(i.coords, a, z) for i in poly.interiors])
    return cq.Solid.extrudeLinear(face, cq.Vector(0, 0, h))


def geom_naar_solids(geom, a, z, h, vereenvoudig=0.002):
    geom = geom.simplify(vereenvoudig, preserve_topology=True) if vereenvoudig else geom
    polys = [geom] if isinstance(geom, Polygon) else [g for g in getattr(geom, 'geoms', []) if isinstance(g, Polygon)]
    solids = []
    for p in polys:
        if p.is_empty or p.area < 1e-6:
            continue
        try:
            solids.append(vlak_naar_solid(p, a, z, h))
        except Exception as e:  # zeldzaam: ongeldig vlak, dan overslaan en melden
            print('  overgeslagen vlak:', round(p.area, 4), 'mm2,', e)
    return cq.Compound.makeCompound(solids), len(polys)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('gerbers'); ap.add_argument('uitvoer')
    ap.add_argument('--dx', type=float, default=0.0); ap.add_argument('--dy', type=float, default=0.0)
    ap.add_argument('--z0', type=float, default=0.0); ap.add_argument('--dikte', type=float, default=1.6)
    ap.add_argument('--opdruk', action='store_true'); ap.add_argument('--koper', action='store_true')
    a = ap.parse_args()

    st = laad(a.gerbers)
    rand, dicht = printrand(st)
    minx, miny, maxx, maxy = rand.bounds
    print(f'printrand: {len(rand.exterior.coords) - 1} punten, {maxx - minx:.2f} x {maxy - miny:.2f} mm, '
          f'oppervlak {rand.area:.1f} mm2; {len(dicht)} kleine gaatjes gedicht (max {max(dicht, default=0) * 1000:.1f} um)')

    rond, sleuf = gaten(st)
    print(f'gaten: {sum(p for *_, p in rond)} PTH + {sum(not p for *_, p in rond)} NPTH rond, '
          f'{sum(p for *_, p in sleuf)} PTH + {sum(not p for *_, p in sleuf)} NPTH sleuven')
    buiten = [h for h in rond if not rand.contains(Point(h[0], h[1]))]
    if buiten:
        print('LET OP: gaten buiten de printrand:', buiten)

    z0, z1 = a.z0, a.z0 + a.dikte
    # Gaten in 2D wegsnijden en dan pas extruderen. Dubbele gaten (zelfde plek en maat, komt voor bij
    # deze omkeerbare print) eerst weghalen: die laten een 3D-booleaanse bewerking stil mislukken.
    uniek = sorted({(round(x, 4), round(y, 4), round(d, 4)) for x, y, d, _ in rond})
    print(f'unieke ronde gaten: {len(uniek)} (dubbel: {len(rond) - len(uniek)})')
    vlak = cq.Face.makeFromWires(wire(Polygon(rand.exterior.coords).exterior.coords, a, z0))
    knip = [cq.Face.makeFromWires(cq.Wire.makeCircle(d / 2, cq.Vector(*T(x, y, a), z0), cq.Vector(0, 0, 1))) for x, y, d in uniek]
    for x1, y1, x2, y2, d, _ in sleuf:
        L = math.dist((x1, y1), (x2, y2)); hoek = math.degrees(math.atan2(y2 - y1, x2 - x1))
        cx, cy = T((x1 + x2) / 2, (y1 + y2) / 2, a)
        knip.append(cq.Face.makeFromWires(cq.Workplane('XY', origin=(cx, cy, z0)).slot2D(L + d, d, hoek).wires().val()))
    vlak = vlak.cut(*knip).clean()
    plaat = cq.Solid.extrudeLinear(vlak.Faces()[0], cq.Vector(0, 0, a.dikte)) if len(vlak.Faces()) == 1 else \
        cq.Compound.makeCompound([cq.Solid.extrudeLinear(f, cq.Vector(0, 0, a.dikte)) for f in vlak.Faces()])
    verwacht = (rand.area - Polygon(rand.exterior.coords).difference(
        shapely.union_all([Point(x, y).buffer(d / 2, quad_segs=64) for x, y, d in uniek] +
                          [LineString([(p, q), (r, s)]).buffer(d / 2, quad_segs=64) for p, q, r, s, d, _ in sleuf])).area) * a.dikte
    weg = rand.area * a.dikte - plaat.Volume()
    print(f'print geldig: {plaat.isValid()} | vlakken: {len(plaat.Faces())} | weggesneden {weg:.1f} mm3, verwacht {verwacht:.1f} mm3')
    if abs(weg - verwacht) > 0.005 * verwacht:
        raise SystemExit('FOUT: niet alle gaten zijn weggesneden')

    ass = cq.Assembly(name='print_uit_gerbers')
    ass.add(plaat, name='print', color=cq.Color(0.10, 0.40, 0.18))
    gat_geom = gaten_geom(rond, sleuf)
    if a.koper:
        for kant, z, kleur in (('top', z1, (0.85, 0.65, 0.25)), ('bottom', z0 - KOPER, (0.85, 0.65, 0.25))):
            g = laag_naar_geom(st.graphic_layers[(kant, 'copper')]).intersection(rand).difference(gat_geom)
            comp, n = geom_naar_solids(g, a, z, KOPER, vereenvoudig=0.02)
            print(f'koper {kant}: {n} losse vlakken, {g.area:.0f} mm2 ({100 * g.area / rand.area:.0f}% van de print)')
            ass.add(comp, name=f'koper_{"boven" if kant == "top" else "onder"}', color=cq.Color(*kleur))
    if a.opdruk:
        for kant in ('top', 'bottom'):
            if (kant, 'silk') not in st.graphic_layers:
                continue
            z = z1 + KOPER if kant == 'top' else z0 - KOPER - OPDRUK
            g = laag_naar_geom(st.graphic_layers[(kant, 'silk')]).intersection(rand).difference(gat_geom)
            comp, n = geom_naar_solids(g, a, z, OPDRUK, vereenvoudig=0.005)
            print(f'opdruk {kant}: {n} losse vlakken')
            ass.add(comp, name=f'opdruk_{"boven" if kant == "top" else "onder"}', color=cq.Color(0.95, 0.95, 0.95))

    ass.save(a.uitvoer, exportType='STEP')
    bb = plaat.BoundingBox()
    print(f'print: x {bb.xmin:.2f}..{bb.xmax:.2f}, y {bb.ymin:.2f}..{bb.ymax:.2f}, z {bb.zmin:.2f}..{bb.zmax:.2f}; '
          f'volume {plaat.Volume():.0f} mm3 (zonder gaten {rand.area * a.dikte:.0f})')
    print('geschreven:', a.uitvoer, f'({os.path.getsize(a.uitvoer) / 1e6:.1f} MB)')


if __name__ == '__main__':
    main()
