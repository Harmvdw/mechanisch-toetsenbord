"""Fusion-script: bouwt de behuizing van beide helften parametrisch op (rechts gemodelleerd, links gespiegeld) in het document "Opzet".

Uitgangspunt: het document bevat de schetsen 'Master toetsposities', 'Plaat uitsparingen' en
'PCB omtrek (Lily58 Pro)' (zie docs/10-fusion-opzet.md). Alles wat daarna in de tijdlijn staat
wordt verwijderd en opnieuw opgebouwd.

Gebruik: in Fusion via Hulpprogramma's > Scripts en add-ins, of in stappen via de Fusion-koppeling
(stap0 t/m stap5). Maten in mm; de API rekent in cm, vandaar de /10.

Assenstelsel: oorsprong = midden bovenste toets kolom 3, x naar de pinkkant, y omhoog,
z = 0 is de onderkant van de bak.
"""
import adsk.core, adsk.fusion, json, math

VI = adsk.core.ValueInput.createByString
FO = adsk.fusion.FeatureOperations
HO = adsk.fusion.DimensionOrientations
ED = adsk.fusion.ExtentDirections

# ---------------------------------------------------------------- gegevens
PARAMS = [
    ('plaat_dikte', '1.5 mm', 'Dikte plaat (W6)'),
    ('pcb_dikte', '1.6 mm', 'Dikte print'),
    ('pcb_plaat', '5 mm', 'MX: bovenkant print tot bovenkant plaat'),
    ('vrij_onder', '3.5 mm', 'Ruimte onder de print (hotswap-voetjes)'),
    ('bodem', '4 mm', 'Bodemdikte bak'),
    ('spleet', '1 mm', 'Print tot binnenwand'),
    ('wand', '7 mm', 'Wanddikte'),
    ('conn_diepte', '9 mm', 'Pennenrij connector tot contactvlak. SCHATTING: opmeten na levering'),
    ('jnp_rand', '2.06 mm', 'Pennenrij J_NP tot printrand'),
    ('r_buiten', '3 mm', 'Afronding buitenhoeken'),
    ('r_binnen', '1.5 mm', 'Minimale binnenradius (E22)'),
    ('kap_hoogte', '10 mm', 'Kap boven plaat'),
    ('kap_dak', '2 mm', 'Dikte dak kap'),
    ('keycap', '18 mm', 'Breedte keycap'),
    ('m3_gat', '2.5 mm', 'Tapgat M3'),
    ('m3_vrij', '3.4 mm', 'Doorgaand gat M3'),
    ('m2_gat', '1.6 mm', 'Tapgat M2 in steunbus'),
    ('bus_d', '5 mm', 'Diameter steunbus onder print'),
    ('voet_d', '10 mm', 'Diameter verdieping rubbervoetje'),
    ('voet_diepte', '1 mm', 'Diepte verdieping rubbervoetje'),
    ('z_pcb_onder', 'bodem + vrij_onder', 'Afgeleid: onderkant print'),
    ('z_pcb_boven', 'z_pcb_onder + pcb_dikte', 'Afgeleid: bovenkant print'),
    ('z_plaat_boven', 'z_pcb_boven + pcb_plaat', 'Afgeleid: bovenkant plaat'),
    ('z_wand', 'z_plaat_boven - plaat_dikte', 'Afgeleid: bovenkant wand = onderkant plaat'),
    ('wand_pink', 'conn_diepte - jnp_rand - spleet', 'Afgeleid: wanddikte pinkkant'),
]

# Printrand route 2 (pinkkant +6 mm) als 24 lijnen en 5 bogen; bron data/lily58-pro-printrand.csv.
# L = lijn (begin, eind); A = boog door drie punten (begin, midden, eind).
PCB = json.loads('[["L", [-54.143, -97.062], [-40.738, -89.301]], ["L", [-40.738, -89.301], [18.219, -89.302]], ["A", [18.219, -89.302], [19.28, -88.863], [19.719, -87.802]], ["L", [19.719, -87.802], [19.719, -78.08]], ["A", [19.719, -78.08], [20.744, -75.604], [23.219, -74.58]], ["L", [23.219, -74.58], [71.36, -74.58]], ["A", [71.36, -74.58], [72.421, -74.141], [72.86, -73.08]], ["L", [72.86, -73.08], [72.86, 2.773]], ["L", [72.86, 2.773], [71.678, 4.054]], ["L", [71.678, 4.054], [62.289, 5.246]], ["L", [62.289, 5.246], [56.926, 6.325]], ["L", [56.926, 6.325], [49.821, 7.264]], ["L", [49.821, 7.264], [41.208, 8.04]], ["L", [41.208, 8.04], [31.32, 8.625]], ["L", [31.32, 8.625], [20.39, 8.994]], ["L", [20.39, 8.994], [8.651, 9.123]], ["L", [8.651, 9.123], [-74.612, 9.123]], ["A", [-74.612, 9.123], [-75.354, 8.816], [-75.662, 8.073]], ["L", [-75.662, 8.073], [-75.662, -42.382]], ["L", [-75.662, -42.382], [-75.464, -46.408]], ["L", [-75.464, -46.408], [-75.11, -50.448]], ["L", [-75.11, -50.448], [-74.579, -54.481]], ["L", [-74.579, -54.481], [-73.853, -58.485]], ["L", [-73.853, -58.485], [-72.912, -62.439]], ["L", [-72.912, -62.439], [-71.737, -66.321]], ["L", [-71.737, -66.321], [-70.308, -70.108]], ["L", [-70.308, -70.108], [-68.607, -73.78]], ["L", [-68.607, -73.78], [-55.202, -96.709]], ["A", [-55.202, -96.709], [-54.758, -97.176], [-54.143, -97.062]]]')

