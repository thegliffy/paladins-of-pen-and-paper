class_name Formulas
## Combat, travel, and reward math.
## Numbers follow the design breakdown. Names in content files are original.

const BASE_STAT := 2
const DR_CAP := 0.5
const DMG_RANGE := 0.25
const SPELL_VARIANCE := 0.1
const MONSTER_GOLD_MULTIPLIER := 15.0


static func compose_stats(
	class_b: int, class_s: int, class_m: int,
	persona_b: int, persona_s: int, persona_m: int,
	race_b: int, race_s: int, race_m: int
) -> Dictionary:
	return {
		"body": class_b + persona_b + race_b + BASE_STAT,
		"senses": class_s + persona_s + race_s + BASE_STAT,
		"mind": class_m + persona_m + race_m + BASE_STAT,
	}


static func max_hp(level: int, body: int, mind: int) -> int:
	return 15 * (level * body - level + body + mind)


static func max_energy(level: int, body: int, mind: int) -> int:
	return 20 * (level * mind - level + body + mind)


static func monster_max_hp(level: int, body: int, mind: int, elite: bool = false) -> int:
	var h := max_hp(level, body, mind)
	if level == 1:
		h = int(float(h) / 3.0)
	if elite:
		h = int(round(float(h) * 1.5))
	return h


static func player_attack(level: int, body: int) -> int:
	return int(round(float(level + body) * 5.0))


static func monster_attack(level: int, body: int, elite: bool = false) -> int:
	var a := int(round(float(level + body) * 20.0))
	if elite:
		a = int(round(float(a) * 1.5))
	return a


static func damage_range(base_attack: int, dmg_range: float = DMG_RANGE) -> Vector2i:
	return Vector2i(
		int(round(float(base_attack) * (1.0 - dmg_range))),
		int(round(float(base_attack) * (1.0 + dmg_range)))
	)


static func rolled_damage(base_attack: int, roll_unit: float, dmg_range: float = DMG_RANGE) -> int:
	## roll_unit is 0..1 across the closed range [1-r, 1+r].
	var span := dmg_range * 2.0
	var mult := (1.0 - dmg_range) + clampf(roll_unit, 0.0, 1.0) * span
	return int(round(float(base_attack) * mult))


static func crit_chance(
	senses: int,
	passive_crit: float = 0.0,
	original_senses: int = -1,
	crit_mult: float = 0.0,
	crit_bonus_pct: float = 0.0
) -> float:
	var orig := senses if original_senses < 0 else original_senses
	var raw := (float(senses) + passive_crit + float(orig) * crit_mult) * (1.0 + crit_bonus_pct)
	return clampf(raw, 0.0, 100.0)


static func is_crit(chance: float, roll_1_to_100: int) -> bool:
	if chance <= 0.0:
		return false
	return float(roll_1_to_100) <= chance


static func damage_taken(raw: float, dr: int, cap: float = DR_CAP) -> int:
	var halved := int(round(raw * (1.0 - cap)))
	var after_dr := int(round(raw)) - dr
	return maxi(1, maxi(halved, after_dr))


static func outgoing_damage(raw: float, weakened: bool) -> float:
	if weakened:
		return raw * 0.5
	return raw


static func xp_to_next(level: int) -> int:
	return level * level * 30 + 30


static func total_skill_points(level: int, bonus_points: int) -> int:
	return (level - 1) + bonus_points


static func monster_base_xp(monster_level: int, party_avg: float) -> float:
	var xp := 15.0 + float(monster_level - 1) * 20.0
	if party_avg > float(monster_level) + 2.0:
		xp *= 0.75
	return xp


static func battle_xp(entries: Array, party_avg: float) -> int:
	## entries: {level, boss, type_id}
	var total := 0.0
	var types := {}
	for entry in entries:
		var xp: float = monster_base_xp(int(entry["level"]), party_avg)
		if bool(entry.get("boss", false)):
			xp *= 2.0
		total += xp
		types[str(entry.get("type_id", entry["level"]))] = true
	var n := entries.size()
	if n <= 0:
		return 0
	var distinct := types.size()
	total *= 1.0 + 0.1 * float(n - 1)
	total *= 1.0 + 0.1 * float(maxi(0, distinct - 1))
	return int(round(total))


