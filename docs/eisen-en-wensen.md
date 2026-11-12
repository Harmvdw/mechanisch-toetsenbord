# Eisen en wensen – metalen split keyboard (inspiratie: Lily58)

Status: versie 6 (12 nov 2026). E = eis, W = wens. Uitwerking: numpad en print in [12-numpad-en-pcb-route2.md](12-numpad-en-pcb-route2.md), behuizing in [13-behuizing.md](13-behuizing.md).

## Besluiten
- 58 toetsen (Lily58-layout), plus een los numpad in dezelfde stijl
- Numpad: 4 kolommen × 5 rijen = 20 toetsen, alles 1u, hotswap, 19,05 mm toetsafstand
- Numpad heeft geen eigen controller. Het heeft een I2C I/O-expander (MCP23017) en wordt met 4 draden (VCC, GND, SDA, SCL) aan de OLED/I2C-bus van een helft gekoppeld; aan links én rechts aan te sluiten. Er is steeds één numpad tegelijk in gebruik.
- Connector: magnetische pogo-connector 4P, 2,54 mm, haaks (AliExpress, "4P With Ear Curved"); contactvlak-helft op elke toetsenbordhelft, pennen-helft aan beide zijkanten van het numpad. Numpad dokt rechtstreeks tegen de zijkant, zonder kabel.
- Firmware: QMK met custom matrix (bestaande voorbeelden: ergodone, ferris, macropod). Pinnen op de Pro Micro blijven ongewijzigd.
- Geen RGB (niet bestukken); OLED blijft; TRRS tussen de helften blijft
- Bedraad (QMK). Op de print komt een onbestukte batterij-aansluiting met schakelaar als optie voor later draadloos (nRF52840 + ZMK); draadloos is dus niet in deze versie
- PCB-route 2 (eigen aanpassing van de Lily58 Pro): numpad-aansluiting J_NP, batterij-pads, via's vergroot; DRC op elk gewijzigd bestand vóór bestelling
- Lily58-print aan de pinkkant 6 mm breder (ruimte voor J_NP); numpad-print 10 mm breder per zijkant
- Logo's op de print: voorlopig ongewijzigd laten
- Bestukken: kale printen bestellen, zelf solderen
- Behuizing (12 nov): vlak (geen typhoek), OLED achter een venster in een gesloten kap, stevig (wand 7 mm, bodem 4 mm); eerst rechterhelft en numpad
- Materiaal: aluminium (behuizing en plaat)
- Productie: zelf frezen; eerst prototype 3D-printen
- Gebruik: ontworpen voor thuis; reisbaar is een wens
- Budget: €120, exclusief onderdelen die al aanwezig zijn
- Alle werk staat in deze repo, zodat het vanaf elke computer bereikbaar is

## 1. Layout en ergonomie
- E1 Gesplitst: twee losse helften
- E2 Kolom-stagger zoals de Lily58 (6 kolommen × 4 rijen + duimcluster)
- E3 Duimcluster met 5 toetsen per helft, schuin geplaatst
- E4 Toetsafstand 19,05 mm (MX-standaard)
- E5 Linker en rechter helft gespiegeld
- E5b Los numpad (4 × 5, 1u): zelfde materiaal, uitstraling en bevestiging als de helften
- W1 Aantal toetsen aanpasbaar (bijv. 5e rij met cijfers)
- W2 Variabele polssteun (los onderdeel)
- W3 Tenting-voetjes (instelbare hoek)
- W4 Instelbare duimhoek via alternatieve plaat

## 2. Mechanica en schakelaars
- E6 Cherry MX-compatibele switches
- E7 Hotswap, zodat switches te wisselen zijn zonder solderen
- E8 Plaatuitsparing 14,0 × 14,0 mm, tolerantie ±0,05 mm
- E9 Geen stabilizers nodig (geen 2u-toetsen)
- W5 3-pin en 5-pin switches ondersteund
- W6 Plaatdikte instelbaar (1,2 / 1,5 mm), bijv. via afstandsringen
- W7 Geluiddemping (schuim of siliconen laag) in de behuizing

## 3. Materiaal en uitstraling
- E10 Aluminium behuizing en plaat
- E11 Vlak, stabiel, geen doorbuiging bij typen
- E12 Antislip onderkant (rubber voetjes)
- W8 Geanodiseerd, kleur nog te kiezen
- W9 Gravure of logo op zijkant of onderkant
- W11 Gewicht per helft: zwaar en stabiel, maximaal ~600 g

## 4. Elektronica
- E13 Controller met QMK/VIA of Vial-ondersteuning
- E14 USB-C naar de computer
- E15 Verbinding tussen de helften (TRRS of USB-C-kabel)
- E16 Eén PCB per helft, past in de behuizing
- E16b Onbestukte batterij-aansluiting met schakelaar op de print, als optie voor later draadloos (niet bestukt in deze versie)
- E16c Numpad-aansluiting J_NP (4 pads: VCC, GND, SDA, SCL) aan de buitenrand van de helft-print; numpad-print met 20 toetsen, diodes, MCP23017 en twee magnetische connectoren
- E16d Numpad werkt aan beide helften en mag tijdens gebruik los- en vastgekoppeld worden (firmware detecteert dit)
- W12 OLED-schermpje per helft (zoals Lily58)
- W13 Draaiknop (rotary encoder)
- W14 (vervallen) RGB: niet gewenst
- W16 Reset-knop bereikbaar zonder demontage

## 5. Ontwerp in Fusion
- E17 Alle onderdelen volledig parametrisch ontworpen
- E18 Eén master-schets voor toetspositie, zodat wijzigingen overal doorwerken
- E19 Assemblage met stuklijst
- W17 Aparte configuraties per variant (58 toetsen, numpad, andere maten)
- W18 Exports voor productie: DXF (plaat) en STEP (behuizing)

## 6. Productie
- E20 Zelf te frezen (CNC)
- E20b Eerste prototype in 3D-print, daarna pas aluminium
- E21 Plaat uit plaatmateriaal (lasersnijden of waterstralen) of gefreesd
- E22 Minimale radius in hoeken passend bij frees (≥ 1 mm)
- W19 Passingen in 3D-print al representatief voor de frees
- W20 Zo min mogelijk verschillende onderdelen
- W21 Geen speciaal gereedschap nodig

## 7. Montage
- E23 Alles te monteren met standaard inbussleutels
- E24 Schroefverbinding (geen lijm), zodat demontage kan
- W22 Draadinserts of getapte gaten in aluminium
- W23 Snelle montage zonder losse kleine onderdelen

## 8. Doel en randvoorwaarden
- E25 Volledig zelf te maken en te onderhouden
- E26 Kosten maximaal €120, exclusief al aanwezige onderdelen
- W24 Opnieuw te maken door anderen (documentatie, open source)
- W25 Foto's en uitleg voor eigen archief
- W26 Reisbaar: lager, lichter, afgeronde randen, afneembare kabel, hoes

## Open punten
1. Welke onderdelen heb je al? (switches, controllers, PCB's, accu's) Bepaalt of €120 past.
2. Connector opmeten na levering (januari): parameter `conn_diepte` in de behuizing.
3. Eén print voor beide helften of twee verschillende?
4. ERC niet gedaan: het schema is KiCad 5-formaat (.sch) en nog niet omgezet.
5. Hoogte Pro Micro en OLED opmeten bij het prototype (kaphoogte, USB-sleuf).
6. KiCad-bestanden en Gerbers van de werkcomputer naar `pcb/` kopiëren.