# Onderdelen op de print (KiCad Lily58_Pro.kicad_pcb, 12 nov), omgerekend: x - 158,6 ; 46,21 - y
J_NP, USB, TRRS, RESET, OLED = (70.8, -35.54), (-57.6, 9.21), (-70.7, 9.21), (-73.6, -21.49), (-58.1, -28.39)
TH = [(-29.0, -13.39), (47.2, -15.59), (-29.0, -51.39), (47.2, -53.79), (-53.6, -68.59), (-72.6, -38.79), (-50.6, -38.79)]
TH12 = TH[5:]                                   # afstandsbussen onder de kap
K_KOL1, K_DUIM = (-38.1, -3.79), (-57.2, -51.29)  # masterpunten: toets kolom 1 en bovenste duimtoets
# 8 x M3 in de wand (verdeling uit behuizing.py); in de schets gekoppeld aan de hartlijn van de wand
M3 = [(-33.9194, -93.8019), (24.219, -85.9998), (76.83, -73.1999), (76.83, -9.8376),
      (30.0352, 13.1709), (-33.321, 13.623), (-80.162, -5.2826), (-75.8429, -68.1862)]
VOET = [(-69.662, 3.123), (65.8, 3.123), (65.8, -75.204), (-40.0, -87.204)]
HOL = [(27.719, -82.58), (-38.589, -97.301)]    # holle hoeken van de buitencontour (bij wand 7, spleet 1)


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

def body(root, name):
    return [b for b in root.bRepBodies if b.name == name][0]

def area(p): return p.areaProperties().area * 100

def biggest(s):
    return max([s.profiles.item(i) for i in range(s.profiles.count)], key=area)

def near(p, x, y, tol=1.0):
    c = p.areaProperties().centroid
    return math.hypot(c.x * 10 - x, c.y * 10 - y) < tol

def find_pt(s, xy):
    for p in s.sketchPoints:
        if abs(p.geometry.x * 10 - xy[0]) < 1e-4 and abs(p.geometry.y * 10 - xy[1]) < 1e-4: return p
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

def pcb_offset(s, pcb, expr, construction):
    """projecteer de printrand (hulplijn) en maak een offset naar buiten"""
    proj = []
    for e in pcb.sketchCurves:
        r = s.project(e)
        for i in range(r.count): proj.append(r.item(i))
    for e in proj: e.isConstruction = True
    chain = s.findConnectedCurves(proj[0])
    for sign in ('%s', '-(%s)'):
        inp = s.geometricConstraints.createOffsetInput([chain.item(i) for i in range(chain.count)], VI(sign % expr))
        inp.isTopologyMatched = False
        oc = s.geometricConstraints.addOffset2(inp)
        ch = list(oc.childCurves)
        if max(c.boundingBox.maxPoint.x for c in ch) * 10 > 72.9: break      # naar buiten
        oc.deleteMe()
        for c in ch:
            if c.isValid: c.deleteMe()
    for c in ch: c.isConstruction = construction
    return ch

def vert_edges(b, test):
    out = []
    for e in b.edges:
        if e.geometry.curveType != adsk.core.Curve3DTypes.Line3DCurveType: continue
        p, q = e.startVertex.geometry, e.endVertex.geometry
        if abs(p.x - q.x) < 1e-6 and abs(p.y - q.y) < 1e-6 and test(p.x * 10, p.y * 10): out.append(e)
    return out

def fillet(root, edges, expr, name, tangent=False):
    inp = root.features.filletFeatures.createInput()
    inp.edgeSetInputs.addConstantRadiusEdgeSet(coll(edges), VI(expr), tangent)
    f = root.features.filletFeatures.add(inp); f.name = name
    return f

