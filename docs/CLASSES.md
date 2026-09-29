# Classes

Eight classes. A party seats one to five heroes, and each class once. Every class has five skills that nobody else uses: three or four actives and one or two passives. Body, Senses, and Mind from the class add up to 6, then persona, race, and the +2 base still apply.

Actives are the Skill buttons. Passives are always on. They are tagged Passive in the creator and on the party panel. The action bar still draws each passive in the octagon frame (`skill_slot_passive`); that slot opens the card and does not cast.

Mana skills use the energy formula `round((base + rank × 20) × (1 + reduction))`. The button shows that rank-1 cost. Cooldown skills arm on use and tick down by 1 at the start of each of your later turns, including a turn you spend stunned. A cooldown of 3 is ready again on the turn it reaches 0. An HP cost is payable only when it would leave at least 1 health. Build-up skills add points up to a cap, and the spender refuses the action until you have the cost.

Passive hooks are `turn_start`, `on_hit`, `on_damaged`, `threat`, and `stat`.

## Threat raffle

A monster picks one living party member by raffle. Dead members are left out. Threat is never below 1, so a living member is never fully safe.

`P(member) = threat / sum of living threat`

Kyle's example: threats 30, 3, 5, and 1 sum to 39, about 77%, 8%, 13%, and 3%.

The number itself is data. Coefficients live in [`data/threat.json`](../data/threat.json). Each class has `base_threat` in [`data/classes.json`](../data/classes.json).

`threat = max(1, round((base_threat + Body × body_per + DR × armor_per + taunt + passive_add) × passive_mult × cover_mult))`

`body_per` is 2 and `armor_per` is 0.05. Cover multiplies by `cover_mult` (0.5) and still cannot drop the result below 1. Taunt skills add a flat amount until that character's next turn. They do not force the next hit. Oathmagnet multiplies by 2. Blood Price multiplies by 1.5.

| Class | Base threat |
| --- | --- |
| Paladin | 16 |
| Barbarian | 12 |
| Cleric | 4 |
| Ranger | 3 |
| Druid | 3 |
| Bard | 2 |
| Wizard | 2 |
| Rogue | 1 |

A Paladin with Body 8, no armor, and Oathmagnet is `round((16 + 16) × 2) = 64`. A Wizard with Body 3 is `round(2 + 6) = 8`. The same formula is written up in [`docs/DESIGN.md`](DESIGN.md).

| Class | Role | Body / Senses / Mind | Actives | Passive |
| --- | --- | --- | --- | --- |
| Paladin | Tank | 4 / 1 / 1 | Oathstrike, Hearthmend, Shieldwall, Rallying Brand | Oathmagnet |
| Wizard | Burst and control | 1 / 2 / 3 | Emberburst, Frostpin, Cinder Needle, Stillglass | Ley Siphon |
| Ranger | Striker | 2 / 3 / 1 | Marked Shot, Thorn Volley, Snare Trap, Quick Draw | First Mark |
| Bard | Support | 2 / 2 / 2 | Mending Verse, Dissonant Chord, Downbeat, Crescendo | Hearth Chorus |
| Cleric | Healer | 2 / 1 / 3 | Lantern Prayer, Warding Light, Purge Hymn, Spark of Mercy | Open Hands |
| Rogue | Burst | 1 / 4 / 1 | Pocket Cut, Kidney Nick, Venom Needle, Ledger Strike | Keen Nick |
| Barbarian | Bruiser | 5 / 1 / 0 | Bloodswing, Roar, Rage Crash, Thick Hide | Blood Price |
| Druid | Damage over time | 2 / 2 / 2 | Briar Seed, Mossknit, Wildshape Guard, Spore Puff | Sap Pulse |

