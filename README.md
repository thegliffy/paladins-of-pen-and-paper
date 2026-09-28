# Paladins of Pen and Paper

A portrait, tabletop-framed pixel RPG. Phase 0 is a playable phone slice: recruit one to five heroes, walk a vertical region map, and fight at the table.

The native viewport is **270×480**, integer-scaled with nearest-neighbor filtering. Screen positions live in [`data/layout.json`](data/layout.json). A `landscape` block is reserved there so a desktop layout can be added later without rewriting the screens. Production sprites live in [`art_source/phase0`](art_source/phase0) and are loaded by [`scripts/core/art_pack.gd`](scripts/core/art_pack.gd). The UI font is [m5x7](https://managore.itch.io/m5x7) by Daniel Linssen, CC0, at size 16 so it sits on the native grid.

Names, dialogue, and art in this repository are original. Combat math and the timing table follow the project's design breakdown.

## Play

Godot **4.7** or newer.

```bash
godot --path .
```

On a phone the window is portrait. On desktop the window opens at 810×1440, which is exactly three times the native grid.

1. **New game** seats one to five heroes. Eight classes are on the Class tab: Paladin, Wizard, Ranger, Bard, Cleric, Rogue, Barbarian, and Druid. Each persona and each class can be used only once. There are five personas, so a full party can still keep them unique. Random fills the paper doll; the arrows and the rows under it edit the current tab. Next seats this hero and opens another slot. Begin starts the campaign with the heroes seated so far, including the one on screen.
2. The table hub has Travel, Fight, Rest, Quest, and Party along the bottom.
3. **Travel** opens the Greenmere map. Drag to scroll. Tap a place, then tap it again or press Travel. Stop ends a multi-hop trip after the hop you are already on.
4. Roads with monsters roll a d20 around the middle of the hop. 1 is lost, 2 through p is an ambush, p+1 through 19 is safe, 20 is lucky. `p = clamp(destination level − party average + 7, 2, 10)`.
5. Combat is stacked for one hand: an initiative strip for up to eight combatants, monsters, the GM behind the table, up to five heroes from behind with HP and MP bars on the chair, then the acting hero's bar. That bar is Attack, Cover, the class's five skills, Item, and Run. The first tap inspects the slot. The second tap uses it. A passive, a locked skill, a cooling skill, and a skill you cannot pay for show the reason and do not cast. The name tab above the bar is whose turn it is. Passives also show in the creator and on the party panel with a Passive tag.

The save is `user://paladins_save.json`. It is written when the app pauses or closes. A fight in progress reloads from the checkpoint taken when the battle started, so a kill during the fight does not keep half-applied rewards.

## Checks

```bash
godot --headless --path . -s res://tests/run_tests.gd
```

That covers the stat, HP, energy, damage, crit, XP, gold, travel-table, dice, timing, path, portrait-layout, party seats, skill-button states, the arm-then-cast inspect card, cooldown, HP-cost, build-up, mana regen, threat raffle, and on-hit passive examples.

The older files under `art/` are still generated with `python3 tools/gen_art.py` and stay in the repo for the title backdrop and the file checks. The creator, map, and combat screens use the production pack.

## Screenshots

Native 270×480 captures of the production art:

![Combat, skill card open](docs/screenshots/skills.png)

![Character creator](docs/screenshots/creator.png)

![Greenmere map](docs/screenshots/map.png)

![Combat](docs/screenshots/combat.png)

![Skill list](docs/screenshots/skills.png)

![Party panel](docs/screenshots/party.png)

## Android

[`export_presets.cfg`](export_presets.cfg) has a debug Android preset locked to portrait (`screen/orientation=1`) and arm64-v8a, plus a Linux preset. The project setting `display/window/handheld/orientation` is portrait.

```bash
godot --headless --export-debug Android build/paladins-0.2.0-debug.apk
```

The export needs the Godot 4.7.2 Android templates (installed into `android/build`, which is gitignored), a `.build_version` of `4.7.2.stable`, Android SDK 36, build-tools 36.1.0, NDK 29.0.14206865, and a JDK. The project enables ETC2/ASTC import, which the Android exporter requires.

The published debug APK is [v0.2.0](https://github.com/thegliffy/paladins-of-pen-and-paper/releases/tag/v0.2.0): [paladins-0.2.0-debug.apk](https://github.com/thegliffy/paladins-of-pen-and-paper/releases/download/v0.2.0/paladins-0.2.0-debug.apk). It is arm64-v8a, portrait, package `com.thegliffy.paladinspenpaper`, and includes the eight classes, passives, the threat raffle, the party of five, inspect-to-cast, and the production sprites. v0.1.0 is the earlier portrait slice and is left as-is.

## Where numbers live

| Data | File |
| --- | --- |
| Personas, races, classes, skills, monsters, items, the quest | `data/*.json` |
| Class roles, passives, and the threat raffle | [`docs/CLASSES.md`](docs/CLASSES.md), [`docs/DESIGN.md`](docs/DESIGN.md) |
| Threat coefficients | [`data/threat.json`](data/threat.json) |
| Places, roads, levels | `data/region.json` |
| Encounter difficulties | `data/encounters.json` |
| Paper-doll colors and layer counts | `data/appearance.json` |
| Screen rectangles | `data/layout.json` |
| Formulas | `scripts/core/formulas.gd` |
| Delays | `scripts/core/timing.gd` |

A level 1 hero is `class + persona + race + 2` on Body, Senses, and Mind. HP is `15 × (L × Body − L + Body + Mind)`. Energy is `20 × (L × Mind − L + Body + Mind)` plus any race bonus. The next level costs `L² × 30 + 30` XP.

## Deviations from the breakdown

- **Portrait.** The playable slice is 270×480, not a landscape 480×270 table. The same staging is stacked: monsters on top, GM and table in the middle, up to five heroes below with bars on the chairs, then the acting hero's bar in thumb reach.
- **Lost** on the road starts an ambush. There is no secret-list yet, so a lost result cannot award one.
- A **natural 20** awards free travel or a Hearth Tonic. It does not pull from a secret list.
- Sable's travel bonus is added to the d20 and the total is clamped to 1–20 before the table is read. A raw 1 with that bonus becomes 2.
- **Gold** is summed per monster (including the 20% chance of bonus gold), then passed through the battle multiplier. The level gap is the party average minus the monster's level, and it does not go below 0.
- The party shares one pouch. There is no shop.
- **Stun** uses the table's two-tick timer.
- The **chicken** runs left and up across the portrait table for 1.8 s. The sound plays at 1.1 s.
- You start with **500 gold**, three Hearth Tonics, and two Lamp Vials.
- Level 1 monsters use the level-1 HP exception (the formula divided by 3), so the pond fight is short.
- Skill ranks use the energy-cost formula on **mana** skills only. Cooldowns, free actions, HP costs, and build-up tracks (Rogue combo, Bard tempo, Barbarian rage) do not go through that formula. Damage and healing add a small per-rank term. There is no separate power-curve table yet.
- Each class has one passive besides its actives. Monsters raffle a living member by threat. Threat is class base plus Body and a little of damage reduction, then taunt and a passive multiplier, and it never drops below 1. Cover halves it. The Wizard regains a share of max energy at the start of each of their turns. Other passives cover crits, healing, initiative, a party damage-reduction aura, health regen, a flat on-hit cut, and damage that rises as health falls. Set `debug` in `data/threat.json` to show each member's threat percent on their chair.
- Monster pictures use the pack's eight bodies. Puddleblob is the slime, Thicket Imp the imp, Cinder Mite a goblin, Briar Hound the wolf, Lantern Wisp a mushroom, Marshlurker a skeleton, Cave Howler the bat, and Gravel Brute the golem. Map nodes use the village, windmill, tavern, shrine, cave, and castle pictures.
- No terrain effects, so the 1.5 s terrain intro does not play.
- No counter-attack skills. The counter delays are still in the timing constants and the tests.
- The bard's second skill applies **poison**, not weakness.
- A wild rest that fails every Senses die is interrupted by an ambush and does not heal first.
- A wipe revives the party to about a quarter of their health and charges the resurrect cost when the purse can pay, so the slice cannot soft-lock.
- Audio is generated tones. There is no music.
- Combat, the creator, and the map use the production sprite pack. The title screen still uses the meadow backdrop from `art/`.

A basic attack's waits are 0.25 s wind-up, 0.20 s to the hit, and a 0.50 s HP tween (0.95 s). Punch and the red blink run inside that tween. On the machine that captured the screenshots, one measured attack completed in 806 ms, inside the 0.8–1.2 s gate.