def report(d, root):
    tl = d.timeline
    print('tijdlijn', tl.count, '| niet gezond:', [tl.item(i).name for i in range(tl.count) if tl.item(i).healthState != 0])
    bodies = list(root.bRepBodies) + [b for o in root.occurrences for b in o.component.bRepBodies]
    for b in bodies:
        bb = b.boundingBox
        print('%-6s %9.1f mm3  vlakken %3d  x[%.2f %.2f] y[%.2f %.2f] z[%.2f %.2f]' % (
            b.name, b.volume * 1000, b.faces.count, bb.minPoint.x * 10, bb.maxPoint.x * 10,
            bb.minPoint.y * 10, bb.maxPoint.y * 10, bb.minPoint.z * 10, bb.maxPoint.z * 10))


# ---------------------------------------------------------------- stap 0: opruimen, parameters, printrand
def stap0():
    app, d, root = ctx()
    tl = d.timeline
    idx = [i for i in range(tl.count) if tl.item(i).name == 'PCB omtrek (Lily58 Pro)'][0]
    tl.markerPosition = idx + 1
    tl.deleteAllAfterMarker()
    up = d.userParameters
    for n, e, c in PARAMS:
        if up.itemByName(n) is None: up.add(n, VI(e), 'mm', c)
    s = root.sketches.itemByName('PCB omtrek (Lily58 Pro)')
    for e in list(s.sketchCurves):
        e.isFixed = False
    for e in list(s.sketchCurves):
        if e.isValid: e.deleteMe()
    prev = None; first = None; ents = []
    for pr in PCB:
        st = prev if prev else P(*pr[1])
        en = first if pr is PCB[-1] else P(*pr[-1])
        if pr[0] == 'L': e = s.sketchCurves.sketchLines.addByTwoPoints(st, en)
        else: e = s.sketchCurves.sketchArcs.addByThreePoints(st, P(*pr[2]), en)
        sp, ep = e.startSketchPoint, e.endSketchPoint
        nxt = ep if abs(ep.geometry.x * 10 - pr[-1][0]) + abs(ep.geometry.y * 10 - pr[-1][1]) < 1e-3 else sp
        if first is None: first = sp if nxt is ep else ep
        prev = nxt; ents.append(e)
    for e in ents: e.isFixed = True
    print('printrand: krommen', s.sketchCurves.count, 'profielen', s.profiles.count, 'opp mm2', round(area(s.profiles.item(0)), 1))


