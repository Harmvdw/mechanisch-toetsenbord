"""Fusion-script: bouwt de behuizing van de numpad (bak en plaat, met draaiknop) parametrisch op in het document "Opzet".

Uitgangspunt: opbouw_helften.py is al uitgevoerd (parameters, helften en draaiknoppen staan in het document).
Alles waarvan de naam met 'Numpad' begint en wat daarna in de tijdlijn staat, wordt verwijderd en opnieuw opgebouwd.

Bron van de maten: pcb/numpad/numpad.kicad_pcb v0.4 en behuizing/behuizing.py (functie numpad).
Numpad-assenstelsel: oorsprong = midden toets (0,0) linksboven, x naar rechts, y omhoog.
KiCad -> numpad: x - 60 ; 60 - y. In het model staat de oorsprong op (np_x ; np_y): rechts naast de
rechterhelft, met de connector van de numpad op de hoogte van J_NP. numpad_afstand = 0 geeft de aangekoppelde stand.

Gebruik: via Hulpprogramma's > Scripts en add-ins, of in stappen via de Fusion-koppeling (n0 t/m n5).
Maten in mm; de API rekent in cm, vandaar de /10.
"""
import adsk.core, adsk.fusion, math

VI = adsk.core.ValueInput.createByString
FO = adsk.fusion.FeatureOperations
HO = adsk.fusion.DimensionOrientations
ED = adsk.fusion.ExtentDirections

# ---------------------------------------------------------------- gegevens
NPARAMS = [
    ('np_steek', '19.05 mm', 'Numpad: steek van de toetsen'),
    ('numpad_afstand', '40 mm', 'Ruimte tussen rechterhelft en numpad in het model (alleen weergave; 0 = aangekoppeld)'),
    ('np_x', '70.8 mm + 2 * conn_diepte + numpad_afstand + 14.8 mm', 'Afgeleid: x van numpad-toets (0,0)'),
    ('np_y', '2.56 mm', 'y van numpad-toets (0,0): connector numpad op de hoogte van J_NP'),
    ('np_bus_d', '6 mm', 'Numpad: diameter steunbus onder de print (M3)'),
    ('np_conn_b', '25 mm', 'Numpad: breedte uitsparing connector in de zijwand'),
    ('np_m3_rand', '12 mm', 'Numpad: buitenste M3 tot de zijkant'),
    ('np_m3_diepte', '8 mm', 'Numpad: diepte tapgat M3 in de wand'),
]
# print (numpad-coordinaten): rand links / rechts / boven / onder ten opzichte van toets (0,0)
PL, PR, PT, PB = 19.525, 76.675, 42.525, 90.225
ENC = (28.575, 32.525)                               # draaiknop ENC1
J = [(-14.8, -38.1), (71.95, -38.1)]                 # pennenrij J1 (links) en J2 (rechts)
J_RAND = 4.725                                       # pennenrij tot printrand
BUS = [(-14.8, 37.025), (71.95, 37.025), (-14.8, -84.225), (71.95, -84.225), (5.0, 13.1), (52.96, 13.1)]
J_HART = 86.75                                       # afstand J1 - J2


# ---------------------------------------------------------------- hulpfuncties
def P(x, y): return adsk.core.Point3D.create(x / 10, y / 10, 0)

def coll(items):
    c = adsk.core.ObjectCollection.create()
    for i in items: c.add(i)
    return c

def ctx():
    app = adsk.core.Application.get()
    d = adsk.fusion.Design.cast(app.activeProduct)
    return app, d, d.rootComponent

def val(d, name): return d.userParameters.itemByName(name).value * 10

def oorsprong(d): return val(d, 'np_x'), val(d, 'np_y')

def body(root, name):
    return [b for b in root.bRepBodies if b.name == name][0]

def area(p): return p.areaProperties().area * 100

def find_pt(s, xy):
    for p in s.sketchPoints:
        if abs(p.geometry.x * 10 - xy[0]) < 1e-3 and abs(p.geometry.y * 10 - xy[1]) < 1e-3: return p
    raise Exception('punt niet gevonden %s' % (xy,))

