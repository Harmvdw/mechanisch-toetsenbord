# Printen (KiCad 10)

| Map | Inhoud |
|---|---|
| `lily58-pro/` | Aangepaste Lily58 Pro-print (route 2): `Lily58_Pro.kicad_pcb` + `.kicad_pro`, eigen footprintbibliotheek, laatste DRC-rapport, **Gerbers voor de bestelling** (`Lily58_Pro_gerbers.zip`, 13 nov, met draaiknop). `Lily58_Pro_uit_gerbers.step`: de print als 3D-model, gemaakt uit die Gerbers (printrand × 1,6 mm met alle gaten en sleuven), in het master-assenstelsel van de behuizing (print op z 7,5–9,1 mm). |
| `lily58-pro/origineel/` | Uitgangspunt: Lily58 Pro van kata0510 (KiCad 5-schema, netlijst) en het bord zoals het in KiCad 10 werd geopend, plus het eerste DRC-rapport (1093 meldingen). |
| `numpad/` | Numpad-print v0.4 met draaiknop (gegenereerd door `scripts/gen_numpad.py`), DRC-rapport `numpad_DRC.rpt` en **Gerbers voor de bestelling** (`numpad_gerbers_v0.4.zip`, 16 nov). De zip van v0.3 (zonder draaiknop) niet meer bestellen. |
| `scripts/` | Scripts die de numpad-print maken en de Lily58-print aanpassen en routeren; `gerber_naar_step.py` maakt een STEP uit Gerbers. |

STEP opnieuw maken (Lily58-helft, master-assenstelsel):

```
python3 pcb/scripts/gerber_naar_step.py pcb/lily58-pro/Lily58_Pro_gerbers.zip pcb/lily58-pro/Lily58_Pro_uit_gerbers.step --dx -158.6 --dy 46.21 --z0 7.5
```

Met `--koper` komen de koperlagen erbij; het bestand wordt dan ca. 140 MB.

Uitleg en DRC-resultaten: [docs/12-numpad-en-pcb-route2.md](../docs/12-numpad-en-pcb-route2.md).

Openen in KiCad: de footprintbibliotheek `Lily58_Pro-footprint.pretty` staat naast het bord, maar is in KiCad niet als bibliotheek geregistreerd (DRC meldt `lib_footprint_issues`). Voor het bord zelf is dat niet nodig.

Licentie Lily58: MIT (kata0510).