# ---------------------------------------------------------------- stap 1: contouren, bak, plaat, kap (ruw)
def stap1():
    app, d, root = ctx()
    sk = root.sketches
    pcb = sk.itemByName('PCB omtrek (Lily58 Pro)')
    master = sk.itemByName('Master toetsposities')
    po = sk.add(root.xYConstructionPlane); po.name = 'Print onderdelen'
    for xy in [J_NP, USB, TRRS, RESET, OLED] + TH:
        po.sketchPoints.add(P(*xy)).isFixed = True
    # buitencontour = printrand + spleet + wand, aan de pinkkant afgesneden op het contactvlak van de connector
    c = sk.add(root.xYConstructionPlane); c.name = 'Contour buiten'
    pcb_offset(c, pcb, 'spleet + wand', False)
    ln = c.sketchCurves.sketchLines.addByTwoPoints(P(79.8, 40), P(79.8, -130))
    c.geometricConstraints.addVertical(ln)
    odim(c, ln, proj_pt(c, po, J_NP), 'conn_diepte', 75, -30)
    c.sketchDimensions.addDistanceDimension(c.originPoint, ln.startSketchPoint, HO.VerticalDimensionOrientation, P(90, 20))
    c.sketchDimensions.addDistanceDimension(c.originPoint, ln.endSketchPoint, HO.VerticalDimensionOrientation, P(90, -60))
    b = sk.add(root.xYConstructionPlane); b.name = 'Contour binnen'
    pcb_offset(b, pcb, 'spleet', False)
    bak = extrude(root, biggest(c), FO.NewBodyFeatureOperation, None, 'z_wand', 'Bak buitenvorm').bodies.item(0); bak.name = 'Bak'
    extrude(root, biggest(b), FO.CutFeatureOperation, 'bodem', 'z_wand - bodem', 'Bak holte', [bak])
    plaat = extrude(root, biggest(c), FO.NewBodyFeatureOperation, 'z_wand', 'plaat_dikte', 'Plaat buitenvorm').bodies.item(0); plaat.name = 'Plaat'
    kap = extrude(root, biggest(c), FO.NewBodyFeatureOperation, 'z_plaat_boven', 'kap_hoogte', 'Kap buitenvorm').bodies.item(0); kap.name = 'Kap'
    # kap: 0,5 mm voor de keycap van kolom 1 en 1 mm boven de keycap van de bovenste duimtoets
    s = sk.add(root.xYConstructionPlane); s.name = 'Kap begrenzing'
    on, re, bo, li = rect(s, -100, -41.29, -47.6, 40)
    odim(s, re, proj_pt(s, master, K_KOL1), 'keycap / 2 + 0.5 mm', -43, 20)
    odim(s, on, proj_pt(s, master, K_DUIM), 'keycap / 2 + 1 mm', -60, -46)
    s.sketchDimensions.addDistanceDimension(s.originPoint, li.startSketchPoint, HO.HorizontalDimensionOrientation, P(-50, 45))
    s.sketchDimensions.addDistanceDimension(s.originPoint, bo.startSketchPoint, HO.VerticalDimensionOrientation, P(5, 20))
    extrude(root, s.profiles.item(0), FO.IntersectFeatureOperation, 'z_plaat_boven', 'kap_hoogte', 'Kap begrenzen', [kap])
    extrude(root, biggest(b), FO.CutFeatureOperation, 'z_plaat_boven', 'kap_hoogte - kap_dak', 'Kap holte', [kap])
    # steunbussen met M2-tapgat onder de 7 printgaten
    s = sk.add(root.xYConstructionPlane); s.name = 'Steunbussen'
    C = s.sketchCurves.sketchCircles; first = None
    for xy in TH:
        pp = proj_pt(s, po, xy)
        c1 = C.addByCenterRadius(pp, 0.25); c2 = C.addByCenterRadius(pp, 0.08)
        if first is None:
            s.sketchDimensions.addDiameterDimension(c1, P(xy[0] + 5, xy[1] + 5)).parameter.expression = 'bus_d'
            s.sketchDimensions.addDiameterDimension(c2, P(xy[0] + 3, xy[1] - 4)).parameter.expression = 'm2_gat'
            first = (c1, c2)
        else:
            s.geometricConstraints.addEqual(first[0], c1); s.geometricConstraints.addEqual(first[1], c2)
    profs = [s.profiles.item(i) for i in range(s.profiles.count)]
    extrude(root, coll(profs), FO.JoinFeatureOperation, 'bodem', 'vrij_onder', 'Steunbussen', [bak])
    extrude(root, coll([p for p in profs if p.profileLoops.count == 1]), FO.CutFeatureOperation, 'bodem - 2 mm', 'vrij_onder + 2 mm', 'M2 tapgaten', [bak])
    report(d, root)


