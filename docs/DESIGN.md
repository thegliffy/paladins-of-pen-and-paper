# Design

Combat math for this slice lives with the code that uses it. This note is the threat raffle. Class bases and the skill table are in [CLASSES.md](CLASSES.md).

## Threat raffle

When a monster attacks, it raffles one living party member. Dead members are excluded. Every living member has threat of at least 1.

`P(member) = that member's threat / the sum of living threat`

A party of 30, 3, 5, and 1 sums to 39. The shares are about 77%, 8%, 13%, and 3%.

Per character, from `data/threat.json` and each class's `base_threat`:

`threat = max(1, round((base_threat + Body × body_per + DR × armor_per + taunt + passive_add) × passive_mult × cover_mult))`

- `body_per` is 2. `armor_per` is 0.05. Damage reduction is the armor term.
- Taunt skills (Oathstrike, Shieldwall, Roar, and the other threat fields) add a flat amount until that character's next turn.
- Oathmagnet multiplies by 2. Blood Price multiplies by 1.5. Neither one forces a target.
- Cover multiplies by `cover_mult` (0.5). The clamp to 1 still applies, so ducking does not make you untargetable.

Tanks start high because their `base_threat` is high: Paladin 16, Barbarian 12. Rogue is 1, Wizard and Bard are 2.
