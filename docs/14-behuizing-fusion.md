# Behuizing in Fusion — parametrisch (v0.4)

Status: 12 november 2026. De behuizing uit [13-behuizing.md](13-behuizing.md) staat nu parametrisch in het Fusion-document **"Opzet 1-0-0"** (map Toetsenbord): rechterhelft gemodelleerd, linkerhelft als spiegeling. Het numpad staat nog niet in Fusion.

Het document is opgeslagen in Fusion (12 nov, 22:20, na v0.4).

Opbouwscript: [`behuizing/fusion/opbouw_helften.py`](../behuizing/fusion/opbouw_helften.py). Het verwijdert alles na de schets "PCB omtrek" en bouwt de tijdlijn opnieuw op (stap 0 t/m 6).

![Beide helften](../behuizing/afbeeldingen/fusion_beide_helften.png)

## Wat er in het document staat

| Component | Massa (alu 6061) |
|---|---|
| Bak rechts / Bak links | 265,4 g |
| Plaat rechts / Plaat links | 41,5 g |
| Kap rechts / Kap links | 19,3 g |
| Print rechts (referentie, 1,6 mm) | — |

Per helft 326,2 g aluminium (CadQuery v0.1: 328 g). Tijdlijn: 65 stappen, alles gezond. Alle nieuwe schetsen zijn volledig bepaald.

## Gebruikersparameters

Naast `uitsparing` en `duimhoek`:

| Naam | Waarde | Doel |
|---|---|---|
| `plaat_dikte` | 1,5 mm | W6 |
| `pcb_dikte` / `pcb_plaat` / `vrij_onder` | 1,6 / 5 / 3,5 mm | hoogte-opbouw |
| `bodem` / `wand` / `spleet` | 4 / 7 / 1 mm | bak |
| `conn_diepte` | 9 mm | **schatting**, opmeten na levering connector |
| `jnp_rand` | 2,06 mm | pennenrij J_NP tot printrand |
| `r_buiten` / `r_binnen` | 3 / 1,5 mm | afrondingen (E22) |
| `kap_hoogte` / `kap_dak` | 10 / 2 mm | kap |
| `keycap` | 18 mm | bepaalt de rand van de kap |
| `m3_gat` / `m3_vrij` / `m2_gat` / `bus_d` | 2,5 / 3,4 / 1,6 / 5 mm | schroeven en steunbussen |
| `voet_d` / `voet_diepte` | 10 / 1 mm | rubbervoetjes |
| `helft_afstand` | 40 mm | ruimte tussen de helften in het model |

Afgeleid: `z_pcb_onder`, `z_pcb_boven`, `z_plaat_boven`, `z_wand`, `wand_pink` (= `conn_diepte − jnp_rand − spleet` = 5,94 mm).

## Wijzigingen ten opzichte van v0.1 (CadQuery)

1. **Printrand als 24 lijnen en 5 bogen** in plaats van 120 lijnstukjes, en 6 mm breder aan de pinkkant (route 2). Oppervlak 13.552,5 mm². Grootste afwijking van de Gerber-punten: 0,02 mm (boogje bij de duimpunt). Gevolg: gladde wanden (bak 128 vlakken) en een model dat heel blijft als `wand` of `conn_diepte` verandert.
2. **Plaat: USB en TRRS zijn één sleuf.** In v0.1 bleef tussen de twee uitsparingen een los stukje plaat van 3,1 × 8 mm staan (37 mm³), dat nergens aan vastzat.
3. **Bovenrand van de kap afgerond** (0,8 mm); dat lukte in CadQuery niet.
4. Buitenhoeken: de offset maakt aan de twee scherpe printhoeken rechtsboven een verstek in plaats van een boog. De twee holle hoeken van de buitencontour zijn afgerond met `r_binnen`, de twee hoeken van het connectorvlak met `r_buiten`.

## Controle (v0.2)

- Volume per deel tegenover CadQuery v0.1: bak 98.371 / 98.356 mm³, plaat 15.361 / 15.359 mm³ (v0.1 zonder het losse stukje), kap 7.554 / 7.579 mm³ (verschil door de afronding).
- Botsingscontrole bak, plaat, kap, print: 0 botsingen. Print ligt op de steunbussen; print tot plaat 3,5 mm.
- Parametertest (waarde gewijzigd, tijdlijn gecontroleerd, teruggezet): `conn_diepte` 6,5 / 8 / 10 mm, `wand` 8 mm, `spleet` 0,5 mm, `plaat_dikte` 1,2 mm, `bodem` 3 mm, `kap_hoogte` 12 mm, `duimhoek` 20°: alles gezond.
- `wand` 6 mm: alleen "Afronding bovenrand kap" faalt (de verzonken M3-kop van 6 mm past niet meer in de wand).
- `conn_diepte` boven 10,06 mm: het connectorvlak valt dan buiten de buitencontour; dan moet `wand` omhoog.