| Class | Skill | Type | Resource | Cost | Target | Effect |
| --- | --- | --- | --- | --- | --- | --- |
| Paladin | Oathstrike | Active | Mana | base 100 (120 EN at rank 1) | One front foe | Weapon hit at 1.55× attack. Threat +3 until your next turn. |
| Paladin | Hearthmend | Active | Mana | base 150 (170 EN at rank 1) | One ally | Heal 28 + 2×Mind + 6 per rank above 1. You also heal 16 if the target is someone else. |
| Paladin | Shieldwall | Active | Cooldown | 3 turns | Self | +10 damage reduction for 2 of your turns. Threat +2. |
| Paladin | Rallying Brand | Active | Free | Free | One ally | Heal 14 + 1×Mind + 4 per rank above 1. |
| Paladin | Oathmagnet | Passive | Threat, on damaged | Always on | Self | Multiplies threat by 2. A hit against you deals 4 damage back. |
| Wizard | Emberburst | Active | Mana | base 150 (170 EN at rank 1) | One foe, back row allowed | Spell 22 + 3×Mind. Half of that splashes to neighbors. Burn 8, Senses save. |
| Wizard | Frostpin | Active | Mana | base 150 (170 EN at rank 1) | One foe, back row allowed | Spell 18 + 2×Mind. Stun, Body save. |
| Wizard | Cinder Needle | Active | Free | Free | One foe, back row allowed | Spell 10 + 2×Mind. |
| Wizard | Stillglass | Active | Cooldown | 3 turns | One foe, back row allowed | Spell 8 + 1×Mind. Stun, Body save. |
| Wizard | Ley Siphon | Passive | Turn start | Always on | Self | Regain 8% of max energy at the start of each of your turns. |
| Ranger | Marked Shot | Active | Mana | base 100 (120 EN at rank 1) | One foe, back row allowed | Spell 16 + 2×Senses. +10 if that foe acts after you. |
| Ranger | Thorn Volley | Active | Mana | base 180 (200 EN at rank 1) | Up to 3 foes | Spell 12 + 1×Senses each. Front or back. |
| Ranger | Snare Trap | Active | Cooldown | 3 turns | One foe, back row allowed | Spell 8 + 1×Senses. Stun, Senses save. |
| Ranger | Quick Draw | Active | Free | Free | One foe, back row allowed | Weapon hit at 0.85× attack. |
| Ranger | First Mark | Passive | Stat | Always on | Self | +5 initiative. |
| Bard | Mending Verse | Active | Mana | base 120 (140 EN at rank 1) | One ally | Heal 24 + 3×Mind + 6 per rank above 1. |
| Bard | Dissonant Chord | Active | Mana | base 150 (170 EN at rank 1) | One front foe | Spell 14 + 2×Mind. Half splashes. Poison 7, Body save. |
| Bard | Downbeat | Active | Free | +1 Tempo (cap 4) | Self | Gain Tempo. No damage. |
| Bard | Crescendo | Active | Tempo | 3 Tempo | One ally | Heal 36 + 4×Mind + 6 per rank above 1. |
| Bard | Hearth Chorus | Passive | Stat | Always on | Party | While the bard is standing, the party has +3 damage reduction. |
| Cleric | Lantern Prayer | Active | Mana | base 160 (180 EN at rank 1) | One ally | Heal 34 + 4×Mind + 8 per rank above 1. |
| Cleric | Warding Light | Active | Mana | base 80 (100 EN at rank 1) | One ally | +8 damage reduction for 2 of that ally's turns. |
| Cleric | Purge Hymn | Active | Cooldown | 3 turns | One ally | Clear burn, poison, and stun, then heal 12 + 1×Mind. |
| Cleric | Spark of Mercy | Active | Free | Free | One ally | Heal 12 + 1×Mind. |
| Cleric | Open Hands | Passive | Stat | Always on | Self | Your heals restore 25% more. |
| Rogue | Pocket Cut | Active | Free | +1 Combo (cap 5) | One front foe | Weapon hit at 0.8× attack. Gain Combo. |
| Rogue | Kidney Nick | Active | Cooldown | 2 turns | One front foe | Weapon hit at 0.7× attack. Stun, Body save. |
| Rogue | Venom Needle | Active | Mana | base 100 (120 EN at rank 1) | One foe, back row allowed | Spell 12 + 1×Senses. Poison 7, Body save. |
| Rogue | Ledger Strike | Active | Combo | 4 Combo | One front foe | Weapon hit at 2.1× attack. |
| Rogue | Keen Nick | Passive | Stat, on hit | Always on | Self | +10 crit chance. Every hit you land deals 6 extra damage. |
| Barbarian | Bloodswing | Active | Health | 12 HP | One front foe | Weapon hit at 1.65× attack. Refused if it would drop you to 0. Threat +1. |
| Barbarian | Roar | Active | Free | +2 Rage (cap 6) | Self | Gain Rage. Threat +2. |
| Barbarian | Rage Crash | Active | Rage | 4 Rage | One front foe | Weapon hit at 1.9× attack. Half splashes to neighbors. |
| Barbarian | Thick Hide | Active | Cooldown | 3 turns | Self | +12 damage reduction for 2 of your turns. |
| Barbarian | Blood Price | Passive | Threat, stat | Always on | Self | Multiplies threat by 1.5. Damage rises as health falls, up to +50% when empty. |
| Druid | Briar Seed | Active | Mana | base 120 (140 EN at rank 1) | One foe, back row allowed | Spell 10 + 2×Mind. Poison 8, Body save. |
| Druid | Mossknit | Active | Mana | base 120 (140 EN at rank 1) | One ally | Heal 22 + 2×Mind + 6 per rank above 1. |
| Druid | Wildshape Guard | Active | Cooldown | 3 turns | Self | +8 damage reduction for 2 of your turns. |
| Druid | Spore Puff | Active | Free | Free | Up to 2 foes | Spell 6 + 1×Mind. Poison 5, Body save. Front or back. |
| Druid | Sap Pulse | Passive | Turn start | Always on | Self | Regain 5% of max health at the start of each of your turns. |