def proj_pt(s, src, xy):
    return s.project(find_pt(src, xy)).item(0)

def extrude(root, prof, op, start, dist, name, bodies=None, direction=ED.PositiveExtentDirection):
    ext = root.features.extrudeFeatures
    inp = ext.createInput(prof, op)
    inp.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(VI(dist)), direction)
    if start: inp.startExtent = adsk.fusion.OffsetStartDefinition.create(VI(start))
    if bodies: inp.participantBodies = bodies
    f = ext.add(inp); f.name = name
    return f

def rect(s, x0, y0, x1, y1):
    """rechthoek; geeft (onder, rechts, boven, links)"""
    L = s.sketchCurves.sketchLines
    a = L.addByTwoPoints(P(x0, y0), P(x1, y0)); b = L.addByTwoPoints(a.endSketchPoint, P(x1, y1))
    c = L.addByTwoPoints(b.endSketchPoint, P(x0, y1)); e = L.addByTwoPoints(c.endSketchPoint, a.startSketchPoint)
    g = s.geometricConstraints
    g.addHorizontal(a); g.addHorizontal(c); g.addVertical(b); g.addVertical(e)
    return a, b, c, e

def odim(s, line, other, expr, tx, ty):
    """afstandsmaat lijn - punt of lijn - lijn"""
    s.sketchDimensions.addOffsetDimension(line, other, P(tx, ty)).parameter.expression = expr

def proj_rect(s, src):
    """projecteer de vier lijnen van een rechthoek uit een andere schets als hulplijn; geeft (onder, rechts, boven, links)"""
    out = []
    for l in src.sketchCurves.sketchLines:
        if l.isConstruction: continue
        r = s.project(l).item(0); r.isConstruction = True
        out.append(r)
    mid = lambda l: ((l.startSketchPoint.geometry.x + l.endSketchPoint.geometry.x) / 2, (l.startSketchPoint.geometry.y + l.endSketchPoint.geometry.y) / 2)
    return (min(out, key=lambda l: mid(l)[1]), max(out, key=lambda l: mid(l)[0]),
            max(out, key=lambda l: mid(l)[1]), min(out, key=lambda l: mid(l)[0]))

def vert_edges(b, test):
    out = []
    for e in b.edges:
        if e.geometry.curveType != adsk.core.Curve3DTypes.Line3DCurveType: continue
        p, q = e.startVertex.geometry, e.endVertex.geometry
        if abs(p.x - q.x) < 1e-6 and abs(p.y - q.y) < 1e-6 and test(p.x * 10, p.y * 10): out.append(e)
    return out

def fillet(root, edges, expr, name):
    inp = root.features.filletFeatures.createInput()
    inp.edgeSetInputs.addConstantRadiusEdgeSet(coll(edges), VI(expr), False)
    f = root.features.filletFeatures.add(inp); f.name = name
    return f

def circles(s, pts, exprs, tx, ty):
    """concentrische cirkels op elk punt; de eerste set krijgt de maat, de rest is gelijk"""
    first = None
    for p in pts:
        if p.isReference:
            # niet rechtstreeks op een geprojecteerd punt: dan volgt de extrusie een verplaatsing niet
            q = s.sketchPoints.add(p.geometry); s.geometricConstraints.addCoincident(q, p); p = q
        cs =[s.sketchCurves.sketchCircles.addByCenterRadius(p, 0.1 + 0.1 * i) for i in range(len(exprs))]
        if first is None:
            first = cs
            for i, (c, e) in enumerate(zip(cs, exprs)):
                s.sketchDimensions.addDiameterDimension(c, P(tx + 3 * i, ty + 3 * i)).parameter.expression = e
        else:
            for c, f in zip(cs, first): s.geometricConstraints.addEqual(f, c)

