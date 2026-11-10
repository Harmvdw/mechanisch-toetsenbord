# PCB-route en bestelling bij PCBWay

Stand van 10 november 2026. Doel: over een week bestellen.

## Bevindingen

1. **De bestaande Lily58 Pro-print (keebs-Gerbers) is bestelklaar.** De zip `lily58/PCB/lily58.zip` heeft 16 bestanden en is identiek aan de map `gerber/`. Het zijn 2 koperlagen, soldeermasker en silkscreen aan beide kanten, plus boorbestanden (PTH en NPTH) en een printrand. Aangemaakt met KiCad 7.0.11 op 11 mei 2024.
2. **Licentie van het ontwerp:** de repo van kata0510 heeft een MIT-licentie (naamsvermelding vereist). Dat staat bijwerken en hergebruik toe. De keebs-repo van vipul-sharma20 bevat alleen Gerbers; de licentie daarvan is niet gelezen.
3. **De originele bronbestanden staan in KiCad 5.1.6-formaat** (`Pro/PCB/Lily58_Pro.kicad_pcb` en `.sch`). Fusion importeert alleen KiCad v7 of hoger. Open de bestanden dus eerst in KiCad 7 of nieuwer en sla ze op als KiCad-project. Dat gaat in KiCad automatisch (bestand openen, opslaan).
4. **`Pro_V2` in dezelfde repo is een ander bord** (KiCad 9): RP2040 op de print, SMD-bestukking, RGB per toets, Choc V2. Dat is niet wat je wilt (handsoldeerbaar, MX, Pro Micro-plek).
5. **Fusion Electronics kan ik via de koppeling alleen lezen.** De API is een preview zonder methoden om onderdelen of sporen aan te maken. Wijzigingen aan de print moet jij in Fusion Electronics doen. Ik kan daarna de ERC- en DRC-meldingen uitlezen.
6. **In deze sessie is geen KiCad** (geen `kicad-cli`, geen `pcbnew`). Ik kan hier dus geen DRC draaien en geen Gerbers genereren. Een nieuwe of gewijzigde print is daarom hier niet te controleren.

## Wat de Pro-print wel en niet heeft (uit de Gerbers)

| Wens | Pro-print |
|---|---|
| 29 toetsen per helft, 19,05 mm | Ja |
| Hotswap (E7) | Ja, socketvoetafdruk op de achterkant (volgens de Pro-gids 58 sockets) |
| MX en Choc | Ja, dubbele pennen-gaten (1,7 mm en 1,9 mm) |
| Eén print voor beide helften | Waarschijnlijk (spiegelbeeld bestukken). De Pro-gids telt 2 prints, de blog suggereert omkeren. Nog uitzoeken in de KiCad-bron. |
| Pro Micro-plek | Ja. RP2040 Pro Micro of nRF52840-module (nice!nano-type) passen fysiek. Pinnen en firmware nog nakijken. |
| Bluetooth, accu, laadschakeling | Niet op de print. De nRF52840-module heeft zelf accu-pads. Een schakelaar komt als losse draad. |
| 8× M3-gaten | Nee. De print heeft 5 grote doorgemetalliseerde boringen (4,7 mm), vermoedelijk M2-montage. |
| USB-C | Via de module op de Pro Micro-plek, niet op de print |

Coördinaten van de grote boringen (Fusion-assen, mm): (−53,6; −68,59), (−29,0; −13,39), (−29,0; −51,39), (47,2; −15,59), (47,2; −53,79). Ze zijn aangeduid als montagegaten maar nog niet bevestigd.

## Instellingen voor de bestelling (uit de bestanden)

| Veld | Waarde |
|---|---|
| Lagen | 2 |
| Afmeting | 142,52 × 106,33 mm (13.077 mm²) |
| Printdikte | 1,6 mm (waarde uit het KiCad 5-ontwerp, niet uit de Gerbers) |
| Aantal | 5 (PCBWay-minimum is typisch 5, nog te bevestigen bij de bestelling) |
| Kleinste boring | 0,3 mm (PTH) |
| Soldeermasker | groen is goedkoper dan zwart (ervaring uit de blog) |

Niet gemeten: kleinste spoorbreedte, kleinste afstand en ringbreedte. Laat PCBWay die bij de upload controleren.

## Plan voor de komende week

| Stap | Wie | Wat |
|---|---|---|
| 1 | Jij | `Lily58_Pro.kicad_pcb` en `.sch` openen in KiCad 7+, opslaan als nieuw project |
| 2 | Jij | In Fusion: Data Panel → Upload → KiCad-project (Sheets translation). Resultaat controleren. |
| 3 | Ik | Fusion Electronics uitlezen: onderdelen, afmetingen, ERC en DRC, de 5 montagegaten |
| 4 | Samen | Kiezen: Pro-print ongewijzigd bestellen, of aanpassen (M3, batterijconnector) |
| 5 | Jij | Gerbers uit Fusion of KiCad exporteren, bij PCBWay uploaden |
| 6 | Ik | Plaat en case afmaken rond de gekozen print |

Als stap 1 of 2 niet lukt, is bestellen met de bestaande Gerbers uit keebs (`lily58.zip`) de veilige terugvaloptie. Dan bepaalt de Pro-print de montagegaten, en komen de 8 M3-schroeven in een rand van de plaat buiten de printrand.

## Plaat en M3 (voorstel)

- Plaat en case gebruiken de printrand uit `data/lily58-pro-printrand.csv` als basis. In Fusion staat die als schets "PCB omtrek (Lily58 Pro)" (120 punten, 13.077 mm²).
- 8× M3 per helft in een rand buiten de printrand (gaten 3,2 mm, minimaal 2 mm materiaal naast het gat). Daardoor is de PCB-keuze onafhankelijk van de schroeven.
- Nog niet gedaan: breedte van die rand, wanddikte van de case en de positie van de 8 gaten.
