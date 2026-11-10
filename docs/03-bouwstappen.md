# Bouwstappen

## A. Lily58 Pro (bron: `Pro/Doc/buildguide_en.md`)

1. **Diodes (achterkant).** Draad van de diode wijst naar het pijlsymbool op de print. Eén pad voorsolderen, diode met pincet plaatsen, één kant vastsolderen, dan de andere kant. Daarna alle verbindingen en de polariteit met een multimeter controleren.
2. **Sockets (achterkant, zelfde kant als de diodes).** Eén pad voorsolderen, socket plaatsen en vasthouden met pincet, dan beide pads solderen. Controleren op speling. Bij Choc komt de socket aan de onderkant (de gids toont een MX-socket).
3. **TRRS-jack en resetknop (voorkant, kant met sticker).** Tijdelijk vastzetten met maskeertape, print omdraaien, pinnen solderen met de onderdelen strak tegen de print.
4. **OLED (voorkant).** Genoeg soldeer op de vier jumperpads in het Pro Micro-gedeelte. OLED-connector plaatsen zoals de TRRS-jack. Niet te veel soldeer: dat loopt in de connector. OLED-pinnen in de socket, module bevestigen, vier pinnen solderen.
5. **Pro Micro.** De meegeleverde pin header niet gebruiken. Bij Yushakobo-kits zit een spring pin header bij. Solderen volgens de Helix-bouwgids en op de print zetten. De aansluitingen verschillen tussen linker- en rechterhelft.
6. **Spacers bij de Pro Micro.** Vier ronde spacers van 10 mm. Schroef van de achterkant erdoor, spacer van boven vastdraaien. Daarna de maskeertape weghalen.
7. **Switches.** Spacers van de bovenplaat plaatsen (MX 7 mm, Choc 4 mm). Eerst vier switches in de plaat, dan in de print om alles uit te lijnen. Pinnen op kromming controleren. Van het midden naar buiten werken. Na het monteren van de plaat de switches nog eens aandrukken.
8. **Beschermacryl Pro Micro.** Folie eraf, acryl op de print. De bredere kant naar buiten. Vastschroeven.
9. **Firmware flashen.** Zie [04-firmware-qmk.md](04-firmware-qmk.md). Elke helft apart.
10. **Test en afwerking.** Helften verbinden met de TRRS-kabel, micro-USB op de Pro Micro van de linkerhelft (standaard keymap), alle toetsen testen. Vier rubberen voetjes onder elke print.

## B. Bouwvolgorde van de blog (bron: vipul.xyz)

1. PCB laten maken.
2. Diodes solderen.
3. Sockets solderen. Beide helften moeten spiegelbeeldig. De auteur solderde per abuis beide als rechterhelft en moest alles ontsolderen.
4. Pro Micro, TRRS-jack en resetknop solderen.
5. Plaat printen en switches plaatsen.
6. Firmware flashen vóór de keycaps.
7. Testen.
8. Keycaps plaatsen.
9. Behuizing printen.
10. Eindmontage.

## Verschil tussen A en B

A zet de switches vóór het flashen. B flasht eerst en plaatst de keycaps daarna. Het advies uit B is om vóór de keycaps te testen, zodat je soldeerfouten vindt zonder alles te demonteren.