def report(d, root, alles=False):
    tl = d.timeline
    print('tijdlijn', tl.count, '| niet gezond:', [tl.item(i).name for i in range(tl.count) if tl.item(i).healthState != 0])
    bodies = list(root.bRepBodies) + [b for o in root.occurrences for b in o.component.bRepBodies]
    for b in bodies:
        if not alles and 'numpad' not in b.name.lower() and 'numpad' not in b.parentComponent.name.lower(): continue
        bb = b.boundingBox
        print('%-18s %9.1f mm3  vlakken %3d  x[%.2f %.2f] y[%.2f %.2f] z[%.2f %.2f]' % (
            b.name, b.volume * 1000, b.faces.count, bb.minPoint.x * 10, bb.maxPoint.x * 10,
            bb.minPoint.y * 10, bb.maxPoint.y * 10, bb.minPoint.z * 10, bb.maxPoint.z * 10))


# ---------------------------------------------------------------- stap n0: opruimen, parameters, basisschets
def n0():
    app, d, root = ctx()
    tl = d.timeline
    idx = [i for i in range(tl.count) if tl.item(i).name.startswith('Numpad')]
    if idx:
        tl.markerPosition = idx[0]
        tl.deleteAllAfterMarker()
    up = d.userParameters
    for n, e, c in NPARAMS:
        if up.itemByName(n) is None: up.add(n, VI(e), 'mm', c)
    X, Y = oorsprong(d)
    s = root.sketches.add(root.xYConstructionPlane); s.name = 'Numpad basis'
    D = s.sketchDimensions
    n = s.sketchPoints.add(P(X, Y))
    D.addDistanceDimension(s.originPoint, n, HO.HorizontalDimensionOrientation, P(X / 2, -110)).parameter.expression = 'np_x'
    D.addDistanceDimension(s.originPoint, n, HO.VerticalDimensionOrientation, P(X + 95, Y / 2)).parameter.expression = 'np_y'
    a, b, c, e = rect(s, X - PL, Y - PB, X + PR, Y + PT)
    odim(s, e, n, '%s mm' % PL, X - 10, Y + 50); odim(s, b, e, '%s mm' % (PL + PR), X + 30, Y + 55)
    odim(s, c, n, '%s mm' % PT, X - 25, Y + 20); odim(s, a, c, '%s mm' % (PT + PB), X - 30, Y - 40)
    for lx, ly in BUS + J + [ENC]:
        p = s.sketchPoints.add(P(X + lx, Y + ly))
        D.addDistanceDimension(n, p, HO.HorizontalDimensionOrientation, P(X + lx / 2, Y + ly + 2)).parameter.expression = '%s mm' % abs(lx)
        D.addDistanceDimension(n, p, HO.VerticalDimensionOrientation, P(X + lx + 2, Y + ly / 2)).parameter.expression = '%s mm' % abs(ly)
    print('basis: profielen', s.profiles.count, 'opp mm2', round(area(s.profiles.item(0)), 1), 'oorsprong', X, Y, 'volledig bepaald', s.isFullyConstrained)


