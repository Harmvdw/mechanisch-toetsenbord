# Numpad en aangepaste Lily58-print (route 2)

Status: 13 november 2026 (draaiknop toegevoegd, §4b). Beide printen zijn gerouteerd, door de DRC en als Gerbers geëxporteerd (op de werkcomputer, zie onderaan). Dit document is de repo-versie van het projectdocument `numpad-ontwerp.md` (versie 5).

## 1. Principe
- Het numpad heeft 20 toetsen (4 × 5, alles 1u, 19,05 mm, MX-hotswap) en een I/O-expander **MCP23017** op de print. Het heeft geen eigen controller.
- De expander scant de numpad-matrix en wordt door de controller van de helft uitgelezen over I2C.
- Verbinding: 4 draden — VCC, GND, SDA, SCL; dezelfde bus als de OLED. Pull-ups R1/R2 (4,7 kΩ) zitten al op elke helft.
- Adres: A0–A2 aan GND → 0x20 (OLED: 0x3C).
- Spanning: VCC van de helft (5 V of 3,3 V); MCP23017 werkt van 1,8 tot 5,5 V.
- Op de numpad-print: U1 MCP23017 (SOIC-28W), C1 100 nF, R1 10 kΩ (RESET naar VCC), 20 diodes (SOD-123), 20 MX-hotswap-voetjes (onderkant), J1/J2.
- **Pennen MCP23017 (voor de firmware):** rij 0 = pen 5 (GPB4), rij 1 = pen 4 (GPB3), rij 2 = pen 3 (GPB2), rij 3 = pen 2 (GPB1), rij 4 = pen 1 (GPB0); kolom 0–3 = pen 21–24 (GPA0–GPA3); 9 VCC; 10, 15, 16, 17 GND; 12 SCL; 13 SDA; 18 nRESET.
- Diodes: kathode (pad 1) aan de rij, toets aan de kolom (zelfde als de Lily58).
- De numpad-print is alleen voor MX en niet omkeerbaar. De 1,7 mm-gaten voor 5-pins switches zitten erin.

## 2. Firmware (QMK)
Custom matrix (`CUSTOM_MATRIX = lite`). Voorbeelden in de QMK-repo: `ktec/ergodone` (driver `mcp23018.c`), `ferris/0_2` (MCP23017 met herstel na I2C-fout), `nek_type_a`, `geistmaschine/macropod` (modulair: detecteert of de module is aangesloten en probeert na 2 s opnieuw).
Opzet: per helft 5 (MCU) + 5 (expander) rijen → `MATRIX_ROWS 20`, `MATRIX_COLS 6`. Beide helften dezelfde code; de helft zonder numpad slaat de expander over. Numpad-rijen twee keer in de keymap (links en rechts). Split blijft serieel over TRRS. Nog niet gebouwd of getest.

## 3. Connector
- Magnetische pogo-connector, 4 pennen, 2,54 mm, haaks. AliExpress, Qing-Tao Store, item 1005008736904631, variant **"4P With Ear Curved"**, ca. €1 per set. **3 sets** (2 nodig), uit dezelfde listing. Levering 3–13 januari 2027.
- Geen maattekening. Footprint generiek: 4 pads op 2,54 mm, gat 1,0 mm. Na ontvangst opmeten; de behuizing gebruikt de parameter `conn_diepte` (zie [13-behuizing.md](13-behuizing.md)).
- Contactvlak-helft op elke toetsenbordhelft (J_NP), pennen-helft op het numpad (J1 links, J2 rechts). Penvolgorde van boven naar beneden: 1 GND, 2 SDA, 3 SCL, 4 VCC.
- Montagezijde (voor gelijke magneetpolariteit): J_NP aan de F.Cu-zijde van de Lily58-print (rechterhelft = bovenkant, linkerhelft = onderkant). Numpad: J1 bovenkant, J2 onderkant.

## 4. Wijzigingen op de Lily58 Pro-print
1. **Printrand aan de pinkkant 6 mm verbreed** (Edge.Cuts-punten met x ≥ 223 mm +6 mm; GND-vlakken mee). Langs de oude rand was geen plek voor 4 pads. Printmaat nu ca. 148,5 × 106,3 mm.
2. **J_NP** op KiCad (229,4; 81,75), ter hoogte van rij 1–2.
3. **Sporen** (0,25 mm, 45°, automatisch gerouteerd met `pcb/scripts/route_lily58.py`): VCC 120 mm, SDA 136 mm (4 via's), SCL 140 mm (5 via's), BAT+ 15 mm, RAW 58 mm. Via's 0,6/0,3 mm.
4. **Batterij, onbestukt**: J_BAT (JST-PH 2-pins) op (87; 78,5), SW_BAT (2 pads) op (87; 93). BAT+ → schakelaar → RAW (U1 pen 24).
5. **RGB**: J1 (LED) niet bestukken.
6. **Via's**: 115 × 0,6 mm, 34 × 0,5 mm rond de Pro Micro (besloten).
7. 58 gaatjes van 0,1 mm verwijderd; nulspoor en 3 stompjes opgeruimd. Logo's ongewijzigd.