# ---------------------------------------------------------------- stap 2: uitsparingen, plaat, voetjes, M3
def stap2():
    app, d, root = ctx()
    sk = root.sketches
    pcb = sk.itemByName('PCB omtrek (Lily58 Pro)')
    po = sk.itemByName('Print onderdelen')
    bak, plaat, kap = body(root, 'Bak'), body(root, 'Plaat'), body(root, 'Kap')
    # plaat: USB en TRRS als een sleuf (anders blijft er een los stukje plaat tussen staan)
    s = sk.add(root.xYConstructionPlane); s.name = 'Plaat sleuf USB-TRRS'
    usb = proj_pt(s, po, USB); trrs = proj_pt(s, po, TRRS)
    a, b, c, e = rect(s, -74.7, 8.21, -51.6, 29.21)
    odim(s, e, trrs, '4 mm', -73, 40); odim(s, b, usb, '6 mm', -50, 36); odim(s, a, usb, '1 mm', -45, 8); odim(s, c, usb, '20 mm', -45, 20)
    extrude(root, s.profiles.item(0), FO.CutFeatureOperation, 'z_wand', 'plaat_dikte', 'Plaat sleuf USB-TRRS (uitsnede)', [plaat])
    # uitsparingen in de wand
    s = sk.add(root.xYConstructionPlane); s.name = 'Uitsparingen wand'
    usb = proj_pt(s, po, USB); trrs = proj_pt(s, po, TRRS); jnp = proj_pt(s, po, J_NP)
    a, b, c, e = rect(s, -63.6, 8.21, -51.6, 29.21)
    odim(s, e, usb, '6 mm', -62, 33); odim(s, b, e, '12 mm', -57, 36); odim(s, a, usb, '1 mm', -45, 8); odim(s, c, usb, '20 mm', -45, 20)
    a, b, c, e = rect(s, -74.7, 8.21, -66.7, 29.21)
    odim(s, e, trrs, '4 mm', -73, 40); odim(s, b, e, '8 mm', -70, 44); odim(s, a, trrs, '1 mm', -85, 8); odim(s, c, trrs, '20 mm', -85, 20)
    a, b, c, e = rect(s, 72.86, -48.04, 84.8, -23.04)
    odim(s, e, jnp, 'jnp_rand', 72, -20); odim(s, b, jnp, 'conn_diepte + 5 mm', 80, -18); odim(s, a, jnp, '12.5 mm', 90, -42); odim(s, c, a, '25 mm', 95, -35)
    pr = [s.profiles.item(i) for i in range(s.profiles.count)]
    alle = [bak, plaat, kap]
    extrude(root, [p for p in pr if near(p, -57.6, 18.71)][0], FO.CutFeatureOperation, 'z_pcb_boven + 0.5 mm', '11.5 mm', 'Uitsparing USB-C', alle)
    extrude(root, [p for p in pr if near(p, -70.7, 18.71)][0], FO.CutFeatureOperation, 'z_pcb_boven - 1 mm', '8 mm', 'Uitsparing TRRS', alle)
    extrude(root, [p for p in pr if near(p, 78.83, -35.54)][0], FO.CutFeatureOperation, 'z_pcb_boven - 0.5 mm', '8 mm', 'Uitsparing connector', [bak, plaat])
    # plaat: 29 switchuitsparingen en de opening boven Pro Micro en OLED
    pu = sk.itemByName('Plaat uitsparingen')
    extrude(root, coll([pu.profiles.item(i) for i in range(pu.profiles.count)]), FO.CutFeatureOperation, 'z_wand', 'plaat_dikte', 'Plaat switchuitsparingen', [plaat])
    s = sk.add(root.xYConstructionPlane); s.name = 'Plaat opening'
    a, b, c, e = rect(s, -75.662, -30.99, -48.0, 9.123)
    odim(s, b, proj_pt(s, po, USB), '9.6 mm', -45, 0)          # 0,5 mm voorbij de rand van de Pro Micro
    odim(s, a, proj_pt(s, po, OLED), '2.6 mm', -40, -30)
    s.sketchDimensions.addDistanceDimension(s.originPoint, e.startSketchPoint, HO.HorizontalDimensionOrientation, P(-40, 14)).parameter.expression = '75.662 mm'
    s.sketchDimensions.addDistanceDimension(s.originPoint, c.startSketchPoint, HO.VerticalDimensionOrientation, P(5, 5)).parameter.expression = '9.123 mm'
    cs = [s.sketchCurves.sketchCircles.addByCenterRadius(proj_pt(s, po, xy), 0.225) for xy in TH12]
    s.sketchDimensions.addDiameterDimension(cs[0], P(-70, -45)).parameter.expression = '4.5 mm'
    s.geometricConstraints.addEqual(cs[0], cs[1])
    extrude(root, coll([s.profiles.item(i) for i in range(s.profiles.count)]), FO.CutFeatureOperation, 'z_wand', 'plaat_dikte', 'Plaat opening controller', [plaat])
    # rubbervoetjes
    s = sk.add(root.xYConstructionPlane); s.name = 'Voetjes'
    cs = []
    for x, y in VOET:
        c1 = s.sketchCurves.sketchCircles.addByCenterRadius(P(x, y), 0.5)
        for o, tp in ((HO.HorizontalDimensionOrientation, P(x, y + 8)), (HO.VerticalDimensionOrientation, P(x + 8, y))):
            try: s.sketchDimensions.addDistanceDimension(s.originPoint, c1.centerSketchPoint, o, tp)
            except RuntimeError: s.geometricConstraints.addHorizontalPoints(cs[0].centerSketchPoint, c1.centerSketchPoint)
        if not cs: s.sketchDimensions.addDiameterDimension(c1, P(x + 6, y + 6)).parameter.expression = 'voet_d'
        else: s.geometricConstraints.addEqual(cs[0], c1)
        cs.append(c1)
    extrude(root, coll([s.profiles.item(i) for i in range(s.profiles.count)]), FO.CutFeatureOperation, None, 'voet_diepte', 'Verdiepingen voetjes', [bak])
    # M3: punten op de hartlijn van de wand (pinkkant: midden van de dunnere wand)
    s = sk.add(root.xYConstructionPlane); s.name = 'M3 gaten'
    mids = pcb_offset(s, pcb, 'spleet + wand / 2', True)
    strokes = []
    for m in mids:
        ev = m.geometry.evaluator
        ok, t0, t1 = ev.getParameterExtents()
        ok, pts = ev.getStrokes(t0, t1, 0.001)
        strokes.append((m, [(p.x * 10, p.y * 10) for p in pts]))
    jnp = proj_pt(s, po, J_NP)
    C = s.sketchCurves.sketchCircles; first = None; kapxy = None
    for x, y in M3:
        pt = s.sketchPoints.add(P(x, y))
        if x > 76:
            s.sketchDimensions.addDistanceDimension(jnp, pt, HO.HorizontalDimensionOrientation, P(x + 6, y + 5)).parameter.expression = 'conn_diepte - wand_pink / 2'
            s.sketchDimensions.addDistanceDimension(s.originPoint, pt, HO.VerticalDimensionOrientation, P(x + 10, y / 2))
        else:
            best = None
            for m, pts in strokes:
                for (ax, ay), (bx, by) in zip(pts, pts[1:]):
                    dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
                    t = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / L2)) if L2 else 0
                    dist = math.hypot(x - ax - t * dx, y - ay - t * dy)
                    if best is None or dist < best[0]: best = (dist, m, dx, dy)
            s.geometricConstraints.addCoincident(pt, best[1])
            if abs(best[2]) >= abs(best[3]): s.sketchDimensions.addDistanceDimension(s.originPoint, pt, HO.HorizontalDimensionOrientation, P(x, y + 8))
            else: s.sketchDimensions.addDistanceDimension(s.originPoint, pt, HO.VerticalDimensionOrientation, P(x + 8, y))
        c1 = C.addByCenterRadius(pt, 0.125); c2 = C.addByCenterRadius(pt, 0.17)
        if first is None:
            s.sketchDimensions.addDiameterDimension(c1, P(x + 3, y + 3)).parameter.expression = 'm3_gat'
            s.sketchDimensions.addDiameterDimension(c2, P(x - 4, y + 4)).parameter.expression = 'm3_vrij'
            first = (c1, c2)
        else:
            s.geometricConstraints.addEqual(first[0], c1); s.geometricConstraints.addEqual(first[1], c2)
        if x < -47.6 and y > -41.29:                      # schroef die ook door de kap gaat: verzonken kop
            c3 = C.addByCenterRadius(pt, 0.3)
            s.sketchDimensions.addDiameterDimension(c3, P(x - 6, y + 6)).parameter.expression = '6 mm'
            kapxy = (pt.geometry.x * 10, pt.geometry.y * 10)
    print('M3 posities', sorted(set((round(c.centerSketchPoint.geometry.x * 10, 3), round(c.centerSketchPoint.geometry.y * 10, 3)) for c in C)))
    profs = [s.profiles.item(i) for i in range(s.profiles.count)]
    vrij = [p for p in profs if area(p) < 5.5]
    kp = [p for p in profs if near(p, kapxy[0], kapxy[1])]
    extrude(root, coll([p for p in vrij if p.profileLoops.count == 1]), FO.CutFeatureOperation, 'z_wand - 8 mm', '8 mm', 'M3 tapgaten', [bak])
    extrude(root, coll(vrij), FO.CutFeatureOperation, 'z_wand', 'plaat_dikte', 'M3 doorgaand plaat', [plaat])
    extrude(root, coll([p for p in kp if area(p) < 5.5]), FO.CutFeatureOperation, 'z_plaat_boven', 'kap_hoogte', 'M3 doorgaand kap', [kap])
    extrude(root, coll(kp), FO.CutFeatureOperation, 'z_plaat_boven + kap_hoogte - 3.2 mm', '3.2 mm', 'M3 verzonken kap', [kap])
    report(d, root)