# ---------------------------------------------------------------- stap n1: contouren, bak en plaat (ruw)
def n1():
    app, d, root = ctx()
    sk = root.sketches
    X, Y = oorsprong(d)
    basis = sk.itemByName('Numpad basis')
    cd, sp, wa = val(d, 'conn_diepte'), val(d, 'spleet'), val(d, 'wand')
    zij = cd - J_RAND
    s = sk.add(root.xYConstructionPlane); s.name = 'Numpad contour buiten'
    po, pr, pb, pl = proj_rect(s, basis)
    a, b, c, e = rect(s, X - PL - zij, Y - PB - sp - wa, X + PR + zij, Y + PT + sp + wa)
    odim(s, e, pl, 'conn_diepte - %s mm' % J_RAND, X - PL - 2, Y + 60); odim(s, b, pr, 'conn_diepte - %s mm' % J_RAND, X + PR + 2, Y + 60)
    odim(s, c, pb, 'spleet + wand', X + 30, Y + PT + 4); odim(s, a, po, 'spleet + wand', X + 30, Y - PB - 4)
    prof = s.profiles.item(0)
    extrude(root, prof, FO.NewBodyFeatureOperation, None, 'z_wand', 'Numpad bak').bodies.item(0).name = 'Bak numpad'
    extrude(root, prof, FO.NewBodyFeatureOperation, 'z_wand', 'plaat_dikte', 'Numpad plaat').bodies.item(0).name = 'Plaat numpad'
    bak, plaat = body(root, 'Bak numpad'), body(root, 'Plaat numpad')
    for bd in (bak, plaat):
        fillet(root, vert_edges(bd, lambda x, y: True), 'r_buiten', 'Numpad afronding buiten ' + bd.name.split()[0].lower())
    s = sk.add(root.xYConstructionPlane); s.name = 'Numpad contour binnen'
    po, pr, pb, pl = proj_rect(s, basis)
    a, b, c, e = rect(s, X - PL - sp, Y - PB - sp, X + PR + sp, Y + PT + sp)
    odim(s, e, pl, 'spleet', X - PL - 1, Y + 20); odim(s, b, pr, 'spleet', X + PR + 1, Y + 20)
    odim(s, c, pb, 'spleet', X + 30, Y + PT + 1); odim(s, a, po, 'spleet', X + 30, Y - PB - 1)
    extrude(root, s.profiles.item(0), FO.CutFeatureOperation, 'bodem', 'z_wand - bodem', 'Numpad holte', [bak])
    xi = (X - PL - sp, X + PR + sp)
    fillet(root, vert_edges(bak, lambda x, y: min(abs(x - v) for v in xi) < 1e-3), 'r_binnen', 'Numpad afronding binnen')
    report(d, root)


# ---------------------------------------------------------------- stap n2: steunbussen en uitsparingen connector
def n2():
    app, d, root = ctx()
    sk = root.sketches
    X, Y = oorsprong(d)
    basis = sk.itemByName('Numpad basis')
    bak = body(root, 'Bak numpad')
    cd, cb = val(d, 'conn_diepte'), val(d, 'np_conn_b')
    s = sk.add(root.xYConstructionPlane); s.name = 'Numpad steunbussen'
    circles(s, [proj_pt(s, basis, (X + x, Y + y)) for x, y in BUS], ['m3_gat', 'np_bus_d'], X + BUS[0][0] + 3, Y + BUS[0][1] + 3)
    profs = [s.profiles.item(i) for i in range(s.profiles.count)]
    extrude(root, coll(profs), FO.JoinFeatureOperation, 'bodem', 'vrij_onder', 'Numpad steunbussen', [bak])
    extrude(root, coll([p for p in profs if p.profileLoops.count == 1]), FO.CutFeatureOperation, 'bodem - 2 mm', 'vrij_onder + 2 mm', 'Numpad tapgat M3 steunbus', [bak])
    s = sk.add(root.xYConstructionPlane); s.name = 'Numpad uitsparing connector'
    for (jx, jy), sg in zip(J, (-1, 1)):
        jp = proj_pt(s, basis, (X + jx, Y + jy))
        x0, x1 = sorted((X + jx + sg * (cd + 5), X + jx - sg * J_RAND))
        a, b, c, e = rect(s, x0, Y + jy - cb / 2, x1, Y + jy + cb / 2)
        buiten, binnen = (e, b) if sg < 0 else (b, e)
        odim(s, a, jp, 'np_conn_b / 2', X + jx + sg * 8, Y + jy - 15); odim(s, c, a, 'np_conn_b', X + jx + sg * 20, Y + jy)
        odim(s, buiten, jp, 'conn_diepte + 5 mm', X + jx + sg * 6, Y + jy + 16); odim(s, binnen, jp, '%s mm' % J_RAND, X + jx - sg * 2, Y + jy + 18)
    extrude(root, coll([s.profiles.item(i) for i in range(s.profiles.count)]), FO.CutFeatureOperation,
            'z_pcb_boven - 0.5 mm', 'z_wand - z_pcb_boven + 0.5 mm', 'Numpad uitsparing connector', [bak])
    report(d, root)


