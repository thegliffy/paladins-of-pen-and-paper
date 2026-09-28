# Paladins of Pen and Paper: Phase 0 sprite pack

Generated 2026-09-28. **Native 270x480 PORTRAIT** (was 480x270 landscape; landscape-only files are marked LEGACY), displayed at 4x with nearest-neighbour. Every PNG is RGBA with binary alpha and uses only the 48 colours in `palette/palette48.hex` (checked in `tools/compose.py`).

## Conventions
- Anchors are `[x, y]` pixel coordinates within ONE frame, measured from the top-left. A bottom-centre anchor marks the feet row.
- Strips are horizontal with equal-size frames, read left to right.
- Monsters: frames are 80x70, feet anchor [40,64]. Forward is +y, toward the party: attack lunges +4px and a hit knocks back 2px up. Death: white flash, then sinking plus a checkerboard dissolve (25/50/75%).

## Damage colours
| use | fill | shade | outline |
|---|---|---|---|
| HP damage | `#ec5a44` | `#c02c2c` | `#120c18` |
| MP | `#4c9ce8` | `#3466cc` | `#120c18` |
| Heal | `#b4dc62` | `#7cbc3c` | `#120c18` |

## Font
**m5x7** by Daniel Linssen, font size **16** (renders 1:1 on the native grid, cap height about 7px). Licence: **CC0 1.0** (attribution appreciated). URL: https://managore.itch.io/m5x7. Not bundled; download it from itch.io. Use m6x11 (same author) for headings. Fallback: Pixel Operator 8 (CC0 since v2018.10.04-1).

## Paperdoll
- Front canvas 32x48, anchor [16,47]. Layer order: `body_skin_N` → `outfit_base` (tinted) → `class_<c>` → `head_N` (skin-remapped) → `hair_N` (tinted) → `class_<c>_hat`.
- While a hat is worn, hide hair rows with y < `hair_clip_y` (see the hat entries).
- Back/seated canvas **48x78, anchor [24,77]** (v2 1.5x redraw, identical to `party/seat_*`). Order: `body_back_skin_N` → `outfit_back` → `class_back_<c>` → `hair_back_N` → `class_back_<c>_hat` → `chair_back`.
- Hair, the shirt and the beard use grayscale keys K1 `#46424e`, K2 `#6c6a76`, K3 `#9c9ca6` and K4 `#cfd0d4`. The ramps are in `paperdoll/palettes/*_ramps.png` (1px per entry). Heads use reference skin tone 3; remap them with `skin_ramps.png` in a single simultaneous lookup. Pre-tinted copies are in `paperdoll/tinted/`.
- Portrait crop: rect `[6,8,20,20]` of the composed front doll. Draw it at [2,2] in `portrait_frame` and at [4,4] in `hp_mp_card`.

### Ramp remap shader (Godot 4)
```glsl
shader_type canvas_item;
// Remap grayscale keys to a ramp row. Hair: ramp=hair_ramps.png (4 cols), outfit: outfit_ramps.png (3 cols, keys K2..K4),
// skin: skin_ramps.png with keys = skin_reference [blush, detail, shadow, base].
uniform sampler2D ramp : filter_nearest;
uniform int row = 0;
uniform vec3 k0 = vec3(0.275, 0.259, 0.306); // #46424e
uniform vec3 k1 = vec3(0.424, 0.416, 0.463); // #6c6a76
uniform vec3 k2 = vec3(0.612, 0.612, 0.651); // #9c9ca6
uniform vec3 k3 = vec3(0.812, 0.816, 0.831); // #cfd0d4
uniform int first_col = 0; // 0 for hair (K1..K4); outfit: set k0..k2 = K2..K4 and use 3 columns
void fragment() {
    vec4 c = texture(TEXTURE, UV);
    vec3 keys[4] = {k0, k1, k2, k3};
    for (int i = 0; i < 4; i++) {
        if (distance(c.rgb, keys[i]) < 0.01) { c.rgb = texelFetch(ramp, ivec2(i + first_col, row), 0).rgb; }
    }
    COLOR = c;
}
// GDScript alternative (bake once, no shader):
// var img := tex.get_image(); for y in img.get_height(): for x in img.get_width():
//     var c := img.get_pixel(x, y); var i := KEYS.find(c.to_html(false)); if i >= 0 and c.a > 0.5: img.set_pixel(x, y, ramp_img.get_pixel(i, row))
// return ImageTexture.create_from_image(img)
```

## Portrait (270x480)
Top to bottom in `scene_test_portrait.png` (v7, **max party 5**): scrollable initiative rail (8 combatants at step 29, next-round portrait clipped at the right), 3 monsters (feet y222-266), GM behind `combat/table_portrait.png` (**266x40**, anchor [133,39], bottom-centre [135,382]), 5 composed seats paladin(active)/cleric/rogue/druid/wizard at x 27/81/135/189/243, y 418/414/418/414/418 (slots 1 and 3 are 4px higher), HP/MP shown as seat-mounted bars (`seat_bars_frame` 44x10: HP 4px over MP 3px, at [seat_x-22, feet_y-11], current-HP number in outlined 3x5 digits at [bar_x+1, bar_y-6], gold-ringed `_active` for the active seat; no card row), v6 per-character action bar `ui/portrait/action_bar_v2.png` (270x50) at y430 with the gold `name_tab` at [4,420]: Attack/Cover (32px), gold divider, the active class skills 1-5 (32px, passives in the octagon slot, MP cost badges below), Item/Run 20px minis at the right. The old 4-seat layout is kept as a note in `portrait.layout.seats_v4_4party_note`.

