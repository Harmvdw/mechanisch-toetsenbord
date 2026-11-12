# Fusion-opzet

Document: "Opzet 1-0-0", map Toetsenbord, project Admin Project. Eenheden: mm, parametrisch ontwerp. Opgeslagen op 10 november 2026.

## Gebruikersparameters

| Naam | Waarde | Doel |
|---|---|---|
| `uitsparing` | 14 mm | Zijde van de plaatuitsparing per switch (E8) |
| `duimhoek` | 30 deg | Draaiing van de gedraaide duimtoets (W4) |

## Schetsen (vlak XY)

**Master toetsposities.** 29 punten voor één helft. Oorsprong: de bovenste toets van kolom 3. Bron: [09-maten-uit-stl-en-gerber.md](09-maten-uit-stl-en-gerber.md) en `data/lily58-pro-switchposities.csv`, verschoven met (−158,6; +46,21) mm. Dit is de enige plek waar toetsposities staan (E18).

**Plaat uitsparingen.** 29 vierkanten van `uitsparing` × `uitsparing`.
- Het middelpunt van elk vierkant is met een middelpuntconstraint gekoppeld aan een geprojecteerd punt uit de master-schets. Verplaats je een masterpunt, dan verplaatst het vierkant mee.
- 28 vierkanten zijn horizontaal gebonden. Eén vierkant heeft een hoekmaat gekoppeld aan `duimhoek`.
- Alle lijnen zijn volledig bepaald. De schets geeft 29 profielen van elk 196 mm² (gecontroleerd).
- De schets bevat ook een geprojecteerde X-as als referentielijn. Die tekent een paarse lijn door de oorsprong en is geen onderdeel van de uitsparingen.

**PCB omtrek (Lily58 Pro).** De printrand uit `Edge_Cuts` van de keebs-Gerbers. Sinds 12 november: 6 mm breder aan de pinkkant (route 2) en opgebouwd uit 24 lijnen en 5 bogen in plaats van 120 lijnstukjes; één gesloten profiel van 13.552,5 mm², alle krommen vastgezet. Zelfde oorsprong als de master-schets. Alle 29 toetsen liggen erbinnen; de kleinste afstand toetsmidden tot rand is 9,12 mm.

## Gecontroleerd

- Alle 29 profielen: oppervlakte 196,0 mm², middelpunt op de masterpunten (afwijking 0,0 mm).
- Gedraaide toets: vier lijnen op 30° (mod 90°), lengte 14,0 mm, tegen de klok in.

## Vervolg

Behuizing (bak, plaat, kap, beide helften) en alle extra parameters: zie [14-behuizing-fusion.md](14-behuizing-fusion.md).

## Nog niet gedaan

- Numpad in Fusion.
- Keuze plaatdikte (W6: 1,2 of 1,5 mm; parameter `plaat_dikte`).