# ---------------------------------------------------------------- stap 3: kap, reset, afrondingen, componenten
def stap3():
    app, d, root = ctx()
    sk = root.sketches
    po = sk.itemByName('Print onderdelen')
    bak, plaat, kap = body(root, 'Bak'), body(root, 'Plaat'), body(root, 'Kap')
    # kap: OLED-venster 9 x 26 mm en M2 naar de afstandsbussen (verzonken kop)
    s = sk.add(root.xYConstructionPlane); s.name = 'Kap dak'
    oled = proj_pt(s, po, OLED)
    a, b, c, e = rect(s, -62.6, -20.89, -53.6, 5.11)
    odim(s, e, oled, '4.5 mm', -66, 8); odim(s, b, e, '9 mm', -58, 10); odim(s, a, oled, '7.5 mm', -45, -24); odim(s, c, a, '26 mm', -45, -8)
    cs = []
    for xy in TH12:
        pp = proj_pt(s, po, xy)
        cs.append((s.sketchCurves.sketchCircles.addByCenterRadius(pp, 0.12), s.sketchCurves.sketchCircles.addByCenterRadius(pp, 0.22)))
    s.sketchDimensions.addDiameterDimension(cs[0][0], P(-70, -34)).parameter.expression = '2.4 mm'
    s.sketchDimensions.addDiameterDimension(cs[0][1], P(-76, -34)).parameter.expression = '4.4 mm'
    s.geometricConstraints.addEqual(cs[0][0], cs[1][0]); s.geometricConstraints.addEqual(cs[0][1], cs[1][1])
    profs = [s.profiles.item(i) for i in range(s.profiles.count)]
    rond = [p for p in profs if area(p) < 100]
    extrude(root, coll([p for p in profs if area(p) > 100]), FO.CutFeatureOperation, 'z_plaat_boven + kap_hoogte - kap_dak', 'kap_dak', 'OLED-venster', [kap])
    extrude(root, coll([p for p in rond if p.profileLoops.count == 1]), FO.CutFeatureOperation, 'z_plaat_boven + kap_hoogte - kap_dak', 'kap_dak', 'M2 doorgaand kap', [kap])
    extrude(root, coll(rond), FO.CutFeatureOperation, 'z_plaat_boven + kap_hoogte - 1.2 mm', '1.2 mm', 'M2 verzonken kap', [kap])
    # resetgat door de linkerwand (aanname: knop wordt van opzij ingedrukt)
    pi = root.constructionPlanes.createInput(); pi.setByOffset(root.yZConstructionPlane, VI('%s mm' % RESET[0]))
    pl = root.constructionPlanes.add(pi); pl.name = 'Vlak reset'
    s = sk.add(pl); s.name = 'Resetgat'
    rp = proj_pt(s, po, RESET)
    cpt = s.modelToSketchSpace(adsk.core.Point3D.create(RESET[0] / 10, RESET[1] / 10, 1.06))
    cc = s.sketchCurves.sketchCircles.addByCenterRadius(cpt, 0.175)
    if abs(cpt.x - rp.geometry.x) < 1e-6: s.geometricConstraints.addVerticalPoints(rp, cc.centerSketchPoint)
    else: s.geometricConstraints.addHorizontalPoints(rp, cc.centerSketchPoint)
    s.sketchDimensions.addDistanceDimension(rp, cc.centerSketchPoint, HO.AlignedDimensionOrientation, adsk.core.Point3D.create(cpt.x + 0.5, cpt.y + 0.5, 0)).parameter.expression = 'z_pcb_boven + 1.5 mm'
    s.sketchDimensions.addDiameterDimension(cc, adsk.core.Point3D.create(cpt.x - 0.5, cpt.y + 0.5, 0)).parameter.expression = '3.5 mm'
    n = s.xDirection.crossProduct(s.yDirection)
    extrude(root, s.profiles.item(0), FO.CutFeatureOperation, None, '15 mm', 'Resetgat', [bak], ED.NegativeExtentDirection if n.x > 0 else ED.PositiveExtentDirection)
    # afrondingen
    for b in (bak, plaat):
        fillet(root, vert_edges(b, lambda x, y: abs(x - 79.8) < 1e-3 and (y > -22.9 or y < -48.2)), 'r_buiten', 'Afronding pinkkant ' + b.name)
        fillet(root, vert_edges(b, lambda x, y: any(abs(x - hx) < 5e-3 and abs(y - hy) < 5e-3 for hx, hy in HOL)), 'r_binnen', 'Afronding holle hoeken ' + b.name)
    top = max([f for f in kap.faces if f.geometry.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType
               and abs(f.boundingBox.minPoint.z * 10 - 24.1) < 1e-3 and abs(f.boundingBox.maxPoint.z * 10 - 24.1) < 1e-3], key=lambda f: f.area)
    fillet(root, list([l for l in top.loops if l.isOuter][0].edges), '0.8 mm', 'Afronding bovenrand kap', True)
    # print als referentie, materiaal, componenten
    pcb = sk.itemByName('PCB omtrek (Lily58 Pro)')
    extrude(root, pcb.profiles.item(0), FO.NewBodyFeatureOperation, 'z_pcb_onder', 'pcb_dikte', 'Print (referentie)').bodies.item(0).name = 'Print'
    alu = app.materialLibraries.itemByName('Fusion Material Library').materials.itemByName('Aluminum 6061')
    names = {'Bak': 'Bak rechts', 'Plaat': 'Plaat rechts', 'Kap': 'Kap rechts', 'Print': 'Print rechts (referentie)'}
    for b in list(root.bRepBodies):
        nm = b.name
        if nm != 'Print': b.material = alu
        b.createComponent().parentComponent.name = names[nm]
    for s in root.sketches: s.isVisible = False
    report(d, root)
    for o in root.occurrences:
        for b in o.component.bRepBodies:
            print('%-28s %6.1f g  %s' % (o.component.name, b.physicalProperties.mass * 1000, b.material.name))

