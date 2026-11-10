# keebs-repo van vipul-sharma20

https://github.com/vipul-sharma20/keebs, branch `main`. Beschrijving: "Resources for custom keyboard builds and other miscellaneous keyboard utilities". Gelezen via de browser op 10 november 2026.

## Structuur

```
keebs/
├── README.md
├── .gitignore
├── .gitmodules
├── footswitch/            (submodule, rgerganov/footswitch, niet relevant voor dit project)
└── lily58/
    ├── PCB/
    │   ├── README.md
    │   ├── gerber/
    │   ├── lily58.zip
    │   └── pcb.png
    ├── firmware/
    │   ├── README.md
    │   ├── lily58_rev1_vipul-sharma20.hex
    │   └── keymaps/
    │       ├── default/
    │       ├── lily58l/
    │       └── vipul-sharma20/   (config.h, keymap.c, rules.mk)
    └── stls/
        ├── README.md
        ├── case.stl
        └── lily58plate.stl
```

## Wat erin staat (voor zover gelezen)

- **PCB:** Gerber-bestanden (projectnaam `Lily58_Pro`), als map en als zip, plus een afbeelding van de print. Dit zijn de bestanden die de blog bij LionCircuits liet maken.
- **STL's:** `case.stl` en `lily58plate.stl`. De blog noemt voor de plaat en behuizing ontwerpen van derden. De README in die map is vrijwel leeg. De maten van de STL's staan in [09-maten-uit-stl-en-gerber.md](09-maten-uit-stl-en-gerber.md).
- **Firmware:** een kant-en-klare `.hex` (de bestandsnaam noemt `rev1`) en drie keymaps. De firmware-README bevat alleen twee links: https://kriscables.com/flash-controller-qmk/ en https://docs.qmk.fm/newbs_getting_started
- **Eigen keymap (`vipul-sharma20/config.h`):** `TAPPING_TERM 100`, `QUICK_TAP_TERM 0`, RGB-lichteffecten aan met `RGBLIGHT_LED_COUNT 27` en `RGBLIGHT_LIMIT_VAL 120`. De onderlaag-LED-regel staat uitgecommentarieerd. Dit zijn persoonlijke voorkeuren, geen hardware-eisen.

## Niet gelezen

`rules.mk` en `keymap.c` van de eigen keymap, de keymaps `default` en `lily58l`, de licentie van de repo. De README in `PCB` bevat alleen de afbeelding `pcb.png`, de README in `stls` is vrijwel leeg. De Gerber-bestanden zijn gelezen voor toetsposities en printrand (zie 09), niet voor de rest.