## 4b. Draaiknop (EC11) op SW25 — 13 nov 2026
Besluit Harm: draaiknop op beide helften, **combinatie** met een toets (die plek is óf toets óf knop).
- Een hotswap-voet en een encoder passen niet samen op één plek van deze omkeerbare print: de hotswap-pads liggen aan beide kanten van de toets precies waar de encoderpennen komen. Doorgerekend over alle vier draaistanden en tot 0,85 mm verschuiving: minimaal 1,2 mm overlap.
- Daarom is SW25 (binnenste duimtoets, onder de Pro Micro) een **gesoldeerde MX-plek** geworden, omkeerbaar: 4 doorgemetalliseerde gaten ø1,5 mm (pad ø1,8). Hotswap-pads, Choc-gaten en de twee pootjesgaten voor 5-pins switches vervallen op die plek; middengat ø4 blijft. Een 5-pins switch past met afgeknipte pootjes.
- **ENC1** (EC11 met drukknop, maten Alps EC11E / KiCad-bibliotheek) op hetzelfde middelpunt, dus geen verschuiving voor plaat of behuizing:
  - A → F4 (Pro Micro pen 20), C → GND, B → F5 (pen 19);
  - S1/S2 → zelfde netten als de toets (D25 en col5): de drukknop zit op de matrixplek van SW25;
  - lipjes in sleuven zonder koper (2,6 × 1,5 mm); niet solderen, ze klemmen.
  - Speling tot de soldeergaten van de switch: 0,09 mm boven het KiCad-minimum.
- Omkeerbaar: bij de linkerhelft gaat de encoder aan de andere printzijde, 180° gedraaid. A en B wisselen dan; dat is één instelling in de firmware.
- Gemaakt met `pcb/scripts/encoder_lily58.py` (bouwt SW25 om, plaatst ENC1, ruimt oude sporen en via's op, routeert col5, D25-net, F4 en F5 opnieuw en controleert dat elk net één geheel is).
- **Solderen:** op elke helft óf een MX-switch óf een encoder in SW25, nooit beide.

## 5. DRC (KiCad 10, 12 nov 2026)
- **Lily58:** 0 niet-verbonden pads, 0 kortsluitingen, 0 kruisende sporen; geen nieuwe meldingen t.o.v. het originele ontwerp. De 17 afstandsmeldingen komen uit het origineel (13× 0,15–0,16 mm rond de Pro Micro, maakbaar bij PCBWay ≥ 0,127 mm).
- **Lily58 met encoder (13 nov):** 0 niet-verbonden pads, geen nieuwe koper-, gat- of afstandsfouten. Twee nieuwe meldingen "starved thermal": de GND-pen C van de encoder en GND van J_BAT sluiten op de bovenlaag met één spaak op het GND-vlak aan in plaats van twee (elektrisch in orde).
- **Numpad:** 0 niet-verbonden pads, 0 fouten in koper, gaten of afstanden. Alleen cosmetische meldingen.

## 6. Gerbers
Per zip: F_Cu, B_Cu, F/B_Mask, F/B_Silkscreen, Edge_Cuts, PTH.drl, NPTH.drl (Protel-extensies, mm).
- Lily58: omtrek tot x = 231,46 mm. **Versie met encoder: 13 nov** (`pcb/lily58-pro/Lily58_Pro_gerbers.zip`). Gecontroleerd: 2 sleuven 2,6 × 1,5 (lipjes), 4 × ø1,5 (switch), 14 × ø1,0 (o.a. 5 encoderpennen); 2 pootjesgaten en 8 hotswap-gaten minder dan de versie van 12 nov.
- Numpad: 96,2 × 113,75 mm, 6 × M3.

## 7. Scripts in deze repo (`pcb/scripts/`)
| Script | Doet |
|---|---|
| `gen_numpad.py` | Maakt `numpad.kicad_pcb` compleet (footprints, sporen, GND-vlakken). Gebruik: `python3 gen_numpad.py <Lily58_Pro.kicad_pcb> <uitvoer>` (de Lily58-print levert de switch- en diode-footprints). |
| `mod_lily58.py` | Plaatst J_NP, J_BAT, SW_BAT; verwijdert 0,1 mm-gaatjes en stompjes. |
| `route_lily58.py` | Verbreedt de rand, zoekt een plek voor J_NP en routeert VCC/SDA/SCL/BAT+/RAW. |
| `encoder_lily58.py` | Draaiknop: SW25 als gesoldeerde MX-plek, ENC1 erbij, opnieuw routeren (gebruikt de router uit `route_lily58.py`). |

## 8. Bestanden
KiCad-bestanden, DRC-rapporten en Gerber-zips staan sinds 13 nov in [`pcb/`](../pcb) (zie `pcb/README.md`).

## Volgende stappen
1. Bestellen bij PCBWay: beide zips; 2 lagen, 1,6 mm, HASL loodvrij; 5 stuks per print.
2. EC11-encoders bestellen (2 stuks, met drukknop, as 20 mm) en knoppen ø ≤ 19 mm.
2. Firmware: QMK-keyboard met custom matrix voor de MCP23017.