# ---------------------------------------------------------------- stap 4: linkerhelft (spiegelbeeld)
def stap4():
    app, d, root = ctx()
    tl = d.timeline
    idx = [i for i in range(tl.count) if tl.item(i).name == 'Print (referentie)'][0]
    tl.markerPosition = idx + 1                      # voor het maken van de componenten
    up = d.userParameters
    if up.itemByName('helft_afstand') is None:
        up.add('helft_afstand', VI('40 mm'), 'mm', 'Ruimte tussen linker- en rechterhelft in het model (alleen weergave)')
    pi = root.constructionPlanes.createInput()
    pi.setByOffset(root.yZConstructionPlane, VI('-(83.662 mm + helft_afstand / 2)'))
    pl = root.constructionPlanes.add(pi); pl.name = 'Spiegelvlak helften'
    mi = root.features.mirrorFeatures.createInput(coll([body(root, n) for n in ('Bak', 'Plaat', 'Kap')]), pl)
    mf = root.features.mirrorFeatures.add(mi); mf.name = 'Linkerhelft (spiegeling)'
    for b in root.bRepBodies:                        # mf.bodies bevat ook de originelen
        if b.name not in ('Bak', 'Plaat', 'Kap', 'Print'):
            v = b.volume * 1000
            b.name = 'Bak links' if v > 50000 else ('Plaat links' if v > 10000 else 'Kap links')
    tl.moveToEnd()
    alu = app.materialLibraries.itemByName('Fusion Material Library').materials.itemByName('Aluminum 6061')
    for b in list(root.bRepBodies):
        nm = b.name
        b.material = alu
        b.createComponent().parentComponent.name = nm
    pl.isLightBulbOn = False
    report(d, root)


