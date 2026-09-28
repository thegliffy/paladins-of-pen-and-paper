# Classes

Eight classes. A party of three can seat each class once. Every class has five skills that nobody else uses: three or four actives and one or two passives. Body, Senses, and Mind from the class add up to 6, then persona, race, and the +2 base still apply.

Actives are the Skill buttons. Passives are always on. They are tagged Passive in the creator and on the party panel, and they never appear in the Skill list.

Mana skills use the energy formula `round((base + rank × 20) × (1 + reduction))`. The button shows that rank-1 cost. Cooldown skills arm on use and tick down by 1 at the start of each of your later turns, including a turn you spend stunned. A cooldown of 3 is ready again on the turn it reaches 0. An HP cost is payable only when it would leave at least 1 health. Build-up skills add points up to a cap, and the spender refuses the action until you have the cost.

Passive hooks are `turn_start`, `on_hit`, `on_damaged`, `threat`, and `stat`. Monster targeting is still Body plus temporary threat. A threat passive multiplies that weight. Cover still removes the unit from the bag.

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
| Paladin | Oathmagnet | Passive | Threat, on damaged | Always on | Self | Foes weigh you ×2 (Body + threat). A hit against you deals 4 damage back. |
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
| Barbarian | Blood Price | Passive | Threat, stat | Always on | Self | Foes weigh you ×1.5. Damage rises as health falls, up to +50% when empty. |
| Druid | Briar Seed | Active | Mana | base 120 (140 EN at rank 1) | One foe, back row allowed | Spell 10 + 2×Mind. Poison 8, Body save. |
| Druid | Mossknit | Active | Mana | base 120 (140 EN at rank 1) | One ally | Heal 22 + 2×Mind + 6 per rank above 1. |
| Druid | Wildshape Guard | Active | Cooldown | 3 turns | Self | +8 damage reduction for 2 of your turns. |
| Druid | Spore Puff | Active | Free | Free | Up to 2 foes | Spell 6 + 1×Mind. Poison 5, Body save. Front or back. |
| Druid | Sap Pulse | Passive | Turn start | Always on | Self | Regain 5% of max health at the start of each of your turns. |

Spell and heal amounts above are the rank-1 base before Mind, Senses, and extra ranks. Ranks above 1 add the per-rank term in the skill data. Conditions use the same save, timer, and damage rules as the rest of combat: burn ticks health, poison drains energy first, stun skips the turn.
