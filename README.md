# Mechanisch toetsenbord (metaal, split, Lily58-geïnspireerd)

Doel: een split keyboard met aluminium behuizing en plaat, zelf ontworpen in Fusion 360 en zelf gefreesd. Inspiratiebron is de Lily58 (58 toetsen, kolom-stagger).

Deze repo bevat alle werk: referentie-informatie, de PCB-scripts, het behuizingsmodel en de documentatie. Alles wordt hier opgeslagen, zodat het vanaf elke computer bereikbaar is.

## Inhoud

| Bestand | Wat staat erin |
|---|---|
| [docs/eisen-en-wensen.md](docs/eisen-en-wensen.md) | Eisen en wensen van dit project (versie 6) |
| [docs/01-lily58-overzicht.md](docs/01-lily58-overzicht.md) | Layout, varianten, verschillen tussen bronnen |
| [docs/02-onderdelenlijst.md](docs/02-onderdelenlijst.md) | Onderdelenlijsten uit de Lily58 Pro-gids en de blogbouw |
| [docs/03-bouwstappen.md](docs/03-bouwstappen.md) | Bouwvolgorde Lily58 Pro, plus de bouwvolgorde van de blog |
| [docs/04-firmware-qmk.md](docs/04-firmware-qmk.md) | QMK-gegevens, make-commando's, flashen |
| [docs/05-lessen-en-problemen.md](docs/05-lessen-en-problemen.md) | Fouten, oplossingen en tips uit de bronnen |
| [docs/06-naar-metaal.md](docs/06-naar-metaal.md) | Wat uit de bronnen telt voor het metalen ontwerp, en wat nog ontbreekt |
| [docs/07-keebs-vipul-repo.md](docs/07-keebs-vipul-repo.md) | Structuur en inhoud van de keebs-repo (PCB, STL's, firmware) |
| [docs/08-printables-handwired-lily58.md](docs/08-printables-handwired-lily58.md) | Handbedraad Lily58 op Printables: onderdelen, matrix, pinnen, licentie |
| [docs/09-maten-uit-stl-en-gerber.md](docs/09-maten-uit-stl-en-gerber.md) | Gemeten maten: toetsraster, stagger, PCB-rand, plaat en case |
| [docs/10-fusion-opzet.md](docs/10-fusion-opzet.md) | Wat er in het Fusion-document staat: schetsen, parameters, koppelingen |
| [docs/11-pcb-route-en-bestelling.md](docs/11-pcb-route-en-bestelling.md) | PCB-route, wat de Pro-print wel en niet heeft, plan voor de bestelling |
| [docs/12-numpad-en-pcb-route2.md](docs/12-numpad-en-pcb-route2.md) | Numpad (MCP23017, I2C), aangepaste Lily58-print, DRC en Gerbers |
| [docs/13-behuizing.md](docs/13-behuizing.md) | Behuizing prototype v0.1: opbouw, maten, aannames |
| [docs/14-behuizing-fusion.md](docs/14-behuizing-fusion.md) | Behuizing parametrisch in Fusion (beide helften): parameters, controle, open punten |
| [behuizing/](behuizing) | Parametrisch model (CadQuery), STEP/STL-exports, controle-afbeeldingen |
| [pcb/scripts/](pcb/scripts) | Scripts die de numpad-print maken en de Lily58-print aanpassen en routeren |
| [data/lily58-pro-printrand.csv](data/lily58-pro-printrand.csv) | Printrand van de Pro-print (120 punten, mm, zelfde oorsprong als de toetsposities) |
| [data/lily58-pro-switchposities.csv](data/lily58-pro-switchposities.csv) | 29 toetsposities per helft in mm, voor een Fusion-schets |
| [tools/](tools) | Scripts waarmee de maten zijn gemeten (STL en drill-bestanden) |
| [docs/bronnen.md](docs/bronnen.md) | Alle links, met per link wat is gelezen en wat niet |

## Status (12 november 2026)

- PCB's (Lily58 route 2 en numpad) gerouteerd, DRC schoon, Gerbers gemaakt. De KiCad-bestanden en Gerber-zips staan nog alleen op de werkcomputer en moeten naar `pcb/`.
- Behuizing prototype v0.1 voor de rechterhelft en het numpad: zie [docs/13-behuizing.md](docs/13-behuizing.md). Klaar om te 3D-printen.
- Behuizing van beide helften staat parametrisch in Fusion: zie [docs/14-behuizing-fusion.md](docs/14-behuizing-fusion.md). Numpad in Fusion volgt. Draaiknop op beide helften staat als referentie in het model; de print moet daarvoor nog worden aangepast.
- Connector (magnetisch) besteld/te bestellen; levering januari. Daarna `conn_diepte` opmeten.
