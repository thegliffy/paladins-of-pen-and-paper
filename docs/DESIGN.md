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

## Party row and the action bar

The portrait party is 1 to 5 heroes (`party_min` / `party_max` in `data/layout.json`). Combat seats five centres at x 27, 81, 135, 189, and 243. Seats 2 and 4 sit 4px higher. A shorter party uses that spacing and is centred on x 135. Each chair has a thin HP bar and, under it, a thin MP bar (`chair_bars` in `data/layout.json`). The HP number sits beside the HP bar, in a box that clears the mana bar under it.

The bottom bar is 270×50 at y 430. A name tab above it names the hero whose turn it is. Left to right: Attack, Cover (32px), that hero's five class skills (32px, with a cost badge), then Item and Run (20px). The bar swaps when initiative reaches the next hero. The first tap on Attack, Cover, Item, or a skill arms it and opens an info card above that slot (`skill_card`). A second tap on the same slot uses it when it can be used. A different slot switches the card. A tap elsewhere dismisses it. A passive, a locked skill, a cooling skill, and a skill you cannot pay for show the card and the reason, and they do not cast. Run still leaves on the first tap.