static func level_gap(party_avg: float, monster_level: int) -> int:
	## Interpreted from the gold line "ceil(L·0.5 − gap)": how many levels
	## the party average sits above the monster. Never negative.
	return maxi(0, int(round(party_avg - float(monster_level))))


static func gold_per_kill(level: int, gap: int, elite_or_boss: bool) -> int:
	var g := int(ceili(float(level) * 0.5 - float(gap)))
	g = maxi(0, g)
	if elite_or_boss:
		g *= 2
	return g


static func battle_gold(per_kill_sum: int, monster_count: int, gold_pct: float = 0.0) -> int:
	if monster_count <= 0:
		return 0
	var total := float(per_kill_sum) * (1.0 + 0.1 * float(monster_count - 1)) + float(monster_count) / 2.0
	total *= (1.0 + gold_pct)
	total *= MONSTER_GOLD_MULTIPLIER
	return int(round(total))


static func bonus_gold_amount(level: int, unit_roll: float) -> int:
	## 20% rider, uniform from L/2 to 2L. unit_roll is 0..1.
	var lo := float(level) / 2.0
	var hi := float(level) * 2.0
	return int(round(lo + clampf(unit_roll, 0.0, 1.0) * (hi - lo)))


static func mp_cost(base_cost: int, skill_level: int, reduction: float = 0.0) -> int:
	var cost := float(base_cost + skill_level * 20) * (1.0 + reduction)
	return maxi(0, int(round(cost)))


static func travel_p(dest_level: int, party_avg: float) -> int:
	return clampi(int(round(float(dest_level) - party_avg + 7.0)), 2, 10)


static func ambush_chance(p: int) -> float:
	return float(p - 1) / 20.0


static func hop_gold(level_a: int, level_b: int) -> int:
	if level_a <= 8 or level_b <= 8:
		return 150
	return 300


static func classify_travel_roll(roll: int, p: int, lucky_branch: int) -> String:
	## lucky_branch is the integer from Random.Range(2, 5) style: 2, 3, or 4+.
	## 2 free travel, 3 item, anything else free travel in this slice
	## (there is no secret-encounter list yet).
	var faced := clampi(roll, 1, 20)
	if faced <= 1:
		return "lost"
	if faced <= p:
		return "ambush"
	if faced >= 20:
		if lucky_branch == 3:
			return "item"
		return "free"
	return "safe"


static func party_die_target(stat: int) -> int:
	return 20 - stat


static func party_die_succeeds(roll: int, stat: int, bonus: int = 0) -> bool:
	if roll <= 1:
		return false
	var total := mini(20, roll + bonus)
	return total >= party_die_target(stat)


static func saving_throw_succeeds(roll: int, stat: int, bonus: int = 0, stunned: bool = false, boss: bool = false) -> bool:
	## Success when d20 <= stat + bonuses. Bosses roll the check with stat ×2.
	## Stunned targets auto-fail. A lower roll is better.
	if stunned:
		return false
	var effective := stat * (2 if boss else 1) + bonus
	return roll <= effective


static func resurrect_cost(level: int) -> int:
	return maxi(2 * level - 5, 0) * 50


static func party_average(levels: Array) -> float:
	if levels.is_empty():
		return 1.0
	var sum := 0.0
	for lv in levels:
		sum += float(lv)
	return sum / float(levels.size())


static func encounter_target_power(party_power: int, difficulty: float, alive_players: int) -> int:
	return int(round(float(party_power) * difficulty * (1.0 + 0.1 * float(alive_players))))