## v0.3: drie punten opgelost (12 nov, keuze Harm)

1. **Resetgat is een sleuf** van 3,5 mm breed, van het gat tot de bovenkant van de wand; de plaat sluit hem af. Het dunne randje van 0,25 mm is weg.
2. **USB en TRRS: één opening** in bak en kap (23,1 mm breed); het pilaartje van 3,1 mm is weg. Onder de TRRS loopt de opening 1,5 mm dieper door, zoals eerst.
3. **M2 in de kap: verzinking 90°** (ø4,0 aan het oppervlak, voor verzonken schroeven) in plaats van een verzonken cilinderkop ø4,4. Afstand tot de rand van de kap aan het oppervlak 0,5 mm, daaronder snel meer.

Na de wijziging: tijdlijn gezond, bak 98.291 mm³, kap 7.142 mm³, plaat ongewijzigd.

## v0.4: draaiknop (12 nov, besluit Harm: op beide helften, indrukbaar)

De knop komt op de plek van de binnenste toets, direct onder de Pro Micro (masterpunt −57,2; −51,29), zoals bij de Lily58L. Per helft 28 toetsen en één knop. In Fusion staat hij als referentie-onderdeel ("Draaiknop rechts/links (referentie)"): huis 12 × 12 × 6,5 mm, as ø6 tot 20 mm boven de print, knop ø15 × 13 mm, 2 mm boven de plaat. **Deze maten zijn aannames voor een EC11; aanpassen zodra het onderdeel gekozen is** (parameters `enc_*` en `knop_*`).

Controle: 0 botsingen; knop tot kap 2,5 mm; huis tot plaatuitsparing 1,0 mm rondom; bovenkant knop 5 mm boven de kap. De plaat hoeft niet te veranderen (uitsparing 14 × 14 mm). Knop maximaal ø19 mm.

**Print aangepast op 13 nov** (zie Nog te doen). Oorspronkelijke notitie: Nodig: EC11-footprint op die toetspositie, draaisignalen naar twee vrije pennen van de Pro Micro (F4 en F5 zijn vrij), drukfunctie op de matrixplek van die toets. Nog na te kijken in de KiCad-bestanden van de Lily58L: exacte footprint en pennen, en of de hotswap-voet op die plek kan blijven.

## Blijft staan

- De M3-posities zijn gekoppeld aan de hartlijn van de wand, maar de verdeling langs de wand is vast (uit `behuizing.py`).
- `wand` 6 mm: de verzonken M3-kop van 6 mm past dan niet meer in de wand van de kap.

## Nog te doen

- ~~Print aanpassen voor de draaiknop~~ gedaan op 13 nov: zie [12-numpad-en-pcb-route2.md §4b](12-numpad-en-pcb-route2.md). De encoder staat precies op het hart van de toets (geen verschuiving); de referentie in Fusion klopt daarmee. Pennen: A/C/B op 7 mm links van het hart, S1/S2 op 7,5 mm rechts, lipjes op ±5,6 mm.

- STEP/STL uit Fusion exporteren naar `behuizing/export/`.
- ~~Numpad in Fusion (bak en plaat)~~ gedaan op 16 nov, zie onderaan. Het document is nog **niet opgeslagen**.
- Stuklijst met schroeven, afstandsbussen en voetjes (E19).
- Na levering van de connector: `conn_diepte` aanpassen.

## Controle 16 nov: draaiknop in Fusion tegenover de print
Uitgelezen uit "Opzet 1-0-0" versie 6 (alleen lezen, niets gewijzigd). Het document staat in hub **maz1** (Admin Project, map Toetsenbord); in hub testteam is het niet te vinden.
- SW25/ENC1 op de print: KiCad (101,4; 97,5) = master (−57,2; −51,29).
- Draaiknop rechts in Fusion: midden (−57,2; −51,29), onderkant op z = 9,1 (bovenkant print). **Gelijk.**
- Draaiknop links: (−150,124; −51,29); spiegelvlak x = −103,662, hetzelfde vlak als bak en plaat links. **Gelijk.**
- Plaat rechts heeft op die plek de uitsparing 14 × 14 mm.


## Numpad in Fusion (16 nov)

Script: [`behuizing/fusion/opbouw_numpad.py`](../behuizing/fusion/opbouw_numpad.py) (stappen n0 t/m n5). Het bouwt verder op het document met de helften en verwijdert eerst alles waarvan de naam met "Numpad" begint. Opslaan vanuit de koppeling is op 16 nov twee keer geprobeerd en niet gelukt (versie blijft 6; de actieve hub is testteam, het document staat in maz1). Harm heeft het daarna zelf opgeslagen als **Opzet 1-0-1** in hub **testteam**, project Intern, map Harm. Opzet 1-0-0 versie 6 is de stand zonder numpad.