Spell and heal amounts above are the rank-1 base before Mind, Senses, and extra ranks. Ranks above 1 add the per-rank term in the skill data. Conditions use the same save, timer, and damage rules as the rest of combat: burn ticks health, poison drains energy first, stun skips the turn.

## Skill icons

Icons are `art_source/phase0/ui/skills/<file>.png`. The number is the Art Director's slot, not the order on the bar. Every passive uses the octagon frame even when the painted icon was an active motif.

| Class | Skill | Icon | Notes |
| --- | --- | --- | --- |
| Paladin | Oathstrike | paladin_1 | Sword of light |
| Paladin | Shieldwall | paladin_2 | Shield |
| Paladin | Hearthmend | paladin_3 | Holy aura |
| Paladin | Rallying Brand | paladin_4 | Shout |
| Paladin | Oathmagnet | paladin_5 | Guardian mark. Passive frame |
| Wizard | Emberburst | wizard_1 | Fireball |
| Wizard | Frostpin | wizard_2 | Ice |
| Wizard | Cinder Needle | wizard_3 | Lightning. No needle was drawn |
| Wizard | Stillglass | wizard_4 | Arcane ward |
| Wizard | Ley Siphon | wizard_5 | Mana flow. Passive frame |
| Ranger | Marked Shot | ranger_1 | Arrow |
| Ranger | Thorn Volley | ranger_2 | Multi-shot |
| Ranger | Snare Trap | ranger_3 | Trap |
| Ranger | Quick Draw | ranger_4 | Paw. No quick-draw icon was drawn |
| Ranger | First Mark | ranger_5 | Keen eye. Passive frame |
| Bard | Dissonant Chord | bard_1 | Damage note |
| Bard | Mending Verse | bard_2 | Song |
| Bard | Hearth Chorus | bard_3 | Lullaby. Passive frame. Every bard icon was painted as an active |
| Bard | Downbeat | bard_4 | Lute |
| Bard | Crescendo | bard_5 | War drum |
| Cleric | Lantern Prayer | cleric_1 | Green cross |
| Cleric | Warding Light | cleric_2 | Holy cross |
| Cleric | Purge Hymn | cleric_3 | Cleanse |
| Cleric | Spark of Mercy | cleric_4 | Hammer. No small-heal icon was drawn |
| Cleric | Open Hands | cleric_5 | Haloed heart. Passive frame |
| Rogue | Pocket Cut | rogue_1 | Dagger |
| Rogue | Venom Needle | rogue_2 | Poison vial |
| Rogue | Kidney Nick | rogue_3 | Smoke |
| Rogue | Ledger Strike | rogue_4 | Backstab |
| Rogue | Keen Nick | rogue_5 | Pickpocket. Passive frame |
| Barbarian | Bloodswing | barbarian_1 | Axe |
| Barbarian | Rage Crash | barbarian_2 | Rage flame |
| Barbarian | Roar | barbarian_3 | Horn |
| Barbarian | Thick Hide | barbarian_4 | Stomp. No hide icon was drawn |
| Barbarian | Blood Price | barbarian_5 | Provoke. Passive frame |
| Druid | Mossknit | druid_1 | Leaf heal |
| Druid | Briar Seed | druid_2 | Thorns |
| Druid | Wildshape Guard | druid_3 | Bear |
| Druid | Spore Puff | druid_4 | Roots |
| Druid | Sap Pulse | druid_5 | Sprout. Passive frame |
