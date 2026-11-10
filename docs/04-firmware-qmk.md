# Firmware (QMK)

## QMK-map

`keyboards/lily58` in https://github.com/qmk/qmk_firmware

- Hardware: Lily58 PCB en Pro Micro.
- Onderhouder: Naoki Katahira.
- Layout: 6×4+5 per helft.

## Commando's

Na het inrichten van de QMK-buildomgeving:

```
make lily58:default
```

Flashen met avrdude (uit de Pro-gids, in de map `qmk_firmware`):

```
sudo make lily58:default:avrdude
```

Als "Detecting USB port, reset your controller now ..." verschijnt: druk op de resetknop van de helft die je flasht. Flash elke helft apart.

Zonder eigen keymap kan QMK Toolbox (GUI) ook. Voor een eigen keymap is een volledige QMK-omgeving aangeraden.

## Links

- Buildomgeving: https://docs.qmk.fm/#/getting_started_build_tools
- Make-gids: https://docs.qmk.fm/#/getting_started_make_guide
- Beginnersgids: https://docs.qmk.fm/#/newbs

## Opmerkingen

- De QMK-readme noemt geen bootloader en geen revisies.
- De Pro-gids zegt niet welke firmware op welke helft hoort, alleen dat elke helft apart wordt geflasht.
- De blog van vipul zegt dat firmware en keymaps in zijn repo staan onder `lily58/firmware`. Wat daar staat, staat in [07-keebs-vipul-repo.md](07-keebs-vipul-repo.md). Concrete QMK-instellingen staan niet in de blogtekst.
- Voor een RP2040 Pro Micro: zie [08-printables-handwired-lily58.md](08-printables-handwired-lily58.md) (pinnen, processor en bootloader aanpassen, extra's uitzetten).
- Windows kan het toetsenbord als JIS herkennen: dan komen bij "@" en "[" verkeerde tekens. Oplossing: in de OS-instellingen het toetsenbord op US zetten.

## Niet in de bronnen

Niet opgehaald en daarom niet hier opgenomen: `config.h`, `rules.mk`, matrix-pinnen, de `info.json` met toetsposities. Die staan in de QMK-map `keyboards/lily58`. Voor Fusion zijn de toetsposities uit `info.json` het nuttigst.