static func compose_encounter(pool: Array, target_power: int, rng_picks: Array, dungeon: bool = false) -> Array:
	## pool entries: {id, power}. rng_picks is a list of indices used in order
	## (tests pass a scripted sequence; the game passes random indices).
	## Monsters with power < target are eligible. At least 1 (2 in a dungeon),
	## at most 7. If nobody is under the target, the weakest is used.
	var result: Array = []
	if pool.is_empty() or target_power <= 0 and pool.is_empty():
		return result
	var min_count := 2 if dungeon else 1
	var eligible: Array = []
	var weakest = pool[0]
	for entry in pool:
		if int(entry["power"]) < int(weakest["power"]):
			weakest = entry
		if int(entry["power"]) < target_power:
			eligible.append(entry)
	var source: Array = eligible if not eligible.is_empty() else [weakest]
	var guard := 0
	var power_sum := 0
	var pick_i := 0
	while result.size() < 7 and guard < 40:
		guard += 1
		var need_more := power_sum < target_power or result.size() < min_count
		if not need_more:
			break
		var idx := 0
		if pick_i < rng_picks.size():
			idx = int(rng_picks[pick_i]) % source.size()
			pick_i += 1
		else:
			idx = result.size() % source.size()
		var chosen = source[idx]
		# Don't keep adding a monster that can never fit if we already have
		# the minimum and it would only overshoot forever. Still allow the
		# first monsters through.
		if result.size() >= min_count and power_sum >= target_power:
			break
		if result.size() >= min_count and int(chosen["power"]) >= target_power and power_sum > 0:
			break
		result.append(chosen)
		power_sum += int(chosen["power"])
	if result.is_empty() and not pool.is_empty():
		result.append(weakest)
	return result


static func member_threat(
	base_threat: int,
	body: int,
	armor: int,
	flat_bonus: int,
	threat_mult: float,
	cover_mult: float,
	body_per: float,
	armor_per: float
) -> int:
	## Class base, Body, armor (damage reduction), and taunt, then multipliers.
	## The result is never below 1, so a living member can always be raffled.
	var raw := float(base_threat) + float(body) * body_per + float(armor) * armor_per + float(flat_bonus)
	raw *= threat_mult
	raw *= cover_mult
	return maxi(1, int(round(raw)))


static func raffle_index(weights: Array, roll_1_to_total: int) -> int:
	var total := 0
	for weight in weights:
		total += maxi(0, int(weight))
	if total <= 0:
		return -1
	var roll := clampi(roll_1_to_total, 1, total)
	var cursor := 0
	for i in weights.size():
		cursor += maxi(0, int(weights[i]))
		if cursor <= 0:
			continue
		if roll <= cursor:
			return i
	return weights.size() - 1


static func raffle_counts(weights: Array, rolls: int, seed: int) -> Array:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed
	var total := 0
	for weight in weights:
		total += maxi(0, int(weight))
	var counts: Array = []
	counts.resize(weights.size())
	for i in counts.size():
		counts[i] = 0
	if total <= 0 or rolls <= 0:
		return counts
	for _n in rolls:
		var idx := raffle_index(weights, rng.randi_range(1, total))
		if idx < 0:
			continue
		counts[idx] = int(counts[idx]) + 1
	return counts


static func living_threats(members: Array) -> Array:
	## members: {hp, threat}. Dead members are omitted. Living threat is at least 1.
	var weights: Array = []
	for member in members:
		if int(member.get("hp", 0)) <= 0:
			continue
		weights.append(maxi(1, int(member.get("threat", 1))))
	return weights


static func spell_flat(skill: Dictionary, mind: int, senses: int, rank: int, spell_bonus: float) -> int:
	var flat := float(int(skill.get("flat_damage", 0)))
	flat += float(int(skill.get("damage_per_mind", 0))) * float(mind)
	flat += float(int(skill.get("damage_per_senses", 0))) * float(senses)
	flat += float(int(skill.get("damage_per_rank", 0))) * float(maxi(0, rank - 1))
	flat *= 1.0 + spell_bonus
	return int(round(flat))


static func heal_amount(skill: Dictionary, mind: int, rank: int) -> int:
	var amount := float(int(skill.get("heal", 0)))
	amount += float(int(skill.get("heal_per_mind", 0))) * float(mind)
	amount += float(int(skill.get("heal_per_rank", 0))) * float(maxi(0, rank - 1))
	return int(round(amount))


static func skill_resource(skill: Dictionary) -> String:
	var resource := str(skill.get("resource", "mana"))
	if resource == "":
		return "mana"
	return resource


static func skill_mana_cost(skill: Dictionary, rank: int) -> int:
	if skill_resource(skill) != "mana":
		return 0
	return mp_cost(int(skill.get("mp_base", 0)), rank)


static func hp_cost_payable(hp: int, cost: int) -> bool:
	if cost <= 0:
		return true
	return hp > cost


static func cooldown_remaining(cooldowns: Dictionary, skill_id: String) -> int:
	return maxi(0, int(cooldowns.get(skill_id, 0)))