# ---------------------------------------------------------------- stap n3: M3 in de wand, voetjes
def n3():
    app, d, root = ctx()
    sk = root.sketches
    X, Y = oorsprong(d)
    buiten = sk.itemByName('Numpad contour buiten')
    bak, plaat = body(root, 'Bak numpad'), body(root, 'Plaat numpad')
    cd, sp, wa, mr = val(d, 'conn_diepte'), val(d, 'spleet'), val(d, 'wand'), val(d, 'np_m3_rand')
    xl, xr = X + J[0][0] - cd, X + J[1][0] + cd
    yb, yo = Y + PT + sp + wa, Y - PB - sp - wa
    br = '(%s mm + 2 * conn_diepte - 2 * np_m3_rand)' % J_HART
    s = sk.add(root.xYConstructionPlane); s.name = 'Numpad M3 gaten'
    lo, lr, lb, ll = proj_rect(s, buiten)
    pts = []
    for yy, lijn, ty in ((yb - wa / 2, lb, yb + 6), (yo + wa / 2, lo, yo - 6)):
        for i in range(4):
            x = xl + mr + i * (xr - xl - 2 * mr) / 3
            p = s.sketchPoints.add(P(x, yy)); pts.append(p)
            odim(s, lijn, p, 'wand / 2', x + 3, ty)
            if i < 3: odim(s, ll, p, 'np_m3_rand' if i == 0 else 'np_m3_rand + %d * %s / 3' % (i, br), x, ty + (2 + 3 * i) * (1 if ty > yy else -1))
            else: odim(s, lr, p, 'np_m3_rand', x, ty + (2 if ty > yy else -2))
    circles(s, pts, ['m3_gat', 'm3_vrij'], xl + mr + 4, yb + 3)
    profs = [s.profiles.item(i) for i in range(s.profiles.count)]
    extrude(root, coll([p for p in profs if p.profileLoops.count == 1]), FO.CutFeatureOperation, 'z_wand - np_m3_diepte', 'np_m3_diepte', 'Numpad tapgat M3 wand', [bak])
    extrude(root, coll(profs), FO.CutFeatureOperation, 'z_wand', 'plaat_dikte', 'Numpad M3 doorgaand plaat', [plaat])
    s = sk.add(root.xYConstructionPlane); s.name = 'Numpad voetjes'
    lo, lr, lb, ll = proj_rect(s, buiten)
    pts = []
    for x, lx in ((xl + mr, ll), (xr - mr, lr)):
        for yy, ly, ex in ((yb - 20, lb, '20 mm'), (yo + 14, lo, '14 mm')):
            p = s.sketchPoints.add(P(x, yy)); pts.append(p)
            odim(s, lx, p, 'np_m3_rand', x, yy + 8); odim(s, ly, p, ex, x + (8 if lx is ll else -8), yy)
    circles(s, pts, ['voet_d'], xl + mr + 8, yb - 12)
    extrude(root, coll([s.profiles.item(i) for i in range(s.profiles.count)]), FO.CutFeatureOperation, None, 'voet_diepte', 'Numpad verdieping voetjes', [bak])
    report(d, root)


