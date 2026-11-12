# Behuizing in Fusion — parametrisch (v0.2)

Status: 12 november 2026. De behuizing uit [13-behuizing.md](13-behuizing.md) staat nu parametrisch in het Fusion-document **"Opzet 1-0-0"** (map Toetsenbord): rechterhelft gemodelleerd, linkerhelft als spiegeling. Het numpad staat nog niet in Fusion.

**Let op: het document is in Fusion gewijzigd maar nog niet opgeslagen.**

Opbouwscript: [`behuizing/fusion/opbouw_helften.py`](../behuizing/fusion/opbouw_helften.py). Het verwijdert alles na de schets "PCB omtrek" en bouwt de tijdlijn opnieuw op (stap 0 t/m 4).

![Beide helften](../behuizing/afbeeldingen/fusion_beide_helften.png)

## Wat er in het document staat

| Component | Massa (alu 6061) |
|---|---|
| Bak rechts / Bak links | 265,6 g |
| Plaat rechts / Plaat links | 41,5 g |
| Kap rechts / Kap links | 20,4 g |
| Print rechts (referentie, 1,6 mm) | — |

Per helft 327,5 g aluminium (CadQuery v0.1: 328 g). Tijdlijn: 54 stappen, alles gezond. Alle nieuwe schetsen zijn volledig bepaald.

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

## Controle

- Volume per deel tegenover CadQuery v0.1: bak 98.371 / 98.356 mm³, plaat 15.361 / 15.359 mm³ (v0.1 zonder het losse stukje), kap 7.554 / 7.579 mm³ (verschil door de afronding).
- Botsingscontrole bak, plaat, kap, print: 0 botsingen. Print ligt op de steunbussen; print tot plaat 3,5 mm.
- Parametertest (waarde gewijzigd, tijdlijn gecontroleerd, teruggezet): `conn_diepte` 6,5 / 8 / 10 mm, `wand` 8 mm, `spleet` 0,5 mm, `plaat_dikte` 1,2 mm, `bodem` 3 mm, `kap_hoogte` 12 mm, `duimhoek` 20°: alles gezond.
- `wand` 6 mm: alleen "Afronding bovenrand kap" faalt (de verzonken M3-kop van 6 mm past niet meer in de wand).
- `conn_diepte` boven 10,06 mm: het connectorvlak valt dan buiten de buitencontour; dan moet `wand` omhoog.

## Opgemerkt, niet aangepast

1. **Resetgat:** boven het gat (ø3,5 op z 10,6) blijft 0,25 mm materiaal tot de bovenkant van de wand. Voor frezen te dun; gat lager, kleiner of als sleuf tot de rand.
2. **Wand tussen USB en TRRS:** in bak en kap blijft een pilaartje van 3,1 mm breed staan. Eén gezamenlijke uitsparing is eenvoudiger te frezen.
3. **M2 in de kap:** de verzonken kop (ø4,4) zit 0,3 mm van de rand van de kap.
4. De M3-posities zijn gekoppeld aan de hartlijn van de wand, maar de verdeling langs de wand is vast (uit `behuizing.py`).

## Nog te doen

- Document opslaan in Fusion; STEP/STL exporteren naar `behuizing/export/`.
- Numpad in Fusion (bak en plaat).
- Stuklijst met schroeven, afstandsbussen en voetjes (E19).
- Na levering van de connector: `conn_diepte` aanpassen.