static func arm_cooldown(cooldowns: Dictionary, skill_id: String, turns: int) -> void:
	cooldowns[skill_id] = maxi(0, turns)


static func tick_cooldowns(cooldowns: Dictionary) -> void:
	for key in cooldowns.keys():
		cooldowns[key] = maxi(0, int(cooldowns[key]) - 1)


static func buildup_amount(buildup: Dictionary, buildup_id: String) -> int:
	return maxi(0, int(buildup.get(buildup_id, 0)))


static func is_passive(skill: Dictionary) -> bool:
	return str(skill.get("type", "active")) == "passive"


static func skill_usable(skill: Dictionary, rank: int, hp: int, mp: int, cooldowns: Dictionary, buildup: Dictionary) -> bool:
	if is_passive(skill):
		return false
	var resource := skill_resource(skill)
	if resource == "mana":
		return mp >= skill_mana_cost(skill, rank)
	if resource == "cooldown":
		return cooldown_remaining(cooldowns, str(skill.get("id", ""))) <= 0
	if resource == "free":
		return true
	if resource == "hp":
		return hp_cost_payable(hp, int(skill.get("hp_cost", 0)))
	if resource == "buildup":
		return buildup_amount(buildup, str(skill.get("buildup_id", ""))) >= int(skill.get("buildup_cost", 0))
	return false


static func apply_skill_payment(skill: Dictionary, rank: int, hp: int, mp: int, cooldowns: Dictionary, buildup: Dictionary) -> Dictionary:
	var next_cd: Dictionary = cooldowns.duplicate(true)
	var next_bu: Dictionary = buildup.duplicate(true)
	var next_hp := hp
	var next_mp := mp
	var resource := skill_resource(skill)
	if resource == "mana":
		next_mp -= skill_mana_cost(skill, rank)
	elif resource == "cooldown":
		arm_cooldown(next_cd, str(skill.get("id", "")), int(skill.get("cooldown", 0)))
	elif resource == "hp":
		next_hp -= int(skill.get("hp_cost", 0))
	elif resource == "buildup":
		var spend_id := str(skill.get("buildup_id", ""))
		next_bu[spend_id] = buildup_amount(next_bu, spend_id) - int(skill.get("buildup_cost", 0))
	var gain := int(skill.get("buildup_gain", 0))
	if gain > 0:
		var gain_id := str(skill.get("buildup_id", ""))
		var cap := int(skill.get("buildup_max", gain))
		next_bu[gain_id] = mini(cap, buildup_amount(next_bu, gain_id) + gain)
	return {
		"hp": next_hp,
		"mp": next_mp,
		"cooldowns": next_cd,
		"buildup": next_bu,
	}


static func skill_cost_label(skill: Dictionary, rank: int, cooldowns: Dictionary, buildup: Dictionary) -> String:
	var name := str(skill.get("name", "Skill"))
	var resource := skill_resource(skill)
	if resource == "mana":
		return "%s  %d EN" % [name, skill_mana_cost(skill, rank)]
	if resource == "cooldown":
		var left := cooldown_remaining(cooldowns, str(skill.get("id", "")))
		if left > 0:
			return "%s  CD %d" % [name, left]
		return "%s  Ready" % name
	if resource == "hp":
		return "%s  %d HP" % [name, int(skill.get("hp_cost", 0))]
	if resource == "buildup":
		var spend_id := str(skill.get("buildup_id", ""))
		var spend_label := str(skill.get("buildup_label", "Stack"))
		return "%s  %d/%d %s" % [name, buildup_amount(buildup, spend_id), int(skill.get("buildup_cost", 0)), spend_label]
	var gain := int(skill.get("buildup_gain", 0))
	if gain > 0:
		return "%s  +%d %s" % [name, gain, str(skill.get("buildup_label", "Stack"))]
	return "%s  Free" % name


static func skill_cost_badge(skill: Dictionary, rank: int, cooldowns: Dictionary, buildup: Dictionary) -> String:
	## Short cost painted on a 32px skill button. A cooling skill shows the turns left.
	if is_passive(skill):
		return ""
	var resource := skill_resource(skill)
	if resource == "mana":
		return str(skill_mana_cost(skill, maxi(1, rank)))
	if resource == "cooldown":
		var left := cooldown_remaining(cooldowns, str(skill.get("id", "")))
		if left > 0:
			return str(left)
		return str(int(skill.get("cooldown", 0)))
	if resource == "hp":
		return str(int(skill.get("hp_cost", 0)))
	if resource == "buildup":
		if int(skill.get("buildup_cost", 0)) > 0:
			return str(int(skill.get("buildup_cost", 0)))
		var gained := int(skill.get("buildup_gain", 0))
		if gained > 0:
			return "+%d" % gained
	return ""