| portrait file | size | anchor | frames | notes |
|---|---|---|---|---|
| combat/bg_forest_portrait.png | 270x480 | [0, 0] | 1 | PORTRAIT 270x480 backdrop recomposed from the same forest source: sky 0-~40, tree line to y~141, meadow below. v3: rows ~196-479 are a seamless procedural meadow (value-noise grass clumps, tufts, scattered dirt patches), dither-blended into the source meadow over y196-231. No repeats or mirror lines. |
| combat/table_portrait.png | 266x40 | [133, 39] | 1 | PORTRAIT table (v5: widened 250->266 for a 5-seat party), procedural 266x40: 3 long planks, 3 flat wood tones, tan highlight lip on the near edge. Bottom-centre anchor; GM hands/props sit on the top surface rows. |
| combat/d20_roll.png | 96x24 | [12, 23] | 4 | v2 24x24. Loop frames 0-2 while tumbling (flat/pointy silhouettes alternate), then land on frame 3 (legible 20) or swap in the rolled face from d20_results.png. |
| combat/d20_results.png | 480x24 | [12, 23] | 20 | result faces: frame i shows number i+1 (bold 5x7 digits in #120c18 on a white triangle). |
| combat/d20_nat20.png | 24x24 | [12, 23] | 1 | gold natural-20 result frame (swap in for frame 3 on a nat 20). |
| party/seat_paladin_idle.png | 48x78 | [24, 77] | 1 | 48x78 seat built from the back-view paperdoll layers. |
| party/seat_paladin_active.png | 48x78 | [24, 77] | 1 | 48x78 seat built from the back-view paperdoll layers. Active: all layers raised 3px + 1px gold #f8d040 outline around the union. |
| party/seat_wizard_idle.png | 48x78 | [24, 77] | 1 | 48x78 seat built from the back-view paperdoll layers. |
| party/seat_wizard_active.png | 48x78 | [24, 77] | 1 | 48x78 seat built from the back-view paperdoll layers. Active: all layers raised 3px + 1px gold #f8d040 outline around the union. |
| party/seat_ranger_idle.png | 48x78 | [24, 77] | 1 | 48x78 seat built from the back-view paperdoll layers. |
| party/seat_ranger_active.png | 48x78 | [24, 77] | 1 | 48x78 seat built from the back-view paperdoll layers. Active: all layers raised 3px + 1px gold #f8d040 outline around the union. |
| party/seat_bard_idle.png | 48x78 | [24, 77] | 1 | 48x78 seat built from the back-view paperdoll layers. |
| party/seat_bard_active.png | 48x78 | [24, 77] | 1 | 48x78 seat built from the back-view paperdoll layers. Active: all layers raised 3px + 1px gold #f8d040 outline around the union. |
| party/seat_cleric_idle.png | 48x78 | [24, 77] | 1 | 48x78 seat built from the back-view paperdoll layers. |
| party/seat_cleric_active.png | 48x78 | [24, 77] | 1 | 48x78 seat built from the back-view paperdoll layers. Active: all layers raised 3px + 1px gold #f8d040 outline around the union. |
| party/seat_rogue_idle.png | 48x78 | [24, 77] | 1 | 48x78 seat built from the back-view paperdoll layers. |
| party/seat_rogue_active.png | 48x78 | [24, 77] | 1 | 48x78 seat built from the back-view paperdoll layers. Active: all layers raised 3px + 1px gold #f8d040 outline around the union. |
| party/seat_barbarian_idle.png | 48x78 | [24, 77] | 1 | 48x78 seat built from the back-view paperdoll layers. |
| party/seat_barbarian_active.png | 48x78 | [24, 77] | 1 | 48x78 seat built from the back-view paperdoll layers. Active: all layers raised 3px + 1px gold #f8d040 outline around the union. |
| party/seat_druid_idle.png | 48x78 | [24, 77] | 1 | 48x78 seat built from the back-view paperdoll layers. |
| party/seat_druid_active.png | 48x78 | [24, 77] | 1 | 48x78 seat built from the back-view paperdoll layers. Active: all layers raised 3px + 1px gold #f8d040 outline around the union. |
| ui/portrait/ability_attack.png | 32x32 |  | 1 | default ability "attack" in the skill-slot style (always available for every class). |
| ui/portrait/ability_attack_active.png | 32x32 |  | 1 | selected state. default ability "attack" in the skill-slot style (always available for every class). |
| ui/portrait/ability_cover.png | 32x32 |  | 1 | default ability "cover" in the skill-slot style (always available for every class). |
| ui/portrait/ability_cover_active.png | 32x32 |  | 1 | selected state. default ability "cover" in the skill-slot style (always available for every class). |
| ui/portrait/action_bar.png | 270x48 | [0, 47] | 1 | LEGACY (landscape 480x270): use ui/portrait/action_bar_v2.png (v6 per-character bar). 270x48 bottom bar; place at y=432 (bottom-left anchor at y 479). 5 buttons 32x32, 18px gaps, order attack/skill/item/cover/run. |
| ui/portrait/action_bar_examples.png | 278x220 |  | 1 | QA: the v6 bar swapping per active character (paladin: selected/cooldown/locked + passive 5; wizard: passive 5; rogue: all 5 active). Not a runtime asset. |
| ui/portrait/action_bar_examples_3x.png | 834x660 |  | 1 | 3x nearest. |
| ui/portrait/action_bar_v2.png | 270x50 | [0, 0] | 1 | v6 per-character action bar (replaces ui/portrait/action_bar.png). Slot top-lefts in bar-local px: attack/cover default abilities (32x32), gold divider at x71, 5 class skills (32x32, step 33), Item/Run mini buttons (20x20) stacked at the right, 16x7 MP cost badges centred under each active skill (y38). |
| ui/portrait/bar_bg_90.png | 90x7 |  | 1 | LEGACY (landscape 480x270): v7: party HP/MP now shown as seat-mounted bars (ui/portrait/seat_bars_frame*.png + seat_bar_hp/mp). 90x7 trough (already baked into the narrow card). |
| ui/portrait/bar_dim_mask.png | 32x32 |  | 1 | 50% dither drawn over every OTHER bar slot while a skill card is open (optional focus dim). |
| ui/portrait/bar_hp_44.png | 44x5 |  | 1 | LEGACY (landscape 480x270): v7: party HP/MP now shown as seat-mounted bars (ui/portrait/seat_bars_frame*.png + seat_bar_hp/mp). 44x5 HP fill for hp_mp_card_compact (rect [4,27,44,5]). |
| ui/portrait/bar_hp_88.png | 88x5 |  | 1 | LEGACY (landscape 480x270): v7: party HP/MP now shown as seat-mounted bars (ui/portrait/seat_bars_frame*.png + seat_bar_hp/mp). 88x5 HP fill for the narrow card. |
| ui/portrait/bar_mp_44.png | 44x5 |  | 1 | LEGACY (landscape 480x270): v7: party HP/MP now shown as seat-mounted bars (ui/portrait/seat_bars_frame*.png + seat_bar_hp/mp). 44x5 MP fill for hp_mp_card_compact (rect [4,34,44,5]). |
| ui/portrait/bar_mp_88.png | 88x5 |  | 1 | LEGACY (landscape 480x270): v7: party HP/MP now shown as seat-mounted bars (ui/portrait/seat_bars_frame*.png + seat_bar_hp/mp). 88x5 MP fill for the narrow card. |
| ui/portrait/btn32_attack.png | 32x32 | [0, 0] | 1 | LEGACY (landscape 480x270): fallback only; the v6 bar uses ability_attack/ability_cover, class skill slots and mini_item/mini_run. 32x32 bottom-bar action button (same icon art as ui/btn_*). |
| ui/portrait/btn32_attack_active.png | 32x32 | [0, 0] | 1 | LEGACY (landscape 480x270): fallback only; the v6 bar uses ability_attack/ability_cover, class skill slots and mini_item/mini_run. selected (gold). 32x32 bottom-bar action button (same icon art as ui/btn_*). |
| ui/portrait/btn32_cover.png | 32x32 | [0, 0] | 1 | LEGACY (landscape 480x270): fallback only; the v6 bar uses ability_attack/ability_cover, class skill slots and mini_item/mini_run. 32x32 bottom-bar action button (same icon art as ui/btn_*). |
| ui/portrait/btn32_cover_active.png | 32x32 | [0, 0] | 1 | LEGACY (landscape 480x270): fallback only; the v6 bar uses ability_attack/ability_cover, class skill slots and mini_item/mini_run. selected (gold). 32x32 bottom-bar action button (same icon art as ui/btn_*). |
| ui/portrait/btn32_item.png | 32x32 | [0, 0] | 1 | LEGACY (landscape 480x270): fallback only; the v6 bar uses ability_attack/ability_cover, class skill slots and mini_item/mini_run. 32x32 bottom-bar action button (same icon art as ui/btn_*). |
| ui/portrait/btn32_item_active.png | 32x32 | [0, 0] | 1 | LEGACY (landscape 480x270): fallback only; the v6 bar uses ability_attack/ability_cover, class skill slots and mini_item/mini_run. selected (gold). 32x32 bottom-bar action button (same icon art as ui/btn_*). |
| ui/portrait/btn32_run.png | 32x32 | [0, 0] | 1 | LEGACY (landscape 480x270): fallback only; the v6 bar uses ability_attack/ability_cover, class skill slots and mini_item/mini_run. 32x32 bottom-bar action button (same icon art as ui/btn_*). |
| ui/portrait/btn32_run_active.png | 32x32 | [0, 0] | 1 | LEGACY (landscape 480x270): fallback only; the v6 bar uses ability_attack/ability_cover, class skill slots and mini_item/mini_run. selected (gold). 32x32 bottom-bar action button (same icon art as ui/btn_*). |
| ui/portrait/btn32_skill.png | 32x32 | [0, 0] | 1 | LEGACY (landscape 480x270): fallback only; the v6 bar uses ability_attack/ability_cover, class skill slots and mini_item/mini_run. 32x32 bottom-bar action button (same icon art as ui/btn_*). |
| ui/portrait/btn32_skill_active.png | 32x32 | [0, 0] | 1 | LEGACY (landscape 480x270): fallback only; the v6 bar uses ability_attack/ability_cover, class skill slots and mini_item/mini_run. selected (gold). 32x32 bottom-bar action button (same icon art as ui/btn_*). |
| ui/portrait/cost_badge.png | 16x7 |  | 1 | MP cost badge (blue pill + drop). Draw digits_3x5 at digit_origin (x 6 for 2 digits). Centre under each ACTIVE skill slot (slot x + 8, bar y 38). Passives get no badge. |
| ui/portrait/cost_badge_0_9.png | 160x7 |  | 10 | pre-rendered cost badges for MP 0..9 (frame i = cost i). |
| ui/portrait/digits_3x5.png | 40x5 |  | 10 | tiny white digits 0-9 (3x5 glyph + 1px advance) for cost badges / cooldown counters. Tint by modulate if needed. |
| ui/portrait/digits_3x5_outlined.png | 50x7 |  | 10 | HP-number digits: cream 3x5 glyph (sand bottom row) with a 1px #120c18 outline (diagonals included) so it reads on any robe incl. white. Draw successive digits 4px apart (outline columns overlap). |
| ui/portrait/hp_mp_card_compact.png | 52x44 | [0, 0] | 1 | LEGACY (landscape 480x270): v7: party HP/MP now shown as seat-mounted bars (ui/portrait/seat_bars_frame*.png + seat_bar_hp/mp). v5 compact vertical party card 52x44 for a 5-wide row (step 54 = 52 + 2px gap). Face crop (paperdoll portrait_crop_rect) at portrait_rect; bar_hp_44/bar_mp_44 at the bar rects, cropped by %. Bars are colour-coded red/blue (no HP/MP text at this size). |
| ui/portrait/hp_mp_card_compact_active.png | 52x44 | [0, 0] | 1 | LEGACY (landscape 480x270): v7: party HP/MP now shown as seat-mounted bars (ui/portrait/seat_bars_frame*.png + seat_bar_hp/mp). ACTIVE/current-turn highlight (gold frame). v5 compact vertical party card 52x44 for a 5-wide row (step 54 = 52 + 2px gap). Face crop (paperdoll portrait_crop_rect) at portrait_rect; bar_hp_44/bar_mp_44 at the bar rects, cropped by %. Bars are colour-coded red/blue (no HP/MP text at this size). |
| ui/portrait/hp_mp_card_narrow.png | 130x28 | [0, 0] | 1 | LEGACY (landscape 480x270): v7: party HP/MP now shown as seat-mounted bars (ui/portrait/seat_bars_frame*.png + seat_bar_hp/mp). 130x28 portrait-layout card (2x2 grid). Draw bar_hp_88/bar_mp_88 at the rects, cropped by %. |
| ui/portrait/icon_cooldown.png | 9x7 |  | 1 | tiny skill-card info icon (cooldown turns); text starts 2px to its right. |
| ui/portrait/lock_icon.png | 10x10 |  | 1 | locked-skill padlock, draw at slot [11,11] over a dimmed icon in skill_slot_locked. |
| ui/portrait/mini_item.png | 20x20 |  | 1 | utility: open inventory (potion). |
| ui/portrait/mini_item_active.png | 20x20 |  | 1 | pressed/selected. utility: open inventory (potion). |
| ui/portrait/mini_run.png | 20x20 |  | 1 | utility: flee (door + arrow). |
| ui/portrait/mini_run_active.png | 20x20 |  | 1 | pressed/selected. utility: flee (door + arrow). |
| ui/portrait/name_tab.png | 64x10 |  | 1 | active-character nameplate tab: draw at bar top-left (x 4, bar_y - 10); class/hero name in the pixel font at text_origin (max ~13 chars). Gold = same highlight as hp_mp_card_compact_active. |
| ui/portrait/passive_dim_mask.png | 24x24 |  | 1 | 25% ink dither drawn over a PASSIVE icon so it reads as non-pressable (binary alpha). |
| ui/portrait/seat_bar_hp.png | 42x4 |  | 1 | HP fill (#ec5a44, #c02c2c bottom shade). Crop width = round(42 * hp%). |
| ui/portrait/seat_bar_hp_lowflash.png | 84x4 |  | 2 | low-HP (<25%) flash: frame 0 normal red, frame 1 cream/amber. Crop both frames to the same fill width. |
| ui/portrait/seat_bar_hp_tile.png | 1x4 |  | 1 | 1px HP fill column; stretch horizontally (nearest) instead of cropping the full strip. |
| ui/portrait/seat_bar_mp.png | 42x3 |  | 1 | MP fill (#4c9ce8 over #3466cc). Crop width = round(42 * mp%). |
| ui/portrait/seat_bar_mp_tile.png | 1x3 |  | 1 | 1px MP fill column; stretch horizontally. |
| ui/portrait/seat_bars_frame.png | 44x10 | [22, 0] | 1 | v7 seat-mounted HP/MP bars: #120c18 outline frame with dark empty tracks (HP #3e1016, MP #161c40). Anchor = top-centre; place at (seat_x, seat_feet_y - 11) so it overlaps the chair seat front + lower rails. Fill with seat_bar_hp/mp (crop by %) or stretch the 1px tiles. |
| ui/portrait/seat_bars_frame_active.png | 46x12 | [23, 1] | 1 | ACTIVE seat variant: gold inner ring + dark outer outline (1px larger each side). Same anchor point as the normal frame (top-centre of the inner frame at [23,1]). |
| ui/portrait/skill_card_examples.png | 480x252 |  | 1 | QA: skill card states (active ready, passive, not enough MP, on cooldown). Placeholder copy. Not a runtime asset. |
| ui/portrait/skill_card_examples_3x.png | 1440x756 |  | 1 | 3x nearest. |
| ui/portrait/skill_card_icon_frame.png | 44x44 |  | 1 | holds the 20x20 skill icon at 2x (nearest) at [2,2]. |
| ui/portrait/skill_card_icon_frame_passive.png | 44x44 |  | 1 | holds the 20x20 skill icon at 2x (nearest) at [2,2]. Octagon = passive. |
| ui/portrait/skill_card_panel.png | 48x48 |  | 1 | notebook-page 9-slice for the skill card: dark outline, parchment, spiral holes along the top edge, red margin line on the left, faint ruled lines. TILE (not stretch) the edges/centre so holes and ruling keep an 8px rhythm; pick widths/heights = 48 + 8k for a seamless look. |
| ui/portrait/skill_card_strip_cooldown.png | 24x14 |  | 1 | prompt strip: 3-slice (caps 5px, tile the middle). Text centred at y 5 in the pack 3x5 font. |
| ui/portrait/skill_card_strip_nomp.png | 24x14 |  | 1 | prompt strip: 3-slice (caps 5px, tile the middle). Text centred at y 5 in the pack 3x5 font. |
| ui/portrait/skill_card_strip_passive.png | 24x14 |  | 1 | prompt strip: 3-slice (caps 5px, tile the middle). Text centred at y 5 in the pack 3x5 font. |
| ui/portrait/skill_card_strip_ready.png | 48x14 |  | 2 | prompt strip: 3-slice (caps 5px, tile the middle). Text centred at y 5 in the pack 3x5 font. 2-frame pulse: swap frame + text colour gold/cream at 3 fps. |
| ui/portrait/skill_card_tail.png | 13x8 | [6, 7] | 1 | pointer: tip (anchor) aims at the tapped slot centre; place so rows 0-1 cover the card bottom edge (tail y = card_bottom - 2). |
| ui/portrait/skill_slot_armed.png | 72x36 |  | 2 | ARMED state (skill card open, next tap casts): 2px pulsing gold/cream glow ring drawn around the 32px slot (outside the frame). Distinct from skill_slot_active (selected). |
| ui/portrait/skill_tag_active.png | 29x9 |  | 1 | ACTIVE tag pill (word baked in the pack 3x5 font), top-right of the card. |
| ui/portrait/skill_tag_passive.png | 33x9 |  | 1 | PASSIVE tag pill (word baked in the pack 3x5 font), top-right of the card. |
| ui/portrait/target_all_allies.png | 9x7 |  | 1 | tiny skill-card info icon (target type); text starts 2px to its right. |
| ui/portrait/target_all_enemies.png | 9x7 |  | 1 | tiny skill-card info icon (target type); text starts 2px to its right. |
| ui/portrait/target_ally.png | 9x7 |  | 1 | tiny skill-card info icon (target type); text starts 2px to its right. |
| ui/portrait/target_enemy.png | 9x7 |  | 1 | tiny skill-card info icon (target type); text starts 2px to its right. |
| ui/portrait/target_self.png | 9x7 |  | 1 | tiny skill-card info icon (target type); text starts 2px to its right. |
| ui/portrait/top_bar.png | 270x20 | [0, 0] | 1 | 270x20 map/creator top bar. |
| ui/skills/barbarian_1.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/barbarian_2.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/barbarian_3.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/barbarian_4.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/barbarian_5.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/bard_1.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/bard_2.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/bard_3.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/bard_4.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/bard_5.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/cleric_1.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/cleric_2.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/cleric_3.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/cleric_4.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/cleric_5.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/druid_1.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/druid_2.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/druid_3.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/druid_4.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/druid_5.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/paladin_1.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/paladin_2.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/paladin_3.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/paladin_4.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/paladin_5.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/ranger_1.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/ranger_2.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/ranger_3.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/ranger_4.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/ranger_5.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/rogue_1.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/rogue_2.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/rogue_3.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/rogue_4.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/rogue_5.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/skill_cooldown_mask.png | 24x24 |  | 1 | 50% checker dither; crop from the top by remaining-cooldown fraction and draw over the icon (binary alpha keeps the pixel look). |
| ui/skills/skill_sheet.png | 346x206 |  | 1 | 8 columns (class) x 5 rows (skill 1..5). Active skills in skill_slot.png, passives in skill_slot_passive.png with a P tag. QA/reference sheet, not a runtime asset. |
| ui/skills/skill_sheet_3x.png | 1038x618 |  | 1 | 3x nearest of skill_sheet.png. |
| ui/skills/skill_slot.png | 32x32 |  | 1 | 32x32 skill slot, same footprint as ui/portrait/btn32_*. Icon area 24x24 inside (4..27). |
| ui/skills/skill_slot_active.png | 32x32 |  | 1 | 32x32 skill slot, same footprint as ui/portrait/btn32_*. Icon area 24x24 inside (4..27). |
| ui/skills/skill_slot_locked.png | 32x32 |  | 1 | 32x32 skill slot, same footprint as ui/portrait/btn32_*. Icon area 24x24 inside (4..27). |
| ui/skills/skill_slot_passive.png | 32x32 |  | 1 | PASSIVE slot: octagon with gold rim (reads differently from the square active slot). Not pressable, so there is no active/pressed state; dim with _locked while unlearned. |
| ui/skills/skill_slot_passive_locked.png | 32x32 |  | 1 | PASSIVE slot: octagon with gold rim (reads differently from the square active slot). Not pressable, so there is no active/pressed state; dim with _locked while unlearned. |
| ui/skills/wizard_1.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/wizard_2.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/wizard_3.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/wizard_4.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/wizard_5.png | 20x20 | [10, 10] | 1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| fx/fx_buff_aura.png | 336x72 | [28, 71] | 6 | gold rising aura + chevrons; anchor on feet. Draw the whole strip BEHIND the seat for a softer look, or in front (ring front arc overlaps feet). |
| fx/fx_fireball.png | 384x48 | [24, 24] | 8 | one strip: travel loop (0-2) + burst (3-7). Same 48x48 cell for both, anchor = ball/burst centre. |
| fx/fx_heal_sparkle.png | 288x64 | [24, 63] | 6 | anchor on the seat/monster feet (bottom-centre). Loop 1-2x. Heal colour lime #b4dc62; pair with ui/dmg_font_heal. |
| fx/fx_lightning.png | 160x96 | [16, 95] | 5 | strike from above; anchor = impact point at the target feet (bottom-centre). Frame 2 = impact flash. Hold frame 1-2 alternation for longer zaps. |
| fx/fx_poison_cloud.png | 336x48 | [28, 36] | 6 | toxic purple puffs with acid-green bubbles (purple keeps it readable over the green meadow); anchor ~ target waist/centre. Frames 2-3 can loop while a DoT ticks. |
| fx/fx_shield.png | 280x72 | [28, 71] | 5 | force bubble around a 48x70 seat/monster; anchor on feet. Play 0-1 once then loop 2-4 while the shield lasts; pixel-hex fill keeps the target visible (binary alpha). |
| fx/fx_slash.png | 240x48 | [24, 24] | 5 | diagonal arc sweep; centre anchor on the target body (e.g. monster centre). Flip h for the other direction. Frame 2 = impact (spawn damage number / hit anim). |
| fx/mana_tick.png | 96x28 | [8, 27] | 6 | subtle MP-regen tick in the MP colour #4c9ce8: blue sparkles rising. Anchor at the seat feet/centre or on the MP bar of the card; play once per regen tick. Pair with fx/mp_plus.png. |
| fx/mp_plus.png | 76x14 | [9, 13] | 4 | '+MP' float in MP colours: rises 1px/frame, last frame dithered out. For numbers use dmg_font_mp + dmg_font_mp_letters instead. |
| fx/taunt_aura.png | 168x16 | [28, 8] | 3 | optional subtle red ground ring for a taunting seat/monster; centre it on the feet row (seat anchor) and draw BEHIND the sprite. |
| fx/taunt_badge.png | 24x13 | [6, 12] | 2 | overhead taunt/aggro badge (red "!" shout). Place the anchor ~2px above the top of the seat/monster sprite (e.g. seat top y = feet-78+hat). 1px bob. Has a dark outline like UI icons. |
| ui/icon_gold.png | 10x10 | [0, 0] | 1 | 10x10 gold coin. |
| ui/btn_menu.png | 18x18 | [0, 0] | 1 | 18x18 menu (hamburger) button. |
| ui/btn_confirm.png | 56x24 | [0, 0] | 1 | 56x24 confirm (check) button. |
| ui/btn_random.png | 56x24 | [0, 0] | 1 | 56x24 randomise (die) button. |
| ui/btn_arrow_left.png | 14x22 | [0, 0] | 1 | 14x22 creator cycle arrow. |
| ui/btn_arrow_right.png | 14x22 | [0, 0] | 1 | 14x22 creator cycle arrow. |
| ui/swatch_frame.png | 16x16 | [0, 0] | 1 | 16x16 colour swatch frame; transparent 12x12 centre for the colour. |
| ui/swatch_frame_active.png | 16x16 | [0, 0] | 1 | 16x16 colour swatch frame; transparent 12x12 centre for the colour. |
| map/marker_arrow.png | 18x12 | [4, 11] | 2 | destination marker, bottom tip at the anchor; 2px bob. |
| map/tile_road_t_ews.png | 16x16 | [0, 0] | 1 | T-junction joining EWS (pre-rotated copy). |
| map/tile_road_t_ewn.png | 16x16 | [0, 0] | 1 | T-junction joining EWN (pre-rotated copy). |
| map/tile_road_t_nse.png | 16x16 | [0, 0] | 1 | T-junction joining NSE (pre-rotated copy). |
| map/tile_road_t_nsw.png | 16x16 | [0, 0] | 1 | T-junction joining NSW (pre-rotated copy). |
| map/tile_road_t.png | 16x16 | [0, 0] | 1 | 16x16 seamless. T-junction joining EAST+WEST+SOUTH; flip_v -> E+W+N; see tile_road_t_* for the vertical variants. |
| scene_test_portrait.png | 270x480 |  | 1 | PORTRAIT 270x480 mock built only from pack files (QA). |
| scene_test_portrait_4x.png | 1080x1920 |  | 1 | 4x nearest upscale. |
| map_test_portrait.png | 270x480 |  | 1 | PORTRAIT 270x480 mock built only from pack files (QA). |
| map_test_portrait_4x.png | 1080x1920 |  | 1 | 4x nearest upscale. |
| creator_test_portrait.png | 270x480 |  | 1 | PORTRAIT 270x480 mock built only from pack files (QA). |
| creator_test_portrait_4x.png | 1080x1920 |  | 1 | 4x nearest upscale. |
| fx_test_portrait.png | 270x360 |  | 1 | QA: one representative frame of each FX on monsters (fx centred on body, lightning/heal/buff/shield on feet) and composed seats, at native scale. |
| fx_test_portrait_3x.png | 810x1080 |  | 1 | 3x nearest. |

## Classes (8)
| class | read | seat defaults (skin/head/hair/hair colour/outfit) |
|---|---|---|
| paladin | plate + visor helm, shield | skin=2, head=1, hair=2, hair_color=brown, outfit=white, hat=True |
| wizard | blue robe, pointed hat, staff | skin=1, head=5, hair=5, hair_color=blonde, outfit=blue, hat=True |
| ranger | green hood, bow | skin=3, head=4, hair=4, hair_color=ginger, outfit=green, hat=True |
| bard | beret + feather, lute | skin=5, head=3, hair=6, hair_color=black, outfit=red, hat=True |
| cleric | white/gold robe, gold holy cross on the back, mitre with lappets | skin=4, head=6, hair=2, hair_color=white, outfit=white, hat=True |
| rogue | dark leather + half-mask hood (pointed tip), dagger on the back | skin=2, head=2, hair=3, hair_color=black, outfit=dark, hat=True |
| barbarian | bare arms, fur pelt/mantle, horned helm, axe on the back (skips outfit_base) | skin=3, head=3, hair=8, hair_color=ginger, outfit=None, hat=True |
| druid | leaf-green robe, antler circlet, tall leaf-topped staff | skin=6, head=6, hair=1, hair_color=white, outfit=green, hat=True |

### Seat = creator doll (recipe)
Canvas 48x78, anchor [24,77]. back/body_back_skin_<skin> → back/outfit_back tinted with outfit ramp (skip for barbarian) → back/class_back_<class> → back/hair_back_<hair> tinted with hair ramp, rows y < class hat hair_clip_y cleared when the hat is worn → back/class_back_<class>_hat (if hat) → back/chair_back (always last). ACTIVE: shift the composed image up 3px, then add a 1px #f8d040 outline (4-neighbour) around the union. party/seat_<class>_idle/active.png are exactly this recipe applied to classes.seat_defaults (built in tools/build_doll.py seat()). A player-made hero uses the same recipe with the creator choices, so seat == creator doll.

## Skill icons (20x20, 5 per class)
20px sits inside the 32px portrait buttons/slots with a 6px border; 16px looked lost in the 24px inner area. Active slot: ui/skills/skill_slot*.png (32x32, icon at offset [6,6]); ui/skills/skill_cooldown_mask.png (24x24 at [4,4]). Passive slot: ui/skills/skill_slot_passive.png (+_locked): octagon, gold rim, not pressable (no active state).

| file | motif | suggested |
|---|---|---|
| ui/skills/barbarian_1.png | axe chop | active |
| ui/skills/barbarian_2.png | rage (angry flame) | active |
| ui/skills/barbarian_3.png | war cry (horn + sound waves) | active |
| ui/skills/barbarian_4.png | stomp (boot + shockwave) | active |
| ui/skills/barbarian_5.png | provoke (taunt/aggro passive: shouting face) | passive |
| ui/skills/bard_1.png | music note (damage note) | active |
| ui/skills/bard_2.png | song buff (note + up arrow) | active |
| ui/skills/bard_3.png | lullaby (moon + zz) | active |
| ui/skills/bard_4.png | lute | active |
| ui/skills/bard_5.png | war drum (active: party haste) | active |
| ui/skills/cleric_1.png | heal (green cross) | active |
| ui/skills/cleric_2.png | holy cross (bless) | active |
| ui/skills/cleric_3.png | resurrect (spirit ankh) | active |
| ui/skills/cleric_4.png | smite (holy hammer) | active |
| ui/skills/cleric_5.png | blessed (regen passive: haloed heart) | passive |
| ui/skills/druid_1.png | leaf heal | active |
| ui/skills/druid_2.png | thorns (thorny vine) | active |
| ui/skills/druid_3.png | bear form | active |
| ui/skills/druid_4.png | entangling roots | active |
| ui/skills/druid_5.png | regrowth (passive: sprout, heal over time) | passive |
| ui/skills/paladin_1.png | sword of light (holy strike) | active |
| ui/skills/paladin_2.png | shield bash | active |
| ui/skills/paladin_3.png | holy aura (radiant halo) | active |
| ui/skills/paladin_4.png | taunt (shout burst "!") | active |
| ui/skills/paladin_5.png | guardian (aggro passive: target reticle on shield) | passive |
| ui/skills/ranger_1.png | arrow shot | active |
| ui/skills/ranger_2.png | multi-shot (3 arrows) | active |
| ui/skills/ranger_3.png | snare trap (bear trap) | active |
| ui/skills/ranger_4.png | animal companion (paw print) | active |
| ui/skills/ranger_5.png | keen eye (accuracy/crit passive) | passive |
| ui/skills/rogue_1.png | dagger strike | active |
| ui/skills/rogue_2.png | poison vial | active |
| ui/skills/rogue_3.png | smoke bomb | active |
| ui/skills/rogue_4.png | backstab (bloody dagger) | active |
| ui/skills/rogue_5.png | pickpocket (active: steal gold) | active |
| ui/skills/wizard_1.png | fireball | active |
| ui/skills/wizard_2.png | ice shard | active |
| ui/skills/wizard_3.png | lightning bolt | active |
| ui/skills/wizard_4.png | arcane shield (hex ward) | active |
| ui/skills/wizard_5.png | mana flow (mana-regen passive: drop + up arrow) | passive |

## Skill card popup (portrait)
Tap a skill once to open its notebook card (9-slice `ui/portrait/skill_card_panel.png`, margins L14 T10 R6 B6, tiled; tail `skill_card_tail.png`) and arm the slot (`skill_slot_armed.png`, 2 frames). Tap the same slot again to cast; another slot switches; elsewhere closes; passives never cast. Card: 2x icon frame, name, ACTIVE/PASSIVE tag, MP badge, target icon + text, cooldown, 3-line description, prompt strip (ready pulse / passive / NOT ENOUGH MP / ON COOLDOWN: n). Rects: `{"icon_frame": [16, 12, 44, 44], "name": [66, 13], "name_scale": 2, "tag_right_margin": 8, "tag_y": 12, "cost_row": [66, 25], "target_row": [66, 35], "cd_row": [66, 45], "desc": [16, 62], "desc_line_h": 8, "desc_chars": 49, "strip_h": 14, "strip_margin_x": 8, "bottom_pad": 5}`. Mocks: `scene_test_portrait_skillcard(+_4x).png`, `ui/portrait/skill_card_examples(+_3x).png`. All copy is PLACEHOLDER.

## Greenmere regions (approved 2026-09-28)
Regions = `places[].kind` in data/region.json. Backdrops `combat/bg_<location>_portrait.png` (270x480, horizon y141, monster feet y222-266, calm below y300). New monsters (same 80x70 strips/anchors/anims) are listed in `manifest.json` under `monsters` with `status: approved`, and the full table is in `regions`. Approval sheets: `approval/backdrops_1x.png` / `_2x`, `approval/monster_lineup.png` / `_2x`, composite `scene_test_portrait_lantern_reach(+_4x).png`, extra `approval/scene_*.png`.

| location | region | lv | existing monsters | new | backdrop |
|---|---|---|---|---|---|
| Candlewick | town | 1 | (none, town) | - | combat/bg_candlewick_portrait.png |
| Millpond | meadow | 1 | puddleblob, thicket_imp | grinmud_toad | combat/bg_millpond_portrait.png |
| Briar Cross | meadow | 2 | cinder_mite, briar_hound, thicket_imp | bramblet | combat/bg_briar_cross_portrait.png |
| Lantern Reach | coast | 2 | lantern_wisp, cinder_mite, briar_hound | bottlecrab, squallgull, kelpback | combat/bg_lantern_reach_portrait.png |
| Howling Cleft | cave | 3 | cave_howler, marshlurker, briar_hound, lantern_wisp | gloomgrub, dripfang | combat/bg_howling_cleft_portrait.png |
| Gravel Keep | keep | 4 | gravel_brute, cave_howler, marshlurker, briar_hound | pebble_squire, hollow_helm, cobble_rat | combat/bg_gravel_keep_portrait.png |

| new monster | region | size | concept |
|---|---|---|---|
| Bramblet (`bramblet`) | meadow | regular | A rolling hedge-ball with leaf ears, berries and a grudge against anyone who cuts the Briar Cross hedge. |
| Grinmud Toad (`grinmud_toad`) | meadow | regular | The thing that grins from the Millpond mud: a squat brown toad with a lily-pad cap and far too many teeth. |
| Bottlecrab (`bottlecrab`) | coast | regular | A hermit crab that moved into a washed-up message bottle; snips first, reads never. |
| Squallgull (`squallgull`) | coast | regular | A scowling grey gull that drags its own tiny storm cloud around the lighthouse. |
| Kelpback Snapper (`kelpback`) | coast | large | A barnacled snapping turtle draped in kelp that hauls itself out of the shallows. |
| Gloomgrub (`gloomgrub`) | cave | regular | A pale segmented cave grub with glowing cyan spots and clacking mandibles. |
| Dripfang (`dripfang`) | cave | regular | A stalagmite that is not a stalagmite: yellow eyes, a stony maw, drips down its sides. |
| Pebble Squire (`pebble_squire`) | keep | regular | A pile of walking pebbles in a dented bucket helm with a wooden sword; the small stones that walk at dusk. |
| Hollow Helm (`hollow_helm`) | keep | regular | An empty great helm and two gauntlets floating over a tattered tabard, still keeping watch. |
| Cobble Rat (`cobble_rat`) | keep | regular | A courtyard rat wearing a patch of cobblestones as a shell. |

## Items + gear overlays (approved 2026-09-28, art/phase0-pack @7946500)
40 item icons `ui/items/<id>.png` (16x16, no rarity border, 1px #120c18 outline, pack palette) and 26 back-view gear overlays `paperdoll/gear/<id>.png` (48x78, anchor [24,77], same canvas as the seat doll; pixels under `chair_back` are cleared). Built by `tools/build_items.py` (art in `draft_items.py`, `draft_gear.py`). Approval: `approval/items_1x.png` / `items_4x.png`, `approval/gear_seated.png` / `gear_seated_4x.png` (+ `gear_seated_runtime_on_top.png`), `approval/gear_overlays(_3x).png`, composite `scene_test_portrait_gear(+_4x).png`.

**Seat layer order with gear:** `back/body_back_skin_<skin>` -> `back/outfit_back (tinted)` -> `back/class_back_<class> (class_back_<class>_noweapon when a main-hand weapon is equipped and the class has one, see class_noweapon)` -> `gear ARMOR: paperdoll/gear/<armor id>` -> `back/hair_back_<hair> (tinted, hat-clipped)` -> `back/class_back_<class>_hat` -> `gear OFF HAND: paperdoll/gear/<off id> (flip horizontally when the off-hand item is a weapon/dagger drawn for the main hand)` -> `gear MAIN HAND: paperdoll/gear/<main id> (a two-hander fills both hands; skip the off-hand)` -> `back/chair_back (always last; gear pixels under the chair are already cleared)` -> `ACTIVE: shift up 3px, then 1px #f8d040 outline around the union (includes the gear)`.

**Placement:** armor: shoulders + upper back; drawn after class_back and BEFORE hair/hood (long hair and hoods fall over the back plate); main1: held at the hero's right side (screen right, x40-47), pointing up/out past the shoulder; the lute is slung diagonally across the back instead; main2: staffs held upright at the right side (x40-48, top y1-16); bows, the gravel axe and Sunbrand slung diagonally across the back, top end over the right shoulder, lower end hidden by the chair; off: on the hero's left arm edge (screen left, x0-10, y40-67).

**Runtime note:** PaperDoll.show_gear() currently draws only main + armor, on top of the finished doll, stretched to the doll size. For these overlays: add the off hand, draw armor before hair/hat (see layer_order), and do not stretch them onto the 32x48 FRONT doll used on the gear screen (these are back-view art).

### Weapon-less class layers (class_noweapon, draft pending approval)
**Rule:** When the hero has a main-hand weapon equipped, draw paperdoll/back/class_back_<class>_noweapon.png instead of class_back_<class>.png (the class art has its own baked weapon that would double up with the gear overlay). The prebuilt default seats party/seat_<class>_idle/active_noweapon.png are the same swap applied to seat_recipe. Classes not listed (cleric, rogue) have no baked weapon: always use class_back_<class>. Nothing else changes: same 48x78 canvas, anchor [24,77], layer slot and hat layer.

tools/build_doll.py class_back(c, noweapon=True): the weapon parts are the last parts of each class layer and are skipped, so every other pixel is identical to class_back_<class> (the arm/robe/cape under the weapon is already fully drawn). Check sheet: `approval/class_noweapon_check.png` / `_4x.png` (shipped seat / noweapon / noweapon + Oath Blade, Sap Crook, Reed Staff, Gravel Axe, Road Lute, Thorn Bow).

| class | removed | noweapon layer | seats |
|---|---|---|---|
| paladin | sword at the left hip | paperdoll/back/class_back_paladin_noweapon.png | party/seat_paladin_idle_noweapon.png, party/seat_paladin_active_noweapon.png |
| druid | leaf-topped staff and the hand holding it (left) | paperdoll/back/class_back_druid_noweapon.png | party/seat_druid_idle_noweapon.png, party/seat_druid_active_noweapon.png |
| wizard | orb staff and the hand holding it (right) | paperdoll/back/class_back_wizard_noweapon.png | party/seat_wizard_idle_noweapon.png, party/seat_wizard_active_noweapon.png |
| barbarian | axe across the back (haft + head; the crossed harness straps stay) | paperdoll/back/class_back_barbarian_noweapon.png | party/seat_barbarian_idle_noweapon.png, party/seat_barbarian_active_noweapon.png |
| bard | lute at the right (body, neck, pegs) | paperdoll/back/class_back_bard_noweapon.png | party/seat_bard_idle_noweapon.png, party/seat_bard_active_noweapon.png |
| ranger | bow and the hand holding it (left; quiver and fletching stay) | paperdoll/back/class_back_ranger_noweapon.png | party/seat_ranger_idle_noweapon.png, party/seat_ranger_active_noweapon.png |

| id | name | slot | rarity | icon | doll | visual |
|---|---|---|---|---|---|---|
| oath_blade | Oath Blade | weapon | common | ui/items/oath_blade.png | paperdoll/gear/oath_blade.png | plain short steel sword, gold vow line in the fuller |
| chapel_mace | Chapel Mace | weapon | common | ui/items/chapel_mace.png | paperdoll/gear/chapel_mace.png | flanged steel ball on a wooden haft, small gold cross |
| reed_staff | Reed Staff | weapon | common | ui/items/reed_staff.png | paperdoll/gear/reed_staff.png | jointed pale reed with copper wire bands and a green tuft |
| sap_crook | Sap Crook | weapon | common | ui/items/sap_crook.png | paperdoll/gear/sap_crook.png | hooked shepherd crook, leaf sprout and an amber sap drip |
| thorn_bow | Thorn Bow | weapon | common | ui/items/thorn_bow.png | paperdoll/gear/thorn_bow.png | simple wooden bow with thorn nubs, cream string |
| pocket_knife | Pocket Knife | weapon | common | ui/items/pocket_knife.png | paperdoll/gear/pocket_knife.png | tiny folding knife, wooden handle with rivet (smallest blade) |
| road_lute | Road Lute | weapon | common | ui/items/road_lute.png | paperdoll/gear/road_lute.png | pear-shaped wooden lute, dark sound hole, cream strings |
| gravel_axe | Gravel Axe | weapon | common | ui/items/gravel_axe.png | paperdoll/gear/gravel_axe.png | long haft, chipped grey stone-like axe head |
| kiln_sword | Kiln Sword | weapon | rare | ui/items/kiln_sword.png | paperdoll/gear/kiln_sword.png | longer, wider blade with a blued edge; brick-red guard and grip |
| lamp_staff | Lamp Staff | weapon | rare | ui/items/lamp_staff.png | paperdoll/gear/lamp_staff.png | staff topped with a glowing gold lantern |
| marsh_bow | Marsh Bow | weapon | rare | ui/items/marsh_bow.png | paperdoll/gear/marsh_bow.png | dark-green waxed recurve, wrapped grip, sky string sparks |
| night_shard | Night Shard | weapon | rare | ui/items/night_shard.png | paperdoll/gear/night_shard.png | jagged black-violet glass shard on a blue grip |
| sunbrand | Sunbrand | weapon | legendary | ui/items/sunbrand.png | paperdoll/gear/sunbrand.png | full-diagonal gold greatsword, long guard, red sun gem, glints |
| howl_fang | Howl Fang | weapon | unique | ui/items/howl_fang.png | paperdoll/gear/howl_fang.png | a curved bone fang bound to a cord |
| kettle_shield | Kettle Shield | off | common | ui/items/kettle_shield.png | paperdoll/gear/kettle_shield.png | dented grey pot lid with a knob handle |
| hymn_board | Hymn Board | off | common | ui/items/hymn_board.png | paperdoll/gear/hymn_board.png | arched wooden board with faded verse lines and a gold cross |
| glass_orb | Glass Orb | off | common | ui/items/glass_orb.png | paperdoll/gear/glass_orb.png | clear glass ball with a gold spark inside, on a wooden stand |
| oak_buckler | Oak Buckler | off | rare | ui/items/oak_buckler.png | paperdoll/gear/oak_buckler.png | round oak with an iron rim, studs and an iron rose boss |
| void_lens | Void Lens | off | rare | ui/items/void_lens.png | paperdoll/gear/void_lens.png | gold-framed hand lens full of dark violet void and a star |
| travel_coat | Travel Coat | armor | common | ui/items/travel_coat.png | paperdoll/gear/travel_coat.png | long brown waxed coat, tan collar, gold buttons |
| reed_wrap | Reed Wrap | armor | common | ui/items/reed_wrap.png | paperdoll/gear/reed_wrap.png | green marsh cloak with woven tan reed strands |
| hedge_mail | Hedge Mail | armor | common | ui/items/hedge_mail.png | paperdoll/gear/hedge_mail.png | hedge-green jack studded with silver rings, leather belt |
| kiln_plate | Kiln Plate | armor | common | ui/items/kiln_plate.png | paperdoll/gear/kiln_plate.png | brick-red breastplate and pauldrons, amber rivets |
| moon_robe | Moon Robe | armor | rare | ui/items/moon_robe.png | paperdoll/gear/moon_robe.png | pale robe with violet V-neck and hem, gold crescent |
| keep_plate | Keep Plate | armor | rare | ui/items/keep_plate.png | paperdoll/gear/keep_plate.png | broad steel plate, double pauldrons, gold trim (heaviest silhouette) |
| lurker_scale | Bone Plate | armor | unique | ui/items/lurker_scale.png | paperdoll/gear/lurker_scale.png | pale bone rib-plate with knuckle-bone pauldrons |
| bread_charm | Bread Charm | trinket | common | ui/items/bread_charm.png | - | bread crust bound with a red thread cross, on a loop |
| wick_ring | Wick Ring | trinket | common | ui/items/wick_ring.png | - | copper ring with a tiny candle stub and flame |
| pond_bead | Pond Bead | trinket | rare | ui/items/pond_bead.png | - | mill-water teal glass bead on a cord |
| threat_bell | Threat Bell | trinket | rare | ui/items/threat_bell.png | - | gold bell with a red ribbon and dark clapper |
| ley_locket | Ley Locket | trinket | legendary | ui/items/ley_locket.png | - | gold heart locket with a violet gem, chain and glints |
| blob_crown | Grinning Crown | trinket | unique | ui/items/blob_crown.png | - | blue slime crown with a grin and drips |
| brute_heart | Brute Heart | trinket | unique | ui/items/brute_heart.png | - | grey stone heart with glowing orange cracks |
| wisp_jar | Cap Jar | trinket | unique | ui/items/wisp_jar.png | - | corked glass jar holding an orange glow |
| tonic | Hearth Tonic | usable | common | ui/items/tonic.png | - | round glass flask of red tonic, cork |
| vial | Lamp Vial | usable | common | ui/items/vial.png | - | slim blue vial with a gold collar |
| loaf_crumb | Loaf Crumb | usable | common | ui/items/loaf_crumb.png | - | torn chunk of brown loaf |
| blue_ether | Blue Ether | usable | rare | ui/items/blue_ether.png | - | bigger blue flask, gold collar and cork, sparkles |
| field_salve | Field Salve | usable | rare | ui/items/field_salve.png | - | silver salve tin with a red cross and a herb sprig |
| kettle_dram | Kettle Dram | usable | common | ui/items/kettle_dram.png | - | little copper kettle, half red / half blue contents, steam |

## Skill FX
| strip | frame size | frames | fps | anchor | loop / segments | notes |
|---|---|---|---|---|---|---|
| fx/fx_buff_aura.png | 56x72 | 6 | 10 | [28, 71] | true | gold rising aura + chevrons; anchor on feet. Draw the whole strip BEHIND the seat for a softer look, or in front (ring front arc overlaps feet). |
| fx/fx_fireball.png | 48x48 | 8 | 14 | [24, 24] | {"travel": {"frames": [0, 1, 2], "fps": 12, "loop": true, "notes": "projectile faces +x; tween the sprite from caster to target, rotate/flip toward the target"}, "burst": {"frames": [3, 4, 5, 6, 7], "fps": 14, "loop": false, "notes": "play at the target centre; frame 4 = impact"}} | one strip: travel loop (0-2) + burst (3-7). Same 48x48 cell for both, anchor = ball/burst centre. |
| fx/fx_heal_sparkle.png | 48x64 | 6 | 10 | [24, 63] | true | anchor on the seat/monster feet (bottom-centre). Loop 1-2x. Heal colour lime #b4dc62; pair with ui/dmg_font_heal. |
| fx/fx_lightning.png | 32x96 | 5 | 16 | [16, 95] | false | strike from above; anchor = impact point at the target feet (bottom-centre). Frame 2 = impact flash. Hold frame 1-2 alternation for longer zaps. |
| fx/fx_poison_cloud.png | 56x48 | 6 | 8 | [28, 36] | false | toxic purple puffs with acid-green bubbles (purple keeps it readable over the green meadow); anchor ~ target waist/centre. Frames 2-3 can loop while a DoT ticks. |
| fx/fx_shield.png | 56x72 | 5 | 10 | [28, 71] | {"form": {"frames": [0, 1], "loop": false}, "hold": {"frames": [2, 3, 4], "loop": true}} | force bubble around a 48x70 seat/monster; anchor on feet. Play 0-1 once then loop 2-4 while the shield lasts; pixel-hex fill keeps the target visible (binary alpha). |
| fx/fx_slash.png | 48x48 | 5 | 20 | [24, 24] | false | diagonal arc sweep; centre anchor on the target body (e.g. monster centre). Flip h for the other direction. Frame 2 = impact (spawn damage number / hit anim). |
| fx/mana_tick.png | 16x28 | 6 | 10 | [8, 27] | false | subtle MP-regen tick in the MP colour #4c9ce8: blue sparkles rising. Anchor at the seat feet/centre or on the MP bar of the card; play once per regen tick. Pair with fx/mp_plus.png. |
| fx/mp_plus.png | 19x14 | 4 | 8 | [9, 13] | false | '+MP' float in MP colours: rises 1px/frame, last frame dithered out. For numbers use dmg_font_mp + dmg_font_mp_letters instead. |
| fx/taunt_aura.png | 56x16 | 3 | 6 | [28, 8] | true | optional subtle red ground ring for a taunting seat/monster; centre it on the feet row (seat anchor) and draw BEHIND the sprite. |
| fx/taunt_badge.png | 12x13 | 2 | 3 | [6, 12] | true | overhead taunt/aggro badge (red "!" shout). Place the anchor ~2px above the top of the seat/monster sprite (e.g. seat top y = feet-78+hat). 1px bob. Has a dark outline like UI icons. |

FX style: no black outline (glow effects); bright core stepping to a darker coloured rim, binary alpha, fades via ordered dither. `fx_test_portrait.png` shows one frame of each at native scale.

**Legacy (landscape-only):** `combat/bg_forest.png`, `combat/table.png`, `scene_test.png`, `scene_test_4x.png`, `ui/bar_bg.png`, `ui/bar_hp.png`, `ui/bar_mp.png`, `ui/btn_attack.png`, `ui/btn_attack_active.png`, `ui/btn_cover.png`, `ui/btn_cover_active.png`, `ui/btn_item.png`, `ui/btn_item_active.png`, `ui/btn_run.png`, `ui/btn_run_active.png`, `ui/btn_skill.png`, `ui/btn_skill_active.png`, `ui/hp_mp_card.png`, `ui/portrait/action_bar.png`, `ui/portrait/bar_bg_90.png`, `ui/portrait/bar_hp_44.png`, `ui/portrait/bar_hp_88.png`, `ui/portrait/bar_mp_44.png`, `ui/portrait/bar_mp_88.png`, `ui/portrait/btn32_attack.png`, `ui/portrait/btn32_attack_active.png`, `ui/portrait/btn32_cover.png`, `ui/portrait/btn32_cover_active.png`, `ui/portrait/btn32_item.png`, `ui/portrait/btn32_item_active.png`, `ui/portrait/btn32_run.png`, `ui/portrait/btn32_run_active.png`, `ui/portrait/btn32_skill.png`, `ui/portrait/btn32_skill_active.png`, `ui/portrait/hp_mp_card_compact.png`, `ui/portrait/hp_mp_card_compact_active.png`, `ui/portrait/hp_mp_card_narrow.png`

## Files
| path | size | frames | frame size | fps | anchor | extra | notes |
|---|---|---|---|---|---|---|---|
| approval/backdrops_1x.png | 1662x506 | 1 | 1662x506 |  |  | status=approved | APPROVAL SHEET (not runtime): the 6 Greenmere location backdrops at 1x, labelled name / region / level. |
| approval/backdrops_2x.png | 3324x1012 | 1 | 3324x1012 |  |  | status=approved | 2x nearest of approval/backdrops_1x.png. |
| approval/class_noweapon_check.png | 332x318 | 1 | 332x318 |  |  | status=draft_pending_approval | APPROVAL SHEET: the 6 classes with a baked weapon (paladin, druid, wizard, barbarian, bard, ranger): shipped seat, the same seat built with class_back_<c>_noweapon, and noweapon + a typical main-hand weapon (paladin Oath Blade, druid Sap Crook, wizard Reed Staff, barbarian Gravel Axe, bard Road Lute, ranger Thorn Bow); all composed in the recommended seat_recipe order (steps_with_gear). |
| approval/class_noweapon_check_4x.png | 1328x1272 | 1 | 1328x1272 |  |  | status=draft_pending_approval | 4x nearest of approval/class_noweapon_check.png. |
| approval/gear_overlays.png | 684x192 | 1 | 684x192 |  |  | status=approved | QA: each of the 26 overlays on the rogue seat (the one class with no baked weapon, so each overlay is seen alone). |
| approval/gear_overlays_3x.png | 2052x576 | 1 | 2052x576 |  |  | status=approved | 3x nearest. |
| approval/gear_seated.png | 440x496 | 1 | 440x496 |  |  | status=approved | APPROVAL SHEET: all 8 classes seated (back view) bare, with a class loadout, heavy plate + two-hander, plate + sword + shield, and robe + staff; recommended layer order (armor under hair/hat, weapons over, chair last). Off-hand daggers are drawn mirrored. |
| approval/gear_seated_4x.png | 1760x1984 | 1 | 1760x1984 |  |  | status=approved | 4x nearest of approval/gear_seated.png. |
| approval/gear_seated_runtime_on_top.png | 440x496 | 1 | 440x496 |  |  | status=approved | QA: the same rows drawn the way PaperDoll.show_gear() currently does it (every overlay on top of the finished doll), to show the hair/hood clash. |
| approval/gear_seats/seat_cleric_active.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved | QA seat: cleric wearing hedge_mail, chapel_mace, hymn_board (recommended layer order). Used by scene_test_portrait_gear.png. |
| approval/gear_seats/seat_cleric_idle.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved | QA seat: cleric wearing hedge_mail, chapel_mace, hymn_board (recommended layer order). Used by scene_test_portrait_gear.png. |
| approval/gear_seats/seat_druid_active.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved | QA seat: druid wearing reed_wrap, sap_crook (recommended layer order). Used by scene_test_portrait_gear.png. |
| approval/gear_seats/seat_druid_idle.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved | QA seat: druid wearing reed_wrap, sap_crook (recommended layer order). Used by scene_test_portrait_gear.png. |
| approval/gear_seats/seat_paladin_active.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved | QA seat: paladin wearing keep_plate, oath_blade, kettle_shield (recommended layer order). Used by scene_test_portrait_gear.png. |
| approval/gear_seats/seat_paladin_idle.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved | QA seat: paladin wearing keep_plate, oath_blade, kettle_shield (recommended layer order). Used by scene_test_portrait_gear.png. |
| approval/gear_seats/seat_rogue_active.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved | QA seat: rogue wearing travel_coat, night_shard, pocket_knife (recommended layer order). Used by scene_test_portrait_gear.png. |
| approval/gear_seats/seat_rogue_idle.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved | QA seat: rogue wearing travel_coat, night_shard, pocket_knife (recommended layer order). Used by scene_test_portrait_gear.png. |
| approval/gear_seats/seat_wizard_active.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved | QA seat: wizard wearing moon_robe, lamp_staff (recommended layer order). Used by scene_test_portrait_gear.png. |
| approval/gear_seats/seat_wizard_idle.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved | QA seat: wizard wearing moon_robe, lamp_staff (recommended layer order). Used by scene_test_portrait_gear.png. |
| approval/items_1x.png | 470x272 | 1 | 470x272 |  |  | status=approved | APPROVAL SHEET: all 40 item icons at 1x grouped by slot, labelled name / rarity / id (rarity colour on the label only; the icons have no border). |
| approval/items_4x.png | 1880x1088 | 1 | 1880x1088 |  |  | status=approved | 4x nearest of approval/items_1x.png. |
| approval/monster_lineup.png | 656x488 | 1 | 656x488 |  |  | status=approved | APPROVAL SHEET (not runtime): monsters grouped by region (existing first, NEW drafts tagged gold), each on a crop of its region backdrop stand zone; existing ones show the pack sprite that data/monsters.json maps them to. |
| approval/monster_lineup_2x.png | 1312x976 | 1 | 1312x976 |  |  | status=approved | 2x nearest of approval/monster_lineup.png. |
| approval/scene_briar_cross.png | 270x480 | 1 | 270x480 |  |  | status=approved | QA composite (not runtime): briar_cross backdrop with bramblet, briar_hound, grinmud_toad and the full portrait UI. |
| approval/scene_gravel_keep.png | 270x480 | 1 | 270x480 |  |  | status=approved | QA composite (not runtime): gravel_keep backdrop with pebble_squire, gravel_brute, hollow_helm and the full portrait UI. |
| approval/scene_howling_cleft.png | 270x480 | 1 | 270x480 |  |  | status=approved | QA composite (not runtime): howling_cleft backdrop with gloomgrub, marshlurker, dripfang and the full portrait UI. |
| combat/bg_briar_cross_portrait.png | 270x480 | 1 | 270x480 |  | [0, 0] | status=approved, location=briar_cross, location_name=Briar Cross, region=meadow, horizon_y=141, monster_feet_band=[222, 266], approval=approved 2026-09-28 by Kyle (via Chief of Staff); pushed to art/phase0-pack @ 122a66a | Briar Cross (meadow) combat backdrop, 270x480, same framing as bg_forest_portrait: sky/landmarks above the horizon (y141), monster stand zone y~180-270 kept low-contrast, calmer texture below y~300 (table y343-382, seats and bars below). Procedural, flat shading, pack palette, alpha 255. |
| combat/bg_candlewick_portrait.png | 270x480 | 1 | 270x480 |  | [0, 0] | status=approved, location=candlewick, location_name=Candlewick, region=town, horizon_y=141, monster_feet_band=[222, 266], approval=approved 2026-09-28 by Kyle (via Chief of Staff); pushed to art/phase0-pack @ 122a66a | Candlewick (town) combat backdrop, 270x480, same framing as bg_forest_portrait: sky/landmarks above the horizon (y141), monster stand zone y~180-270 kept low-contrast, calmer texture below y~300 (table y343-382, seats and bars below). Procedural, flat shading, pack palette, alpha 255. Candlewick has no monsters in data/region.json (town / inn); backdrop provided for completeness. |
| combat/bg_forest.png | 480x270 | 1 | 480x270 |  | [0, 0] | legacy=true | LEGACY (landscape 480x270): use combat/bg_forest_portrait.png. 480x270 full-screen backdrop; sky/treeline top, meadow starts ~y108; place monster feet on y~115-135 (upper half). Rows 214-269 are a mirrored meadow band (normally hidden by table/UI). |
| combat/bg_forest_portrait.png | 270x480 | 1 | 270x480 |  | [0, 0] | meadow_start_y=141, monster_feet_band=[150, 200] | PORTRAIT 270x480 backdrop recomposed from the same forest source: sky 0-~40, tree line to y~141, meadow below. v3: rows ~196-479 are a seamless procedural meadow (value-noise grass clumps, tufts, scattered dirt patches), dither-blended into the source meadow over y196-231. No repeats or mirror lines. |
| combat/bg_gravel_keep_portrait.png | 270x480 | 1 | 270x480 |  | [0, 0] | status=approved, location=gravel_keep, location_name=Gravel Keep, region=keep, horizon_y=141, monster_feet_band=[222, 266], approval=approved 2026-09-28 by Kyle (via Chief of Staff); pushed to art/phase0-pack @ 122a66a | Gravel Keep (keep) combat backdrop, 270x480, same framing as bg_forest_portrait: sky/landmarks above the horizon (y141), monster stand zone y~180-270 kept low-contrast, calmer texture below y~300 (table y343-382, seats and bars below). Procedural, flat shading, pack palette, alpha 255. |
| combat/bg_howling_cleft_portrait.png | 270x480 | 1 | 270x480 |  | [0, 0] | status=approved, location=howling_cleft, location_name=Howling Cleft, region=cave, horizon_y=141, monster_feet_band=[222, 266], approval=approved 2026-09-28 by Kyle (via Chief of Staff); pushed to art/phase0-pack @ 122a66a | Howling Cleft (cave) combat backdrop, 270x480, same framing as bg_forest_portrait: sky/landmarks above the horizon (y141), monster stand zone y~180-270 kept low-contrast, calmer texture below y~300 (table y343-382, seats and bars below). Procedural, flat shading, pack palette, alpha 255. |
| combat/bg_lantern_reach_portrait.png | 270x480 | 1 | 270x480 |  | [0, 0] | status=approved, location=lantern_reach, location_name=Lantern Reach, region=coast, horizon_y=141, monster_feet_band=[222, 266], approval=approved 2026-09-28 by Kyle (via Chief of Staff); pushed to art/phase0-pack @ 122a66a | Lantern Reach (coast) combat backdrop, 270x480, same framing as bg_forest_portrait: sky/landmarks above the horizon (y141), monster stand zone y~180-270 kept low-contrast, calmer texture below y~300 (table y343-382, seats and bars below). Procedural, flat shading, pack palette, alpha 255. |
| combat/bg_millpond_portrait.png | 270x480 | 1 | 270x480 |  | [0, 0] | status=approved, location=millpond, location_name=Millpond, region=meadow, horizon_y=141, monster_feet_band=[222, 266], approval=approved 2026-09-28 by Kyle (via Chief of Staff); pushed to art/phase0-pack @ 122a66a | Millpond (meadow) combat backdrop, 270x480, same framing as bg_forest_portrait: sky/landmarks above the horizon (y141), monster stand zone y~180-270 kept low-contrast, calmer texture below y~300 (table y343-382, seats and bars below). Procedural, flat shading, pack palette, alpha 255. |
| combat/d20_nat20.png | 24x24 | 1 | 24x24 |  | [12, 23] |  | gold natural-20 result frame (swap in for frame 3 on a nat 20). |
| combat/d20_results.png | 480x24 | 20 | 24x24 |  | [12, 23] |  | result faces: frame i shows number i+1 (bold 5x7 digits in #120c18 on a white triangle). |
| combat/d20_roll.png | 96x24 | 4 | 24x24 | 12 | [12, 23] |  | v2 24x24. Loop frames 0-2 while tumbling (flat/pointy silhouettes alternate), then land on frame 3 (legible 20) or swap in the rolled face from d20_results.png. |
| combat/d6_all.png | 48x48 | 1 | 8x8 |  |  |  | 6x6 grid: rows white,red,blue,green,yellow,black; columns faces 1-6. |
| combat/d6_black.png | 48x8 | 6 | 8x8 | 12 | [4, 7] |  | frame i = face i+1. Cycle randomly while rolling, stop on the result face. |
| combat/d6_blue.png | 48x8 | 6 | 8x8 | 12 | [4, 7] |  | frame i = face i+1. Cycle randomly while rolling, stop on the result face. |
| combat/d6_green.png | 48x8 | 6 | 8x8 | 12 | [4, 7] |  | frame i = face i+1. Cycle randomly while rolling, stop on the result face. |
| combat/d6_red.png | 48x8 | 6 | 8x8 | 12 | [4, 7] |  | frame i = face i+1. Cycle randomly while rolling, stop on the result face. |
| combat/d6_white.png | 48x8 | 6 | 8x8 | 12 | [4, 7] |  | frame i = face i+1. Cycle randomly while rolling, stop on the result face. |
| combat/d6_yellow.png | 48x8 | 6 | 8x8 | 12 | [4, 7] |  | frame i = face i+1. Cycle randomly while rolling, stop on the result face. |
| combat/gm_idle.png | 44x46 | 1 | 44x46 |  | [22, 45] |  | bottom-centre anchor; place so the table overlaps his hands (bottom ~8px). |
| combat/gm_screen.png | 35x30 | 1 | 35x30 |  | [17, 29] |  | bottom-centre anchor; stands on the table top in front of the GM. |
| combat/gm_strip.png | 88x46 | 2 | 44x46 | 6 | [22, 45] |  | frame0 idle, frame1 talk (mouth open + 1px head bob); alternate while GM speaks. |
| combat/gm_talk.png | 44x46 | 1 | 44x46 |  | [22, 45] |  | bottom-centre anchor; place so the table overlaps his hands (bottom ~8px). |
| combat/table.png | 300x44 | 1 | 300x44 |  | [150, 43] | top_surface_rows=[1, 13], near_edge_y=14, apron_rows=[15, 20], legacy=true | LEGACY (landscape 480x270): use combat/table_portrait.png (250x40). v2 procedural 300x44, calm grain. Bottom-centre anchor. |
| combat/table_portrait.png | 266x40 | 1 | 266x40 |  | [133, 39] | top_surface_rows=[1, 12], near_edge_y=13, apron_rows=[14, 19] | PORTRAIT table (v5: widened 250->266 for a 5-seat party), procedural 266x40: 3 long planks, 3 flat wood tones, tan highlight lip on the near edge. Bottom-centre anchor; GM hands/props sit on the top surface rows. |
| contact_sheet.png | 2400x23574 | 1 | 2400x23574 |  |  |  | every primary asset at 3x nearest (items <=8px shown at an extra 2x). paperdoll/tinted/* variants are represented by the ramp previews and paperdoll_preview.png. |
| creator_test_portrait.png | 270x480 | 1 | 270x480 |  |  |  | PORTRAIT 270x480 mock built only from pack files (QA). |
| creator_test_portrait_4x.png | 1080x1920 | 1 | 1080x1920 |  |  |  | 4x nearest upscale. |
| fx/fx_buff_aura.png | 336x72 | 6 | 56x72 | 10 | [28, 71] | style=no black outline (glow FX): bright core -> darker coloured rim, binary alpha, fades via ordered dither | gold rising aura + chevrons; anchor on feet. Draw the whole strip BEHIND the seat for a softer look, or in front (ring front arc overlaps feet). |
| fx/fx_fireball.png | 384x48 | 8 | 48x48 | 14 | [24, 24] | segments={"travel": {"frames": [0, 1, 2], "fps": 12, "loop": true, "notes": "projectile faces +x; tween the sprite from caster to target, rotate/flip toward the target"}, "burst": {"frames": [3, 4, 5, 6, 7], "fps": 14, "loop": false, "notes": "play at the target centre; frame 4 = impact"}}, style=no black outline (glow FX): bright core -> darker coloured rim, binary alpha, fades via ordered dither | one strip: travel loop (0-2) + burst (3-7). Same 48x48 cell for both, anchor = ball/burst centre. |
| fx/fx_heal_sparkle.png | 288x64 | 6 | 48x64 | 10 | [24, 63] | style=no black outline (glow FX): bright core -> darker coloured rim, binary alpha, fades via ordered dither | anchor on the seat/monster feet (bottom-centre). Loop 1-2x. Heal colour lime #b4dc62; pair with ui/dmg_font_heal. |
| fx/fx_lightning.png | 160x96 | 5 | 32x96 | 16 | [16, 95] | style=no black outline (glow FX): bright core -> darker coloured rim, binary alpha, fades via ordered dither | strike from above; anchor = impact point at the target feet (bottom-centre). Frame 2 = impact flash. Hold frame 1-2 alternation for longer zaps. |
| fx/fx_poison_cloud.png | 336x48 | 6 | 56x48 | 8 | [28, 36] | style=no black outline (glow FX): bright core -> darker coloured rim, binary alpha, fades via ordered dither | toxic purple puffs with acid-green bubbles (purple keeps it readable over the green meadow); anchor ~ target waist/centre. Frames 2-3 can loop while a DoT ticks. |
| fx/fx_shield.png | 280x72 | 5 | 56x72 | 10 | [28, 71] | segments={"form": {"frames": [0, 1], "loop": false}, "hold": {"frames": [2, 3, 4], "loop": true}}, style=no black outline (glow FX): bright core -> darker coloured rim, binary alpha, fades via ordered dither | force bubble around a 48x70 seat/monster; anchor on feet. Play 0-1 once then loop 2-4 while the shield lasts; pixel-hex fill keeps the target visible (binary alpha). |
| fx/fx_slash.png | 240x48 | 5 | 48x48 | 20 | [24, 24] | style=no black outline (glow FX): bright core -> darker coloured rim, binary alpha, fades via ordered dither | diagonal arc sweep; centre anchor on the target body (e.g. monster centre). Flip h for the other direction. Frame 2 = impact (spawn damage number / hit anim). |
| fx/mana_tick.png | 96x28 | 6 | 16x28 | 10 | [8, 27] | style=no black outline (glow FX): bright core -> darker coloured rim, binary alpha, fades via ordered dither | subtle MP-regen tick in the MP colour #4c9ce8: blue sparkles rising. Anchor at the seat feet/centre or on the MP bar of the card; play once per regen tick. Pair with fx/mp_plus.png. |
| fx/mp_plus.png | 76x14 | 4 | 19x14 | 8 | [9, 13] | style=no black outline (glow FX): bright core -> darker coloured rim, binary alpha, fades via ordered dither | '+MP' float in MP colours: rises 1px/frame, last frame dithered out. For numbers use dmg_font_mp + dmg_font_mp_letters instead. |
| fx/taunt_aura.png | 168x16 | 3 | 56x16 | 6 | [28, 8] | style=no black outline (glow FX): bright core -> darker coloured rim, binary alpha, fades via ordered dither | optional subtle red ground ring for a taunting seat/monster; centre it on the feet row (seat anchor) and draw BEHIND the sprite. |
| fx/taunt_badge.png | 24x13 | 2 | 12x13 | 3 | [6, 12] | style=no black outline (glow FX): bright core -> darker coloured rim, binary alpha, fades via ordered dither | overhead taunt/aggro badge (red "!" shout). Place the anchor ~2px above the top of the seat/monster sprite (e.g. seat top y = feet-78+hat). 1px bob. Has a dark outline like UI icons. |
| fx_test_portrait.png | 270x360 | 1 | 270x360 |  |  |  | QA: one representative frame of each FX on monsters (fx centred on body, lightning/heal/buff/shield on feet) and composed seats, at native scale. |
| fx_test_portrait_3x.png | 810x1080 | 1 | 810x1080 |  |  |  | 3x nearest. |
| map/loc_castle.png | 32x32 | 1 | 32x32 |  | [16, 28] |  | 32x32; anchor = node centre on the round ground base. |
| map/loc_cave.png | 32x32 | 1 | 32x32 |  | [16, 28] |  | 32x32; anchor = node centre on the round ground base. |
| map/loc_shrine.png | 32x32 | 1 | 32x32 |  | [16, 28] |  | 32x32; anchor = node centre on the round ground base. |
| map/loc_tavern.png | 32x32 | 1 | 32x32 |  | [16, 28] |  | 32x32; anchor = node centre on the round ground base. |
| map/loc_village.png | 32x32 | 1 | 32x32 |  | [16, 28] |  | 32x32; anchor = node centre on the round ground base. |
| map/loc_windmill.png | 32x32 | 1 | 32x32 |  | [16, 28] |  | 32x32; anchor = node centre on the round ground base. |
| map/marker_arrow.png | 18x12 | 2 | 9x12 | 3 | [4, 11] |  | destination marker, bottom tip at the anchor; 2px bob. |
| map/pawn_walk.png | 96x20 | 4 | 24x20 | 8 | [12, 19] |  | faces right; flip_h for left. Bottom-centre (hooves). |
| map/tile_bridge_h.png | 16x16 | 1 | 16x16 |  | [0, 0] |  | 16x16 seamless. road E-W over a N-S river; joins road_h and river_v. |
| map/tile_bridge_v.png | 16x16 | 1 | 16x16 |  | [0, 0] |  | 16x16 seamless. bridge_h rotated 90 (road N-S over an E-W river). |
| map/tile_grass.png | 16x16 | 1 | 16x16 |  | [0, 0] |  | 16x16 seamless.  |
| map/tile_grass_flowers.png | 16x16 | 1 | 16x16 |  | [0, 0] |  | 16x16 seamless.  |
| map/tile_river_corner.png | 16x16 | 1 | 16x16 |  | [0, 0] |  | 16x16 seamless. connects EAST+SOUTH; flips give the other 3 rotations. |
| map/tile_river_h.png | 16x16 | 1 | 16x16 |  | [0, 0] |  | 16x16 seamless.  |
| map/tile_river_v.png | 16x16 | 1 | 16x16 |  | [0, 0] |  | 16x16 seamless. river_h rotated 90. |
| map/tile_road_corner.png | 16x16 | 1 | 16x16 |  | [0, 0] |  | 16x16 seamless. connects EAST+SOUTH; flip_h -> W+S, flip_v -> E+N, flip_h+flip_v -> W+N. |
| map/tile_road_corner_en.png | 16x16 | 1 | 16x16 |  | [0, 0] |  | road corner joining EN (pre-flipped copy). |
| map/tile_road_corner_es.png | 16x16 | 1 | 16x16 |  | [0, 0] |  | road corner joining ES (pre-flipped copy). |
| map/tile_road_corner_wn.png | 16x16 | 1 | 16x16 |  | [0, 0] |  | road corner joining WN (pre-flipped copy). |
| map/tile_road_corner_ws.png | 16x16 | 1 | 16x16 |  | [0, 0] |  | road corner joining WS (pre-flipped copy). |
| map/tile_road_cross.png | 16x16 | 1 | 16x16 |  | [0, 0] |  | 16x16 seamless.  |
| map/tile_road_h.png | 16x16 | 1 | 16x16 |  | [0, 0] |  | 16x16 seamless.  |
| map/tile_road_t.png | 16x16 | 1 | 16x16 |  | [0, 0] |  | 16x16 seamless. T-junction joining EAST+WEST+SOUTH; flip_v -> E+W+N; see tile_road_t_* for the vertical variants. |
| map/tile_road_t_ewn.png | 16x16 | 1 | 16x16 |  | [0, 0] |  | T-junction joining EWN (pre-rotated copy). |
| map/tile_road_t_ews.png | 16x16 | 1 | 16x16 |  | [0, 0] |  | T-junction joining EWS (pre-rotated copy). |
| map/tile_road_t_nse.png | 16x16 | 1 | 16x16 |  | [0, 0] |  | T-junction joining NSE (pre-rotated copy). |
| map/tile_road_t_nsw.png | 16x16 | 1 | 16x16 |  | [0, 0] |  | T-junction joining NSW (pre-rotated copy). |
| map/tile_road_v.png | 16x16 | 1 | 16x16 |  | [0, 0] |  | 16x16 seamless. road_h rotated 90. |
| map/tiles_preview.png | 128x112 | 1 | 128x112 |  |  |  | QA preview showing tiles assembled (not a runtime asset). |
| map_test_portrait.png | 270x480 | 1 | 270x480 |  |  |  | PORTRAIT 270x480 mock built only from pack files (QA). |
| map_test_portrait_4x.png | 1080x1920 | 1 | 1080x1920 |  |  |  | 4x nearest upscale. |
| monsters/bat/bat_attack.png | 240x70 | 3 | 80x70 | 5 | [40, 64] | hp_bar_anchor=[40, 22], portrait_rect=[30, 28, 20, 20] |  |
| monsters/bat/bat_death.png | 320x70 | 4 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 22], portrait_rect=[30, 28, 20, 20] |  |
| monsters/bat/bat_hit.png | 160x70 | 2 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 22], portrait_rect=[30, 28, 20, 20] |  |
| monsters/bat/bat_idle.png | 160x70 | 2 | 80x70 | 2 | [40, 64] | hp_bar_anchor=[40, 22], portrait_rect=[30, 28, 20, 20] |  |
| monsters/bat/bat_portrait.png | 20x20 | 1 | 20x20 |  |  |  | 20x20 head crop (rect [30, 28, 20, 20] of the rest frame) for the initiative strip. |
| monsters/bat/bat_still.png | 80x70 | 1 | 80x70 |  | [40, 64] | hp_bar_anchor=[40, 22] | single rest frame (portraits / initiative). |
| monsters/bottlecrab/bottlecrab_attack.png | 240x70 | 3 | 80x70 | 5 | [40, 64] | hp_bar_anchor=[40, 3], portrait_rect=[30, 35, 20, 20], status=approved, region=coast, monster_size=regular |  |
| monsters/bottlecrab/bottlecrab_death.png | 320x70 | 4 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 3], portrait_rect=[30, 35, 20, 20], status=approved, region=coast, monster_size=regular |  |
| monsters/bottlecrab/bottlecrab_hit.png | 160x70 | 2 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 3], portrait_rect=[30, 35, 20, 20], status=approved, region=coast, monster_size=regular |  |
| monsters/bottlecrab/bottlecrab_idle.png | 160x70 | 2 | 80x70 | 2 | [40, 64] | hp_bar_anchor=[40, 3], portrait_rect=[30, 35, 20, 20], status=approved, region=coast, monster_size=regular |  |
| monsters/bottlecrab/bottlecrab_portrait.png | 20x20 | 1 | 20x20 |  |  | status=approved | 20x20 head crop (rect [30, 35, 20, 20] of the rest frame) for the initiative strip. |
| monsters/bottlecrab/bottlecrab_still.png | 80x70 | 1 | 80x70 |  | [40, 64] | hp_bar_anchor=[40, 3], status=approved | single rest frame (portraits / initiative). |
| monsters/bramblet/bramblet_attack.png | 240x70 | 3 | 80x70 | 5 | [40, 64] | hp_bar_anchor=[40, 12], portrait_rect=[30, 31, 20, 20], status=approved, region=meadow, monster_size=regular |  |
| monsters/bramblet/bramblet_death.png | 320x70 | 4 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 12], portrait_rect=[30, 31, 20, 20], status=approved, region=meadow, monster_size=regular |  |
| monsters/bramblet/bramblet_hit.png | 160x70 | 2 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 12], portrait_rect=[30, 31, 20, 20], status=approved, region=meadow, monster_size=regular |  |
| monsters/bramblet/bramblet_idle.png | 160x70 | 2 | 80x70 | 2 | [40, 64] | hp_bar_anchor=[40, 12], portrait_rect=[30, 31, 20, 20], status=approved, region=meadow, monster_size=regular |  |
| monsters/bramblet/bramblet_portrait.png | 20x20 | 1 | 20x20 |  |  | status=approved | 20x20 head crop (rect [30, 31, 20, 20] of the rest frame) for the initiative strip. |
| monsters/bramblet/bramblet_still.png | 80x70 | 1 | 80x70 |  | [40, 64] | hp_bar_anchor=[40, 12], status=approved | single rest frame (portraits / initiative). |
| monsters/cobble_rat/cobble_rat_attack.png | 240x70 | 3 | 80x70 | 5 | [40, 64] | hp_bar_anchor=[40, 28], portrait_rect=[11, 39, 20, 20], status=approved, region=keep, monster_size=regular |  |
| monsters/cobble_rat/cobble_rat_death.png | 320x70 | 4 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 28], portrait_rect=[11, 39, 20, 20], status=approved, region=keep, monster_size=regular |  |
| monsters/cobble_rat/cobble_rat_hit.png | 160x70 | 2 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 28], portrait_rect=[11, 39, 20, 20], status=approved, region=keep, monster_size=regular |  |
| monsters/cobble_rat/cobble_rat_idle.png | 160x70 | 2 | 80x70 | 2 | [40, 64] | hp_bar_anchor=[40, 28], portrait_rect=[11, 39, 20, 20], status=approved, region=keep, monster_size=regular |  |
| monsters/cobble_rat/cobble_rat_portrait.png | 20x20 | 1 | 20x20 |  |  | status=approved | 20x20 head crop (rect [11, 39, 20, 20] of the rest frame) for the initiative strip. |
| monsters/cobble_rat/cobble_rat_still.png | 80x70 | 1 | 80x70 |  | [40, 64] | hp_bar_anchor=[40, 28], status=approved | single rest frame (portraits / initiative). |
| monsters/dripfang/dripfang_attack.png | 240x70 | 3 | 80x70 | 5 | [40, 64] | hp_bar_anchor=[40, 1], portrait_rect=[31, 24, 20, 20], status=approved, region=cave, monster_size=regular |  |
| monsters/dripfang/dripfang_death.png | 320x70 | 4 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 1], portrait_rect=[31, 24, 20, 20], status=approved, region=cave, monster_size=regular |  |
| monsters/dripfang/dripfang_hit.png | 160x70 | 2 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 1], portrait_rect=[31, 24, 20, 20], status=approved, region=cave, monster_size=regular |  |
| monsters/dripfang/dripfang_idle.png | 160x70 | 2 | 80x70 | 2 | [40, 64] | hp_bar_anchor=[40, 1], portrait_rect=[31, 24, 20, 20], status=approved, region=cave, monster_size=regular |  |
| monsters/dripfang/dripfang_portrait.png | 20x20 | 1 | 20x20 |  |  | status=approved | 20x20 head crop (rect [31, 24, 20, 20] of the rest frame) for the initiative strip. |
| monsters/dripfang/dripfang_still.png | 80x70 | 1 | 80x70 |  | [40, 64] | hp_bar_anchor=[40, 1], status=approved | single rest frame (portraits / initiative). |
| monsters/gloomgrub/gloomgrub_attack.png | 240x70 | 3 | 80x70 | 5 | [40, 64] | hp_bar_anchor=[40, 22], portrait_rect=[10, 36, 20, 20], status=approved, region=cave, monster_size=regular |  |
| monsters/gloomgrub/gloomgrub_death.png | 320x70 | 4 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 22], portrait_rect=[10, 36, 20, 20], status=approved, region=cave, monster_size=regular |  |
| monsters/gloomgrub/gloomgrub_hit.png | 160x70 | 2 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 22], portrait_rect=[10, 36, 20, 20], status=approved, region=cave, monster_size=regular |  |
| monsters/gloomgrub/gloomgrub_idle.png | 160x70 | 2 | 80x70 | 2 | [40, 64] | hp_bar_anchor=[40, 22], portrait_rect=[10, 36, 20, 20], status=approved, region=cave, monster_size=regular |  |
| monsters/gloomgrub/gloomgrub_portrait.png | 20x20 | 1 | 20x20 |  |  | status=approved | 20x20 head crop (rect [10, 36, 20, 20] of the rest frame) for the initiative strip. |
| monsters/gloomgrub/gloomgrub_still.png | 80x70 | 1 | 80x70 |  | [40, 64] | hp_bar_anchor=[40, 22], status=approved | single rest frame (portraits / initiative). |
| monsters/goblin/goblin_attack.png | 240x70 | 3 | 80x70 | 5 | [40, 64] | hp_bar_anchor=[40, 12], portrait_rect=[26, 16, 20, 20] |  |
| monsters/goblin/goblin_death.png | 320x70 | 4 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 12], portrait_rect=[26, 16, 20, 20] |  |
| monsters/goblin/goblin_hit.png | 160x70 | 2 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 12], portrait_rect=[26, 16, 20, 20] |  |
| monsters/goblin/goblin_idle.png | 160x70 | 2 | 80x70 | 2 | [40, 64] | hp_bar_anchor=[40, 12], portrait_rect=[26, 16, 20, 20] |  |
| monsters/goblin/goblin_portrait.png | 20x20 | 1 | 20x20 |  |  |  | 20x20 head crop (rect [26, 16, 20, 20] of the rest frame) for the initiative strip. |
| monsters/goblin/goblin_still.png | 80x70 | 1 | 80x70 |  | [40, 64] | hp_bar_anchor=[40, 12] | single rest frame (portraits / initiative). |
| monsters/golem/golem_attack.png | 240x70 | 3 | 80x70 | 5 | [40, 64] | hp_bar_anchor=[40, 1], portrait_rect=[22, 4, 20, 20] |  |
| monsters/golem/golem_death.png | 320x70 | 4 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 1], portrait_rect=[22, 4, 20, 20] |  |
| monsters/golem/golem_hit.png | 160x70 | 2 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 1], portrait_rect=[22, 4, 20, 20] |  |
| monsters/golem/golem_idle.png | 160x70 | 2 | 80x70 | 2 | [40, 64] | hp_bar_anchor=[40, 1], portrait_rect=[22, 4, 20, 20] |  |
| monsters/golem/golem_portrait.png | 20x20 | 1 | 20x20 |  |  |  | 20x20 head crop (rect [22, 4, 20, 20] of the rest frame) for the initiative strip. |
| monsters/golem/golem_still.png | 80x70 | 1 | 80x70 |  | [40, 64] | hp_bar_anchor=[40, 1] | single rest frame (portraits / initiative). |
| monsters/grinmud_toad/grinmud_toad_attack.png | 240x70 | 3 | 80x70 | 5 | [40, 64] | hp_bar_anchor=[40, 20], portrait_rect=[30, 29, 20, 20], status=approved, region=meadow, monster_size=regular |  |
| monsters/grinmud_toad/grinmud_toad_death.png | 320x70 | 4 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 20], portrait_rect=[30, 29, 20, 20], status=approved, region=meadow, monster_size=regular |  |
| monsters/grinmud_toad/grinmud_toad_hit.png | 160x70 | 2 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 20], portrait_rect=[30, 29, 20, 20], status=approved, region=meadow, monster_size=regular |  |
| monsters/grinmud_toad/grinmud_toad_idle.png | 160x70 | 2 | 80x70 | 2 | [40, 64] | hp_bar_anchor=[40, 20], portrait_rect=[30, 29, 20, 20], status=approved, region=meadow, monster_size=regular |  |
| monsters/grinmud_toad/grinmud_toad_portrait.png | 20x20 | 1 | 20x20 |  |  | status=approved | 20x20 head crop (rect [30, 29, 20, 20] of the rest frame) for the initiative strip. |
| monsters/grinmud_toad/grinmud_toad_still.png | 80x70 | 1 | 80x70 |  | [40, 64] | hp_bar_anchor=[40, 20], status=approved | single rest frame (portraits / initiative). |
| monsters/hollow_helm/hollow_helm_attack.png | 240x70 | 3 | 80x70 | 5 | [40, 64] | hp_bar_anchor=[40, 1], portrait_rect=[28, 17, 20, 20], status=approved, region=keep, monster_size=regular |  |
| monsters/hollow_helm/hollow_helm_death.png | 320x70 | 4 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 1], portrait_rect=[28, 17, 20, 20], status=approved, region=keep, monster_size=regular |  |
| monsters/hollow_helm/hollow_helm_hit.png | 160x70 | 2 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 1], portrait_rect=[28, 17, 20, 20], status=approved, region=keep, monster_size=regular |  |
| monsters/hollow_helm/hollow_helm_idle.png | 160x70 | 2 | 80x70 | 2 | [40, 64] | hp_bar_anchor=[40, 1], portrait_rect=[28, 17, 20, 20], status=approved, region=keep, monster_size=regular |  |
| monsters/hollow_helm/hollow_helm_portrait.png | 20x20 | 1 | 20x20 |  |  | status=approved | 20x20 head crop (rect [28, 17, 20, 20] of the rest frame) for the initiative strip. |
| monsters/hollow_helm/hollow_helm_still.png | 80x70 | 1 | 80x70 |  | [40, 64] | hp_bar_anchor=[40, 1], status=approved | single rest frame (portraits / initiative). |
| monsters/imp/imp_attack.png | 240x70 | 3 | 80x70 | 5 | [40, 64] | hp_bar_anchor=[40, 11], portrait_rect=[19, 17, 20, 20] |  |
| monsters/imp/imp_death.png | 320x70 | 4 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 11], portrait_rect=[19, 17, 20, 20] |  |
| monsters/imp/imp_hit.png | 160x70 | 2 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 11], portrait_rect=[19, 17, 20, 20] |  |
| monsters/imp/imp_idle.png | 160x70 | 2 | 80x70 | 2 | [40, 64] | hp_bar_anchor=[40, 11], portrait_rect=[19, 17, 20, 20] |  |
| monsters/imp/imp_portrait.png | 20x20 | 1 | 20x20 |  |  |  | 20x20 head crop (rect [19, 17, 20, 20] of the rest frame) for the initiative strip. |
| monsters/imp/imp_still.png | 80x70 | 1 | 80x70 |  | [40, 64] | hp_bar_anchor=[40, 11] | single rest frame (portraits / initiative). |
| monsters/kelpback/kelpback_attack.png | 240x70 | 3 | 80x70 | 5 | [40, 64] | hp_bar_anchor=[40, 12], portrait_rect=[6, 30, 20, 20], status=approved, region=coast, monster_size=large |  |
| monsters/kelpback/kelpback_death.png | 320x70 | 4 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 12], portrait_rect=[6, 30, 20, 20], status=approved, region=coast, monster_size=large |  |
| monsters/kelpback/kelpback_hit.png | 160x70 | 2 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 12], portrait_rect=[6, 30, 20, 20], status=approved, region=coast, monster_size=large |  |
| monsters/kelpback/kelpback_idle.png | 160x70 | 2 | 80x70 | 2 | [40, 64] | hp_bar_anchor=[40, 12], portrait_rect=[6, 30, 20, 20], status=approved, region=coast, monster_size=large |  |
| monsters/kelpback/kelpback_portrait.png | 20x20 | 1 | 20x20 |  |  | status=approved | 20x20 head crop (rect [6, 30, 20, 20] of the rest frame) for the initiative strip. |
| monsters/kelpback/kelpback_still.png | 80x70 | 1 | 80x70 |  | [40, 64] | hp_bar_anchor=[40, 12], status=approved | single rest frame (portraits / initiative). |
| monsters/mushroom/mushroom_attack.png | 240x70 | 3 | 80x70 | 5 | [40, 64] | hp_bar_anchor=[40, 15], portrait_rect=[30, 33, 20, 20] |  |
| monsters/mushroom/mushroom_death.png | 320x70 | 4 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 15], portrait_rect=[30, 33, 20, 20] |  |
| monsters/mushroom/mushroom_hit.png | 160x70 | 2 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 15], portrait_rect=[30, 33, 20, 20] |  |
| monsters/mushroom/mushroom_idle.png | 160x70 | 2 | 80x70 | 2 | [40, 64] | hp_bar_anchor=[40, 15], portrait_rect=[30, 33, 20, 20] |  |
| monsters/mushroom/mushroom_portrait.png | 20x20 | 1 | 20x20 |  |  |  | 20x20 head crop (rect [30, 33, 20, 20] of the rest frame) for the initiative strip. |
| monsters/mushroom/mushroom_still.png | 80x70 | 1 | 80x70 |  | [40, 64] | hp_bar_anchor=[40, 15] | single rest frame (portraits / initiative). |
| monsters/pebble_squire/pebble_squire_attack.png | 240x70 | 3 | 80x70 | 5 | [40, 64] | hp_bar_anchor=[40, 2], portrait_rect=[29, 15, 20, 20], status=approved, region=keep, monster_size=regular |  |
| monsters/pebble_squire/pebble_squire_death.png | 320x70 | 4 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 2], portrait_rect=[29, 15, 20, 20], status=approved, region=keep, monster_size=regular |  |
| monsters/pebble_squire/pebble_squire_hit.png | 160x70 | 2 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 2], portrait_rect=[29, 15, 20, 20], status=approved, region=keep, monster_size=regular |  |
| monsters/pebble_squire/pebble_squire_idle.png | 160x70 | 2 | 80x70 | 2 | [40, 64] | hp_bar_anchor=[40, 2], portrait_rect=[29, 15, 20, 20], status=approved, region=keep, monster_size=regular |  |
| monsters/pebble_squire/pebble_squire_portrait.png | 20x20 | 1 | 20x20 |  |  | status=approved | 20x20 head crop (rect [29, 15, 20, 20] of the rest frame) for the initiative strip. |
| monsters/pebble_squire/pebble_squire_still.png | 80x70 | 1 | 80x70 |  | [40, 64] | hp_bar_anchor=[40, 2], status=approved | single rest frame (portraits / initiative). |
| monsters/skeleton/skeleton_attack.png | 240x70 | 3 | 80x70 | 5 | [40, 64] | hp_bar_anchor=[40, 9], portrait_rect=[33, 13, 20, 20] |  |
| monsters/skeleton/skeleton_death.png | 320x70 | 4 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 9], portrait_rect=[33, 13, 20, 20] |  |
| monsters/skeleton/skeleton_hit.png | 160x70 | 2 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 9], portrait_rect=[33, 13, 20, 20] |  |
| monsters/skeleton/skeleton_idle.png | 160x70 | 2 | 80x70 | 2 | [40, 64] | hp_bar_anchor=[40, 9], portrait_rect=[33, 13, 20, 20] |  |
| monsters/skeleton/skeleton_portrait.png | 20x20 | 1 | 20x20 |  |  |  | 20x20 head crop (rect [33, 13, 20, 20] of the rest frame) for the initiative strip. |
| monsters/skeleton/skeleton_still.png | 80x70 | 1 | 80x70 |  | [40, 64] | hp_bar_anchor=[40, 9] | single rest frame (portraits / initiative). |
| monsters/slime/slime_attack.png | 240x70 | 3 | 80x70 | 5 | [40, 64] | hp_bar_anchor=[40, 30], portrait_rect=[30, 38, 20, 20] |  |
| monsters/slime/slime_death.png | 320x70 | 4 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 30], portrait_rect=[30, 38, 20, 20] |  |
| monsters/slime/slime_hit.png | 160x70 | 2 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 30], portrait_rect=[30, 38, 20, 20] |  |
| monsters/slime/slime_idle.png | 160x70 | 2 | 80x70 | 2 | [40, 64] | hp_bar_anchor=[40, 30], portrait_rect=[30, 38, 20, 20] |  |
| monsters/slime/slime_portrait.png | 20x20 | 1 | 20x20 |  |  |  | 20x20 head crop (rect [30, 38, 20, 20] of the rest frame) for the initiative strip. |
| monsters/slime/slime_still.png | 80x70 | 1 | 80x70 |  | [40, 64] | hp_bar_anchor=[40, 30] | single rest frame (portraits / initiative). |
| monsters/squallgull/squallgull_attack.png | 240x70 | 3 | 80x70 | 5 | [40, 64] | hp_bar_anchor=[40, 12], portrait_rect=[31, 26, 20, 20], status=approved, region=coast, monster_size=regular |  |
| monsters/squallgull/squallgull_death.png | 320x70 | 4 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 12], portrait_rect=[31, 26, 20, 20], status=approved, region=coast, monster_size=regular |  |
| monsters/squallgull/squallgull_hit.png | 160x70 | 2 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 12], portrait_rect=[31, 26, 20, 20], status=approved, region=coast, monster_size=regular |  |
| monsters/squallgull/squallgull_idle.png | 160x70 | 2 | 80x70 | 2 | [40, 64] | hp_bar_anchor=[40, 12], portrait_rect=[31, 26, 20, 20], status=approved, region=coast, monster_size=regular |  |
| monsters/squallgull/squallgull_portrait.png | 20x20 | 1 | 20x20 |  |  | status=approved | 20x20 head crop (rect [31, 26, 20, 20] of the rest frame) for the initiative strip. |
| monsters/squallgull/squallgull_still.png | 80x70 | 1 | 80x70 |  | [40, 64] | hp_bar_anchor=[40, 12], status=approved | single rest frame (portraits / initiative). |
| monsters/wolf/wolf_attack.png | 240x70 | 3 | 80x70 | 5 | [40, 64] | hp_bar_anchor=[40, 12], portrait_rect=[12, 17, 20, 20] |  |
| monsters/wolf/wolf_death.png | 320x70 | 4 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 12], portrait_rect=[12, 17, 20, 20] |  |
| monsters/wolf/wolf_hit.png | 160x70 | 2 | 80x70 | 8 | [40, 64] | hp_bar_anchor=[40, 12], portrait_rect=[12, 17, 20, 20] |  |
| monsters/wolf/wolf_idle.png | 160x70 | 2 | 80x70 | 2 | [40, 64] | hp_bar_anchor=[40, 12], portrait_rect=[12, 17, 20, 20] |  |
| monsters/wolf/wolf_portrait.png | 20x20 | 1 | 20x20 |  |  |  | 20x20 head crop (rect [12, 17, 20, 20] of the rest frame) for the initiative strip. |
| monsters/wolf/wolf_still.png | 80x70 | 1 | 80x70 |  | [40, 64] | hp_bar_anchor=[40, 12] | single rest frame (portraits / initiative). |
| palette/palette48.png | 384x8 | 1 | 384x8 |  |  |  | 48 swatches, 8x8 each, index order = palette48.hex order. |
| paperdoll/back/body_back_skin_1.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=0 | seated, seen from behind. |
| paperdoll/back/body_back_skin_2.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=0 | seated, seen from behind. |
| paperdoll/back/body_back_skin_3.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=0 | seated, seen from behind. |
| paperdoll/back/body_back_skin_4.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=0 | seated, seen from behind. |
| paperdoll/back/body_back_skin_5.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=0 | seated, seen from behind. |
| paperdoll/back/body_back_skin_6.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=0 | seated, seen from behind. |
| paperdoll/back/chair_back.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=5 | chair backrest, drawn LAST (in front of the seated body). Active seat: raise all layers 3px and add a 1px gold #f8d040 outline around the union. |
| paperdoll/back/class_back_barbarian.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=2 |  |
| paperdoll/back/class_back_barbarian_hat.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=4, hair_clip_y=30 | drawn above hair_back; hide hair rows y < hair_clip_y while worn. |
| paperdoll/back/class_back_barbarian_noweapon.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=2, variant_of=paperdoll/back/class_back_barbarian.png, status=draft_pending_approval | class_back_barbarian without the baked axe across the back; everything else pixel-identical (the weapon parts were the last parts of the layer, so the arm/robe/cape underneath is already fully drawn). Use when a main-hand weapon is equipped. |
| paperdoll/back/class_back_bard.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=2 |  |
| paperdoll/back/class_back_bard_hat.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=4, hair_clip_y=21 | drawn above hair_back; hide hair rows y < hair_clip_y while worn. |
| paperdoll/back/class_back_bard_noweapon.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=2, variant_of=paperdoll/back/class_back_bard.png, status=draft_pending_approval | class_back_bard without the baked lute at the right; everything else pixel-identical (the weapon parts were the last parts of the layer, so the arm/robe/cape underneath is already fully drawn). Use when a main-hand weapon is equipped. |
| paperdoll/back/class_back_cleric.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=2 |  |
| paperdoll/back/class_back_cleric_hat.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=4, hair_clip_y=19 | drawn above hair_back; hide hair rows y < hair_clip_y while worn. |
| paperdoll/back/class_back_druid.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=2 |  |
| paperdoll/back/class_back_druid_hat.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=4, hair_clip_y=0 | drawn above hair_back; hide hair rows y < hair_clip_y while worn. |
| paperdoll/back/class_back_druid_noweapon.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=2, variant_of=paperdoll/back/class_back_druid.png, status=draft_pending_approval | class_back_druid without the baked staff (and its hand) at the left; everything else pixel-identical (the weapon parts were the last parts of the layer, so the arm/robe/cape underneath is already fully drawn). Use when a main-hand weapon is equipped. |
| paperdoll/back/class_back_paladin.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=2 |  |
| paperdoll/back/class_back_paladin_hat.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=4, hair_clip_y=33 | drawn above hair_back; hide hair rows y < hair_clip_y while worn. |
| paperdoll/back/class_back_paladin_noweapon.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=2, variant_of=paperdoll/back/class_back_paladin.png, status=draft_pending_approval | class_back_paladin without the baked sword at the left hip; everything else pixel-identical (the weapon parts were the last parts of the layer, so the arm/robe/cape underneath is already fully drawn). Use when a main-hand weapon is equipped. |
| paperdoll/back/class_back_ranger.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=2 |  |
| paperdoll/back/class_back_ranger_hat.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=4, hair_clip_y=60 | drawn above hair_back; hide hair rows y < hair_clip_y while worn. |
| paperdoll/back/class_back_ranger_noweapon.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=2, variant_of=paperdoll/back/class_back_ranger.png, status=draft_pending_approval | class_back_ranger without the baked bow (and its hand) at the left; everything else pixel-identical (the weapon parts were the last parts of the layer, so the arm/robe/cape underneath is already fully drawn). Use when a main-hand weapon is equipped. |
| paperdoll/back/class_back_rogue.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=2 |  |
| paperdoll/back/class_back_rogue_hat.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=4, hair_clip_y=60 | drawn above hair_back; hide hair rows y < hair_clip_y while worn. |
| paperdoll/back/class_back_wizard.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=2 |  |
| paperdoll/back/class_back_wizard_hat.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=4, hair_clip_y=21 | drawn above hair_back; hide hair rows y < hair_clip_y while worn. |
| paperdoll/back/class_back_wizard_noweapon.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=2, variant_of=paperdoll/back/class_back_wizard.png, status=draft_pending_approval | class_back_wizard without the baked staff (and its hand) at the right; everything else pixel-identical (the weapon parts were the last parts of the layer, so the arm/robe/cape underneath is already fully drawn). Use when a main-hand weapon is equipped. |
| paperdoll/back/hair_back_1.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=3 | bald (grayscale keys). |
| paperdoll/back/hair_back_2.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=3 | short (grayscale keys). |
| paperdoll/back/hair_back_3.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=3 | spiky (grayscale keys). |
| paperdoll/back/hair_back_4.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=3 | ponytail (grayscale keys). |
| paperdoll/back/hair_back_5.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=3 | long (grayscale keys). |
| paperdoll/back/hair_back_6.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=3 | braids (grayscale keys). |
| paperdoll/back/hair_back_7.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=3 | afro (grayscale keys). |
| paperdoll/back/hair_back_8.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=3 | mohawk (grayscale keys). |
| paperdoll/back/outfit_back.png | 48x78 | 1 | 48x78 |  | [24, 77] | layer=1 | grayscale shirt keys + brown shorts. |
| paperdoll/body_skin_1.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=0 | skin tone 1 (skin1), light->deep. Includes shoes. |
| paperdoll/body_skin_2.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=0 | skin tone 2 (skin2), light->deep. Includes shoes. |
| paperdoll/body_skin_3.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=0 | skin tone 3 (skin3), light->deep. Includes shoes. |
| paperdoll/body_skin_4.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=0 | skin tone 4 (skin4), light->deep. Includes shoes. |
| paperdoll/body_skin_5.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=0 | skin tone 5 (skin5), light->deep. Includes shoes. |
| paperdoll/body_skin_6.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=0 | skin tone 6 (skin6), light->deep. Includes shoes. |
| paperdoll/class_barbarian.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=2 | full-colour class outfit overlay (drawn over outfit_base; may also be used without it). |
| paperdoll/class_barbarian_hat.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=5, hair_clip_y=14 | optional headgear, drawn ABOVE hair. While worn, hide hair rows y < hair_clip_y (e.g. region rect or shader). |
| paperdoll/class_bard.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=2 | full-colour class outfit overlay (drawn over outfit_base; may also be used without it). |
| paperdoll/class_bard_hat.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=5, hair_clip_y=14 | optional headgear, drawn ABOVE hair. While worn, hide hair rows y < hair_clip_y (e.g. region rect or shader). |
| paperdoll/class_cleric.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=2 | full-colour class outfit overlay (drawn over outfit_base; may also be used without it). |
| paperdoll/class_cleric_hat.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=5, hair_clip_y=13 | optional headgear, drawn ABOVE hair. While worn, hide hair rows y < hair_clip_y (e.g. region rect or shader). |
| paperdoll/class_druid.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=2 | full-colour class outfit overlay (drawn over outfit_base; may also be used without it). |
| paperdoll/class_druid_hat.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=5, hair_clip_y=0 | optional headgear, drawn ABOVE hair. While worn, hide hair rows y < hair_clip_y (e.g. region rect or shader). |
| paperdoll/class_paladin.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=2 | full-colour class outfit overlay (drawn over outfit_base; may also be used without it). |
| paperdoll/class_paladin_hat.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=5, hair_clip_y=16 | optional headgear, drawn ABOVE hair. While worn, hide hair rows y < hair_clip_y (e.g. region rect or shader). |
| paperdoll/class_ranger.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=2 | full-colour class outfit overlay (drawn over outfit_base; may also be used without it). |
| paperdoll/class_ranger_hat.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=5, hair_clip_y=17 | optional headgear, drawn ABOVE hair. While worn, hide hair rows y < hair_clip_y (e.g. region rect or shader). |
| paperdoll/class_rogue.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=2 | full-colour class outfit overlay (drawn over outfit_base; may also be used without it). |
| paperdoll/class_rogue_hat.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=5, hair_clip_y=17 | optional headgear, drawn ABOVE hair. While worn, hide hair rows y < hair_clip_y (e.g. region rect or shader). |
| paperdoll/class_wizard.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=2 | full-colour class outfit overlay (drawn over outfit_base; may also be used without it). |
| paperdoll/class_wizard_hat.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=5, hair_clip_y=14 | optional headgear, drawn ABOVE hair. While worn, hide hair rows y < hair_clip_y (e.g. region rect or shader). |
| paperdoll/gear/chapel_mace.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=chapel_mace, gear_layer=main, two_handed=false | back-view seat overlay, 48x78, anchor (24,77). held at the hero's right side (screen right, x40-47), pointing up/out past the shoulder; the lute is slung diagonally across the back instead. Pixels under chair_back are cleared. |
| paperdoll/gear/glass_orb.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=glass_orb, gear_layer=off, two_handed=false | back-view seat overlay, 48x78, anchor (24,77). on the hero's left arm edge (screen left, x0-10, y40-67). Pixels under chair_back are cleared. |
| paperdoll/gear/gravel_axe.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=gravel_axe, gear_layer=main, two_handed=true | back-view seat overlay, 48x78, anchor (24,77). staffs held upright at the right side (x40-48, top y1-16); bows, the gravel axe and Sunbrand slung diagonally across the back, top end over the right shoulder, lower end hidden by the chair. Pixels under chair_back are cleared. |
| paperdoll/gear/hedge_mail.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=hedge_mail, gear_layer=armor, two_handed=false | back-view seat overlay, 48x78, anchor (24,77). shoulders + upper back; drawn after class_back and BEFORE hair/hood (long hair and hoods fall over the back plate). Pixels under chair_back are cleared. |
| paperdoll/gear/howl_fang.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=howl_fang, gear_layer=main, two_handed=false | back-view seat overlay, 48x78, anchor (24,77). held at the hero's right side (screen right, x40-47), pointing up/out past the shoulder; the lute is slung diagonally across the back instead. Pixels under chair_back are cleared. |
| paperdoll/gear/hymn_board.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=hymn_board, gear_layer=off, two_handed=false | back-view seat overlay, 48x78, anchor (24,77). on the hero's left arm edge (screen left, x0-10, y40-67). Pixels under chair_back are cleared. |
| paperdoll/gear/keep_plate.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=keep_plate, gear_layer=armor, two_handed=false | back-view seat overlay, 48x78, anchor (24,77). shoulders + upper back; drawn after class_back and BEFORE hair/hood (long hair and hoods fall over the back plate). Pixels under chair_back are cleared. |
| paperdoll/gear/kettle_shield.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=kettle_shield, gear_layer=off, two_handed=false | back-view seat overlay, 48x78, anchor (24,77). on the hero's left arm edge (screen left, x0-10, y40-67). Pixels under chair_back are cleared. |
| paperdoll/gear/kiln_plate.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=kiln_plate, gear_layer=armor, two_handed=false | back-view seat overlay, 48x78, anchor (24,77). shoulders + upper back; drawn after class_back and BEFORE hair/hood (long hair and hoods fall over the back plate). Pixels under chair_back are cleared. |
| paperdoll/gear/kiln_sword.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=kiln_sword, gear_layer=main, two_handed=false | back-view seat overlay, 48x78, anchor (24,77). held at the hero's right side (screen right, x40-47), pointing up/out past the shoulder; the lute is slung diagonally across the back instead. Pixels under chair_back are cleared. |
| paperdoll/gear/lamp_staff.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=lamp_staff, gear_layer=main, two_handed=true | back-view seat overlay, 48x78, anchor (24,77). staffs held upright at the right side (x40-48, top y1-16); bows, the gravel axe and Sunbrand slung diagonally across the back, top end over the right shoulder, lower end hidden by the chair. Pixels under chair_back are cleared. |
| paperdoll/gear/lurker_scale.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=lurker_scale, gear_layer=armor, two_handed=false | back-view seat overlay, 48x78, anchor (24,77). shoulders + upper back; drawn after class_back and BEFORE hair/hood (long hair and hoods fall over the back plate). Pixels under chair_back are cleared. |
| paperdoll/gear/marsh_bow.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=marsh_bow, gear_layer=main, two_handed=true | back-view seat overlay, 48x78, anchor (24,77). staffs held upright at the right side (x40-48, top y1-16); bows, the gravel axe and Sunbrand slung diagonally across the back, top end over the right shoulder, lower end hidden by the chair. Pixels under chair_back are cleared. |
| paperdoll/gear/moon_robe.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=moon_robe, gear_layer=armor, two_handed=false | back-view seat overlay, 48x78, anchor (24,77). shoulders + upper back; drawn after class_back and BEFORE hair/hood (long hair and hoods fall over the back plate). Pixels under chair_back are cleared. |
| paperdoll/gear/night_shard.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=night_shard, gear_layer=main, two_handed=false | back-view seat overlay, 48x78, anchor (24,77). held at the hero's right side (screen right, x40-47), pointing up/out past the shoulder; the lute is slung diagonally across the back instead. Pixels under chair_back are cleared. |
| paperdoll/gear/oak_buckler.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=oak_buckler, gear_layer=off, two_handed=false | back-view seat overlay, 48x78, anchor (24,77). on the hero's left arm edge (screen left, x0-10, y40-67). Pixels under chair_back are cleared. |
| paperdoll/gear/oath_blade.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=oath_blade, gear_layer=main, two_handed=false | back-view seat overlay, 48x78, anchor (24,77). held at the hero's right side (screen right, x40-47), pointing up/out past the shoulder; the lute is slung diagonally across the back instead. Pixels under chair_back are cleared. |
| paperdoll/gear/pocket_knife.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=pocket_knife, gear_layer=main, two_handed=false | back-view seat overlay, 48x78, anchor (24,77). held at the hero's right side (screen right, x40-47), pointing up/out past the shoulder; the lute is slung diagonally across the back instead. Pixels under chair_back are cleared. |
| paperdoll/gear/reed_staff.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=reed_staff, gear_layer=main, two_handed=true | back-view seat overlay, 48x78, anchor (24,77). staffs held upright at the right side (x40-48, top y1-16); bows, the gravel axe and Sunbrand slung diagonally across the back, top end over the right shoulder, lower end hidden by the chair. Pixels under chair_back are cleared. |
| paperdoll/gear/reed_wrap.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=reed_wrap, gear_layer=armor, two_handed=false | back-view seat overlay, 48x78, anchor (24,77). shoulders + upper back; drawn after class_back and BEFORE hair/hood (long hair and hoods fall over the back plate). Pixels under chair_back are cleared. |
| paperdoll/gear/road_lute.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=road_lute, gear_layer=main, two_handed=false | back-view seat overlay, 48x78, anchor (24,77). held at the hero's right side (screen right, x40-47), pointing up/out past the shoulder; the lute is slung diagonally across the back instead. Pixels under chair_back are cleared. |
| paperdoll/gear/sap_crook.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=sap_crook, gear_layer=main, two_handed=true | back-view seat overlay, 48x78, anchor (24,77). staffs held upright at the right side (x40-48, top y1-16); bows, the gravel axe and Sunbrand slung diagonally across the back, top end over the right shoulder, lower end hidden by the chair. Pixels under chair_back are cleared. |
| paperdoll/gear/sunbrand.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=sunbrand, gear_layer=main, two_handed=true | back-view seat overlay, 48x78, anchor (24,77). staffs held upright at the right side (x40-48, top y1-16); bows, the gravel axe and Sunbrand slung diagonally across the back, top end over the right shoulder, lower end hidden by the chair. Pixels under chair_back are cleared. |
| paperdoll/gear/thorn_bow.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=thorn_bow, gear_layer=main, two_handed=true | back-view seat overlay, 48x78, anchor (24,77). staffs held upright at the right side (x40-48, top y1-16); bows, the gravel axe and Sunbrand slung diagonally across the back, top end over the right shoulder, lower end hidden by the chair. Pixels under chair_back are cleared. |
| paperdoll/gear/travel_coat.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=travel_coat, gear_layer=armor, two_handed=false | back-view seat overlay, 48x78, anchor (24,77). shoulders + upper back; drawn after class_back and BEFORE hair/hood (long hair and hoods fall over the back plate). Pixels under chair_back are cleared. |
| paperdoll/gear/void_lens.png | 48x78 | 1 | 48x78 |  | [24, 77] | status=approved, item=void_lens, gear_layer=off, two_handed=false | back-view seat overlay, 48x78, anchor (24,77). on the hero's left arm edge (screen left, x0-10, y40-67). Pixels under chair_back are cleared. |
| paperdoll/hair_1.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=4 | bald; GRAYSCALE keys, tint with hair_ramps.png. (empty = bald) |
| paperdoll/hair_2.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=4 | short; GRAYSCALE keys, tint with hair_ramps.png. |
| paperdoll/hair_3.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=4 | spiky; GRAYSCALE keys, tint with hair_ramps.png. |
| paperdoll/hair_4.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=4 | ponytail; GRAYSCALE keys, tint with hair_ramps.png. |
| paperdoll/hair_5.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=4 | long; GRAYSCALE keys, tint with hair_ramps.png. |
| paperdoll/hair_6.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=4 | braids; GRAYSCALE keys, tint with hair_ramps.png. |
| paperdoll/hair_7.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=4 | afro; GRAYSCALE keys, tint with hair_ramps.png. |
| paperdoll/hair_8.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=4 | mohawk; GRAYSCALE keys, tint with hair_ramps.png. |
| paperdoll/head_1.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=3 | round head drawn in REFERENCE skin (tone 3); swap skin via skin_ramps.png.  |
| paperdoll/head_2.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=3 | square head drawn in REFERENCE skin (tone 3); swap skin via skin_ramps.png.  |
| paperdoll/head_3.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=3 | chubby head drawn in REFERENCE skin (tone 3); swap skin via skin_ramps.png.  |
| paperdoll/head_4.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=3 | freckles head drawn in REFERENCE skin (tone 3); swap skin via skin_ramps.png.  |
| paperdoll/head_5.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=3 | glasses head drawn in REFERENCE skin (tone 3); swap skin via skin_ramps.png.  |
| paperdoll/head_6.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=3 | beard head drawn in REFERENCE skin (tone 3); swap skin via skin_ramps.png. Beard uses the grayscale hair keys -> tint with the chosen hair ramp. |
| paperdoll/outfit_base.png | 32x48 | 1 | 32x48 |  | [16, 47] | layer=1 | shirt in grayscale keys (tint with outfit_ramps.png), shorts fixed brown. |
| paperdoll/palettes/afro_back_check.png | 402x82 | 1 | 402x82 |  |  |  | QA: back-view afro (hair_back_7) in all 8 hair ramps on the seated body. |
| paperdoll/palettes/classes_check.png | 402x136 | 1 | 402x136 |  |  |  | QA: all 8 classes, default front doll (top) and composed seat (bottom; paladin active). |
| paperdoll/palettes/hair_ramps.png | 4x8 | 1 | 4x8 |  |  |  | 4x8 px. Row = colour (black,brown,blonde,ginger,white,blue,pink,green); column i replaces grayscale key i (K1 #46424e, K2 #6c6a76, K3 #9c9ca6, K4 #cfd0d4). |
| paperdoll/palettes/hair_ramps_preview.png | 272x74 | 1 | 272x74 |  |  |  | swatches + pre-tinted example per hair colour. |
| paperdoll/palettes/outfit_ramps.png | 3x8 | 1 | 3x8 |  |  |  | 3x8 px. Row = colour (white,red,blue,purple,green,yellow,brown,dark); columns replace K2,K3,K4. |
| paperdoll/palettes/outfit_ramps_preview.png | 272x58 | 1 | 272x58 |  |  |  | swatches + pre-tinted example per outfit colour. |
| paperdoll/palettes/skin_ramps.png | 4x6 | 1 | 4x6 |  |  |  | 4x6 px. Row = tone 1..6; columns replace the reference-skin keys [blush #ec5a44, detail #8c5836, shadow #b27a4e, base #d89c72] in head_*.png (apply as ONE simultaneous lookup). |
| paperdoll/paperdoll_preview.png | 660x606 | 1 | 660x606 |  |  |  | 3x nearest. 12 random front combos built from the layers + 4 seated back combos (2nd one shows the active raise + gold outline). |
| paperdoll/portrait_crop_examples.png | 132x22 | 1 | 132x22 |  |  | portrait_crop_rect=[6, 8, 20, 20] | examples of the 20x20 portrait crop taken from the composed front doll. |
| paperdoll/tinted/hair_2_black.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_2_blonde.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_2_blue.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_2_brown.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_2_ginger.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_2_green.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_2_pink.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_2_white.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_3_black.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_3_blonde.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_3_blue.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_3_brown.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_3_ginger.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_3_green.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_3_pink.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_3_white.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_4_black.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_4_blonde.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_4_blue.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_4_brown.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_4_ginger.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_4_green.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_4_pink.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_4_white.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_5_black.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_5_blonde.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_5_blue.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_5_brown.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_5_ginger.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_5_green.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_5_pink.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_5_white.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_6_black.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_6_blonde.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_6_blue.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_6_brown.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_6_ginger.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_6_green.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_6_pink.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_6_white.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_7_black.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_7_blonde.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_7_blue.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_7_brown.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_7_ginger.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_7_green.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_7_pink.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_7_white.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_8_black.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_8_blonde.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_8_blue.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_8_brown.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_8_ginger.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_8_green.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_8_pink.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/hair_8_white.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_1_skin1.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_1_skin2.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_1_skin3.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_1_skin4.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_1_skin5.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_1_skin6.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_2_skin1.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_2_skin2.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_2_skin3.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_2_skin4.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_2_skin5.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_2_skin6.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_3_skin1.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_3_skin2.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_3_skin3.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_3_skin4.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_3_skin5.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_3_skin6.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_4_skin1.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_4_skin2.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_4_skin3.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_4_skin4.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_4_skin5.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_4_skin6.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_5_skin1.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_5_skin2.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_5_skin3.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_5_skin4.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_5_skin5.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_5_skin6.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_6_skin1.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_6_skin2.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_6_skin3.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_6_skin4.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_6_skin5.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/head_6_skin6.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/outfit_blue.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/outfit_brown.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/outfit_dark.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/outfit_green.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/outfit_purple.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/outfit_red.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/outfit_white.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| paperdoll/tinted/outfit_yellow.png | 32x48 | 1 | 32x48 |  | [16, 47] |  | pre-tinted variant (same canvas/anchor as its grayscale/reference source). |
| party/seat_barbarian_active.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=paperdoll/back/* (see manifest paperdoll.seat_recipe), defaults={"skin": 3, "head": 3, "hair": 8, "hair_color": "ginger", "outfit": null, "hat": true} | 48x78 seat built from the back-view paperdoll layers. Active: all layers raised 3px + 1px gold #f8d040 outline around the union. |
| party/seat_barbarian_active_noweapon.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=seat_recipe with back/class_back_barbarian_noweapon, defaults={"skin": 3, "head": 3, "hair": 8, "hair_color": "ginger", "outfit": null, "hat": true}, status=draft_pending_approval | party/seat_barbarian_active without the baked class weapon (for a hero with a main-hand weapon equipped; draw the gear overlays on top per seat_recipe steps_with_gear). |
| party/seat_barbarian_idle.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=paperdoll/back/* (see manifest paperdoll.seat_recipe), defaults={"skin": 3, "head": 3, "hair": 8, "hair_color": "ginger", "outfit": null, "hat": true} | 48x78 seat built from the back-view paperdoll layers. |
| party/seat_barbarian_idle_noweapon.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=seat_recipe with back/class_back_barbarian_noweapon, defaults={"skin": 3, "head": 3, "hair": 8, "hair_color": "ginger", "outfit": null, "hat": true}, status=draft_pending_approval | party/seat_barbarian_idle without the baked class weapon (for a hero with a main-hand weapon equipped; draw the gear overlays on top per seat_recipe steps_with_gear). |
| party/seat_bard_active.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=paperdoll/back/* (see manifest paperdoll.seat_recipe), defaults={"skin": 5, "head": 3, "hair": 6, "hair_color": "black", "outfit": "red", "hat": true} | 48x78 seat built from the back-view paperdoll layers. Active: all layers raised 3px + 1px gold #f8d040 outline around the union. |
| party/seat_bard_active_noweapon.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=seat_recipe with back/class_back_bard_noweapon, defaults={"skin": 5, "head": 3, "hair": 6, "hair_color": "black", "outfit": "red", "hat": true}, status=draft_pending_approval | party/seat_bard_active without the baked class weapon (for a hero with a main-hand weapon equipped; draw the gear overlays on top per seat_recipe steps_with_gear). |
| party/seat_bard_idle.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=paperdoll/back/* (see manifest paperdoll.seat_recipe), defaults={"skin": 5, "head": 3, "hair": 6, "hair_color": "black", "outfit": "red", "hat": true} | 48x78 seat built from the back-view paperdoll layers. |
| party/seat_bard_idle_noweapon.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=seat_recipe with back/class_back_bard_noweapon, defaults={"skin": 5, "head": 3, "hair": 6, "hair_color": "black", "outfit": "red", "hat": true}, status=draft_pending_approval | party/seat_bard_idle without the baked class weapon (for a hero with a main-hand weapon equipped; draw the gear overlays on top per seat_recipe steps_with_gear). |
| party/seat_cleric_active.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=paperdoll/back/* (see manifest paperdoll.seat_recipe), defaults={"skin": 4, "head": 6, "hair": 2, "hair_color": "white", "outfit": "white", "hat": true} | 48x78 seat built from the back-view paperdoll layers. Active: all layers raised 3px + 1px gold #f8d040 outline around the union. |
| party/seat_cleric_idle.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=paperdoll/back/* (see manifest paperdoll.seat_recipe), defaults={"skin": 4, "head": 6, "hair": 2, "hair_color": "white", "outfit": "white", "hat": true} | 48x78 seat built from the back-view paperdoll layers. |
| party/seat_druid_active.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=paperdoll/back/* (see manifest paperdoll.seat_recipe), defaults={"skin": 6, "head": 6, "hair": 1, "hair_color": "white", "outfit": "green", "hat": true} | 48x78 seat built from the back-view paperdoll layers. Active: all layers raised 3px + 1px gold #f8d040 outline around the union. |
| party/seat_druid_active_noweapon.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=seat_recipe with back/class_back_druid_noweapon, defaults={"skin": 6, "head": 6, "hair": 1, "hair_color": "white", "outfit": "green", "hat": true}, status=draft_pending_approval | party/seat_druid_active without the baked class weapon (for a hero with a main-hand weapon equipped; draw the gear overlays on top per seat_recipe steps_with_gear). |
| party/seat_druid_idle.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=paperdoll/back/* (see manifest paperdoll.seat_recipe), defaults={"skin": 6, "head": 6, "hair": 1, "hair_color": "white", "outfit": "green", "hat": true} | 48x78 seat built from the back-view paperdoll layers. |
| party/seat_druid_idle_noweapon.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=seat_recipe with back/class_back_druid_noweapon, defaults={"skin": 6, "head": 6, "hair": 1, "hair_color": "white", "outfit": "green", "hat": true}, status=draft_pending_approval | party/seat_druid_idle without the baked class weapon (for a hero with a main-hand weapon equipped; draw the gear overlays on top per seat_recipe steps_with_gear). |
| party/seat_paladin_active.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=paperdoll/back/* (see manifest paperdoll.seat_recipe), defaults={"skin": 2, "head": 1, "hair": 2, "hair_color": "brown", "outfit": "white", "hat": true} | 48x78 seat built from the back-view paperdoll layers. Active: all layers raised 3px + 1px gold #f8d040 outline around the union. |
| party/seat_paladin_active_noweapon.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=seat_recipe with back/class_back_paladin_noweapon, defaults={"skin": 2, "head": 1, "hair": 2, "hair_color": "brown", "outfit": "white", "hat": true}, status=draft_pending_approval | party/seat_paladin_active without the baked class weapon (for a hero with a main-hand weapon equipped; draw the gear overlays on top per seat_recipe steps_with_gear). |
| party/seat_paladin_idle.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=paperdoll/back/* (see manifest paperdoll.seat_recipe), defaults={"skin": 2, "head": 1, "hair": 2, "hair_color": "brown", "outfit": "white", "hat": true} | 48x78 seat built from the back-view paperdoll layers. |
| party/seat_paladin_idle_noweapon.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=seat_recipe with back/class_back_paladin_noweapon, defaults={"skin": 2, "head": 1, "hair": 2, "hair_color": "brown", "outfit": "white", "hat": true}, status=draft_pending_approval | party/seat_paladin_idle without the baked class weapon (for a hero with a main-hand weapon equipped; draw the gear overlays on top per seat_recipe steps_with_gear). |
| party/seat_ranger_active.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=paperdoll/back/* (see manifest paperdoll.seat_recipe), defaults={"skin": 3, "head": 4, "hair": 4, "hair_color": "ginger", "outfit": "green", "hat": true} | 48x78 seat built from the back-view paperdoll layers. Active: all layers raised 3px + 1px gold #f8d040 outline around the union. |
| party/seat_ranger_active_noweapon.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=seat_recipe with back/class_back_ranger_noweapon, defaults={"skin": 3, "head": 4, "hair": 4, "hair_color": "ginger", "outfit": "green", "hat": true}, status=draft_pending_approval | party/seat_ranger_active without the baked class weapon (for a hero with a main-hand weapon equipped; draw the gear overlays on top per seat_recipe steps_with_gear). |
| party/seat_ranger_idle.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=paperdoll/back/* (see manifest paperdoll.seat_recipe), defaults={"skin": 3, "head": 4, "hair": 4, "hair_color": "ginger", "outfit": "green", "hat": true} | 48x78 seat built from the back-view paperdoll layers. |
| party/seat_ranger_idle_noweapon.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=seat_recipe with back/class_back_ranger_noweapon, defaults={"skin": 3, "head": 4, "hair": 4, "hair_color": "ginger", "outfit": "green", "hat": true}, status=draft_pending_approval | party/seat_ranger_idle without the baked class weapon (for a hero with a main-hand weapon equipped; draw the gear overlays on top per seat_recipe steps_with_gear). |
| party/seat_rogue_active.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=paperdoll/back/* (see manifest paperdoll.seat_recipe), defaults={"skin": 2, "head": 2, "hair": 3, "hair_color": "black", "outfit": "dark", "hat": true} | 48x78 seat built from the back-view paperdoll layers. Active: all layers raised 3px + 1px gold #f8d040 outline around the union. |
| party/seat_rogue_idle.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=paperdoll/back/* (see manifest paperdoll.seat_recipe), defaults={"skin": 2, "head": 2, "hair": 3, "hair_color": "black", "outfit": "dark", "hat": true} | 48x78 seat built from the back-view paperdoll layers. |
| party/seat_wizard_active.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=paperdoll/back/* (see manifest paperdoll.seat_recipe), defaults={"skin": 1, "head": 5, "hair": 5, "hair_color": "blonde", "outfit": "blue", "hat": true} | 48x78 seat built from the back-view paperdoll layers. Active: all layers raised 3px + 1px gold #f8d040 outline around the union. |
| party/seat_wizard_active_noweapon.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=seat_recipe with back/class_back_wizard_noweapon, defaults={"skin": 1, "head": 5, "hair": 5, "hair_color": "blonde", "outfit": "blue", "hat": true}, status=draft_pending_approval | party/seat_wizard_active without the baked class weapon (for a hero with a main-hand weapon equipped; draw the gear overlays on top per seat_recipe steps_with_gear). |
| party/seat_wizard_idle.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=paperdoll/back/* (see manifest paperdoll.seat_recipe), defaults={"skin": 1, "head": 5, "hair": 5, "hair_color": "blonde", "outfit": "blue", "hat": true} | 48x78 seat built from the back-view paperdoll layers. |
| party/seat_wizard_idle_noweapon.png | 48x78 | 1 | 48x78 |  | [24, 77] | composed_from=seat_recipe with back/class_back_wizard_noweapon, defaults={"skin": 1, "head": 5, "hair": 5, "hair_color": "blonde", "outfit": "blue", "hat": true}, status=draft_pending_approval | party/seat_wizard_idle without the baked class weapon (for a hero with a main-hand weapon equipped; draw the gear overlays on top per seat_recipe steps_with_gear). |
| scene_test.png | 480x270 | 1 | 480x270 |  |  | legacy=true | LEGACY (landscape 480x270): see scene_test_portrait.png. 480x270 composite built only from pack files (QA). |
| scene_test_4x.png | 1920x1080 | 1 | 1920x1080 |  |  | legacy=true | LEGACY (landscape 480x270): see scene_test_portrait_4x.png. 4x nearest upscale of scene_test.png. |
| scene_test_portrait.png | 270x480 | 1 | 270x480 |  |  |  | PORTRAIT 270x480 mock built only from pack files (QA). |
| scene_test_portrait_4x.png | 1080x1920 | 1 | 1080x1920 |  |  |  | 4x nearest upscale. |
| scene_test_portrait_gear.png | 270x480 | 1 | 270x480 |  |  | status=approved | QA composite (not runtime): party wearing the approved gear overlays (paladin keep_plate+oath_blade+kettle_shield, cleric hedge_mail+chapel_mace+hymn_board, rogue travel_coat+night_shard+pocket_knife (mirrored off hand), druid reed_wrap+sap_crook, wizard moon_robe+lamp_staff) at Gravel Keep. |
| scene_test_portrait_gear_4x.png | 1080x1920 | 1 | 1080x1920 |  |  | status=approved | 4x nearest. |
| scene_test_portrait_lantern_reach.png | 270x480 | 1 | 270x480 |  |  | status=approved | QA composite (not runtime): Lantern Reach backdrop + coast monsters Bottlecrab / Kelpback Snapper (LARGE) / Squallgull at the standard monster marks, with the v7 party, table, seat bars + HP numbers and v6 action bar. |
| scene_test_portrait_lantern_reach_4x.png | 1080x1920 | 1 | 1080x1920 |  |  | status=approved | 4x nearest. |
| scene_test_portrait_skillcard.png | 270x480 | 1 | 270x480 |  |  |  | PORTRAIT mock: paladin_1 tapped once -> slot armed (pulsing glow), other slots dimmed, skill card open above the seats (clears the seat bars + HP numbers). Placeholder copy. |
| scene_test_portrait_skillcard_4x.png | 1080x1920 | 1 | 1080x1920 |  |  |  | 4x nearest. |
| ui/bar_bg.png | 56x7 | 1 | 56x7 |  |  | fill_rect=[1, 1, 54, 5], legacy=true | LEGACY (landscape 480x270): baked into the narrow card. 56x7 under-texture; fill goes at offset [1,1]. |
| ui/bar_hp.png | 54x5 | 1 | 54x5 |  |  | legacy=true | LEGACY (landscape 480x270): use ui/portrait/bar_hp_88.png or bar_hp_tile. TextureProgressBar fill (54x5). Row0 highlight, row4 shadow. Crop/scale width only (nearest). |
| ui/bar_hp_tile.png | 12x5 | 1 | 12x5 |  |  |  | 12x5 horizontally tileable fill for arbitrary bar lengths. |
| ui/bar_mp.png | 54x5 | 1 | 54x5 |  |  | legacy=true | LEGACY (landscape 480x270): use ui/portrait/bar_mp_88.png or bar_mp_tile. MP fill (54x5). |
| ui/bar_mp_tile.png | 12x5 | 1 | 12x5 |  |  |  | 12x5 horizontally tileable fill. |
| ui/btn_arrow_left.png | 14x22 | 1 | 14x22 |  | [0, 0] |  | 14x22 creator cycle arrow. |
| ui/btn_arrow_right.png | 14x22 | 1 | 14x22 |  | [0, 0] |  | 14x22 creator cycle arrow. |
| ui/btn_attack.png | 28x28 | 1 | 28x28 |  | [0, 0] | legacy=true | LEGACY (landscape 480x270): portrait bottom bar is now the v6 per-character bar (ui/portrait/action_bar_v2.png). normal state. 28x28, icon area rect [4,4,20,20]. |
| ui/btn_attack_active.png | 28x28 | 1 | 28x28 |  | [0, 0] | legacy=true | LEGACY (landscape 480x270): portrait bottom bar is now the v6 per-character bar (ui/portrait/action_bar_v2.png). highlighted/selected state (gold frame). 28x28, icon area rect [4,4,20,20]. |
| ui/btn_confirm.png | 56x24 | 1 | 56x24 |  | [0, 0] |  | 56x24 confirm (check) button. |
| ui/btn_cover.png | 28x28 | 1 | 28x28 |  | [0, 0] | legacy=true | LEGACY (landscape 480x270): portrait bottom bar is now the v6 per-character bar (ui/portrait/action_bar_v2.png). normal state. 28x28, icon area rect [4,4,20,20]. |
| ui/btn_cover_active.png | 28x28 | 1 | 28x28 |  | [0, 0] | legacy=true | LEGACY (landscape 480x270): portrait bottom bar is now the v6 per-character bar (ui/portrait/action_bar_v2.png). highlighted/selected state (gold frame). 28x28, icon area rect [4,4,20,20]. |
| ui/btn_item.png | 28x28 | 1 | 28x28 |  | [0, 0] | legacy=true | LEGACY (landscape 480x270): portrait bottom bar is now the v6 per-character bar (ui/portrait/action_bar_v2.png). normal state. 28x28, icon area rect [4,4,20,20]. |
| ui/btn_item_active.png | 28x28 | 1 | 28x28 |  | [0, 0] | legacy=true | LEGACY (landscape 480x270): portrait bottom bar is now the v6 per-character bar (ui/portrait/action_bar_v2.png). highlighted/selected state (gold frame). 28x28, icon area rect [4,4,20,20]. |
| ui/btn_menu.png | 18x18 | 1 | 18x18 |  | [0, 0] |  | 18x18 menu (hamburger) button. |
| ui/btn_random.png | 56x24 | 1 | 56x24 |  | [0, 0] |  | 56x24 randomise (die) button. |
| ui/btn_run.png | 28x28 | 1 | 28x28 |  | [0, 0] | legacy=true | LEGACY (landscape 480x270): portrait bottom bar is now the v6 per-character bar (ui/portrait/action_bar_v2.png). normal state. 28x28, icon area rect [4,4,20,20]. |
| ui/btn_run_active.png | 28x28 | 1 | 28x28 |  | [0, 0] | legacy=true | LEGACY (landscape 480x270): portrait bottom bar is now the v6 per-character bar (ui/portrait/action_bar_v2.png). highlighted/selected state (gold frame). 28x28, icon area rect [4,4,20,20]. |
| ui/btn_skill.png | 28x28 | 1 | 28x28 |  | [0, 0] | legacy=true | LEGACY (landscape 480x270): portrait bottom bar is now the v6 per-character bar (ui/portrait/action_bar_v2.png). normal state. 28x28, icon area rect [4,4,20,20]. |
| ui/btn_skill_active.png | 28x28 | 1 | 28x28 |  | [0, 0] | legacy=true | LEGACY (landscape 480x270): portrait bottom bar is now the v6 per-character bar (ui/portrait/action_bar_v2.png). highlighted/selected state (gold frame). 28x28, icon area rect [4,4,20,20]. |
| ui/dmg_font_heal.png | 84x9 | 12 | 7x9 |  |  |  | glyph order '0123456789+-'; advance 6px (1px outline overlap). Colour b4dc62 / shade 7cbc3c, outline #120c18. |
| ui/dmg_font_hp.png | 84x9 | 12 | 7x9 |  |  |  | glyph order '0123456789+-'; advance 6px (1px outline overlap). Colour ec5a44 / shade c02c2c, outline #120c18. |
| ui/dmg_font_mp.png | 84x9 | 12 | 7x9 |  |  |  | glyph order '0123456789+-'; advance 6px (1px outline overlap). Colour 4c9ce8 / shade 3466cc, outline #120c18. |
| ui/dmg_font_mp_letters.png | 14x9 | 2 | 7x9 |  |  |  | glyph order 'MP', same style/advance (6px) as ui/dmg_font_mp.png so code can draw '+5 MP' (digits from dmg_font_mp). |
| ui/dmg_numbers_preview.png | 120x50 | 1 | 120x50 |  |  |  | QA preview of damage numbers over the forest backdrop (not a runtime asset). |
| ui/enemy_bar_bg.png | 32x5 | 1 | 32x5 |  | [16, 4] | fill_rect=[1, 1, 30, 3] | small monster HP bar trough; bottom-centre anchor goes on the monster hp_bar_anchor. |
| ui/enemy_bar_hp.png | 30x3 | 1 | 30x3 |  |  |  | 30x3 monster HP fill, draw at [1,1] inside enemy_bar_bg, crop width by HP%. |
| ui/hp_mp_card.png | 96x28 | 1 | 96x28 |  | [0, 0] | portrait_rect=[4, 4, 20, 20], hp_bar_rect=[36, 6, 54, 5], mp_bar_rect=[36, 16, 54, 5], hp_label=[27, 7], mp_label=[27, 17], legacy=true | LEGACY (landscape 480x270): use ui/portrait/hp_mp_card_narrow.png. 96x28. Empty bar troughs are baked in; draw bar_hp/bar_mp fills (54x5) at the rects, scaled/cropped horizontally by HP%. |
| ui/icon_gold.png | 10x10 | 1 | 10x10 |  | [0, 0] |  | 10x10 gold coin. |
| ui/items/blob_crown.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=blob_crown, name=Grinning Crown, slot=trinket, rarity=unique | 16x16 item icon (Grinning Crown): blue slime crown with a grin and drips. No rarity border (UI tints by rarity). |
| ui/items/blue_ether.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=blue_ether, name=Blue Ether, slot=usable, rarity=rare | 16x16 item icon (Blue Ether): bigger blue flask, gold collar and cork, sparkles. No rarity border (UI tints by rarity). |
| ui/items/bread_charm.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=bread_charm, name=Bread Charm, slot=trinket, rarity=common | 16x16 item icon (Bread Charm): bread crust bound with a red thread cross, on a loop. No rarity border (UI tints by rarity). |
| ui/items/brute_heart.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=brute_heart, name=Brute Heart, slot=trinket, rarity=unique | 16x16 item icon (Brute Heart): grey stone heart with glowing orange cracks. No rarity border (UI tints by rarity). |
| ui/items/chapel_mace.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=chapel_mace, name=Chapel Mace, slot=weapon, rarity=common | 16x16 item icon (Chapel Mace): flanged steel ball on a wooden haft, small gold cross. No rarity border (UI tints by rarity). |
| ui/items/field_salve.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=field_salve, name=Field Salve, slot=usable, rarity=rare | 16x16 item icon (Field Salve): silver salve tin with a red cross and a herb sprig. No rarity border (UI tints by rarity). |
| ui/items/glass_orb.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=glass_orb, name=Glass Orb, slot=off, rarity=common | 16x16 item icon (Glass Orb): clear glass ball with a gold spark inside, on a wooden stand. No rarity border (UI tints by rarity). |
| ui/items/gravel_axe.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=gravel_axe, name=Gravel Axe, slot=weapon, rarity=common | 16x16 item icon (Gravel Axe): long haft, chipped grey stone-like axe head. No rarity border (UI tints by rarity). |
| ui/items/hedge_mail.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=hedge_mail, name=Hedge Mail, slot=armor, rarity=common | 16x16 item icon (Hedge Mail): hedge-green jack studded with silver rings, leather belt. No rarity border (UI tints by rarity). |
| ui/items/howl_fang.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=howl_fang, name=Howl Fang, slot=weapon, rarity=unique | 16x16 item icon (Howl Fang): a curved bone fang bound to a cord. No rarity border (UI tints by rarity). |
| ui/items/hymn_board.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=hymn_board, name=Hymn Board, slot=off, rarity=common | 16x16 item icon (Hymn Board): arched wooden board with faded verse lines and a gold cross. No rarity border (UI tints by rarity). |
| ui/items/keep_plate.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=keep_plate, name=Keep Plate, slot=armor, rarity=rare | 16x16 item icon (Keep Plate): broad steel plate, double pauldrons, gold trim (heaviest silhouette). No rarity border (UI tints by rarity). |
| ui/items/kettle_dram.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=kettle_dram, name=Kettle Dram, slot=usable, rarity=common | 16x16 item icon (Kettle Dram): little copper kettle, half red / half blue contents, steam. No rarity border (UI tints by rarity). |
| ui/items/kettle_shield.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=kettle_shield, name=Kettle Shield, slot=off, rarity=common | 16x16 item icon (Kettle Shield): dented grey pot lid with a knob handle. No rarity border (UI tints by rarity). |
| ui/items/kiln_plate.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=kiln_plate, name=Kiln Plate, slot=armor, rarity=common | 16x16 item icon (Kiln Plate): brick-red breastplate and pauldrons, amber rivets. No rarity border (UI tints by rarity). |
| ui/items/kiln_sword.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=kiln_sword, name=Kiln Sword, slot=weapon, rarity=rare | 16x16 item icon (Kiln Sword): longer, wider blade with a blued edge; brick-red guard and grip. No rarity border (UI tints by rarity). |
| ui/items/lamp_staff.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=lamp_staff, name=Lamp Staff, slot=weapon, rarity=rare | 16x16 item icon (Lamp Staff): staff topped with a glowing gold lantern. No rarity border (UI tints by rarity). |
| ui/items/ley_locket.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=ley_locket, name=Ley Locket, slot=trinket, rarity=legendary | 16x16 item icon (Ley Locket): gold heart locket with a violet gem, chain and glints. No rarity border (UI tints by rarity). |
| ui/items/loaf_crumb.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=loaf_crumb, name=Loaf Crumb, slot=usable, rarity=common | 16x16 item icon (Loaf Crumb): torn chunk of brown loaf. No rarity border (UI tints by rarity). |
| ui/items/lurker_scale.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=lurker_scale, name=Bone Plate, slot=armor, rarity=unique | 16x16 item icon (Bone Plate): pale bone rib-plate with knuckle-bone pauldrons. No rarity border (UI tints by rarity). |
| ui/items/marsh_bow.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=marsh_bow, name=Marsh Bow, slot=weapon, rarity=rare | 16x16 item icon (Marsh Bow): dark-green waxed recurve, wrapped grip, sky string sparks. No rarity border (UI tints by rarity). |
| ui/items/moon_robe.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=moon_robe, name=Moon Robe, slot=armor, rarity=rare | 16x16 item icon (Moon Robe): pale robe with violet V-neck and hem, gold crescent. No rarity border (UI tints by rarity). |
| ui/items/night_shard.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=night_shard, name=Night Shard, slot=weapon, rarity=rare | 16x16 item icon (Night Shard): jagged black-violet glass shard on a blue grip. No rarity border (UI tints by rarity). |
| ui/items/oak_buckler.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=oak_buckler, name=Oak Buckler, slot=off, rarity=rare | 16x16 item icon (Oak Buckler): round oak with an iron rim, studs and an iron rose boss. No rarity border (UI tints by rarity). |
| ui/items/oath_blade.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=oath_blade, name=Oath Blade, slot=weapon, rarity=common | 16x16 item icon (Oath Blade): plain short steel sword, gold vow line in the fuller. No rarity border (UI tints by rarity). |
| ui/items/pocket_knife.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=pocket_knife, name=Pocket Knife, slot=weapon, rarity=common | 16x16 item icon (Pocket Knife): tiny folding knife, wooden handle with rivet (smallest blade). No rarity border (UI tints by rarity). |
| ui/items/pond_bead.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=pond_bead, name=Pond Bead, slot=trinket, rarity=rare | 16x16 item icon (Pond Bead): mill-water teal glass bead on a cord. No rarity border (UI tints by rarity). |
| ui/items/reed_staff.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=reed_staff, name=Reed Staff, slot=weapon, rarity=common | 16x16 item icon (Reed Staff): jointed pale reed with copper wire bands and a green tuft. No rarity border (UI tints by rarity). |
| ui/items/reed_wrap.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=reed_wrap, name=Reed Wrap, slot=armor, rarity=common | 16x16 item icon (Reed Wrap): green marsh cloak with woven tan reed strands. No rarity border (UI tints by rarity). |
| ui/items/road_lute.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=road_lute, name=Road Lute, slot=weapon, rarity=common | 16x16 item icon (Road Lute): pear-shaped wooden lute, dark sound hole, cream strings. No rarity border (UI tints by rarity). |
| ui/items/sap_crook.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=sap_crook, name=Sap Crook, slot=weapon, rarity=common | 16x16 item icon (Sap Crook): hooked shepherd crook, leaf sprout and an amber sap drip. No rarity border (UI tints by rarity). |
| ui/items/sunbrand.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=sunbrand, name=Sunbrand, slot=weapon, rarity=legendary | 16x16 item icon (Sunbrand): full-diagonal gold greatsword, long guard, red sun gem, glints. No rarity border (UI tints by rarity). |
| ui/items/thorn_bow.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=thorn_bow, name=Thorn Bow, slot=weapon, rarity=common | 16x16 item icon (Thorn Bow): simple wooden bow with thorn nubs, cream string. No rarity border (UI tints by rarity). |
| ui/items/threat_bell.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=threat_bell, name=Threat Bell, slot=trinket, rarity=rare | 16x16 item icon (Threat Bell): gold bell with a red ribbon and dark clapper. No rarity border (UI tints by rarity). |
| ui/items/tonic.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=tonic, name=Hearth Tonic, slot=usable, rarity=common | 16x16 item icon (Hearth Tonic): round glass flask of red tonic, cork. No rarity border (UI tints by rarity). |
| ui/items/travel_coat.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=travel_coat, name=Travel Coat, slot=armor, rarity=common | 16x16 item icon (Travel Coat): long brown waxed coat, tan collar, gold buttons. No rarity border (UI tints by rarity). |
| ui/items/vial.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=vial, name=Lamp Vial, slot=usable, rarity=common | 16x16 item icon (Lamp Vial): slim blue vial with a gold collar. No rarity border (UI tints by rarity). |
| ui/items/void_lens.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=void_lens, name=Void Lens, slot=off, rarity=rare | 16x16 item icon (Void Lens): gold-framed hand lens full of dark violet void and a star. No rarity border (UI tints by rarity). |
| ui/items/wick_ring.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=wick_ring, name=Wick Ring, slot=trinket, rarity=common | 16x16 item icon (Wick Ring): copper ring with a tiny candle stub and flame. No rarity border (UI tints by rarity). |
| ui/items/wisp_jar.png | 16x16 | 1 | 16x16 |  |  | status=approved, item=wisp_jar, name=Cap Jar, slot=trinket, rarity=unique | 16x16 item icon (Cap Jar): corked glass jar holding an orange glow. No rarity border (UI tints by rarity). |
| ui/panel_dark.png | 48x48 | 1 | 48x48 |  |  | nine_slice_margins={"left": 6, "top": 6, "right": 6, "bottom": 6} | 48x48 NinePatchRect source; margins 6px each side (frame 5px + 1px interior). Centre may tile or stretch (speckle is sparse). |
| ui/panel_parchment.png | 48x48 | 1 | 48x48 |  |  | nine_slice_margins={"left": 6, "top": 6, "right": 6, "bottom": 6} | 48x48 NinePatchRect source; margins 6px each side (frame 5px + 1px interior). Centre may tile or stretch (speckle is sparse). |
| ui/portrait/ability_attack.png | 32x32 | 1 | 32x32 |  |  |  | default ability "attack" in the skill-slot style (always available for every class). |
| ui/portrait/ability_attack_active.png | 32x32 | 1 | 32x32 |  |  |  | selected state. default ability "attack" in the skill-slot style (always available for every class). |
| ui/portrait/ability_cover.png | 32x32 | 1 | 32x32 |  |  |  | default ability "cover" in the skill-slot style (always available for every class). |
| ui/portrait/ability_cover_active.png | 32x32 | 1 | 32x32 |  |  |  | selected state. default ability "cover" in the skill-slot style (always available for every class). |
| ui/portrait/action_bar.png | 270x48 | 1 | 270x48 |  | [0, 47] | nine_slice_margins={"left": 6, "top": 6, "right": 6, "bottom": 6}, button_rects=[[19, 8, 32, 32], [69, 8, 32, 32], [119, 8, 32, 32], [169, 8, 32, 32], [219, 8, 32, 32]], legacy=true | LEGACY (landscape 480x270): use ui/portrait/action_bar_v2.png (v6 per-character bar). 270x48 bottom bar; place at y=432 (bottom-left anchor at y 479). 5 buttons 32x32, 18px gaps, order attack/skill/item/cover/run. |
| ui/portrait/action_bar_examples.png | 278x220 | 1 | 278x220 |  |  |  | QA: the v6 bar swapping per active character (paladin: selected/cooldown/locked + passive 5; wizard: passive 5; rogue: all 5 active). Not a runtime asset. |
| ui/portrait/action_bar_examples_3x.png | 834x660 | 1 | 834x660 |  |  |  | 3x nearest. |
| ui/portrait/action_bar_v2.png | 270x50 | 1 | 270x50 |  | [0, 0] | slots={"attack": [4, 4], "cover": [37, 4], "divider_x": 71, "skills": [[75, 4], [108, 4], [141, 4], [174, 4], [207, 4]], "item": [245, 4], "run": [245, 26], "cost_badges": [[83, 38], [116, 38], [149, 38], [182, 38], [215, 38]]}, slot_size=32, mini_size=20 | v6 per-character action bar (replaces ui/portrait/action_bar.png). Slot top-lefts in bar-local px: attack/cover default abilities (32x32), gold divider at x71, 5 class skills (32x32, step 33), Item/Run mini buttons (20x20) stacked at the right, 16x7 MP cost badges centred under each active skill (y38). |
| ui/portrait/bar_bg_90.png | 90x7 | 1 | 90x7 |  |  | fill_rect=[1, 1, 88, 5], legacy=true | LEGACY (landscape 480x270): v7: party HP/MP now shown as seat-mounted bars (ui/portrait/seat_bars_frame*.png + seat_bar_hp/mp). 90x7 trough (already baked into the narrow card). |
| ui/portrait/bar_dim_mask.png | 32x32 | 1 | 32x32 |  |  |  | 50% dither drawn over every OTHER bar slot while a skill card is open (optional focus dim). |
| ui/portrait/bar_hp_44.png | 44x5 | 1 | 44x5 |  |  | legacy=true | LEGACY (landscape 480x270): v7: party HP/MP now shown as seat-mounted bars (ui/portrait/seat_bars_frame*.png + seat_bar_hp/mp). 44x5 HP fill for hp_mp_card_compact (rect [4,27,44,5]). |
| ui/portrait/bar_hp_88.png | 88x5 | 1 | 88x5 |  |  | legacy=true | LEGACY (landscape 480x270): v7: party HP/MP now shown as seat-mounted bars (ui/portrait/seat_bars_frame*.png + seat_bar_hp/mp). 88x5 HP fill for the narrow card. |
| ui/portrait/bar_mp_44.png | 44x5 | 1 | 44x5 |  |  | legacy=true | LEGACY (landscape 480x270): v7: party HP/MP now shown as seat-mounted bars (ui/portrait/seat_bars_frame*.png + seat_bar_hp/mp). 44x5 MP fill for hp_mp_card_compact (rect [4,34,44,5]). |
| ui/portrait/bar_mp_88.png | 88x5 | 1 | 88x5 |  |  | legacy=true | LEGACY (landscape 480x270): v7: party HP/MP now shown as seat-mounted bars (ui/portrait/seat_bars_frame*.png + seat_bar_hp/mp). 88x5 MP fill for the narrow card. |
| ui/portrait/btn32_attack.png | 32x32 | 1 | 32x32 |  | [0, 0] | icon_rect=[6, 6, 20, 20], legacy=true | LEGACY (landscape 480x270): fallback only; the v6 bar uses ability_attack/ability_cover, class skill slots and mini_item/mini_run. 32x32 bottom-bar action button (same icon art as ui/btn_*). |
| ui/portrait/btn32_attack_active.png | 32x32 | 1 | 32x32 |  | [0, 0] | icon_rect=[6, 6, 20, 20], legacy=true | LEGACY (landscape 480x270): fallback only; the v6 bar uses ability_attack/ability_cover, class skill slots and mini_item/mini_run. selected (gold). 32x32 bottom-bar action button (same icon art as ui/btn_*). |
| ui/portrait/btn32_cover.png | 32x32 | 1 | 32x32 |  | [0, 0] | icon_rect=[6, 6, 20, 20], legacy=true | LEGACY (landscape 480x270): fallback only; the v6 bar uses ability_attack/ability_cover, class skill slots and mini_item/mini_run. 32x32 bottom-bar action button (same icon art as ui/btn_*). |
| ui/portrait/btn32_cover_active.png | 32x32 | 1 | 32x32 |  | [0, 0] | icon_rect=[6, 6, 20, 20], legacy=true | LEGACY (landscape 480x270): fallback only; the v6 bar uses ability_attack/ability_cover, class skill slots and mini_item/mini_run. selected (gold). 32x32 bottom-bar action button (same icon art as ui/btn_*). |
| ui/portrait/btn32_item.png | 32x32 | 1 | 32x32 |  | [0, 0] | icon_rect=[6, 6, 20, 20], legacy=true | LEGACY (landscape 480x270): fallback only; the v6 bar uses ability_attack/ability_cover, class skill slots and mini_item/mini_run. 32x32 bottom-bar action button (same icon art as ui/btn_*). |
| ui/portrait/btn32_item_active.png | 32x32 | 1 | 32x32 |  | [0, 0] | icon_rect=[6, 6, 20, 20], legacy=true | LEGACY (landscape 480x270): fallback only; the v6 bar uses ability_attack/ability_cover, class skill slots and mini_item/mini_run. selected (gold). 32x32 bottom-bar action button (same icon art as ui/btn_*). |
| ui/portrait/btn32_run.png | 32x32 | 1 | 32x32 |  | [0, 0] | icon_rect=[6, 6, 20, 20], legacy=true | LEGACY (landscape 480x270): fallback only; the v6 bar uses ability_attack/ability_cover, class skill slots and mini_item/mini_run. 32x32 bottom-bar action button (same icon art as ui/btn_*). |
| ui/portrait/btn32_run_active.png | 32x32 | 1 | 32x32 |  | [0, 0] | icon_rect=[6, 6, 20, 20], legacy=true | LEGACY (landscape 480x270): fallback only; the v6 bar uses ability_attack/ability_cover, class skill slots and mini_item/mini_run. selected (gold). 32x32 bottom-bar action button (same icon art as ui/btn_*). |
| ui/portrait/btn32_skill.png | 32x32 | 1 | 32x32 |  | [0, 0] | icon_rect=[6, 6, 20, 20], legacy=true | LEGACY (landscape 480x270): fallback only; the v6 bar uses ability_attack/ability_cover, class skill slots and mini_item/mini_run. 32x32 bottom-bar action button (same icon art as ui/btn_*). |
| ui/portrait/btn32_skill_active.png | 32x32 | 1 | 32x32 |  | [0, 0] | icon_rect=[6, 6, 20, 20], legacy=true | LEGACY (landscape 480x270): fallback only; the v6 bar uses ability_attack/ability_cover, class skill slots and mini_item/mini_run. selected (gold). 32x32 bottom-bar action button (same icon art as ui/btn_*). |
| ui/portrait/cost_badge.png | 16x7 | 1 | 16x7 |  |  | digit_origin=[7, 1] | MP cost badge (blue pill + drop). Draw digits_3x5 at digit_origin (x 6 for 2 digits). Centre under each ACTIVE skill slot (slot x + 8, bar y 38). Passives get no badge. |
| ui/portrait/cost_badge_0_9.png | 160x7 | 10 | 16x7 |  |  |  | pre-rendered cost badges for MP 0..9 (frame i = cost i). |
| ui/portrait/digits_3x5.png | 40x5 | 10 | 4x5 |  |  |  | tiny white digits 0-9 (3x5 glyph + 1px advance) for cost badges / cooldown counters. Tint by modulate if needed. |
| ui/portrait/digits_3x5_outlined.png | 50x7 | 10 | 5x7 |  |  | advance=4 | HP-number digits: cream 3x5 glyph (sand bottom row) with a 1px #120c18 outline (diagonals included) so it reads on any robe incl. white. Draw successive digits 4px apart (outline columns overlap). |
| ui/portrait/hp_mp_card_compact.png | 52x44 | 1 | 52x44 |  | [0, 0] | portrait_rect=[16, 4, 20, 20], hp_bar_rect=[4, 27, 44, 5], mp_bar_rect=[4, 34, 44, 5], legacy=true | LEGACY (landscape 480x270): v7: party HP/MP now shown as seat-mounted bars (ui/portrait/seat_bars_frame*.png + seat_bar_hp/mp). v5 compact vertical party card 52x44 for a 5-wide row (step 54 = 52 + 2px gap). Face crop (paperdoll portrait_crop_rect) at portrait_rect; bar_hp_44/bar_mp_44 at the bar rects, cropped by %. Bars are colour-coded red/blue (no HP/MP text at this size). |
| ui/portrait/hp_mp_card_compact_active.png | 52x44 | 1 | 52x44 |  | [0, 0] | portrait_rect=[16, 4, 20, 20], hp_bar_rect=[4, 27, 44, 5], mp_bar_rect=[4, 34, 44, 5], legacy=true | LEGACY (landscape 480x270): v7: party HP/MP now shown as seat-mounted bars (ui/portrait/seat_bars_frame*.png + seat_bar_hp/mp). ACTIVE/current-turn highlight (gold frame). v5 compact vertical party card 52x44 for a 5-wide row (step 54 = 52 + 2px gap). Face crop (paperdoll portrait_crop_rect) at portrait_rect; bar_hp_44/bar_mp_44 at the bar rects, cropped by %. Bars are colour-coded red/blue (no HP/MP text at this size). |
| ui/portrait/hp_mp_card_narrow.png | 130x28 | 1 | 130x28 |  | [0, 0] | portrait_rect=[4, 4, 20, 20], hp_bar_rect=[36, 6, 88, 5], mp_bar_rect=[36, 16, 88, 5], hp_label=[27, 7], mp_label=[27, 17], legacy=true | LEGACY (landscape 480x270): v7: party HP/MP now shown as seat-mounted bars (ui/portrait/seat_bars_frame*.png + seat_bar_hp/mp). 130x28 portrait-layout card (2x2 grid). Draw bar_hp_88/bar_mp_88 at the rects, cropped by %. |
| ui/portrait/icon_cooldown.png | 9x7 | 1 | 9x7 |  |  |  | tiny skill-card info icon (cooldown turns); text starts 2px to its right. |
| ui/portrait/lock_icon.png | 10x10 | 1 | 10x10 |  |  |  | locked-skill padlock, draw at slot [11,11] over a dimmed icon in skill_slot_locked. |
| ui/portrait/mini_item.png | 20x20 | 1 | 20x20 |  |  | icon_rect=[3, 3, 14, 14] | utility: open inventory (potion). |
| ui/portrait/mini_item_active.png | 20x20 | 1 | 20x20 |  |  | icon_rect=[3, 3, 14, 14] | pressed/selected. utility: open inventory (potion). |
| ui/portrait/mini_run.png | 20x20 | 1 | 20x20 |  |  | icon_rect=[3, 3, 14, 14] | utility: flee (door + arrow). |
| ui/portrait/mini_run_active.png | 20x20 | 1 | 20x20 |  |  | icon_rect=[3, 3, 14, 14] | pressed/selected. utility: flee (door + arrow). |
| ui/portrait/name_tab.png | 64x10 | 1 | 64x10 |  |  | text_origin=[5, 2], text_color=#120c18 | active-character nameplate tab: draw at bar top-left (x 4, bar_y - 10); class/hero name in the pixel font at text_origin (max ~13 chars). Gold = same highlight as hp_mp_card_compact_active. |
| ui/portrait/passive_dim_mask.png | 24x24 | 1 | 24x24 |  |  | offset_in_slot=[4, 4] | 25% ink dither drawn over a PASSIVE icon so it reads as non-pressable (binary alpha). |
| ui/portrait/seat_bar_hp.png | 42x4 | 1 | 42x4 |  |  |  | HP fill (#ec5a44, #c02c2c bottom shade). Crop width = round(42 * hp%). |
| ui/portrait/seat_bar_hp_lowflash.png | 84x4 | 2 | 42x4 | 4 |  |  | low-HP (<25%) flash: frame 0 normal red, frame 1 cream/amber. Crop both frames to the same fill width. |
| ui/portrait/seat_bar_hp_tile.png | 1x4 | 1 | 1x4 |  |  |  | 1px HP fill column; stretch horizontally (nearest) instead of cropping the full strip. |
| ui/portrait/seat_bar_mp.png | 42x3 | 1 | 42x3 |  |  |  | MP fill (#4c9ce8 over #3466cc). Crop width = round(42 * mp%). |
| ui/portrait/seat_bar_mp_tile.png | 1x3 | 1 | 1x3 |  |  |  | 1px MP fill column; stretch horizontally. |
| ui/portrait/seat_bars_frame.png | 44x10 | 1 | 44x10 |  | [22, 0] | hp_fill_rect=[1, 1, 42, 4], mp_fill_rect=[1, 6, 42, 3] | v7 seat-mounted HP/MP bars: #120c18 outline frame with dark empty tracks (HP #3e1016, MP #161c40). Anchor = top-centre; place at (seat_x, seat_feet_y - 11) so it overlaps the chair seat front + lower rails. Fill with seat_bar_hp/mp (crop by %) or stretch the 1px tiles. |
| ui/portrait/seat_bars_frame_active.png | 46x12 | 1 | 46x12 |  | [23, 1] | hp_fill_rect=[2, 2, 42, 4], mp_fill_rect=[2, 7, 42, 3] | ACTIVE seat variant: gold inner ring + dark outer outline (1px larger each side). Same anchor point as the normal frame (top-centre of the inner frame at [23,1]). |
| ui/portrait/skill_card_examples.png | 480x252 | 1 | 480x252 |  |  |  | QA: skill card states (active ready, passive, not enough MP, on cooldown). Placeholder copy. Not a runtime asset. |
| ui/portrait/skill_card_examples_3x.png | 1440x756 | 1 | 1440x756 |  |  |  | 3x nearest. |
| ui/portrait/skill_card_icon_frame.png | 44x44 | 1 | 44x44 |  |  | icon_rect=[2, 2, 40, 40] | holds the 20x20 skill icon at 2x (nearest) at [2,2]. |
| ui/portrait/skill_card_icon_frame_passive.png | 44x44 | 1 | 44x44 |  |  | icon_rect=[2, 2, 40, 40] | holds the 20x20 skill icon at 2x (nearest) at [2,2]. Octagon = passive. |
| ui/portrait/skill_card_panel.png | 48x48 | 1 | 48x48 |  |  | nine_slice_margins={"left": 14, "top": 10, "right": 6, "bottom": 6}, tile_period=8 | notebook-page 9-slice for the skill card: dark outline, parchment, spiral holes along the top edge, red margin line on the left, faint ruled lines. TILE (not stretch) the edges/centre so holes and ruling keep an 8px rhythm; pick widths/heights = 48 + 8k for a seamless look. |
| ui/portrait/skill_card_strip_cooldown.png | 24x14 | 1 | 24x14 | None |  | three_slice={"left": 5, "right": 5}, text_y=5, text=ON COOLDOWN: {n}, text_colors=["#cfd0d4"] | prompt strip: 3-slice (caps 5px, tile the middle). Text centred at y 5 in the pack 3x5 font. |
| ui/portrait/skill_card_strip_nomp.png | 24x14 | 1 | 24x14 | None |  | three_slice={"left": 5, "right": 5}, text_y=5, text=NOT ENOUGH MP, text_colors=["#ec5a44"] | prompt strip: 3-slice (caps 5px, tile the middle). Text centred at y 5 in the pack 3x5 font. |
| ui/portrait/skill_card_strip_passive.png | 24x14 | 1 | 24x14 | None |  | three_slice={"left": 5, "right": 5}, text_y=5, text=PASSIVE: ALWAYS ACTIVE, text_colors=["#fcb8d4"] | prompt strip: 3-slice (caps 5px, tile the middle). Text centred at y 5 in the pack 3x5 font. |
| ui/portrait/skill_card_strip_ready.png | 48x14 | 2 | 24x14 | 3 |  | three_slice={"left": 5, "right": 5}, text_y=5, text=TAP AGAIN TO CAST, text_colors=["#f8d040", "#fcf0a0"] | prompt strip: 3-slice (caps 5px, tile the middle). Text centred at y 5 in the pack 3x5 font. 2-frame pulse: swap frame + text colour gold/cream at 3 fps. |
| ui/portrait/skill_card_tail.png | 13x8 | 1 | 13x8 |  | [6, 7] | overlap_rows=2 | pointer: tip (anchor) aims at the tapped slot centre; place so rows 0-1 cover the card bottom edge (tail y = card_bottom - 2). |
| ui/portrait/skill_slot_armed.png | 72x36 | 2 | 36x36 | 4 |  | offset_from_slot=[-2, -2] | ARMED state (skill card open, next tap casts): 2px pulsing gold/cream glow ring drawn around the 32px slot (outside the frame). Distinct from skill_slot_active (selected). |
| ui/portrait/skill_tag_active.png | 29x9 | 1 | 29x9 |  |  |  | ACTIVE tag pill (word baked in the pack 3x5 font), top-right of the card. |
| ui/portrait/skill_tag_passive.png | 33x9 | 1 | 33x9 |  |  |  | PASSIVE tag pill (word baked in the pack 3x5 font), top-right of the card. |
| ui/portrait/target_all_allies.png | 9x7 | 1 | 9x7 |  |  |  | tiny skill-card info icon (target type); text starts 2px to its right. |
| ui/portrait/target_all_enemies.png | 9x7 | 1 | 9x7 |  |  |  | tiny skill-card info icon (target type); text starts 2px to its right. |
| ui/portrait/target_ally.png | 9x7 | 1 | 9x7 |  |  |  | tiny skill-card info icon (target type); text starts 2px to its right. |
| ui/portrait/target_enemy.png | 9x7 | 1 | 9x7 |  |  |  | tiny skill-card info icon (target type); text starts 2px to its right. |
| ui/portrait/target_self.png | 9x7 | 1 | 9x7 |  |  |  | tiny skill-card info icon (target type); text starts 2px to its right. |
| ui/portrait/top_bar.png | 270x20 | 1 | 270x20 |  | [0, 0] | nine_slice_margins={"left": 3, "top": 3, "right": 3, "bottom": 3}, gold_icon_pos=[5, 5], gold_text_pos=[18, 8], menu_btn_pos=[249, 1] | 270x20 map/creator top bar. |
| ui/portrait_frame.png | 24x24 | 1 | 24x24 |  | [0, 0] | portrait_rect=[2, 2, 20, 20] | 24x24 (2px border). Draw the 20x20 portrait crop at [2,2]; ink fill behind. |
| ui/portrait_frame_active.png | 24x24 | 1 | 24x24 |  | [0, 0] | portrait_rect=[2, 2, 20, 20] | 24x24 (2px border). Draw the 20x20 portrait crop at [2,2]; ink fill behind. |
| ui/skills/barbarian_1.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=axe chop, kind=active, slot_frame=ui/skills/skill_slot.png, cls=barbarian, slot=1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/barbarian_2.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=rage (angry flame), kind=active, slot_frame=ui/skills/skill_slot.png, cls=barbarian, slot=2 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/barbarian_3.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=war cry (horn + sound waves), kind=active, slot_frame=ui/skills/skill_slot.png, cls=barbarian, slot=3 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/barbarian_4.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=stomp (boot + shockwave), kind=active, slot_frame=ui/skills/skill_slot.png, cls=barbarian, slot=4 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/barbarian_5.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=provoke (taunt/aggro passive: shouting face), kind=passive, slot_frame=ui/skills/skill_slot_passive.png, cls=barbarian, slot=5 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/bard_1.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=music note (damage note), kind=active, slot_frame=ui/skills/skill_slot.png, cls=bard, slot=1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/bard_2.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=song buff (note + up arrow), kind=active, slot_frame=ui/skills/skill_slot.png, cls=bard, slot=2 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/bard_3.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=lullaby (moon + zz), kind=active, slot_frame=ui/skills/skill_slot.png, cls=bard, slot=3 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/bard_4.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=lute, kind=active, slot_frame=ui/skills/skill_slot.png, cls=bard, slot=4 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/bard_5.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=war drum (active: party haste), kind=active, slot_frame=ui/skills/skill_slot.png, cls=bard, slot=5 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/cleric_1.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=heal (green cross), kind=active, slot_frame=ui/skills/skill_slot.png, cls=cleric, slot=1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/cleric_2.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=holy cross (bless), kind=active, slot_frame=ui/skills/skill_slot.png, cls=cleric, slot=2 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/cleric_3.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=resurrect (spirit ankh), kind=active, slot_frame=ui/skills/skill_slot.png, cls=cleric, slot=3 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/cleric_4.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=smite (holy hammer), kind=active, slot_frame=ui/skills/skill_slot.png, cls=cleric, slot=4 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/cleric_5.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=blessed (regen passive: haloed heart), kind=passive, slot_frame=ui/skills/skill_slot_passive.png, cls=cleric, slot=5 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/druid_1.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=leaf heal, kind=active, slot_frame=ui/skills/skill_slot.png, cls=druid, slot=1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/druid_2.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=thorns (thorny vine), kind=active, slot_frame=ui/skills/skill_slot.png, cls=druid, slot=2 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/druid_3.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=bear form, kind=active, slot_frame=ui/skills/skill_slot.png, cls=druid, slot=3 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/druid_4.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=entangling roots, kind=active, slot_frame=ui/skills/skill_slot.png, cls=druid, slot=4 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/druid_5.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=regrowth (passive: sprout, heal over time), kind=passive, slot_frame=ui/skills/skill_slot_passive.png, cls=druid, slot=5 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/paladin_1.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=sword of light (holy strike), kind=active, slot_frame=ui/skills/skill_slot.png, cls=paladin, slot=1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/paladin_2.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=shield bash, kind=active, slot_frame=ui/skills/skill_slot.png, cls=paladin, slot=2 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/paladin_3.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=holy aura (radiant halo), kind=active, slot_frame=ui/skills/skill_slot.png, cls=paladin, slot=3 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/paladin_4.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=taunt (shout burst "!"), kind=active, slot_frame=ui/skills/skill_slot.png, cls=paladin, slot=4 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/paladin_5.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=guardian (aggro passive: target reticle on shield), kind=passive, slot_frame=ui/skills/skill_slot_passive.png, cls=paladin, slot=5 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/ranger_1.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=arrow shot, kind=active, slot_frame=ui/skills/skill_slot.png, cls=ranger, slot=1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/ranger_2.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=multi-shot (3 arrows), kind=active, slot_frame=ui/skills/skill_slot.png, cls=ranger, slot=2 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/ranger_3.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=snare trap (bear trap), kind=active, slot_frame=ui/skills/skill_slot.png, cls=ranger, slot=3 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/ranger_4.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=animal companion (paw print), kind=active, slot_frame=ui/skills/skill_slot.png, cls=ranger, slot=4 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/ranger_5.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=keen eye (accuracy/crit passive), kind=passive, slot_frame=ui/skills/skill_slot_passive.png, cls=ranger, slot=5 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/rogue_1.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=dagger strike, kind=active, slot_frame=ui/skills/skill_slot.png, cls=rogue, slot=1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/rogue_2.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=poison vial, kind=active, slot_frame=ui/skills/skill_slot.png, cls=rogue, slot=2 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/rogue_3.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=smoke bomb, kind=active, slot_frame=ui/skills/skill_slot.png, cls=rogue, slot=3 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/rogue_4.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=backstab (bloody dagger), kind=active, slot_frame=ui/skills/skill_slot.png, cls=rogue, slot=4 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/rogue_5.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=pickpocket (active: steal gold), kind=active, slot_frame=ui/skills/skill_slot.png, cls=rogue, slot=5 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/skill_cooldown_mask.png | 24x24 | 1 | 24x24 |  |  | offset_in_slot=[4, 4] | 50% checker dither; crop from the top by remaining-cooldown fraction and draw over the icon (binary alpha keeps the pixel look). |
| ui/skills/skill_sheet.png | 346x206 | 1 | 346x206 |  |  |  | 8 columns (class) x 5 rows (skill 1..5). Active skills in skill_slot.png, passives in skill_slot_passive.png with a P tag. QA/reference sheet, not a runtime asset. |
| ui/skills/skill_sheet_3x.png | 1038x618 | 1 | 1038x618 |  |  |  | 3x nearest of skill_sheet.png. |
| ui/skills/skill_slot.png | 32x32 | 1 | 32x32 |  |  | icon_offset=[6, 6] | 32x32 skill slot, same footprint as ui/portrait/btn32_*. Icon area 24x24 inside (4..27). |
| ui/skills/skill_slot_active.png | 32x32 | 1 | 32x32 |  |  | icon_offset=[6, 6] | 32x32 skill slot, same footprint as ui/portrait/btn32_*. Icon area 24x24 inside (4..27). |
| ui/skills/skill_slot_locked.png | 32x32 | 1 | 32x32 |  |  | icon_offset=[6, 6] | 32x32 skill slot, same footprint as ui/portrait/btn32_*. Icon area 24x24 inside (4..27). |
| ui/skills/skill_slot_passive.png | 32x32 | 1 | 32x32 |  |  | icon_offset=[6, 6] | PASSIVE slot: octagon with gold rim (reads differently from the square active slot). Not pressable, so there is no active/pressed state; dim with _locked while unlearned. |
| ui/skills/skill_slot_passive_locked.png | 32x32 | 1 | 32x32 |  |  | icon_offset=[6, 6] | PASSIVE slot: octagon with gold rim (reads differently from the square active slot). Not pressable, so there is no active/pressed state; dim with _locked while unlearned. |
| ui/skills/wizard_1.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=fireball, kind=active, slot_frame=ui/skills/skill_slot.png, cls=wizard, slot=1 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/wizard_2.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=ice shard, kind=active, slot_frame=ui/skills/skill_slot.png, cls=wizard, slot=2 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/wizard_3.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=lightning bolt, kind=active, slot_frame=ui/skills/skill_slot.png, cls=wizard, slot=3 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/wizard_4.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=arcane shield (hex ward), kind=active, slot_frame=ui/skills/skill_slot.png, cls=wizard, slot=4 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/skills/wizard_5.png | 20x20 | 1 | 20x20 |  | [10, 10] | motif=mana flow (mana-regen passive: drop + up arrow), kind=passive, slot_frame=ui/skills/skill_slot_passive.png, cls=wizard, slot=5 | placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6). |
| ui/swatch_frame.png | 16x16 | 1 | 16x16 |  | [0, 0] | swatch_rect=[2, 2, 12, 12] | 16x16 colour swatch frame; transparent 12x12 centre for the colour. |
| ui/swatch_frame_active.png | 16x16 | 1 | 16x16 |  | [0, 0] | swatch_rect=[2, 2, 12, 12] | 16x16 colour swatch frame; transparent 12x12 centre for the colour. |
| palette/palette48.gpl | - | | | | | | GIMP/Aseprite palette, 48 named colours. |
| palette/palette48.hex | - | | | | | | 48 hex colours, one per line (Lospec .hex format). |
| tools/ | - | | | | | | reproducible build scripts: build_cut.py -> build_proc.py -> build_doll.py -> build_skills.py -> build_regions.py -> build_items.py -> compose.py (python w/ pillow+numpy+scipy). tools/_work holds intermediates. |
