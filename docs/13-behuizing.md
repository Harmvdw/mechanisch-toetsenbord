# Behuizing — prototype v0.1

Status: 12 november 2026. Eerste model van de behuizing voor de **rechterhelft** en het **numpad**, gemaakt als parametrisch CadQuery-script omdat Fusion op dat moment niet bereikbaar was. Het is bedoeld voor een 3D-print-prototype (E20b) en als basis voor het Fusion-ontwerp. De linkerhelft is het spiegelbeeld en volgt later.

Bestanden:
- Model: [`behuizing/behuizing.py`](../behuizing/behuizing.py) — alle maten staan bovenaan als parameters.
- Export: `behuizing/export/*.step` (importeren in Fusion) en `*.stl` (3D-printen).
- Controle: [`behuizing/afbeeldingen/`](../behuizing/afbeeldingen) (doorsneden en 3D-aanzichten).

Opnieuw maken: `pip install cadquery trimesh matplotlib`, dan `python3 behuizing/behuizing.py`.

## Keuzes (Harm, 12 nov)
- Vlak (geen typhoek); later eventueel klapvoetjes.
- OLED achter een venster in een gesloten kap.
- Stevig: dikke wand en bodem.
- Eerst één helft en het numpad.

## Opbouw
| Deel | Wat |
|---|---|
| **Bak** | Bodem 4 mm, wand 7 mm (pinkkant 5,94 mm, zie connector), open bovenkant. Steunbussen ø5 mm met M2-tapgat onder de 7 printgaten (TH1–TH7). 8 × M3-tapgat in de wandbovenkant. 4 verdiepingen ø10 × 1 mm voor rubbervoetjes. |
| **Plaat** | 1,5 mm, volle buitenmaat (ligt op de wand, "sandwich"). 29 uitsparingen 14 × 14 mm, één 30° gedraaid. Opening boven Pro Micro en OLED; doorvoer ø4,5 voor 2 afstandsbussen. |
| **Kap** (helft) | Dak 2 mm, 10 mm boven de plaat, over Pro Micro, OLED en TRRS. Wanden alleen aan de buitenkant (links en boven); de binnenkant is open omdat de keycap van kolom 1 maar 1,4 mm van de Pro Micro zit. OLED-venster 9 × 26 mm. Gedragen door 2 afstandsbussen M2 × 13 mm op TH1/TH2 (zoals de originele Lily58-OLED-kap) en één M3-schroef in de wand. |

Hoogtes (z = 0 onderkant bak): bodem 0–4, print 7,5–9,1 (3,5 mm vrij eronder voor hotswap-voetjes), wand tot 12,6, plaat 12,6–14,1 (MX-norm: 5,0 mm boven de print), kap tot 24,1.

## Maten en gewicht (aluminium 2,70 g/cm³)
| | Buitenmaat | Gewicht |
|---|---|---|
| Helft rechts (bak + plaat + kap) | 163,5 × 122,3 × 14,1 mm (kap tot 24,1) | 328 g |
| Numpad (bak + plaat) | 104,7 × 129,8 × 14,1 mm | 235 g |

Beide onder de 600 g van W11. Schroeven, switches en print niet meegerekend.

## Uitsparingen
- **USB-C** (Pro Micro): 12 mm breed, z 9,6–21,1, in bak, plaat en kap.
- **TRRS**: 8 mm breed, z 8,1–16,1.
- **Reset**: gat ø3,5 in de linkerwand, z 10,6. *Aanname:* de resetknop (TVBP06) wordt van opzij ingedrukt. Controleren.
- **Connector**: sleuf 25 × 8 mm door de wand ter hoogte van J_NP (helft) en J1/J2 (numpad).

## Connector en wanddikte
Het contactvlak van de magnetische connector moet gelijk liggen met de buitenwand, anders sluiten numpad en helft niet aan. De wanddikte aan de connectorkant volgt daarom uit de parameter **`conn_diepte`** (afstand pennenrij tot contactvlak), nu geschat op **9,0 mm**:
- helft, pinkkant: 9,0 − 2,06 (pennen tot printrand) − 1,0 (spleet) = **5,94 mm** wand;
- numpad, zijkanten: 9,0 − 4,73 − 1,0 = **3,27 mm** wand. Daarom zitten de M3-schroeven van het numpad alleen in de voor- en achterwand.

**Na levering van de connectoren (januari) opmeten en `conn_diepte` aanpassen.** Is de werkelijke diepte kleiner dan ca. 6,1 mm, dan past het niet bij het numpad en moet de numpad-print anders.

## Aannames en open punten
1. Hoogte van Pro Micro en OLED: geschat (OLED-bovenkant ca. 11,5 mm boven de print). Bepaalt kaphoogte en USB-sleuf. Opmeten bij het prototype.
2. Positie van de OLED-module: staand boven de Pro Micro, header onderaan (zoals Lily58). Venster daarop afgestemd.
3. De plaat ligt bovenop de wand; de naad is aan de zijkant zichtbaar. Alternatief later: plaat verzonken in een sponning.
4. De bovenkant van de kap is niet afgerond (afronding mislukte in CadQuery); in Fusion afronden.
5. Linkerhelft (spiegelen), klapvoetjes/tenting (W3), polssteun (W2) nog niet.
6. Fusion: dit model omzetten naar het parametrische Fusion-document (E17/E18), gekoppeld aan de master-schets.

## Controle uitgevoerd
- Doorsneden op printhoogte en plaathoogte naast de printrand, componentposities (uit KiCad) en de footprint van Pro Micro en OLED gelegd: geen botsingen, kap valt 0,5 mm voor de keycap van kolom 1 en 1 mm voor de bovenste duimtoets.
- Eerste versie had een rechterwand aan de kap die de keycap raakte en USB/TRRS-uitsparingen die het dak openzaagden; beide opgelost.
