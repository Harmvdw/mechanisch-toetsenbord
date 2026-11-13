# Printen (KiCad 10)

| Map | Inhoud |
|---|---|
| `lily58-pro/` | Aangepaste Lily58 Pro-print (route 2): `Lily58_Pro.kicad_pcb` + `.kicad_pro`, eigen footprintbibliotheek, laatste DRC-rapport, **Gerbers voor de bestelling** (`Lily58_Pro_gerbers.zip`, 12 nov). |
| `lily58-pro/origineel/` | Uitgangspunt: Lily58 Pro van kata0510 (KiCad 5-schema, netlijst) en het bord zoals het in KiCad 10 werd geopend, plus het eerste DRC-rapport (1093 meldingen). |
| `numpad/` | Numpad-print v0.4 met draaiknop (gegenereerd door `scripts/gen_numpad.py`, **nog niet door de DRC, nog geen Gerbers**). DRC-rapport en Gerbers van v0.3 (zonder draaiknop, niet meer bestellen). |
| `scripts/` | Scripts die de numpad-print maken en de Lily58-print aanpassen en routeren. |

Uitleg en DRC-resultaten: [docs/12-numpad-en-pcb-route2.md](../docs/12-numpad-en-pcb-route2.md).

Openen in KiCad: de footprintbibliotheek `Lily58_Pro-footprint.pretty` staat naast het bord, maar is in KiCad niet als bibliotheek geregistreerd (DRC meldt `lib_footprint_issues`). Voor het bord zelf is dat niet nodig.

Licentie Lily58: MIT (kata0510).