![Helften en numpad](../behuizing/afbeeldingen/fusion_met_numpad.png)
![Bovenaanzicht](../behuizing/afbeeldingen/fusion_met_numpad_boven.png)

Onderdelen (componenten): Bak numpad, Plaat numpad, Print numpad (referentie), Draaiknop numpad (referentie).

| Gegeven | Waarde |
|---|---|
| Buitenmaat | 104,75 × 148,75 × 14,1 mm |
| Bak / plaat (alu 6061) | 220 g / 46 g, samen 266 g (gelijk aan `behuizing.py`) |
| Zijwand | 3,275 mm (volgt uit `conn_diepte`) |
| Plaats in het model | toets (0,0) op (`np_x`; `np_y`) = (143,6; 2,56) |

Nieuwe parameters:

| Naam | Waarde | Betekenis |
|---|---|---|
| `np_steek` | 19,05 mm | steek van de toetsen |
| `numpad_afstand` | 40 mm | ruimte tussen rechterhelft en numpad, alleen weergave; 0 = aangekoppeld |
| `np_x` | 70,8 mm + 2 · conn_diepte + numpad_afstand + 14,8 mm | afgeleid |
| `np_y` | 2,56 mm | connector van de numpad op de hoogte van J_NP |
| `np_bus_d` | 6 mm | steunbus onder de print (M3) |
| `np_conn_b` | 25 mm | breedte uitsparing connector |
| `np_m3_rand` | 12 mm | buitenste M3 tot de zijkant |
| `np_m3_diepte` | 8 mm | diepte tapgat M3 in de wand |

Bestaande parameters die de numpad ook gebruikt: `wand`, `spleet`, `bodem`, `vrij_onder`, `plaat_dikte`, `conn_diepte`, `uitsparing`, `r_buiten`, `r_binnen`, `m3_gat`, `m3_vrij`, `voet_d`, `voet_diepte`, `enc_*`, `knop_*`.

Opbouw:
- Schets "Numpad basis": oorsprong, printrand 96,2 × 132,75 mm, 6 steunbussen, 2 connectoren, draaiknop. Alle andere schetsen hangen hieraan; alle 11 schetsen zijn volledig bepaald.
- Bak: buitencontour, holte (print + `spleet`), 6 steunbussen ø6 met M3, uitsparing connector in beide zijwanden, 8 × M3 in voor- en achterwand, 4 verdiepingen voor voetjes.
- Plaat: 20 uitsparingen 14 × 14 mm (één uitsparing + patroon 4 × 5), uitsparing draaiknop, 8 × M3 doorgaand.

Controle (waarden gewijzigd en weer teruggezet):
- `numpad_afstand` = 0: numpad sluit aan op de rechterhelft (x = 79,8), 0 botsingen, tijdlijn gezond.
- `conn_diepte` 6 t/m 10,05 mm: alles gezond (helften en numpad). Bij 5 mm is de zijwand van de numpad nog 0,3 mm en gaat het fout.
- `conn_diepte` boven 10,06 mm: "Afronding pinkkant Bak" en "Afronding pinkkant Plaat" geven een fout. Oorzaak: de buitencontour van de helft is printrand + `spleet` + `wand` (x = 80,86) en wordt aan de pinkkant afgesneden op het contactvlak (x = 70,8 + `conn_diepte`). Boven 10,06 mm (= `wand` + `spleet` + `jnp_rand`) ligt het contactvlak buiten de contour en valt er niets meer af te snijden. Het is dus een grens van de vorm, geen fout in de afronding. Als de connector dieper blijkt dan 10 mm moet de wand aan de pinkkant plaatselijk dikker worden; dat is een aanpassing van "Contour buiten" in `opbouw_helften.py`. Nog niet gedaan.
- `np_steek` 19, `uitsparing` 13,9, `plaat_dikte` 2, `bodem` 3, `knop_d` 18: gezond.

Les voor de scripts: een cirkel niet rechtstreeks op een geprojecteerd punt zetten. De schets volgt een verplaatsing dan wel, de extrusie niet. Oplossing: eigen punt met een samenvallend-voorwaarde (functie `circles`). In `opbouw_helften.py` zit dit nog op de oude manier; daar verschuiven de bronpunten niet, dus het geeft nu geen fout.

Open punten numpad:
- Uitsparing connector is 25 mm breed en loopt van 0,5 mm onder de bovenkant van de print tot de bovenkant van de wand (4 mm hoog). Aanpassen na het opmeten van de connector.
- Geen kap en geen USB-opening: de numpad heeft geen eigen controller.