# ---------------------------------------------------------------- stap n4: uitsparingen in de plaat
def n4():
    app, d, root = ctx()
    sk = root.sketches
    X, Y = oorsprong(d)
    basis = sk.itemByName('Numpad basis')
    plaat = body(root, 'Plaat numpad')
    u = val(d, 'uitsparing') / 2
    feats = []
    for naam, (lx, ly) in (('toets', (0.0, 0.0)), ('draaiknop', ENC)):
        s = sk.add(root.xYConstructionPlane); s.name = 'Numpad uitsparing ' + naam
        kp = proj_pt(s, basis, (X + lx, Y + ly))
        x, y = X + lx, Y + ly
        a, b, c, e = rect(s, x - u, y - u, x + u, y + u)
        odim(s, e, kp, 'uitsparing / 2', x - 10, y); odim(s, b, e, 'uitsparing', x, y + 10)
        odim(s, a, kp, 'uitsparing / 2', x, y - 10); odim(s, c, a, 'uitsparing', x + 10, y)
        feats.append(extrude(root, s.profiles.item(0), FO.CutFeatureOperation, 'z_wand', 'plaat_dikte', 'Numpad uitsparing ' + naam, [plaat]))
    rp = root.features.rectangularPatternFeatures
    inp = rp.createInput(coll([feats[0]]), root.xConstructionAxis, VI('4'), VI('np_steek'), adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
    inp.setDirectionTwo(root.yConstructionAxis, VI('5'), VI('-np_steek'))
    rp.add(inp).name = 'Numpad patroon toetsen 4 x 5'
    report(d, root)


# ---------------------------------------------------------------- stap n5: print en draaiknop als referentie, componenten
def n5():
    app, d, root = ctx()
    sk = root.sketches
    X, Y = oorsprong(d)
    basis = sk.itemByName('Numpad basis')
    extrude(root, basis.profiles.item(0), FO.NewBodyFeatureOperation, 'z_pcb_onder', 'pcb_dikte', 'Numpad print (referentie)').bodies.item(0).name = 'Print numpad'
    x, y = X + ENC[0], Y + ENC[1]
    h = val(d, 'enc_huis') / 2
    s = sk.add(root.xYConstructionPlane); s.name = 'Numpad draaiknop huis'
    kp = proj_pt(s, basis, (x, y))
    a, b, c, e = rect(s, x - h, y - h, x + h, y + h)
    odim(s, e, kp, 'enc_huis / 2', x - 10, y); odim(s, b, e, 'enc_huis', x, y + 10); odim(s, a, kp, 'enc_huis / 2', x, y - 10); odim(s, c, a, 'enc_huis', x + 10, y)
    knop = extrude(root, s.profiles.item(0), FO.NewBodyFeatureOperation, 'z_pcb_boven', 'enc_huis_h', 'Numpad draaiknop huis (referentie)').bodies.item(0); knop.name = 'Draaiknop numpad'
    s = sk.add(root.xYConstructionPlane); s.name = 'Numpad draaiknop as en knop'
    kp = proj_pt(s, basis, (x, y))
    circles(s, [kp], ['enc_as_d', 'knop_d'], x + 4, y + 4)
    profs = [s.profiles.item(i) for i in range(s.profiles.count)]
    extrude(root, coll([p for p in profs if p.profileLoops.count == 1]), FO.JoinFeatureOperation, 'z_pcb_boven', 'enc_as_h', 'Numpad draaiknop as (referentie)', [knop])
    extrude(root, coll(profs), FO.JoinFeatureOperation, 'z_plaat_boven + knop_vrij', 'knop_h', 'Numpad knop (referentie)', [knop])
    alu = app.materialLibraries.itemByName('Fusion Material Library').materials.itemByName('Aluminum 6061')
    names = {'Bak numpad': 'Bak numpad', 'Plaat numpad': 'Plaat numpad', 'Print numpad': 'Print numpad (referentie)', 'Draaiknop numpad': 'Draaiknop numpad (referentie)'}
    for bd in list(root.bRepBodies):
        nm = bd.name
        if nm in ('Bak numpad', 'Plaat numpad'): bd.material = alu
        bd.createComponent().parentComponent.name = names[nm]
    for s2 in root.sketches: s2.isVisible = False
    report(d, root)
    for o in root.occurrences:
        if 'numpad' not in o.component.name.lower(): continue
        for bd in o.component.bRepBodies:
            print('%-30s %6.1f g  %s' % (o.component.name, bd.physicalProperties.mass * 1000, bd.material.name))


def run(_context: str):
    n0(); n1(); n2(); n3(); n4(); n5()
