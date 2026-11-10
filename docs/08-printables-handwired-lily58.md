# Printables: Handwired Lily58 (Person20020)

https://www.printables.com/model/1321348-handwired-lily58

Case en plaat voor een handbedraad Lily58 (zonder PCB). Laatst bijgewerkt 10 juni 2025. Gelezen via de browser op 10 november 2026.

## Licentie

GNU General Public License v3.0. Op de pagina staat: delen zonder naamsvermelding is niet toegestaan, remixen en commercieel gebruik mogen, en delen moet onder dezelfde licentie. Het model is door de auteur als eigen origineel gemarkeerd. Verwijst voor het originele ontwerp naar de Lily58-repo.

## Aanpak van de auteur

- Controller: RP2040 Pro Micro (twee stuks, één per helft).
- Verbinding tussen de helften: DuPont-connectors in plaats van TRRS, omdat die bij loskoppelen niet kortsluiten. Eén middelste pin is geblokkeerd met een polariserende pinplug (https://www.printables.com/model/242297-dupont-polarizing-pin-plug), zodat de stekker niet omgekeerd past. De auteur raadt aan het toetsenbord toch los te koppelen bij het verbinden van de helften.
- Interconnect-kabel van 1 m. In de case zit de vrouwelijke kant van de connector, in de kabel de mannelijke. De connectors zijn met hete lijm vastgezet.

## Onderdelenlijst (zoals op de pagina)

| Onderdeel | Aantal | Opmerking |
|---|---|---|
| RP2040 Pro Micro | 2 | |
| 1N4148-diodes | 68 | Zie de opmerking onder de tabel |
| MX-switches | 68 | Auteur: Akko Lavender Purple (doos van 45) |
| MX-keycaps | 68 | 66 × 1u, 2 × 1,5u. Geprinte caps van Joe Scotto (ScottoCaps) genoemd |
| Blanke massieve koperdraad | – | Voor de matrix |
| Krimpkous | – | Isoleert de massieve draad op kruisingen |
| Soepele draad | – | Naar de controller. Auteur gebruikte draad uit een ethernetkabel. |
| M2 × 8 mm afstandhouders | 10 | |
| M2 × 6 mm bouten | 20 | |
| 4-pin DuPont-behuizingen | 4 | Alleen bij zelf krimpen |
| Mannelijke DuPont-krimppennen | 6 | Alleen bij zelf krimpen |
| Vrouwelijke DuPont-krimppennen | 6 | Alleen bij zelf krimpen |

Een Lily58 heeft 58 toetsen. De lijst noemt 68 voor diodes, switches en keycaps. Het schema op dezelfde pagina toont 29 switches per helft (SW1 t/m SW29, rijen van 6, 6, 6, 6 en 5), dus 58 in totaal. Reken met 58 plus eventueel reserve, tenzij je de auteur bevestigt dat er een reden voor 68 is.

## Matrix en pinnen (RP2040)

| Signaal | Pinnen |
|---|---|
| Kolommen, van buiten naar binnen | GP27, GP26, GP22, GP20, GP23, GP21 |
| Rijen, van boven naar onder | GP5, GP6, GP7, GP8, GP9 |
| Interconnect | GP1, GND, +5V |

Beide helften zijn elkaars spiegelbeeld. Dat geldt ook voor de kolomvolgorde: "van buiten naar binnen" is op de rechterhelft de andere kant op. De 5 rijen horen bij 4 toetsrijen plus de duimrij. Het schema staat op de pagina als afbeelding. De auteur verwijst voor de bedrading naar een video (link op de pagina).

## Bouw

- Na het printen van case en plaat: snij met een mes de "sacrificial bridging" in de schroefgaten door.
- Firmware: de standaard Lily58-firmware uit QMK, aangepast. Voor een RP2040 pas je de pinnen aan, zet je de processor en bootloader op RP2040 en schakel je de extra's (scherm, LED's) uit. De auteur gebruikt een eigen keymap (Colemak) en extra mediatoetsen.
- Alternatief: KMK POG, waarmee je het toetsenbord grafisch instelt.

## Niet gelezen

Het tabblad Files (4 bestanden), de opmerkingen en de links naar het originele GitHub-repo en de bedradingsvideo. Plaatdikte, schroefposities en printinstellingen zijn niet bekeken.
