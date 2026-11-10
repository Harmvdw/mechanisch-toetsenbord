# Maten uit de STL's en Gerber-bestanden (keebs-repo)

Gemeten op 10 november 2026 uit de bestanden in https://github.com/vipul-sharma20/keebs, map `lily58/`. De scripts staan in [../tools](../tools). De toetsposities staan als CSV in [../data/lily58-pro-switchposities.csv](../data/lily58-pro-switchposities.csv).

Dit zijn gemeten waarden uit bestanden, niet uit een tekening met maatvoering. Controleer kritieke maten in Fusion voordat je iets freest.

## 1. PCB (Gerber, `lily58/PCB/gerber`)

- Projectnaam in de bestanden: `Lily58_Pro`, KiCad 7.0.11, aangemaakt 11 mei 2024.
- Eén PCB heeft 29 middengaten van 4,0 mm (het MX-middengat), dus één helft. De Pro-gids telt 2 prints (links en rechts). De blog suggereert dat dezelfde print voor beide helften dient, omgekeerd bestukt. Welke van de twee klopt, is niet uitgezocht.
- Afmeting printrand: ca. 142,5 × 106,3 mm. Dit komt uit de eindpunten van de lijnstukken in `Edge_Cuts`. Bogen kunnen de echte rand iets verder uitbuigen.
- Eenheden: millimeter. Coördinaten staan in het Gerber-assenstelsel (y omhoog), de oorsprong ligt willekeurig.

### Toetsraster

29 toetsen per helft: 24 in een 6×4-raster met kolom-stagger en 5 daarbuiten (de duimtoetsen).

| Eigenschap | Gemeten |
|---|---|
| Toetsafstand | 19,05 mm (gemeten tussen 18,9 en 19,13 mm; de afwijking komt van afronding op 2 decimalen) |
| Kolomposities x (links naar rechts) | 120,5 / 139,5 / 158,6 / 177,6 / 196,7 / 215,7 mm |
| Bovenste toets per kolom, y | −50,0 / −47,6 / −46,2 / −47,6 / −52,4 / −53,9 mm |
| Stagger t.o.v. kolom 3 (hoger = 0) | 3,8 / 1,4 / 0 / 1,4 / 6,2 / 7,7 mm lager |
| Duimtoetsen (x, y) | (101,4; −97,5), (105,0; −127,0), (130,0; −126,0), (149,0; −123,75), (168,1; −123,75) |

De duimtoetsen zitten onder kolom 1 t/m 3 en steken links uit. Daaruit volgt dat kolom 1 de binnenste kolom is. Dat is een afleiding uit de geometrie, geen vermelding in de bestanden.

De draaiing is bepaald uit de posities van de 1,7 mm- en 1,9 mm-gaten rond elke toets (de pennen van de switch). Beide gatgroepen geven dezelfde hoek. 28 van de 29 toetsen staan recht (0°). Alleen de toets op (105,0; −127,0) is gedraaid: de pennen staan onder 120°, dus de vierkante uitsparing staat 30° tegen de klok in gedraaid (zie `tools/angles.py`).

### Boringen

| Bestand | Diameter (mm) | Aantal |
|---|---|---|
| NPTH | 0,1 | 58 |
| NPTH | 1,2 | 4 |
| NPTH | 1,7 | 58 |
| NPTH | 1,9 | 58 |
| NPTH | 3,0 | 232 |
| NPTH | 4,0 | 29 |
| PTH | 0,3 | 149 |
| PTH | 0,4 | 58 |
| PTH | 0,81 | 58 |
| PTH | 1,0 | 3 |
| PTH | 1,3 | 2 |
| PTH | 2,4 | 2 |
| PTH | 4,7 | 5 |

Alleen de 4,0 mm-gaten (29, het MX-middengat) heb ik gekoppeld aan toetsposities. Wat de andere gatgroepen zijn (schroefgaten, pinnen van de controller, socketpennen) is niet uitgezocht. De drill-bestanden staan in inches. Ik heb ze omgerekend naar mm en afgerond.

## 2. Plaat en behuizing (STL)

De STL-bestanden zijn binair. Het formaat vermeldt geen eenheid. Ik ga uit van mm, omdat de plaat past bij de PCB-maten.

| Bestand | Breedte (x) | Diepte (y) | Hoogte (z) | z-bereik |
|---|---|---|---|---|
| `case.stl` | 150,5 mm | 114,0 mm | 23,0 mm | 0 tot 23,0 |
| `lily58plate.stl` | 145,1 mm | 108,7 mm | 6,5 mm | −1,51 tot 5,04 |

- `case.stl` is ca. 8 mm breder en 8 mm dieper dan de PCB. Dat past bij één helft met een wand rond de print. Dat het één helft is, volgt uit dit maatverschil, niet uit een bestandsbeschrijving.
- De 23 mm hoogte van de case en de opbouw van de plaat in z (de plaat heeft meerdere niveaus tussen −1,51 en 5,04) zijn niet verder uitgezocht.
- Wanddikte, schroefposities en de uitsparingen voor USB en TRRS zijn niet gemeten.

## 3. Wat dit betekent voor je eisen

- E3 (duimcluster schuin geplaatst): in dit ontwerp is maar één van de 5 duimtoetsen gedraaid (30°). Of je dat zo wilt, of meer toetsen schuin, is een ontwerpkeuze.
- E4 (19,05 mm toetsafstand) klopt met het raster van het Lily58 Pro-ontwerp.
- E2 en E3 (6 kolommen × 4 rijen + 5 duimtoetsen): bevestigd, 24 + 5 per helft.
- De stagger-waarden in de tabel kun je als startpunt gebruiken voor de master-schets (E18). Het totaal is dan 29 punten per helft, met de CSV als invoer.
- De plaat uit de repo is bedoeld voor 3D-printen. Voor een gefreesde aluminium plaat (E8: 14,0 × 14,0 mm uitsparing) moet je de plaatdikte en schroefposities zelf bepalen.

## 4. Nog niet gemeten

- Exacte positie van de schroefgaten (uit `NPTH`-gaten van 3,0 mm of uit de plaat).
- Binnenmaten van de case: wanddikte, bodemdikte, bevestigingsdomen.
- Afmetingen van de controller-uitsparing.