# ---------------------------------------------------------------- stap 5: verbeteringen v0.3
def tl_index(d, test):
    tl = d.timeline
    return [i for i in range(tl.count) if test(tl.item(i).name)]

def stap5():
    """Ingevoegd op de juiste plek in de tijdlijn (dus voor de afrondingen en de spiegeling)."""
    app, d, root = ctx()
    sk = root.sketches
    tl = d.timeline
    po = sk.itemByName('Print onderdelen')
    # 1. M2 in de kap: verzinking 90 graden (ø4,0) in plaats van een verzonken cilinderkop (ø4,4)
    i = tl_index(d, lambda n: n == 'M2 verzonken kap')[0]
    tl.item(i).entity.deleteMe()
    tl.markerPosition = i
    kap = body(root, 'Kap')
    edges = [e for e in kap.edges if e.geometry.curveType == adsk.core.Curve3DTypes.Circle3DCurveType
             and abs(e.geometry.radius * 10 - 1.2) < 1e-3 and abs(e.geometry.center.z * 10 - 24.1) < 1e-3]
    ci = root.features.chamferFeatures.createInput2()
    ci.chamferEdgeSets.addEqualDistanceChamferEdgeSet(coll(edges), VI('0.8 mm'), False)
    root.features.chamferFeatures.add(ci).name = 'M2 verzinking kap'
    tl.moveToEnd()
    # 2. resetgat wordt een sleuf tot de bovenkant van de wand (de plaat sluit hem af)
    i = tl_index(d, lambda n: n.startswith('Resetgat'))[-1]
    tl.markerPosition = i + 1
    bak = body(root, 'Bak')
    s = sk.add(root.xYConstructionPlane); s.name = 'Resetsleuf'
    rp = proj_pt(s, po, RESET)
    a, b, c, e = rect(s, -90, -23.24, -74.6, -19.74)
    odim(s, a, rp, '1.75 mm', -95, -22); odim(s, c, a, '3.5 mm', -98, -21); odim(s, b, rp, '1 mm', -72, -17)
    s.sketchDimensions.addDistanceDimension(s.originPoint, e.startSketchPoint, HO.HorizontalDimensionOrientation, P(-80, -10))
    extrude(root, s.profiles.item(0), FO.CutFeatureOperation, 'z_pcb_boven + 1.5 mm', 'z_wand - z_pcb_boven - 1.5 mm', 'Resetsleuf (uitsnede)', [bak])
    tl.moveToEnd()
    # 3. tussenwand USB-TRRS weg in bak en kap: een gezamenlijke opening
    i = tl_index(d, lambda n: n == 'Uitsparing TRRS')[0]
    tl.markerPosition = i + 1
    ps = sk.itemByName('Plaat sleuf USB-TRRS')
    extrude(root, ps.profiles.item(0), FO.CutFeatureOperation, 'z_pcb_boven + 0.5 mm', '11.5 mm', 'Tussenwand USB-TRRS weg', [body(root, 'Bak'), body(root, 'Kap')])
    tl.moveToEnd()
    for s2 in root.sketches: s2.isVisible = False
    report(d, root)


def run(_context: str):
    stap0(); stap1(); stap2(); stap3(); stap4(); stap5()
