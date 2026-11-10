# Wat telt voor het metalen ontwerp

Dit bestand koppelt de bronnen aan [eisen-en-wensen.md](eisen-en-wensen.md). Alleen punt 1 en 2 komen uit de bronnen. De rest zijn conclusies uit de vergelijking en zijn gemarkeerd als eigen aandachtspunt.

## 1. Direct overneembaar uit de Lily58

- 58 toetsen, 6×4+5 per helft (E2, E3).
- TRRS tussen de helften (E15).
- Pro Micro met QMK (E13).
- Resetknop (tact switch) per helft (W16).
- OLED per helft (W12).
- Platenopbouw: bovenplaat met switchgaten, bodemplaat, spacers. Spacerhoogte MX 7 mm, Choc 4 mm. De bron noemt de aantallen onduidelijk, dus zelf narekenen.
- Rubberen voetjes onder elke helft (E12).

## 2. Wat de bronnen niet geven

- Plaatuitsparing, tolerantie en plaatdikte: niet opgehaald. Eis E8 uit het project (14,0 × 14,0 mm) is de MX-standaard.
- Toetspositie-coördinaten en schuine duimcluster-hoeken: niet opgehaald. Ze staan in de QMK-map (`info.json`) en in de PCB-bestanden van kata0510 (`Pro/PCB`).
- Afmetingen van de PCB en gaatposities voor schroeven: niet opgehaald.
- Pin-toewijzing en matrix voor de Pro Micro (AVR): niet opgehaald. Voor een RP2040-variant staat de pin-toewijzing in [08-printables-handwired-lily58.md](08-printables-handwired-lily58.md).
- Maten uit de 3D-ontwerpen die de blog noemt: niet opgehaald.

## 3. Eigen aandachtspunten (niet uit de bronnen)

- Hotswap (E7): de Pro-gids gebruikt 58 switch-sockets die op de achterkant van de print worden gesoldeerd. Controleer in de PCB-bestanden (`Pro/PCB`) welk socketlabel en welke voetafdruk daarbij horen, voordat je de plaat daarop ontwerpt.
- Bluetooth en accu (E16b): de Lily58 in de bronnen is bedraad met een Pro Micro. Er staat niets over Bluetooth, accu of laadcircuit. Dat vraagt een andere controller of een andere PCB en wijzigt de ruimte in de behuizing.
- Mechanische plaat in aluminium: de bronnen gebruiken geprinte PLA (blog) en kant-en-klare cases (Pro). De wanddikte en schroefposities zijn dus niet te herleiden uit de bronnen.
- De blog gebruikt plaat- en behuizingsontwerpen van derden (volgens de samenvatting: "serverwentdown/lily58-3d" voor de plaat en "Capsule Deluxe (Manta58)" voor de behuizing, low-profile). Controleer licentie en maten bij de bron voordat je daar iets van overneemt.

## 4. Vervolgstappen om de gaten te vullen

1. `keyboards/lily58/` uit QMK openen en `info.json` ophalen.
2. De mappen `Pro/PCB`, `case` en `pcb` van kata0510 bekijken (Gerber- en maatinformatie).
3. De STL's in `lily58/stls` (keebs) en de bestanden op de Printables-pagina openen om maten af te lezen (zie [07](07-keebs-vipul-repo.md) en [08](08-printables-handwired-lily58.md)).
4. Licentie checken: het Printables-model is GPL v3 met naamsvermelding. De licentie van keebs en van de kata0510-bestanden is niet gelezen.
