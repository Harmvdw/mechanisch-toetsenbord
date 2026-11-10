# Lily58: overzicht

## Wat het is

- Split toetsenbord met kolom-stagger.
- Ontwerper en QMK-onderhouder: Naoki Katahira (GitHub: kata0510).
- Hardware (PCB en case) staat in https://github.com/kata0510/Lily58
- Documentatiesite: https://kata0510.github.io/Lily58-Document/
- Controller: Pro Micro, per helft één.

## Aantal toetsen

- QMK-readme: 6×4+5 toetsen per helft, dus 2 × (24 + 5) = 58 toetsen.
- README van kata0510: "6×4+4keys". Dit past niet bij 58 toetsen. Ga uit van 6×4+5 (QMK en bouwgids tellen 58 switches).

## Varianten in de repo van kata0510

Mappen in de root: `Lite/Doc`, `Lite_Rev3`, `Pro`, `Pro_V2`, `case`, `doc`, `pcb`.

| Variant | PCB-data | Bouwgids |
|---|---|---|
| Lily58 Pro | `Pro/PCB` | EN: `Pro/Doc/buildguide_en.md`, IT: `Pro/Doc/buildguide_it.md`, JP: https://kata0510.github.io/Lily58-Document/Lily58_Pro_BG/ |
| Lily58 Lite Rev2 | niet genoemd in de README | Video: https://www.youtube.com/watch?v=t6HLQvqlsVM, info: https://kata0510.github.io/Lily58-Document/Lily58_Lite_Rev2_help.md |
| Lily58 (oud) | `pcb` | https://kata0510.github.io/Lily58-Document/Lily58_BG/ |
| Lily58 Lite Rev1 (oud) | `pcb` | https://kata0510.github.io/Lily58-Document/Lily58_Lite_BG/ |

De mappen `Lite_Rev3` en `Pro_V2` staan niet in de README. Wat erin zit is niet bekeken.

## Switch-ondersteuning

De Pro-gids noemt Cherry MX en Kailh Choc. Die hebben verschillende connectors.

## Verbinding tussen de helften

- TRRS-kabel (4-polig aanbevolen), TRRS-jack op elke helft.
- Eén helft krijgt de USB-verbinding naar de computer. Bij de standaard keymap is dat de linkerhelft.

## Display

OLED-module per helft (de Pro-gids telt 2).