static func skill_button_state(skill: Dictionary, rank: int, hp: int, mp: int, cooldowns: Dictionary, buildup: Dictionary, selected: bool) -> String:
	## ready, selected, disabled, cooldown, locked, or passive.
	## Passive and locked are never clickable. Cooldown wins over selected.
	if is_passive(skill):
		return "passive"
	if rank <= 0:
		return "locked"
	if skill_resource(skill) == "cooldown" and cooldown_remaining(cooldowns, str(skill.get("id", ""))) > 0:
		return "cooldown"
	if selected:
		return "selected"
	if not skill_usable(skill, rank, hp, mp, cooldowns, buildup):
		return "disabled"
	return "ready"


static func mp_regen_amount(max_mp: int, effects: Array) -> int:
	return _regen_amount(max_mp, effects, "mp_regen_pct")


static func hp_regen_amount(max_hp: int, effects: Array) -> int:
	return _regen_amount(max_hp, effects, "hp_regen_pct")


static func _regen_amount(maximum: int, effects: Array, key: String) -> int:
	if maximum <= 0:
		return 0
	var pct := 0.0
	for effect in effects:
		if str(effect.get("hook", "")) != "turn_start":
			continue
		pct += float(effect.get(key, 0.0))
	if pct <= 0.0:
		return 0
	return maxi(0, int(round(float(maximum) * pct)))


static func threat_multiplier(effects: Array) -> float:
	var mult := 1.0
	for effect in effects:
		if str(effect.get("hook", "")) != "threat":
			continue
		mult *= float(effect.get("threat_mult", 1.0))
	return mult


static func threat_flat(effects: Array) -> int:
	var bonus := 0
	for effect in effects:
		if str(effect.get("hook", "")) != "threat":
			continue
		bonus += int(effect.get("threat_add", 0))
	return bonus


static func on_hit_bonus(effects: Array) -> int:
	var bonus := 0
	for effect in effects:
		if str(effect.get("hook", "")) != "on_hit":
			continue
		bonus += int(effect.get("bonus_damage", 0))
	return bonus


static func on_damaged_reflect(effects: Array) -> int:
	var amount := 0
	for effect in effects:
		if str(effect.get("hook", "")) != "on_damaged":
			continue
		amount += int(effect.get("reflect", 0))
	return amount


static func crit_flat_bonus(effects: Array) -> float:
	var bonus := 0.0
	for effect in effects:
		if str(effect.get("hook", "")) != "stat":
			continue
		bonus += float(effect.get("crit_bonus", 0.0))
	return bonus


static func heal_multiplier(effects: Array) -> float:
	var mult := 1.0
	for effect in effects:
		if str(effect.get("hook", "")) != "stat":
			continue
		mult += float(effect.get("heal_bonus", 0.0))
	return mult


static func boost_heal(amount: int, effects: Array) -> int:
	return maxi(0, int(round(float(amount) * heal_multiplier(effects))))


static func initiative_bonus(effects: Array) -> int:
	var bonus := 0
	for effect in effects:
		if str(effect.get("hook", "")) != "stat":
			continue
		bonus += int(effect.get("initiative", 0))
	return bonus


static func party_dr_aura(effects: Array) -> int:
	var extra := 0
	for effect in effects:
		if str(effect.get("hook", "")) != "stat":
			continue
		extra += int(effect.get("party_dr", 0))
	return extra


static func outgoing_damage_multiplier(hp: int, max_hp: int, effects: Array) -> float:
	var scale := 0.0
	for effect in effects:
		if str(effect.get("hook", "")) != "stat":
			continue
		scale += float(effect.get("missing_hp_damage", 0.0))
	if scale <= 0.0 or max_hp <= 0:
		return 1.0
	var missing := clampf(1.0 - float(maxi(0, hp)) / float(max_hp), 0.0, 1.0)
	return 1.0 + scale * missing
