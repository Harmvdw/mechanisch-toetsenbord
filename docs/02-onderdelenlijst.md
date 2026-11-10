# Onderdelenlijsten uit de bronnen

## A. Lily58 Pro (bron: `Pro/Doc/buildguide_en.md`, kata0510)

Voor één compleet toetsenbord (twee helften).

| Onderdeel | Aantal | Opmerking |
|---|---|---|
| Lily58 PCB | 2 | Eén links, één rechts |
| Lily58 case | 1 set (4 stuks) | 2 volle platen, 2 platen met gaten voor switches |
| Pro Micro | 2 | Optioneel met spring pin header |
| Key switches (Cherry MX of Kailh Choc) | 58 | MX en Choc hebben andere connectors |
| Switch sockets | 58 | |
| Diodes 1N4148W | 58 | |
| Keycaps | 58 | 1.5U, 1U mag ook |
| OLED-module | 2 | |
| Tact switch (reset) | 2 | |
| TRRS-jack | 2 | |
| M2 spacers | 10 + 4 | Choc 4 mm, MX 7 mm. De gids legt de aantallen niet duidelijk uit: controleer dit. |
| M2 schroeven | 28 | |
| TRRS-kabel | 1 | 4-polig aanbevolen |
| Micro-USB-kabel | 1 | Magnetische connector aanbevolen |
| Rubberen voetjes | 4 per PCB | Genoemd in de laatste bouwstap |

## B. Blogbouw (bron: vipul.xyz, oktober 2024)

| Onderdeel | Aantal / type | Opmerking |
|---|---|---|
| PCB | 6 stuks (voor 3 keyboards) | Gerber-bestanden uit de repo, besteld bij LionCircuits. Zwart soldeermasker kostte meer dan groen. |
| Arduino Pro Micro | 1 | |
| OLED-module | 1 | Bovenop de Pro Micro |
| Diodes 1N4148W | 58 | |
| Switch sockets | 58 | |
| Switches | Cherry MX Brown | Gebruikt wat al aanwezig was |
| Keycaps | Ortholineair profiel | |
| TRRS-jack en -kabel | 1 + 1 | |
| Tact switch | 1 | Reset |
| M2 spacers en schroeven | aantal niet genoemd | |
| Plaat en behuizing | 3D-print in PLA | Ca. 150 g filament |

Kosten volgens de blog: ca. ₹8300 (ca. $100) voor de hele build. De bron spreekt zichzelf tegen over de PCB-prijs (₹1000 in de tabel, ca. ₹6000 voor zes stuks in de tekst). Gebruik dit getal alleen als grove indicatie.

Aantallen in B gelden voor de bouw van de auteur. Voor twee volledige helften klopt 58 diodes en 58 sockets met lijst A.

## Vergelijking met je eisen

Zie [06-naar-metaal.md](06-naar-metaal.md). Kort: de Lily58-lijsten hebben geen hotswap-sockets in aluminium, geen accu, geen Bluetooth en geen laadcircuit.
