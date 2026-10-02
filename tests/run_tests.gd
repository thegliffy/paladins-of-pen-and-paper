extends SceneTree
## Headless checks for the reference stat, HP, energy, travel, and reward numbers.
## Run: godot --headless --path . -s res://tests/run_tests.gd

var failed := 0
var passed := 0


func _init() -> void:
	_test_reference_character()
	_test_monster_examples()
	_test_damage_and_crit()
	_test_xp_curve_and_rewards()
	_test_travel_table()
	_test_party_and_save_dice()
	_test_timing()
	_test_route_and_encounter()
	_test_content_shape()
	_test_skill_resources()
	_test_passives()
	_test_threat_raffle()
	_test_portrait_layout()
	_test_party_bar()
	_test_art_present()
	_test_wrapped_labels()
	_test_targeting_and_lineup()
	_test_table_space()
	_test_place_rosters()
	_test_gear()
	_test_seat_gear()
	_test_quests()
	_test_towns_and_craft()
	_test_levels_and_pools()
	print("Tests: %d passed, %d failed" % [passed, failed])
	quit(1 if failed else 0)


func check(cond: bool, label: String) -> void:
	if cond:
		passed += 1
	else:
		failed += 1
		push_error("FAIL " + label)


func near(a: float, b: float, eps: float, label: String) -> void:
	check(absf(a - b) <= eps, "%s (got %s expected %s)" % [label, a, b])


func eq(a, b, label: String) -> void:
	check(a == b, "%s (got %s expected %s)" % [label, a, b])


func _test_reference_character() -> void:
	# Class 4/1/1 + persona 3/0/0 + race +1 body + base 2/2/2.
	var stats := Formulas.compose_stats(4, 1, 1, 3, 0, 0, 1, 0, 0)
	eq(stats["body"], 10, "reference body")
	eq(stats["senses"], 3, "reference senses")
	eq(stats["mind"], 3, "reference mind")
	eq(Formulas.max_hp(1, 10, 3), 330, "reference HP")
	eq(Formulas.max_energy(1, 10, 3), 300, "reference energy")
	eq(Formulas.player_attack(1, 10), 55, "reference attack")
	var rng := Formulas.damage_range(55)
	eq(rng.x, 41, "attack min")
	eq(rng.y, 69, "attack max")
	eq(Formulas.total_skill_points(1, 1), 1, "bonus skill point at level 1")
	eq(Formulas.total_skill_points(1, 0), 0, "no bonus skill point")
	eq(Formulas.total_skill_points(2, 1), 2, "level 2 with bonus")


func _test_monster_examples() -> void:
	# Level 4, body 3, senses 2, mind 2 → HP 195, attack 140, range 105–175.
	eq(Formulas.monster_max_hp(4, 3, 2), 195, "L4 monster HP")
	eq(Formulas.monster_attack(4, 3), 140, "L4 monster attack")
	var rng := Formulas.damage_range(140)
	eq(rng.x, 105, "monster min")
	eq(rng.y, 175, "monster max")
	# Level 1 divides HP by 3. 15*(2-1+2+1)=60, /3 = 20.
	eq(Formulas.monster_max_hp(1, 2, 1), 20, "L1 monster HP / 3")
	eq(Formulas.monster_max_hp(1, 2, 1, true), 30, "L1 elite HP")
	eq(Formulas.monster_attack(4, 3, true), 210, "elite attack ×1.5")
	eq(Formulas.max_energy(1, 10, 3) + 400, 700, "energy passive stacks after the formula")


func _test_damage_and_crit() -> void:
	eq(Formulas.damage_taken(100.0, 20), 80, "DR partial")
	eq(Formulas.damage_taken(100.0, 80), 50, "DR cap 50%")
	eq(Formulas.damage_taken(100.0, 0), 100, "no DR")
	eq(Formulas.damage_taken(1.0, 100), 1, "minimum 1")
	eq(Formulas.outgoing_damage(40.0, true), 20.0, "weakness half")
	near(Formulas.crit_chance(3), 3.0, 0.001, "crit equals senses")
	near(Formulas.crit_chance(80, 30.0), 100.0, 0.001, "crit clamps at 100")
	near(Formulas.crit_chance(0), 0.0, 0.001, "crit clamps at 0")
	check(Formulas.is_crit(3.0, 3), "roll 3 crits at 3%")
	check(not Formulas.is_crit(3.0, 4), "roll 4 misses a 3% crit")
	check(not Formulas.is_crit(0.0, 1), "zero crit never hits")
	eq(Formulas.mp_cost(150, 1), 170, "mp cost base+20")
	eq(Formulas.mp_cost(100, 1), 120, "mp cost 100")
	eq(Formulas.rolled_damage(55, 0.0), 41, "low roll")
	eq(Formulas.rolled_damage(55, 1.0), 69, "high roll")


func _test_xp_curve_and_rewards() -> void:
	eq(Formulas.xp_to_next(1), 60, "xp L1")
	eq(Formulas.xp_to_next(10), 3030, "xp L10")
	eq(Formulas.xp_to_next(30), 27030, "xp L30")
	var two := Formulas.battle_xp([
		{"level": 1, "boss": false, "type_id": "a"},
		{"level": 1, "boss": false, "type_id": "a"},
	], 1.0)
	eq(two, 33, "group bonus 10% on two level-1 monsters")
	var reduced := Formulas.monster_base_xp(1, 4.0)
	near(reduced, 11.25, 0.001, "xp ×0.75 when party is more than 2 levels up")
	var boss := Formulas.battle_xp([
		{"level": 4, "boss": true, "type_id": "boss"},
	], 4.0)
	# 15+60 = 75, ×2 boss = 150, no group/variety extra.
	eq(boss, 150, "boss xp ×2")
	eq(Formulas.level_gap(4.0, 4), 0, "no gap at equal level")
	eq(Formulas.level_gap(6.4, 4), 2, "gap rounds")
	eq(Formulas.gold_per_kill(4, 0, false), 2, "gold ceil(L*0.5)")
	eq(Formulas.gold_per_kill(4, 0, true), 4, "elite gold ×2")
	eq(Formulas.gold_per_kill(1, 0, false), 1, "L1 gold")
	# One L4 kill, gap 0: per=2; total (2 + 0.5) * 15 = 37.5 → 38.
	eq(Formulas.battle_gold(2, 1), 38, "battle gold ×15 rounded")
	eq(Formulas.hop_gold(1, 4), 150, "low-level hop is 150")
	eq(Formulas.hop_gold(9, 12), 300, "high-level hop is 300")
	eq(Formulas.hop_gold(9, 8), 150, "either endpoint ≤8 stays 150")
	eq(Formulas.resurrect_cost(1), 0, "resurrect free at level 1")
	eq(Formulas.resurrect_cost(3), 50, "resurrect at level 3")


func _test_travel_table() -> void:
	eq(Formulas.travel_p(4, 4.0), 7, "equal level p=7")
	near(Formulas.ambush_chance(7), 0.30, 0.0001, "30% ambush at equal level")
	eq(Formulas.travel_p(1, 10.0), 2, "p min 2")
	near(Formulas.ambush_chance(2), 0.05, 0.0001, "5% ambush at the floor")
	eq(Formulas.travel_p(10, 1.0), 10, "p max 10")
	near(Formulas.ambush_chance(10), 0.45, 0.0001, "45% ambush at the ceiling")
	# Destination 5 below: (L-5) - L + 7 = 2. Destination 3 above: 3+7 = 10.
	eq(Formulas.travel_p(5, 10.0), 2, "five levels below")
	eq(Formulas.travel_p(8, 5.0), 10, "three levels above")
	eq(Formulas.classify_travel_roll(1, 7, 2), "lost", "roll 1 lost")
	eq(Formulas.classify_travel_roll(2, 7, 2), "ambush", "roll 2 ambush")
	eq(Formulas.classify_travel_roll(7, 7, 2), "ambush", "roll p ambush")
	eq(Formulas.classify_travel_roll(8, 7, 2), "safe", "roll p+1 safe")
	eq(Formulas.classify_travel_roll(19, 7, 2), "safe", "roll 19 safe")
	eq(Formulas.classify_travel_roll(20, 7, 2), "free", "natural 20 branch 2 is free")
	eq(Formulas.classify_travel_roll(20, 7, 3), "item", "natural 20 branch 3 is an item")
	eq(Formulas.classify_travel_roll(20, 7, 4), "free", "natural 20 other branch is free in this slice")
	eq(Formulas.classify_travel_roll(1, 2, 2), "lost", "roll 1 is lost even when p is 2")
	near(Timing.safe_hop_seconds(), 2.5, 0.001, "safe hop 2.5s")
	check(Timing.safe_hop_seconds() >= 2.4 and Timing.safe_hop_seconds() <= 2.5, "safe hop inside 2.4–2.5")


func _test_party_and_save_dice() -> void:
	eq(Formulas.party_die_target(8), 12, "die label target")
	check(not Formulas.party_die_succeeds(1, 30), "natural 1 always fails")
	check(Formulas.party_die_succeeds(12, 8), "12 succeeds versus body 8")
	check(not Formulas.party_die_succeeds(11, 8), "11 fails versus body 8")
	check(Formulas.party_die_succeeds(11, 8, 1), "bonus can save a miss")
	check(not Formulas.party_die_succeeds(1, 8, 20), "natural 1 ignores bonuses")
	check(Formulas.saving_throw_succeeds(5, 8), "save succeeds when roll <= stat")
	check(not Formulas.saving_throw_succeeds(9, 8), "save fails when roll > stat")
	check(not Formulas.saving_throw_succeeds(2, 8, 0, true), "stun auto-fails a save")
	check(Formulas.saving_throw_succeeds(16, 8, 0, false, true), "boss save uses stat ×2")
	check(not Formulas.saving_throw_succeeds(17, 8, 0, false, true), "boss save still fails above stat ×2")


func _test_timing() -> void:
	near(Timing.player_basic_attack_seconds(), 0.95, 0.001, "player attack duration")
	check(Timing.player_basic_attack_seconds() >= 0.8 and Timing.player_basic_attack_seconds() <= 1.2, "player attack in 0.8–1.2")
	near(Timing.monster_basic_attack_seconds(2), 0.95, 0.001, "monster frame-2 attack")
	near(Timing.monster_time_to_damage(2), 0.2, 0.001, "frame 2 at 5 fps is 0.2s")
	near(Timing.monster_time_to_damage(6), 1.0, 0.001, "frame 6 at 5 fps is 1.0s")
	near(Timing.monster_time_to_damage(4), 0.6, 0.001, "frame 4 at 5 fps is 0.6s")
	near(Timing.death_blink_seconds(), 1.35, 0.001, "death blink ~1.35s")
	eq(Timing.HP_TWEEN, 0.5, "hp tween")
	eq(Timing.HIT_PUNCH, 0.3, "hit punch")
	eq(Timing.HIT_BLINK_IN, 0.1, "blink in")
	eq(Timing.HIT_BLINK_OUT, 0.1, "blink out")
	eq(Timing.FLOATER_QUEUE, 0.25, "floater queue")
	eq(Timing.PLAYER_NEXT_TURN, 0.3, "player gap")
	eq(Timing.MONSTER_WINDUP, 0.25, "monster wind-up")
	eq(Timing.XP_TWEEN, 2.0, "xp tween")
	eq(Timing.VICTORY_DELAY, 2.0, "victory delay")
	eq(Timing.CHICKEN_MOVE, 1.8, "chicken move")
	eq(Timing.TRAVEL_ROLL_SPIN, 0.9, "travel die spin")
	near(Timing.travel_roll_lead(), 0.1, 0.001, "roll starts 0.1s after hop begin")


func _region() -> Dictionary:
	var raw: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/region.json"))
	return Formulas.active_region(raw)


func _test_route_and_encounter() -> void:
	var region: Dictionary = _region()
	var edges: Array = region["edges"]
	var path: Array = RouteFinder.fewest_hops("candlewick", "lantern_reach", edges)
	eq(path[0], "candlewick", "route starts at origin")
	eq(path[path.size() - 1], "lantern_reach", "route ends at goal")
	eq(path.size() - 1, 2, "lantern reach is two hops from candlewick")
	var same: Array = RouteFinder.fewest_hops("millpond", "millpond", edges)
	eq(same, ["millpond"], "zero-hop route")
	var keep: Array = RouteFinder.fewest_hops("candlewick", "gravel_keep", edges)
	eq(keep.size() - 1, 1, "the keep is one hop from the hamlet")
	var offset := RouteFinder.spring_offset(Vector2(448, 214), Vector2(520, 300), Vector2(400, 176))
	check(offset.x >= 0.0 and offset.x <= 72.0, "spring x stays inside the pannable range")
	check(offset.y >= 0.0 and offset.y <= 86.0, "spring y stays inside the pannable range")
	var fitted := RouteFinder.spring_offset(Vector2(520, 300), Vector2(520, 300), Vector2(10, 10))
	eq(fitted, Vector2.ZERO, "a map that fits the view does not pan")
	var pool: Array = [
		{"id": "a", "power": 12},
		{"id": "b", "power": 18},
		{"id": "c", "power": 40},
	]
	var pack: Array = Formulas.compose_encounter(pool, 50, [0, 1, 0])
	var power := 0
	for entry in pack:
		power += int(entry["power"])
	check(pack.size() >= 1 and pack.size() <= 7, "encounter size bounds")
	check(power >= 50 or pack.size() == 7, "encounter reaches the target or the cap")
	var tiny: Array = Formulas.compose_encounter(pool, 5, [0])
	eq(tiny.size(), 1, "always at least one monster")
	eq(tiny[0]["id"], "a", "under-target fallback uses the weakest")


func _test_content_shape() -> void:
	var personas: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/personas.json"))
	var races: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/races.json"))
	var classes: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/classes.json"))
	var skills: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/skills.json"))
	var monsters: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/monsters.json"))
	var region: Dictionary = _region()
	eq(personas.size(), 5, "5 personas")
	eq(races.size(), 3, "3 races")
	eq(classes.size(), 8, "8 classes")
	eq(monsters.size(), 18, "eight originals plus ten region monsters")
	var places: Array = region["places"]
	eq(places.size(), 9, "9 places")
	var by_id := {}
	for skill in skills:
		by_id[str(skill["id"])] = skill
	var seen := {}
	var expected := ["paladin", "wizard", "ranger", "bard", "cleric", "rogue", "barbarian", "druid"]
	var present := {}
	for cls in classes:
		present[str(cls["id"])] = true
		var ids: Array = cls["skills"]
		eq(ids.size(), 5, str(cls["name"]) + " has 5 skills")
		eq(int(cls["body"]) + int(cls["senses"]) + int(cls["mind"]), 6, str(cls["name"]) + " stat budget")
		var non_mana := false
		var passives := 0
		var actives := 0
		for skill_id in ids:
			var sid := str(skill_id)
			check(not seen.has(sid), "skill used once: " + sid)
			seen[sid] = true
			var skill: Dictionary = by_id[sid]
			eq(str(skill["owner"]), str(cls["id"]), sid + " belongs to " + str(cls["name"]))
			if Formulas.is_passive(skill):
				passives += 1
				var effects: Array = skill.get("effects", [])
				check(not effects.is_empty(), sid + " has passive effects")
			else:
				actives += 1
				var resource := str(skill.get("resource", ""))
				check(resource == "mana" or resource == "cooldown" or resource == "free" or resource == "hp" or resource == "buildup", sid + " resource")
				if resource != "mana":
					non_mana = true
		check(passives >= 1 and passives <= 2, str(cls["name"]) + " passive count")
		check(actives >= 3 and actives <= 4, str(cls["name"]) + " active count")
		check(non_mana, str(cls["name"]) + " has a non-mana skill")
	for id in expected:
		check(present.has(id), "class " + id)
	eq(seen.size(), 40, "40 class skills")
	var monster_skills := 0
	for skill in skills:
		if str(skill["owner"]) == "monster":
			monster_skills += 1
	eq(monster_skills, 15, "each new region monster has a skill")


func _test_skill_resources() -> void:
	var shield := {
		"id": "shieldwall",
		"name": "Shieldwall",
		"resource": "cooldown",
		"cooldown": 3,
	}
	var cds := {}
	check(Formulas.skill_usable(shield, 1, 40, 0, cds, {}), "cooldown skill starts ready")
	var paid: Dictionary = Formulas.apply_skill_payment(shield, 1, 40, 80, cds, {})
	var left: Dictionary = paid["cooldowns"]
	eq(int(paid["mp"]), 80, "cooldown does not spend energy")
	eq(int(paid["hp"]), 40, "cooldown does not spend health")
	eq(Formulas.cooldown_remaining(left, "shieldwall"), 3, "cooldown armed at 3")
	check(not Formulas.skill_usable(shield, 1, 40, 80, left, {}), "armed cooldown is unavailable")
	Formulas.tick_cooldowns(left)
	eq(Formulas.cooldown_remaining(left, "shieldwall"), 2, "first later turn ticks 3 to 2")
	Formulas.tick_cooldowns(left)
	Formulas.tick_cooldowns(left)
	eq(Formulas.cooldown_remaining(left, "shieldwall"), 0, "three ticks clear a 3-turn cooldown")
	check(Formulas.skill_usable(shield, 1, 40, 80, left, {}), "cooldown is usable after three ticks")
	Formulas.tick_cooldowns(left)
	eq(Formulas.cooldown_remaining(left, "shieldwall"), 0, "cooldown does not go negative")
	eq(Formulas.skill_cost_label(shield, 1, {"shieldwall": 2}, {}), "Shieldwall  CD 2", "cooldown label")
	eq(Formulas.skill_cost_label(shield, 1, {}, {}), "Shieldwall  Ready", "ready label")

	var swing := {"id": "bloodswing", "name": "Bloodswing", "resource": "hp", "hp_cost": 12}
	check(not Formulas.hp_cost_payable(12, 12), "hp cost must leave at least 1")
	check(Formulas.hp_cost_payable(13, 12), "hp above the cost is payable")
	check(not Formulas.skill_usable(swing, 1, 12, 0, {}, {}), "cannot pay hp cost with 12 hp")
	check(Formulas.skill_usable(swing, 1, 13, 0, {}, {}), "hp cost payable at 13")
	var cut: Dictionary = Formulas.apply_skill_payment(swing, 1, 40, 90, {}, {})
	eq(int(cut["hp"]), 28, "hp cost subtracts")
	eq(int(cut["mp"]), 90, "hp skill does not spend energy")
	eq(Formulas.skill_cost_label(swing, 1, {}, {}), "Bloodswing  12 HP", "hp label")

	var nick := {
		"id": "pocket_cut",
		"name": "Pocket Cut",
		"resource": "free",
		"buildup_id": "combo",
		"buildup_gain": 1,
		"buildup_max": 5,
		"buildup_label": "Combo",
	}
	var ledger := {
		"id": "ledger_strike",
		"name": "Ledger Strike",
		"resource": "buildup",
		"buildup_id": "combo",
		"buildup_cost": 4,
		"buildup_label": "Combo",
	}
	var stacks := {}
	var gained: Dictionary = Formulas.apply_skill_payment(nick, 1, 30, 10, {}, stacks)
	eq(int(gained["buildup"]["combo"]), 1, "combo gains 1")
	eq(stacks.size(), 0, "payment does not mutate the caller's buildup")
	var capped: Dictionary = Formulas.apply_skill_payment(nick, 1, 30, 10, {}, {"combo": 5})
	eq(int(capped["buildup"]["combo"]), 5, "combo clamps at the cap")
	check(not Formulas.skill_usable(ledger, 1, 30, 10, {}, {"combo": 3}), "spend refused below the cost")
	check(Formulas.skill_usable(ledger, 1, 30, 10, {}, {"combo": 4}), "spend allowed at the cost")
	var spent: Dictionary = Formulas.apply_skill_payment(ledger, 1, 30, 10, {}, {"combo": 5})
	eq(int(spent["buildup"]["combo"]), 1, "spend subtracts the cost")
	eq(int(spent["mp"]), 10, "buildup spend does not spend energy")
	eq(int(spent["hp"]), 30, "buildup spend does not spend health")
	eq(Formulas.skill_cost_label(ledger, 1, {}, {"combo": 2}), "Ledger Strike  2/4 Combo", "buildup label")
	eq(Formulas.skill_cost_label(nick, 1, {}, {}), "Pocket Cut  +1 Combo", "gain label")

	var mana := {"id": "oathstrike", "name": "Oathstrike", "resource": "mana", "mp_base": 100}
	eq(Formulas.skill_mana_cost(mana, 1), 120, "mana skill uses the energy formula")
	eq(Formulas.skill_mana_cost(swing, 1), 0, "hp skill ignores the energy formula")
	check(not Formulas.skill_usable(mana, 1, 40, 119, {}, {}), "mana skill unavailable under the cost")
	check(Formulas.skill_usable(mana, 1, 40, 120, {}, {}), "mana skill ready at the cost")
	var roared: Dictionary = Formulas.apply_skill_payment({
		"id": "roar",
		"resource": "free",
		"buildup_id": "rage",
		"buildup_gain": 2,
		"buildup_max": 6,
	}, 1, 50, 0, {}, {"rage": 5})
	eq(int(roared["buildup"]["rage"]), 6, "rage clamps at 6")
	eq(int(roared["mp"]), 0, "free skill does not spend energy")


func _test_passives() -> void:
	var skills: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/skills.json"))
	var by_id := {}
	var hooks := {}
	for skill in skills:
		by_id[str(skill["id"])] = skill
		if not Formulas.is_passive(skill):
			continue
		var effects: Array = skill.get("effects", [])
		for effect in effects:
			hooks[str(effect.get("hook", ""))] = true
	for hook in ["turn_start", "on_hit", "on_damaged", "threat", "stat"]:
		check(hooks.has(hook), "passive hook " + hook)
	var siphon: Dictionary = by_id["ley_siphon"]
	var siphon_fx: Array = siphon["effects"]
	check(Formulas.is_passive(siphon), "ley siphon is passive")
	check(not Formulas.skill_usable(siphon, 1, 40, 999, {}, {}), "passives are not skill buttons")
	eq(Formulas.mp_regen_amount(200, siphon_fx), 16, "8% of 200 energy")
	eq(Formulas.mp_regen_amount(125, siphon_fx), 10, "8% of 125 energy rounds")
	eq(Formulas.mp_regen_amount(0, siphon_fx), 0, "no regen from an empty pool")
	eq(Formulas.mp_regen_amount(200, []), 0, "no regen without the passive")
	var sap: Dictionary = by_id["sap_pulse"]
	var sap_fx: Array = sap["effects"]
	eq(Formulas.hp_regen_amount(80, sap_fx), 4, "5% of 80 health")
	var oath: Dictionary = by_id["oathmagnet"]
	var oath_fx: Array = oath["effects"]
	near(Formulas.threat_multiplier(oath_fx), 2.0, 0.001, "paladin threat multiplier")
	var plain := Formulas.member_threat(16, 8, 0, 0, 1.0, 1.0, 2.0, 0.0)
	var doubled := Formulas.member_threat(16, 8, 0, 0, Formulas.threat_multiplier(oath_fx), 1.0, 2.0, 0.0)
	eq(plain, 32, "threat before the aggro passive")
	eq(doubled, 64, "aggro passive doubles threat")
	var share_plain := float(plain) / float(plain + 9)
	var share_aggro := float(doubled) / float(doubled + 9)
	check(share_aggro > share_plain + 0.05, "aggro passive raises threat share")
	var price: Dictionary = by_id["blood_price"]
	var price_fx: Array = price["effects"]
	near(Formulas.threat_multiplier(price_fx), 1.5, 0.001, "barbarian threat multiplier")
	var bare := Formulas.member_threat(12, 5, 0, 0, 1.0, 1.0, 2.0, 0.0)
	var priced := Formulas.member_threat(12, 5, 0, 0, Formulas.threat_multiplier(price_fx), 1.0, 2.0, 0.0)
	check(priced > bare, "barbarian threat passive raises threat")
	var nick: Dictionary = by_id["keen_nick"]
	var nick_fx: Array = nick["effects"]
	eq(Formulas.on_hit_bonus(nick_fx), 6, "on-hit passive adds 6")
	eq(Formulas.on_hit_bonus([]), 0, "no on-hit bonus without the passive")
	near(Formulas.crit_flat_bonus(nick_fx), 10.0, 0.001, "rogue crit bonus")
	eq(Formulas.on_damaged_reflect(oath_fx), 4, "paladin reflect")
	near(Formulas.outgoing_damage_multiplier(50, 100, price_fx), 1.25, 0.001, "half health adds half the missing-hp scale")
	near(Formulas.outgoing_damage_multiplier(100, 100, price_fx), 1.0, 0.001, "full health does not add damage")
	near(Formulas.outgoing_damage_multiplier(0, 100, price_fx), 1.5, 0.001, "empty health reaches +50%")
	var hands: Dictionary = by_id["open_hands"]
	var hands_fx: Array = hands["effects"]
	eq(Formulas.boost_heal(40, hands_fx), 50, "cleric heals gain 25%")
	var mark: Dictionary = by_id["first_mark"]
	var mark_fx: Array = mark["effects"]
	eq(Formulas.initiative_bonus(mark_fx), 5, "ranger initiative")
	var chorus: Dictionary = by_id["hearth_chorus"]
	var chorus_fx: Array = chorus["effects"]
	eq(Formulas.party_dr_aura(chorus_fx), 3, "bard aura")


func _test_threat_raffle() -> void:
	eq(Formulas.member_threat(0, 0, 0, 0, 1.0, 1.0, 2.0, 0.05), 1, "threat floor is 1")
	eq(Formulas.member_threat(0, 0, 0, -40, 1.0, 1.0, 2.0, 0.05), 1, "negative threat clamps to 1")
	eq(Formulas.member_threat(4, 0, 0, 0, 1.0, 0.0, 2.0, 0.05), 1, "a zero multiplier still leaves 1")
	var open_threat := Formulas.member_threat(16, 8, 0, 0, 1.0, 1.0, 2.0, 0.0)
	var ducked := Formulas.member_threat(16, 8, 0, 0, 1.0, 0.5, 2.0, 0.0)
	check(ducked >= 1 and ducked < open_threat, "cover lowers threat without hiding")
	var quiet := Formulas.member_threat(16, 8, 0, 0, 2.0, 1.0, 2.0, 0.0)
	var taunted := Formulas.member_threat(16, 8, 0, 3, 2.0, 1.0, 2.0, 0.0)
	check(taunted > quiet, "taunt adds threat instead of forcing a target")
	var weights := [30, 3, 5, 1]
	eq(Formulas.raffle_index(weights, 1), 0, "roll 1 is the high threat")
	eq(Formulas.raffle_index(weights, 30), 0, "roll 30 is still the high threat")
	eq(Formulas.raffle_index(weights, 31), 1, "roll 31 is the second weight")
	eq(Formulas.raffle_index(weights, 33), 1, "roll 33 is still the second weight")
	eq(Formulas.raffle_index(weights, 34), 2, "roll 34 is the third weight")
	eq(Formulas.raffle_index(weights, 38), 2, "roll 38 is still the third weight")
	eq(Formulas.raffle_index(weights, 39), 3, "roll 39 is the last weight")
	var counts: Array = Formulas.raffle_counts(weights, 4000, 30)
	var expected := [30.0 / 39.0, 3.0 / 39.0, 5.0 / 39.0, 1.0 / 39.0]
	for i in 4:
		near(float(int(counts[i])) / 4000.0, expected[i], 0.04, "raffle share %d" % i)
	var living: Array = Formulas.living_threats([
		{"hp": 0, "threat": 30},
		{"hp": 12, "threat": 3},
		{"hp": 9, "threat": 5},
		{"hp": 4, "threat": 0},
	])
	eq(living.size(), 3, "dead member is excluded")
	eq(int(living[0]), 3, "first living threat")
	eq(int(living[1]), 5, "second living threat")
	eq(int(living[2]), 1, "a living zero is clamped to 1")
	var rules: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/threat.json"))
	var classes: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/classes.json"))
	var bases := {}
	for cls in classes:
		bases[str(cls["id"])] = int(cls["base_threat"])
		check(int(cls["base_threat"]) >= 1, str(cls["name"]) + " base threat")
	check(int(bases["paladin"]) > int(bases["wizard"]), "paladin base threat beats the wizard")
	check(int(bases["barbarian"]) > int(bases["rogue"]), "barbarian base threat beats the rogue")
	check(int(bases["paladin"]) > int(bases["bard"]), "paladin base threat beats the bard")
	var body_per := float(rules["body_per"])
	var armor_per := float(rules["armor_per"])
	var tank := Formulas.member_threat(int(bases["paladin"]), 8, 0, 0, 2.0, 1.0, body_per, armor_per)
	var mage := Formulas.member_threat(int(bases["wizard"]), 3, 0, 0, 1.0, 1.0, body_per, armor_per)
	check(tank > mage * 2, "tank threat stays well above the mage")


func _test_portrait_layout() -> void:
	var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/layout.json"))
	eq(str(layout["active"]), "portrait", "portrait is the active layout")
	eq(int(layout["portrait"]["viewport"][0]), 270, "viewport width")
	eq(int(layout["portrait"]["viewport"][1]), 480, "viewport height")
	check(layout.has("landscape"), "landscape layout slot is reserved")
	check(not bool(layout["landscape"].get("ready", false)), "landscape is not marked ready")
	var view: Array = layout["portrait"]["map"]["view"]
	var content: Array = layout["portrait"]["map"]["content"]
	check(int(content[1]) > int(view[3]), "map content is taller than the view")
	check(int(content[0]) <= int(view[2]), "map content fits the portrait width")
	var region: Dictionary = _region()
	eq(int(region["map_size"][0]), int(content[0]), "region width matches layout")
	eq(int(region["map_size"][1]), int(content[1]), "region height matches layout")
	var actions: Array = layout["portrait"]["combat"]["action_bar"]
	eq(int(actions[0]), 0, "action bar x")
	eq(int(actions[1]), 430, "action bar y")
	eq(int(actions[2]), 270, "action bar width")
	eq(int(actions[3]), 50, "action bar height")
	check(int(actions[1]) + int(actions[3]) >= 460, "action bar sits in the bottom thumb zone")
	var chair: Dictionary = layout["portrait"]["combat"]["chair_bars"]
	check(chair.has("hp") and chair.has("mp") and chair.has("hp_text") and chair.has("mp_text"), "chair bars are data")
	var hp_text: Array = chair["hp_text"]
	var mp_text: Array = chair["mp_text"]
	var threat: Array = chair["threat"]
	check(int(hp_text[2]) >= 28 and int(hp_text[3]) >= 7, "hp number box fits a cur/max readout")
	check(int(mp_text[2]) >= 28 and int(mp_text[3]) >= 7, "mp number box fits a cur/max readout")
	check(int(hp_text[1]) + int(hp_text[3]) <= int(mp_text[1]), "hp number sits above the energy number")
	check(int(mp_text[1]) + int(mp_text[3]) <= 0, "energy number sits above the chair bars")
	check(int(threat[1]) + int(threat[3]) <= int(hp_text[1]), "threat sits above the health number")
	var name_tab: Array = layout["portrait"]["combat"]["name_tab"]
	var anchor: Array = layout["portrait"]["combat"]["seat_anchor"]
	var offset: Array = chair["offset"]
	var mp_bottom := int(layout["portrait"]["combat"]["seat_y"]) - int(anchor[1]) + int(offset[1]) + int(mp_text[1]) + int(mp_text[3])
	check(mp_bottom <= int(name_tab[1]), "chair numbers clear the turn tab")
	var skill_card: Array = layout["portrait"]["combat"]["skill_card"]
	eq(skill_card.size(), 4, "skill card rect")
	check(int(skill_card[2]) > 0 and int(skill_card[3]) > 0, "skill card has a size")
	eq(int(layout["portrait"]["party_min"]), 1, "party minimum")
	eq(int(layout["portrait"]["party_max"]), 5, "party maximum")
	var strip: Array = layout["portrait"]["combat"]["initiative"]
	var slot_px := int(layout["portrait"]["combat"]["initiative_slot"])
	var slot_n := int(layout["portrait"]["combat"]["initiative_slots"])
	eq(slot_n, 8, "initiative holds eight combatants")
	check(slot_n * slot_px + (slot_n - 1) * 2 <= int(strip[2]), "eight initiative portraits fit the strip")
	var main_px := int(layout["portrait"]["combat"]["action_main"])
	var small_px := int(layout["portrait"]["combat"]["action_small"])
	eq(main_px, 32, "attack, cover, and skills are 32px")
	eq(small_px, 20, "item and run are 20px")
	check(7 * main_px + 2 * small_px <= 270, "nine combat buttons fit the bar")


func _test_party_bar() -> void:
	var full: Array = Layout.party_seat_points(5)
	eq(full.size(), 5, "five seat points")
	near(float(full[0].x), 27.0, 0.01, "seat 1 x")
	near(float(full[1].x), 81.0, 0.01, "seat 2 x")
	near(float(full[2].x), 135.0, 0.01, "seat 3 x")
	near(float(full[3].x), 189.0, 0.01, "seat 4 x")
	near(float(full[4].x), 243.0, 0.01, "seat 5 x")
	near(float(full[1].y), float(full[0].y) - 4.0, 0.01, "seat 2 is 4px higher")
	near(float(full[3].y), float(full[0].y) - 4.0, 0.01, "seat 4 is 4px higher")
	near(float(full[2].y), float(full[0].y), 0.01, "seat 3 stays on the base line")
	near(float(full[4].y), float(full[0].y), 0.01, "seat 5 stays on the base line")
	var three: Array = Layout.party_seat_points(3)
	near((float(three[0].x) + float(three[2].x)) * 0.5, 135.0, 0.01, "party of 3 is centred")
	var one: Array = Layout.party_seat_points(1)
	near(float(one[0].x), 135.0, 0.01, "party of 1 sits in the middle")
	var four: Array = Layout.party_seat_points(4)
	near((float(four[0].x) + float(four[3].x)) * 0.5, 135.0, 0.01, "party of 4 is centred")
	eq(Layout.party_seat_points(0).size(), 0, "an empty party has no seats")
	var by_id := {}
	var skill_rows: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/skills.json"))
	for skill in skill_rows:
		by_id[str(skill["id"])] = skill
	var shield: Dictionary = by_id["shieldwall"]
	var strike: Dictionary = by_id["oathstrike"]
	var oath: Dictionary = by_id["oathmagnet"]
	eq(Formulas.skill_button_state(oath, 1, 80, 200, {}, {}, false), "passive", "passive is not a button")
	eq(Formulas.skill_button_state(shield, 0, 80, 200, {}, {}, false), "locked", "rank 0 is locked")
	eq(Formulas.skill_button_state(shield, 1, 80, 200, {"shieldwall": 2}, {}, true), "cooldown", "cooldown wins over selected")
	eq(Formulas.skill_cost_badge(shield, 1, {"shieldwall": 2}, {}), "2", "cooldown badge is the turns left")
	eq(Formulas.skill_button_state(strike, 1, 80, 200, {}, {}, true), "selected", "selected attack skill")
	eq(Formulas.skill_button_state(strike, 1, 80, 10, {}, {}, false), "disabled", "unaffordable skill is disabled")
	eq(Formulas.skill_cost_badge(strike, 1, {}, {}), "120", "mana badge is the energy cost")
	var armed: Dictionary = Formulas.arm_action("", "attack", true)
	eq(str(armed["armed"]), "attack", "first tap arms attack")
	check(not bool(armed["cast"]), "first tap does not cast")
	var casted: Dictionary = Formulas.arm_action("attack", "attack", true)
	check(bool(casted["cast"]), "second tap casts")
	eq(str(casted["armed"]), "", "a cast clears the arm")
	var switched: Dictionary = Formulas.arm_action("attack", "cover", true)
	eq(str(switched["armed"]), "cover", "a different slot switches the card")
	check(not bool(switched["cast"]), "switching does not cast")
	var dismissed: Dictionary = Formulas.arm_action("cover", "", true)
	eq(str(dismissed["armed"]), "", "an empty tap dismisses")
	check(not bool(dismissed["cast"]), "dismiss does not cast")
	var blocked_arm: Dictionary = Formulas.arm_action("skill:shieldwall", "skill:shieldwall", false)
	eq(str(blocked_arm["armed"]), "skill:shieldwall", "a blocked second tap stays armed")
	check(not bool(blocked_arm["cast"]), "a blocked second tap does not cast")
	var cooling: Dictionary = Formulas.skill_inspect(shield, 1, 80, 200, {"shieldwall": 2}, {})
	eq(str(cooling["hint"]), "On cooldown", "cooldown card explains itself")
	check(not bool(cooling["can_cast"]), "cooldown card cannot cast")
	var ready: Dictionary = Formulas.skill_inspect(strike, 1, 80, 200, {}, {})
	eq(str(ready["hint"]), "Tap again to cast", "ready card invites a second tap")
	eq(str(ready["tag"]), "Active", "active tag")
	check(bool(ready["can_cast"]), "ready card can cast")
	var passive_card: Dictionary = Formulas.skill_inspect(oath, 1, 80, 200, {}, {})
	eq(str(passive_card["tag"]), "Passive", "passive tag")
	eq(str(passive_card["hint"]), "Always on", "passive card cannot invite a cast")
	check(not bool(passive_card["can_cast"]), "passive card cannot cast")
	eq(Formulas.heal_timing(by_id["hearthmend"]), "Immediate", "a direct heal is immediate")
	eq(str(Formulas.skill_inspect(by_id["hearthmend"], 1, 40, 200, {}, {})["timing"]), "Immediate", "heal card says immediate")
	eq(Formulas.heal_timing(by_id["sap_pulse"]), "Each turn", "turn-start health is each turn")
	eq(str(Formulas.skill_inspect(by_id["sap_pulse"], 1, 40, 200, {}, {})["timing"]), "Each turn", "regen card says each turn")
	eq(Formulas.heal_timing(strike), "", "a strike is not a heal")


func _test_art_present() -> void:
	var appearance: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/appearance.json"))
	check(FileAccess.file_exists("res://art/doll/front/body.png"), "front body")
	check(FileAccess.file_exists("res://art/doll/back/body.png"), "back body")
	for i in int(appearance["head_count"]):
		check(FileAccess.file_exists("res://art/doll/front/head_%d.png" % i), "head %d" % i)
		check(FileAccess.file_exists("res://art/doll/front/hair_%d.png" % i), "hair %d" % i)
	for class_id in ["paladin", "wizard", "ranger", "bard", "cleric", "rogue", "barbarian", "druid"]:
		check(FileAccess.file_exists("res://art/doll/front/outfit_%s.png" % class_id), class_id + " outfit")
		check(FileAccess.file_exists("res://art/doll/front/weapon_%s.png" % class_id), class_id + " weapon")
		check(FileAccess.file_exists("res://art/doll/back/outfit_%s.png" % class_id), class_id + " back outfit")
	var monsters: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/monsters.json"))
	for monster in monsters:
		var sprite := str(monster.get("sprite", ""))
		var legacy := FileAccess.file_exists("res://art/monsters/%s.png" % monster["id"])
		var idle := FileAccess.file_exists("res://art_source/phase0/monsters/%s/%s_idle.png" % [sprite, sprite])
		check(legacy or idle, monster["id"] + " sprite")
		if sprite == "":
			continue
		for anim in ["idle", "attack", "hit", "death"]:
			var frame: Texture2D = ArtPack.monster_frame(sprite, anim, 0)
			check(frame != null and frame.get_width() > 0, monster["id"] + " " + anim + " frame")
		var still := FileAccess.file_exists("res://art_source/phase0/monsters/%s/%s_still.png" % [sprite, sprite])
		var portrait := FileAccess.file_exists("res://art_source/phase0/monsters/%s/%s_portrait.png" % [sprite, sprite])
		check(still and portrait, monster["id"] + " still and portrait")
	check(FileAccess.file_exists("res://art/map/greenmere.png"), "region map")
	check(FileAccess.file_exists("res://art/ui/table.png"), "table")
	check(FileAccess.file_exists("res://art/ui/gm.png"), "gm")
	check(FileAccess.file_exists("res://art_source/phase0/manifest.json"), "production manifest")
	var grass: Texture2D = ArtPack.texture("map/tile_grass.png")
	check(grass != null and grass.get_width() > 0, "map grass loads through ArtPack")
	for sprite_name in ["village", "windmill", "tavern", "shrine", "cave", "castle", "brinewick", "ashgate", "pebblegate"]:
		var loc: Texture2D = ArtPack.texture("map/loc_%s.png" % sprite_name)
		check(loc != null and loc.get_width() == 32 and loc.get_height() == 32, "map place %s is a 32x32 pin" % sprite_name)
	var pin_anchor := ArtPack.map_pin_anchor()
	eq(pin_anchor, Vector2(16, 28), "map pins anchor at 16,28")
	var seat: Texture2D = ArtPack.texture("party/seat_paladin_idle.png")
	check(seat != null and seat.get_width() > 0, "seat doll loads through ArtPack")
	var skill_icon: Texture2D = ArtPack.texture("ui/skills/paladin_1.png")
	check(skill_icon != null and skill_icon.get_width() > 0, "skill icon loads through ArtPack")
	var combat_bg: Texture2D = ArtPack.texture("combat/bg_forest_portrait.png")
	check(combat_bg != null and combat_bg.get_width() > 0, "combat backdrop loads through ArtPack")
	check(ResourceLoader.exists("res://art/ui/icon_die.png"), "ui icon resolves as a resource")
	check(ResourceLoader.exists("res://art/sfx/tap.wav"), "sfx resolves as a resource")
	check(FileAccess.file_exists("res://art_source/phase0/ui/portrait/action_bar_v2.png"), "action bar art")
	check(FileAccess.file_exists("res://art_source/phase0/ui/portrait/digits_3x5_outlined.png"), "hp digit font")
	check(FileAccess.file_exists("res://art_source/phase0/ui/skills/skill_slot_passive.png"), "passive skill frame")
	check(FileAccess.file_exists("res://art/fonts/m5x7.ttf"), "m5x7 font")
	eq(ArtPack.slot_file("passive"), "ui/skills/skill_slot_passive.png", "passives use the passive frame")
	var skill_rows: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/skills.json"))
	for skill in skill_rows:
		if str(skill.get("owner", "")) == "monster":
			continue
		var icon := str(skill.get("icon", ""))
		check(icon != "" and FileAccess.file_exists("res://art_source/phase0/ui/skills/%s.png" % icon), str(skill["id"]) + " icon")


func _test_wrapped_labels() -> void:
	var font: Font = Widgets.ui_font()
	var font_size := Layout.font_size()
	var line_h := font.get_height(font_size)
	var card := Layout.rect("combat", "skill_card")
	var text_w := card.size.x - 28.0
	var skill_rows: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/skills.json"))
	for skill in skill_rows:
		if str(skill.get("owner", "")) == "monster":
			continue
		var desc := str(skill.get("description", ""))
		var block := Widgets.wrap_size(desc, text_w, font_size)
		var height := Widgets.inspect_card_height(desc, card.size.x)
		check(block.x <= text_w + 0.01, str(skill["id"]) + " description stays inside the card")
		check(62.0 + block.y + 22.0 <= height + 0.01, str(skill["id"]) + " card grows for the wrapped description")
		var chars := int((card.size.x - 32.0 + 1.0) / 4.0)
		var lines := PixelFont.wrap(desc, chars)
		var pixel_h := Widgets.pixel_card_height(desc, card.size.x)
		check(62.0 + float(lines.size()) * 8.0 + 22.0 <= pixel_h + 0.01, str(skill["id"]) + " pixel card fits the description")
	var oath := Widgets.wrap_size("A heavy blow that draws enemy attention until your next turn.", text_w, font_size)
	check(oath.y >= line_h * 2.0 - 0.01, "oathstrike description wraps onto a second line")
	var stats := Formulas.compose_stats(1, 2, 3, 0, 0, 3, 0, 1, 0)
	var attack := Formulas.player_attack(1, int(stats["body"]))
	var attack_range := Formulas.damage_range(attack)
	var stat_line := "Nim the Glenfolk Wizard\nB%d S%d M%d  HP %d  EN %d  Atk %d-%d" % [
		int(stats["body"]), int(stats["senses"]), int(stats["mind"]),
		Formulas.max_hp(1, int(stats["body"]), int(stats["mind"])),
		Formulas.max_energy(1, int(stats["body"]), int(stats["mind"])) + 400,
		attack_range.x, attack_range.y
	]
	var stats_rect := Layout.rect("creator", "stats")
	var actions_rect := Layout.rect("creator", "actions")
	var stat_block := Widgets.wrap_size(stat_line, stats_rect.size.x, font_size)
	check(stat_block.y > line_h + 0.01, "creator stats use more than one line")
	check(stat_block.y <= stats_rect.size.y + 0.01, "creator stats fit above the buttons")
	check(stat_block.x <= stats_rect.size.x + 0.01, "creator stats stay inside the stats width")
	check(stats_rect.position.y + stats_rect.size.y <= actions_rect.position.y + 0.01, "creator stats end above Random, Next, and Begin")
	var info := Layout.rect("map", "info")
	var row := Layout.rect("map", "travel_row")
	check(info.position.y + info.size.y <= row.position.y + 0.01, "map description ends above the travel buttons")
	var region: Dictionary = _region()
	for place in region["places"]:
		var blurb := Widgets.place_blurb(place, 4, 99, false)
		var wrapped := Widgets.wrap_size(blurb, info.size.x, font_size)
		check(wrapped.x <= info.size.x + 0.01, str(place["id"]) + " description stays inside the panel")
		check(wrapped.y <= info.size.y + 0.01, str(place["id"]) + " description wraps inside the panel")
	_test_quest_text_fit(font_size)
	_test_hub_text_fit()


func _test_quest_text_fit(font_size: int) -> void:
	var quests: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/quests.json"))
	var item_names := {}
	var item_rows: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/items.json"))
	for item in item_rows:
		item_names[str(item["id"])] = str(item["name"])
	var tiny := Layout.font_tiny()
	var flavor := ""
	for step in quests["story"]:
		var step_name := str(step["name"])
		if flavor == "":
			flavor = str(step["gm"])
		_fit_text(step_name, 246, 20, font_size, step_name + " title")
		_fit_text(str(step["objective"]), 246, 32, font_size, step_name + " objective")
		_fit_text(str(step["gm"]), 246, 64, tiny, step_name + " flavor")
		_fit_text(_reward_line(step, item_names), 246, 16, tiny, step_name + " reward")
		_fit_text(QuestRules.tracker_line(step), 262, 16, tiny, step_name + " tracker")
		_fit_text("%s is done. +%d gold." % [step_name, int(step.get("gold", 0))], 230, 120, tiny, step_name + " toast")
	_fit_text(QuestRules.tracker_line({}), 262, 16, tiny, "quiet tracker")
	for quest in quests["board"]:
		var quest_name := str(quest["name"])
		var progress := QuestRules.progress_line(quest, int(quest.get("count", 1)))
		_fit_text(quest_name, 220, 16, font_size, quest_name + " notice")
		var ask := "Bring %d %s." % [int(quest["count"]), str(quest.get("item_name", ""))]
		if str(quest.get("kind", "")) == "kill":
			ask = "Defeat %d %s." % [int(quest["count"]), str(quest.get("monster_name", ""))]
		_fit_text(ask, 220, 16, tiny, quest_name + " ask")
		_fit_text(progress, 246, 16, font_size, quest_name + " counter")
		_fit_text("%s  %s" % [quest_name, progress], 160, 28, tiny, quest_name + " turn-in")
		_fit_text(_reward_line(quest, item_names), 220, 16, tiny, quest_name + " pay")
		_fit_text(progress, 230, 120, tiny, quest_name + " toast")
	var sample := Widgets.label(flavor, tiny)
	Widgets.place_wrapped(sample, Vector2(12, 80), Vector2(246, 64))
	check(sample.size.x <= 246.01, "quest flavor label stays at the panel width")
	check(sample.get_combined_minimum_size().x <= 246.01, "quest flavor label wraps instead of growing")
	sample.free()
	var victory := "XP 40, split across the table.\nGold +45. Purse 515.\nCrab Shell 2/5\nGrin in the Reeds is done. +45 gold."
	_fit_text(victory, 230, 120, tiny, "victory toast")


func _test_hub_text_fit() -> void:
	var caption := Layout.rect("combat", "caption")
	var banner := Layout.rect("hub", "banner")
	var tiny := Layout.font_tiny()
	var small := Layout.font_small()
	var caption_w := caption.size.x - 8.0
	var caption_h := caption.size.y - 2.0
	var banner_w := banner.size.x - 8.0
	var banner_h := banner.size.y - 2.0
	var region: Dictionary = _region()
	for place in region["places"]:
		_fit_text(str(place["description"]), caption_w, caption_h, tiny, str(place["id"]) + " hub caption")
		_fit_text("%s   %d gold" % [str(place["name"]), 9999], banner_w, banner_h, small, str(place["id"]) + " hub banner")
	check(Widgets.header_back().a >= 0.99, "hub header backing is opaque")
	check(Widgets.contrast_ratio(Widgets.header_ink(), Widgets.header_back()) >= 4.5, "hub header text contrasts with its parchment")
	var bar := Layout.rect("combat", "action_bar")
	var gap := 3.0
	var width := (bar.size.x - 4.0 - gap * 4.0) / 5.0
	var height := bar.size.y - 8.0
	var labels := PackedStringArray(["Travel", "Fight", "Rest", "Quest", "Gear"])
	var fit: Dictionary = Widgets.action_row_fit(labels, width, height, true)
	var font: Font = Widgets.ui_font()
	var font_size := int(fit["font_size"])
	var icon_w := int(fit["icon_width"])
	var extra := 0.0 if icon_w == 0 else float(icon_w) + float(fit["gap"])
	check(font_size >= 12, "hub buttons stay readable")
	for label in labels:
		var text_w := font.get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x
		check(text_w + extra + float(fit["side"]) <= width + 0.01, "%s fits on the hub button" % label)
	var back: Dictionary = Widgets.action_row_fit(PackedStringArray(["Back"]), bar.size.x - 4.0, height, false)
	var back_w := font.get_string_size("Back", HORIZONTAL_ALIGNMENT_LEFT, -1, int(back["font_size"])).x
	check(back_w + float(back["side"]) <= bar.size.x - 4.0 + 0.01, "Back fits on the action bar")


func _fit_text(text: String, width: float, height: float, font_size: int, label: String) -> void:
	var block := Widgets.wrap_size(text, width, font_size)
	check(block.x <= width + 0.01, label + " stays inside the width")
	check(block.y <= height + 0.01, label + " wraps inside the height")


func _reward_line(step: Dictionary, item_names: Dictionary) -> String:
	var parts: PackedStringArray = []
	if int(step.get("xp", 0)) > 0:
		parts.append("%d xp" % int(step.get("xp", 0)))
	if int(step.get("gold", 0)) > 0:
		parts.append("%d gold" % int(step.get("gold", 0)))
	var reward := str(step.get("reward", ""))
	if reward != "":
		parts.append(str(item_names.get(reward, reward)))
	if parts.is_empty():
		return "No reward."
	return ", ".join(parts)


func _test_targeting_and_lineup() -> void:
	check(Formulas.needs_chosen_target("enemy", false), "an enemy skill needs a tap")
	check(Formulas.needs_chosen_target("ally", false), "an ally skill needs a tap")
	check(not Formulas.needs_chosen_target("self", false), "a self skill does not need a tap")
	check(not Formulas.needs_chosen_target("enemies", false), "a crowd skill does not need a tap")
	check(not Formulas.needs_chosen_target("enemy", true), "a passive is not aimed")
	var armed: Dictionary = Formulas.turn_tap({}, "skill:oathstrike", true, true)
	eq(str(armed["armed"]), "skill:oathstrike", "first tap arms a targeted skill")
	check(bool(armed["picking"]), "first tap of a targeted skill starts picking")
	check(not bool(armed["cast"]), "arming a targeted skill does not cast")
	var cancelled: Dictionary = Formulas.turn_tap(armed, "skill:oathstrike", true, true)
	eq(str(cancelled["armed"]), "", "tapping the armed skill again cancels")
	check(not bool(cancelled["picking"]), "cancel leaves pick mode")
	var blocked: Dictionary = Formulas.turn_tap({}, "skill:oathstrike", false, true)
	check(not bool(blocked["picking"]), "an unaffordable skill is not armed for a pick")
	check(not bool(blocked["cast"]), "an unaffordable skill does not cast")
	var wall: Dictionary = Formulas.turn_tap({}, "skill:shieldwall", true, false)
	check(not bool(wall["picking"]), "a self skill does not enter pick mode")
	var wall_cast: Dictionary = Formulas.turn_tap(wall, "skill:shieldwall", true, false)
	check(bool(wall_cast["cast"]), "a self skill still casts on the second tap")
	var attack: Dictionary = Formulas.turn_tap({}, "attack", true, false)
	check(not bool(attack["picking"]), "the attack button shows its card first")
	var attack_pick: Dictionary = Formulas.turn_tap(attack, "attack", true, false)
	check(bool(attack_pick["picking"]) and not bool(attack_pick["cast"]), "the attack button's second tap asks for a target")
	var dismissed: Dictionary = Formulas.turn_tap(armed, "", true, true)
	eq(str(dismissed["armed"]), "", "an empty tap clears the card")
	var order := ["puddleblob", "thicket_imp", "gravel_brute"]
	var counts := {}
	for _i in 8:
		counts = Formulas.adjust_count(order, counts, "puddleblob", 1)
	eq(Formulas.lineup_from_counts(order, counts).size(), 5, "the lineup caps at five")
	counts = Formulas.adjust_count(order, counts, "thicket_imp", 1)
	eq(int(counts["thicket_imp"]), 0, "a full table refuses another type")
	counts = Formulas.adjust_count(order, counts, "puddleblob", -1)
	counts = Formulas.adjust_count(order, counts, "thicket_imp", 1)
	var mixed: Array = Formulas.lineup_from_counts(order, counts)
	eq(mixed.size(), 5, "a mixed lineup still totals five")
	eq(int(counts["puddleblob"]), 4, "four of the first type remain")
	eq(str(mixed[4]), "thicket_imp", "the fifth foe is the second type")
	var one: Dictionary = Formulas.expected_battle_rewards([{"id": "puddleblob", "level": 1}], 1.0)
	var two: Dictionary = Formulas.expected_battle_rewards([
		{"id": "puddleblob", "level": 1},
		{"id": "puddleblob", "level": 1},
	], 1.0)
	var tough: Dictionary = Formulas.expected_battle_rewards([{"id": "gravel_brute", "level": 4}], 1.0)
	check(int(two["xp"]) > int(one["xp"]), "two foes are worth more xp than one")
	check(int(two["gold"]) > int(one["gold"]), "two foes are worth more gold than one")
	check(int(tough["xp"]) > int(one["xp"]), "a higher level foe is worth more xp")
	check(int(tough["gold"]) > int(one["gold"]), "a higher level foe is worth more gold")
	eq(str(one["difficulty"]), "Even", "a matching level is even")
	eq(str(tough["difficulty"]), "Hard", "a much higher level is hard")
	var easy: Dictionary = Formulas.expected_battle_rewards([{"id": "puddleblob", "level": 1}], 5.0)
	eq(str(easy["difficulty"]), "Easy", "a weaker foe is easy")
	var seen := {}
	var region_ids: Array = []
	var region_rows: Dictionary = _region()
	var places: Array = region_rows["places"]
	for place in places:
		for monster_id in place.get("monsters", []):
			var key := str(monster_id)
			if seen.has(key):
				continue
			seen[key] = true
			region_ids.append(key)
	check(region_ids.size() >= 2, "the region offers more than one monster")
	eq(str(region_ids[0]), "puddleblob", "region monsters follow the places")


func _test_table_space() -> void:
	eq(Formulas.monster_size_tag({"size": "large"}), "large", "explicit large tag")
	eq(Formulas.monster_size_tag({"size": "regular", "boss": true}), "regular", "an explicit regular tag wins")
	eq(Formulas.monster_size_tag({"boss": true}), "large", "a boss without a tag is large")
	eq(Formulas.monster_size_tag({"elite": true}), "regular", "an elite without a tag stays regular")
	eq(Formulas.monster_size_tag({}), "regular", "a plain foe is regular")
	eq(Formulas.table_cost("regular"), 3, "regular cost")
	eq(Formulas.table_cost("large"), 5, "large cost")
	eq(Formulas.TABLE_CAPACITY, 15, "table capacity")
	var monsters: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/monsters.json"))
	var large_ids := {"briar_hound": true, "marshlurker": true, "gravel_brute": true, "kelpback": true}
	for monster in monsters:
		var mid := str(monster["id"])
		var tag := str(monster.get("size", ""))
		if large_ids.has(mid):
			eq(tag, "large", mid + " is large")
		else:
			eq(tag, "regular", mid + " is regular")
	var order := ["blob", "brute"]
	var sizes := {"blob": "regular", "brute": "large"}
	var counts := {}
	for _i in 8:
		counts = Formulas.adjust_count(order, counts, "blob", 1, sizes)
	eq(Formulas.lineup_from_counts(order, counts, sizes).size(), 5, "five regulars fill the table")
	eq(Formulas.space_used(order, counts, sizes), 15, "five regulars spend 15")
	eq(Formulas.space_left(order, counts, sizes), 0, "five regulars leave no space")
	counts = Formulas.adjust_count(order, counts, "brute", 1, sizes)
	eq(int(counts["brute"]), 0, "a full regular table refuses a large foe")
	counts = {}
	for _i in 5:
		counts = Formulas.adjust_count(order, counts, "brute", 1, sizes)
	eq(int(counts["brute"]), 3, "three larges fill the table")
	eq(Formulas.space_used(order, counts, sizes), 15, "three larges spend 15")
	counts = Formulas.adjust_count(order, counts, "blob", 1, sizes)
	eq(int(counts["blob"]), 0, "a full large table refuses a regular foe")
	counts = {}
	counts = Formulas.adjust_count(order, counts, "brute", 1, sizes)
	for _i in 4:
		counts = Formulas.adjust_count(order, counts, "blob", 1, sizes)
	eq(int(counts["brute"]), 1, "one large stays")
	eq(int(counts["blob"]), 3, "three regulars join one large")
	eq(Formulas.space_used(order, counts, sizes), 14, "one large and three regulars spend 14")
	eq(Formulas.lineup_from_counts(order, counts, sizes).size(), 4, "that mix is four foes")
	counts = {}
	counts = Formulas.adjust_count(order, counts, "brute", 2, sizes)
	counts = Formulas.adjust_count(order, counts, "blob", 1, sizes)
	eq(int(counts["brute"]), 2, "two larges stay")
	eq(int(counts["blob"]), 1, "one regular joins two larges")
	eq(Formulas.space_used(order, counts, sizes), 13, "two larges and one regular spend 13")
	var blocked: Dictionary = Formulas.adjust_count(order, counts, "brute", 1, sizes)
	eq(int(blocked["brute"]), 2, "a third large does not fit with a regular")
	blocked = Formulas.adjust_count(order, counts, "blob", 1, sizes)
	eq(int(blocked["blob"]), 1, "a second regular does not fit with two larges")
	counts = {}
	for _i in 4:
		counts = Formulas.adjust_count(order, counts, "blob", 1, sizes)
	blocked = Formulas.adjust_count(order, counts, "brute", 1, sizes)
	eq(int(blocked["brute"]), 0, "a large foe does not fit after four regulars")
	var large_first := ["brute", "blob"]
	var clamped: Dictionary = Formulas.clamp_counts(large_first, {"brute": 5, "blob": 2}, sizes)
	eq(int(clamped["brute"]), 3, "a saved stack of larges clamps to three")
	eq(int(clamped["blob"]), 0, "regulars after a full large stack are dropped")
	var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/layout.json"))
	var table_top := float(layout["portrait"]["combat"]["table"][1])
	var card_top := float(layout["portrait"]["combat"]["skill_card"][1])
	var packs := [
		[{"size": "regular"}, {"size": "regular"}, {"size": "regular"}, {"size": "regular"}, {"size": "regular"}],
		[{"size": "large"}, {"size": "large"}, {"size": "large"}],
		[{"size": "large"}, {"size": "regular"}, {"size": "regular"}, {"size": "regular"}],
		[{"size": "large", "back": true}, {"size": "large"}, {"size": "regular"}],
		[{"size": "regular"}, {"size": "regular"}, {"size": "regular"}, {"size": "regular"}, {"size": "regular"}, {"size": "regular"}, {"size": "regular"}],
	]
	var labels := ["five regular", "three large", "one large three regular", "two large one regular", "seven regular ambush"]
	for p in packs.size():
		_assert_row_fit(packs[p], labels[p], table_top, card_top)
	var mixed: Array = Formulas.enemy_layout([{"size": "large"}, {"size": "regular", "back": true}])
	check(mixed[1].position.y < mixed[0].position.y, "a back-row foe stands higher")
	check(mixed[0].size.x > mixed[1].size.x, "a large foe is wider than a regular foe")


func _assert_row_fit(entries: Array, label: String, table_top: float, card_top: float) -> void:
	var rects: Array = Formulas.enemy_layout(entries)
	eq(rects.size(), entries.size(), label + " places every foe")
	var large_w := 0
	var regular_w := 0
	for i in rects.size():
		var rect: Rect2 = rects[i]
		check(rect.position.x >= -0.01 and rect.position.y >= 30.0, label + " stays on the meadow")
		check(rect.end.x <= 270.01 and rect.end.y <= 480.01, label + " stays inside 270x480")
		check(rect.end.y <= table_top + 0.01, label + " stays above the table")
		check(rect.end.y <= card_top + 0.01, label + " stays above the skill card")
		check(rect.size.x >= 24.0 and rect.size.y >= 24.0, label + " hitbox stays tappable")
		if str(entries[i].get("size", "regular")) == "large":
			large_w = int(rect.size.x)
		else:
			regular_w = int(rect.size.x)
		for j in i:
			var other: Rect2 = rects[j]
			var hit := rect.intersection(other)
			check(hit.size.x <= 0.05 or hit.size.y <= 0.05, label + " foes do not overlap")
	if large_w > 0 and regular_w > 0:
		check(large_w > regular_w, label + " large footprint is wider")


func _test_place_rosters() -> void:
	var wrapped: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/region.json"))
	eq(str(wrapped["active"]), "greenmere", "the file names the active region")
	check(wrapped["regions"] is Array and (wrapped["regions"] as Array).size() >= 1, "regions are a list of entries")
	var picked: Dictionary = Formulas.active_region({
		"active": "b",
		"regions": [{"id": "a", "name": "Aye"}, {"id": "b", "name": "Bee"}],
	})
	eq(str(picked["name"]), "Bee", "active id selects the region entry")
	eq(str(Formulas.active_region({"id": "flat", "places": []})["id"]), "flat", "a single region still loads")
	var merged: Array = Formulas.encounter_roster(["briar_hound", "puddleblob"], ["briar_hound", "lantern_wisp"])
	eq(merged.size(), 3, "wanderers append without repeating an id")
	eq(str(merged[0]), "briar_hound", "local monsters stay first")
	eq(str(merged[2]), "lantern_wisp", "a new wanderer is added")
	var monsters := {}
	var monster_rows: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/monsters.json"))
	for row in monster_rows:
		monsters[str(row["id"])] = row
	var region := _region()
	var wanderers: Array = region.get("wanderers", [])
	check(wanderers.is_empty(), "places do not share a wanderer on top of the region table")
	var meadow := ["puddleblob", "thicket_imp", "cinder_mite", "briar_hound", "bramblet", "grinmud_toad"]
	var coast := ["cinder_mite", "briar_hound", "lantern_wisp", "bottlecrab", "squallgull", "kelpback"]
	var cave := ["cave_howler", "lantern_wisp", "briar_hound", "marshlurker", "gloomgrub", "dripfang"]
	var keep_table := ["cave_howler", "briar_hound", "marshlurker", "gravel_brute", "pebble_squire", "hollow_helm", "cobble_rat"]
	var expected := {
		"candlewick": [],
		"millpond": meadow,
		"briar_cross": meadow,
		"lantern_reach": coast,
		"howling_cleft": cave,
		"gravel_keep": keep_table,
		"brinewick": [],
		"ashgate": [],
		"pebblegate": [],
	}
	for place in region["places"]:
		var place_id := str(place["id"])
		var roster: Array = Formulas.encounter_roster(place.get("monsters", []), wanderers)
		var wanted: Array = expected[place_id]
		eq(roster, wanted, place_id + " lists only its region table")
		var backdrop := str(place.get("backdrop", ""))
		eq(backdrop, "combat/bg_%s_portrait.png" % place_id, place_id + " names its portrait backdrop")
		var tex: Texture2D = ArtPack.texture(backdrop)
		check(tex != null and tex.get_width() == 270 and tex.get_height() == 480, place_id + " backdrop is 270x480")
		if place_id == "brinewick" or place_id == "ashgate" or place_id == "pebblegate":
			eq(str(place.get("sprite", "")), place_id, place_id + " uses its own map pin")
			var candle: Texture2D = ArtPack.texture("combat/bg_candlewick_portrait.png")
			check(candle != null and not _is_recolor(candle.get_image(), tex.get_image()), place_id + " backdrop is not a tinted Candlewick")
		if str(place.get("kind", "")) == "town":
			check(roster.is_empty(), place_id + " has no fights")
			continue
		var large := 0
		var regular := 0
		for monster_id in roster:
			check(monsters.has(str(monster_id)), place_id + " names a real monster")
			if Formulas.monster_size_tag(monsters[str(monster_id)]) == "large":
				large += 1
			else:
				regular += 1
		check(regular >= 4 and large >= 1, place_id + " has four regulars and a large foe")
	var keep: Array = expected["gravel_keep"]
	eq(str(keep[0]), "cave_howler", "the keep's first foe is a regular")
	check(keep.has("gravel_brute") and keep.has("kelpback") == false, "the keep lists its brute and not the snapper")


func _test_gear() -> void:
	var sword := {"id": "sword", "slot": "weapon", "tag": "sword", "hands": 1, "offhand": false}
	var staff := {"id": "staff", "slot": "weapon", "tag": "staff", "hands": 2, "offhand": false}
	var shield := {"id": "shield", "slot": "off", "tag": "shield", "hands": 1}
	var plate := {"id": "plate", "slot": "armor", "weight": "heavy"}
	var coat := {"id": "coat", "slot": "armor", "weight": "light"}
	var ring := {"id": "ring", "slot": "trinket"}
	var paladin := {"weights": ["light", "medium", "heavy"], "tags": ["sword", "shield"]}
	var wizard := {"weights": ["light"], "tags": ["staff"]}
	eq(Formulas.wear_block(plate, paladin), "", "a paladin may wear heavy plate")
	eq(Formulas.wear_block(plate, wizard), "weight", "a wizard cannot wear heavy plate")
	eq(Formulas.wear_block(sword, wizard), "tag", "a wizard cannot wield a sword")
	eq(Formulas.wear_block(coat, wizard), "", "a wizard may wear a light coat")
	var gear := Formulas.empty_gear()
	gear["main"] = "sword"
	gear["off"] = "shield"
	var two: Dictionary = Formulas.equip_plan(gear, staff, "main", 1)
	check(bool(two["ok"]), "a two-hander can be equipped")
	eq(str(two["gear"]["main"]), "staff", "the two-hander takes the main hand")
	eq(str(two["gear"]["off"]), "", "a two-hander clears the off hand")
	check((two["removed"] as Array).has("sword") and (two["removed"] as Array).has("shield"), "both hands return to the bag")
	var off: Dictionary = Formulas.equip_plan(two["gear"], shield, "off", 2)
	check(bool(off["ok"]), "an off-hand item can replace a two-hander")
	eq(str(off["gear"]["main"]), "", "the two-hander leaves when the off hand is filled")
	eq(str(off["gear"]["off"]), "shield", "the shield takes the off hand")
	var trinket: Dictionary = Formulas.equip_plan(Formulas.empty_gear(), ring, "", 1)
	eq(str(trinket["gear"]["trinkets"][0]), "ring", "the first trinket slot fills first")
	var second: Dictionary = Formulas.equip_plan(trinket["gear"], {"id": "bead", "slot": "trinket"}, "", 1)
	eq(str(second["gear"]["trinkets"][1]), "bead", "the next trinket uses the next slot")
	var third: Dictionary = Formulas.equip_plan(second["gear"], {"id": "bell", "slot": "trinket"}, "trinket:2", 1)
	eq(str(third["gear"]["trinkets"][2]), "bell", "the third trinket has its own slot")
	var bonus := Formulas.sum_bonus([
		{"stats": {"attack": 4, "body": 1, "dr": 2, "crit": 3, "max_hp": 10}},
		{"stats": {"attack": 1, "mind": 2, "threat": 4}},
	])
	eq(int(bonus["attack"]), 5, "weapon attack adds")
	eq(int(bonus["body"]), 1, "body adds before derived stats")
	eq(int(bonus["dr"]), 2, "armor adds")
	eq(int(bonus["mind"]), 2, "mind adds")
	eq(int(bonus["threat"]), 4, "threat adds")
	near(float(bonus["crit"]), 3.0, 0.01, "crit adds")
	var naked_hp := Formulas.max_hp(1, 8, 3)
	var geared_hp := Formulas.max_hp(1, 8 + int(bonus["body"]), 3) + int(bonus["max_hp"])
	var naked_atk := Formulas.player_attack(1, 8)
	var geared_atk := Formulas.player_attack(1, 8 + int(bonus["body"])) + int(bonus["attack"])
	check(geared_hp > naked_hp, "body and flat health raise max HP")
	check(geared_atk > naked_atk, "body and flat attack raise the swing")
	eq(Formulas.sell_value(24), 12, "sell price is half")
	eq(Formulas.sell_value(25), 12, "half a gold rounds down")
	var low: Array = Formulas.loot_categories(1, false, 0.04, 0.09, 0.19)
	check(low.has("equipment") and low.has("trinket") and low.has("usable"), "level 1 rolls just under the cuts")
	var miss: Array = Formulas.loot_categories(1, false, 0.05, 0.1, 0.2)
	check(miss.is_empty(), "the drop cuts are strict")
	var boss: Array = Formulas.loot_categories(1, true, 0.49, 0.99, 0.19)
	check(boss.has("equipment") and boss.has("trinket") and boss.has("usable"), "a boss drops gear at 0.5 and always a trinket")
	check(not Formulas.loot_categories(1, true, 0.5, 0.0, 0.2).has("equipment"), "a boss misses equipment at 0.5")
	eq(Formulas.unique_drop("fang", false, 0.07), "fang", "a monster unique can drop")
	eq(Formulas.unique_drop("fang", false, 0.08), "", "a unique misses on the cut")
	eq(Formulas.unique_drop("fang", true, 0.39), "fang", "a boss unique is more likely")
	eq(Formulas.unique_drop("", true, 0.0), "", "no unique id means no unique drop")
	var catalog: Array = [
		{"id": "sword", "slot": "weapon", "rarity": "common", "level": 1},
		{"id": "ring", "slot": "trinket", "rarity": "common", "level": 1},
		{"id": "potion", "slot": "usable", "rarity": "common", "level": 1},
		{"id": "crown", "slot": "trinket", "rarity": "unique", "level": 1},
		{"id": "plate", "slot": "armor", "rarity": "rare", "level": 3},
	]
	eq(Formulas.pick_loot(catalog, "equipment", 1, 0), "sword", "equipment ignores the high-level plate")
	eq(Formulas.pick_loot(catalog, "equipment", 3, 1), "plate", "a higher roll can pick the second equipment")
	eq(Formulas.pick_loot(catalog, "trinket", 1, 0), "ring", "uniques stay out of the trinket table")
	eq(Formulas.pick_loot(catalog, "usable", 1, 0), "potion", "usables come from the usable table")
	var rows: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/items.json"))
	var by_id := {}
	var slots := {"weapon": 0, "off": 0, "armor": 0, "trinket": 0, "usable": 0, "quest": 0}
	var rarities := {"common": 0, "rare": 0, "legendary": 0, "unique": 0}
	var gear_items := 0
	for row in rows:
		by_id[str(row["id"])] = row
		check(str(row.get("name", "")) != "", str(row["id"]) + " has a name")
		check(str(row.get("icon", "")) != "", str(row["id"]) + " names an icon")
		var slot_name := str(row["slot"])
		slots[slot_name] = int(slots.get(slot_name, 0)) + 1
		rarities[str(row["rarity"])] = int(rarities.get(str(row["rarity"]), 0)) + 1
		if slot_name != "quest":
			gear_items += 1
	check(gear_items >= 70 and gear_items <= 90, "tiered shop and craft gear")
	check(int(slots["quest"]) >= 8, "quest tokens for the board")
	check(int(slots["weapon"]) >= 8, "weapons for the classes")
	check(int(slots["armor"]) >= 4, "armor tiers")
	check(int(slots["trinket"]) >= 4, "trinkets")
	check(int(slots["usable"]) >= 6 and int(slots["usable"]) <= 10, "consumables through tier 4")
	check(int(rarities["legendary"]) >= 1 and int(rarities["unique"]) >= 1, "legendary and unique tiers")
	var classes: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/classes.json"))
	for cls in classes:
		var kit: Dictionary = cls.get("kit", {})
		var main := str(kit.get("main", ""))
		check(by_id.has(main), str(cls["id"]) + " starts with a real weapon")
		eq(Formulas.wear_block(by_id[main], cls), "", str(cls["id"]) + " can wear the starting weapon")
	var monsters: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/monsters.json"))
	var uniques := 0
	for monster in monsters:
		var unique := str(monster.get("unique", ""))
		if unique == "":
			continue
		uniques += 1
		check(by_id.has(unique), str(monster["id"]) + " unique exists")
		eq(str(by_id[unique]["rarity"]), "unique", str(unique) + " is unique")
	check(uniques >= 4, "several monsters carry a unique")
	eq(str(by_id["lurker_scale"]["name"]), "Bone Plate", "lurker scale stays Bone Plate")
	eq(str(by_id["wisp_jar"]["name"]), "Cap Jar", "wisp jar stays Cap Jar")
	for row in rows:
		var icon := "ui/items/%s.png" % str(row["id"])
		eq(str(row["icon"]), icon, str(row["id"]) + " icon path")
		check(ArtPack.has(icon), str(row["id"]) + " icon file")
		var icon_tex := ArtPack.texture(icon)
		check(icon_tex != null and icon_tex.get_width() == 16 and icon_tex.get_height() == 16, str(row["id"]) + " icon is 16x16")
		check(not ArtPack.icon_is_placeholder(icon_tex), str(row["id"]) + " icon is not a parchment placeholder")
		var doll := str(row.get("doll", ""))
		if doll == "":
			continue
		check(ArtPack.has(doll), str(row["id"]) + " seat overlay")
		var overlay := ArtPack.texture(doll)
		check(overlay != null and overlay.get_width() == 48 and overlay.get_height() == 78, str(row["id"]) + " overlay is 48x78")


func _test_seat_gear() -> void:
	var recipe := ArtPack.recipe_gear_order()
	var expected := PackedStringArray(["body", "outfit", "class", "armor", "hair", "hat", "off", "main", "chair"])
	eq(recipe, expected, "seat recipe order is body through chair")
	eq(ArtPack.seat_gear_order(), expected, "composer order matches the recipe")
	var look := ArtPack.default_look("paladin")
	var full := {
		"armor": "paperdoll/gear/travel_coat.png",
		"off": "paperdoll/gear/kettle_shield.png",
		"off_flip": false,
		"main": "paperdoll/gear/oath_blade.png",
		"main_weapon": true,
		"two_hand": false,
	}
	var ids: PackedStringArray = []
	for step in ArtPack.seat_blit_plan("paladin", full):
		ids.append(str(step["id"]))
	eq(ids, expected, "a full seat blits every recipe layer")
	var two := {
		"off": "paperdoll/gear/kettle_shield.png",
		"off_flip": false,
		"main": "paperdoll/gear/reed_staff.png",
		"main_weapon": true,
		"two_hand": true,
	}
	var two_ids: PackedStringArray = []
	for step in ArtPack.seat_blit_plan("wizard", two):
		two_ids.append(str(step["id"]))
	check(not two_ids.has("off"), "a two-hander clears the off hand")
	check(two_ids.has("main") and two_ids.find("main") < two_ids.find("chair"), "the main hand sits under the chair")
	check(two_ids.find("class") < two_ids.find("hair") and two_ids.find("hair") < two_ids.find("main"), "hair stays above the class and under the weapon")
	eq(ArtPack.pick_class_back("paladin", true, false), "paperdoll/back/class_back_paladin.png", "missing noweapon falls back")
	eq(ArtPack.pick_class_back("paladin", true, true), "paperdoll/back/class_back_paladin_noweapon.png", "a noweapon layer replaces the armed class")
	eq(ArtPack.pick_class_back("paladin", false, true), "paperdoll/back/class_back_paladin.png", "an empty main hand keeps the painted class weapon")
	for class_id in ["paladin", "druid", "wizard", "barbarian", "bard", "ranger"]:
		var bare := ArtPack.class_noweapon_rel(class_id)
		check(ArtPack.has(bare), class_id + " noweapon layer is painted")
		eq(ArtPack.class_back_rel(class_id, true), bare, class_id + " drops the baked weapon while armed")
		eq(ArtPack.class_back_rel(class_id, false), "paperdoll/back/class_back_%s.png" % class_id, class_id + " keeps the class weapon when unarmed")
		var idle := ArtPack.seat_sheet_rel(class_id, "seat_idle", true)
		var active := ArtPack.seat_sheet_rel(class_id, "seat_active", true)
		check(idle.ends_with("_noweapon.png") and ArtPack.has(idle), class_id + " idle seat drops the baked weapon")
		check(active.ends_with("_noweapon.png") and ArtPack.has(active), class_id + " active seat drops the baked weapon")
	eq(ArtPack.class_back_rel("cleric", true), "paperdoll/back/class_back_cleric.png", "cleric keeps the normal layer")
	eq(ArtPack.class_back_rel("rogue", true), "paperdoll/back/class_back_rogue.png", "rogue keeps the normal layer")
	eq(ArtPack.seat_sheet_rel("cleric", "seat_idle", true), "party/seat_cleric_idle.png", "cleric seat stays the normal bake")
	_test_ranger_quiver()
	_test_one_equipped_weapon()
	check(ArtPack.offhand_flips({"slot": "weapon", "tag": "dagger", "hands": 1}), "a dagger flips in the off hand")
	check(ArtPack.offhand_flips({"slot": "weapon", "tag": "sword", "hands": 1}), "a one-handed sword flips in the off hand")
	check(not ArtPack.offhand_flips({"slot": "off", "tag": "shield", "hands": 1}), "a shield keeps its own art")
	check(not ArtPack.offhand_flips({"slot": "off", "tag": "orb", "hands": 1}), "an orb keeps its own art")
	check(not ArtPack.offhand_flips({"slot": "weapon", "tag": "staff", "hands": 2}), "a two-hander is not an off-hand flip")
	var knife := "paperdoll/gear/pocket_knife.png"
	var plain := ArtPack.gear_image(knife, false)
	var flipped := ArtPack.gear_image(knife, true)
	var turned := plain.duplicate()
	turned.flip_x()
	check(_same_image(flipped, turned), "off-hand flip is a horizontal mirror")
	var rogue := ArtPack.default_look("rogue")
	var bare := ArtPack.compose_doll("back", rogue, "rogue")
	var worn := ArtPack.compose_doll("back", rogue, "rogue", {"off": knife, "off_flip": true})
	var unflipped := ArtPack.compose_doll("back", rogue, "rogue", {"off": knife, "off_flip": false})
	check(not _same_image(worn.get_image(), unflipped.get_image()), "the off hand renders the flipped dagger")
	check(_gear_pixel_matches(bare.get_image(), worn.get_image(), flipped, plain), "flipped dagger pixels land on the seat")
	var shield := "paperdoll/gear/kettle_shield.png"
	var shield_img := ArtPack.gear_image(shield, false)
	var shielded := ArtPack.compose_doll("back", look, "paladin", {"off": shield, "off_flip": false})
	check(_gear_pixel_matches(ArtPack.compose_doll("back", look, "paladin").get_image(), shielded.get_image(), shield_img, ArtPack.gear_image(shield, true)), "a shield is drawn unflipped")
	var staff := "paperdoll/gear/reed_staff.png"
	var wizard := ArtPack.default_look("wizard")
	var staff_only := ArtPack.compose_doll("back", wizard, "wizard", {"main": staff, "main_weapon": true, "two_hand": true})
	var staff_and_off := ArtPack.compose_doll("back", wizard, "wizard", {"main": staff, "main_weapon": true, "two_hand": true, "off": shield, "off_flip": false})
	check(_same_image(staff_only.get_image(), staff_and_off.get_image()), "a two-hander hides the off-hand overlay")
	var with_shield := ArtPack.compose_doll("back", wizard, "wizard", {"main": staff, "main_weapon": true, "two_hand": false, "off": shield, "off_flip": false})
	check(not _same_image(staff_only.get_image(), with_shield.get_image()), "the off hand draws when two_hand is off")
	ArtPack.clear_bake_cache()
	var front_bare := ArtPack.compose_doll("front", look, "paladin")
	ArtPack.clear_bake_cache()
	var front := ArtPack.compose_doll("front", look, "paladin", full)
	check(front.get_width() == 32 and front.get_height() == 48, "the front doll stays 32x48")
	check(_same_image(front.get_image(), front_bare.get_image()), "seat overlays are not baked onto the front doll")


func _test_ranger_quiver() -> void:
	var normal := "paperdoll/back/class_back_ranger.png"
	var bow_layer := "paperdoll/back/class_back_ranger_noweapon.png"
	var bare_layer := "paperdoll/back/class_back_ranger_noweapon_noquiver.png"
	eq(ArtPack.class_back_rel("ranger", false, ""), normal, "an unarmed ranger keeps the bow and quiver")
	eq(ArtPack.class_back_rel("ranger", true, "bow"), bow_layer, "a bow keeps the quiver")
	eq(ArtPack.class_back_rel("ranger", true, "dagger"), bare_layer, "a dagger drops the quiver")
	eq(ArtPack.pick_class_back("ranger", true, true, "axe"), bare_layer, "any non-bow tag drops the quiver")
	eq(ArtPack.seat_sheet_rel("ranger", "seat_idle", false, ""), "party/seat_ranger_idle.png", "unarmed ranger seat")
	eq(ArtPack.seat_sheet_rel("ranger", "seat_active", true, "bow"), "party/seat_ranger_active_noweapon.png", "bow ranger active seat keeps the quiver")
	eq(ArtPack.seat_sheet_rel("ranger", "seat_idle", true, "dagger"), "party/seat_ranger_idle_noweapon_noquiver.png", "dagger ranger idle seat drops the quiver")
	eq(ArtPack.seat_sheet_rel("ranger", "seat_active", true, "dagger"), "party/seat_ranger_active_noweapon_noquiver.png", "dagger ranger active seat drops the quiver")
	for rel in [bare_layer, "party/seat_ranger_idle_noweapon_noquiver.png", "party/seat_ranger_active_noweapon_noquiver.png"]:
		var sheet := ArtPack.texture(rel)
		check(sheet != null and sheet.get_width() == 48 and sheet.get_height() == 78, rel + " loads at 48x78")
	var look := ArtPack.default_look("ranger")
	var bow_gear := {"main": "paperdoll/gear/thorn_bow.png", "main_weapon": true, "main_tag": "bow"}
	var knife_gear := {"main": "paperdoll/gear/pocket_knife.png", "main_weapon": true, "main_tag": "dagger"}
	var bow_plan: Array = ArtPack.seat_blit_plan("ranger", bow_gear)
	var knife_plan: Array = ArtPack.seat_blit_plan("ranger", knife_gear)
	var bow_class := ""
	var knife_class := ""
	for bow_step in bow_plan:
		if str(bow_step["id"]) == "class":
			bow_class = str(bow_step["path"])
	for knife_step in knife_plan:
		if str(knife_step["id"]) == "class":
			knife_class = str(knife_step["path"])
	eq(bow_class, bow_layer, "composing a bow uses the quiver layer")
	eq(knife_class, bare_layer, "composing a dagger uses the no-quiver layer")
	var bare := ArtPack.compose_doll("back", look, "ranger")
	var with_bow := ArtPack.compose_doll("back", look, "ranger", bow_gear)
	var with_knife := ArtPack.compose_doll("back", look, "ranger", knife_gear)
	check(bare.get_width() == 48 and with_bow.get_height() == 78, "ranger seats compose at 48x78")
	check(not _same_image(bare.get_image(), with_bow.get_image()), "a bow changes the ranger seat")
	check(not _same_image(with_bow.get_image(), with_knife.get_image()), "a dagger seat is not the bow seat")
	var idle_sheet := ArtPack.seat_idle("ranger", true, "dagger")
	var active_sheet := ArtPack.seat_active("ranger", true, "dagger")
	check(idle_sheet != null and active_sheet != null, "no-quiver seat sheets load")


func _is_recolor(source: Image, other: Image) -> bool:
	if source == null or other == null:
		return true
	if source.get_width() != other.get_width() or source.get_height() != other.get_height():
		return false
	var sample := source.get_pixel(10, 10)
	var tint := other.get_pixel(10, 10)
	if sample.r < 0.05 or sample.g < 0.05 or sample.b < 0.05:
		return false
	var kr := tint.r / sample.r
	var kg := tint.g / sample.g
	var kb := tint.b / sample.b
	var hit := 0
	var total := 0
	var y := 0
	while y < source.get_height():
		var x := 0
		while x < source.get_width():
			var a := source.get_pixel(x, y)
			var b := other.get_pixel(x, y)
			total += 1
			if absf(a.r * kr - b.r) < 0.05 and absf(a.g * kg - b.g) < 0.05 and absf(a.b * kb - b.b) < 0.05:
				hit += 1
			x += 8
		y += 8
	return total > 0 and float(hit) / float(total) > 0.85


func _test_one_equipped_weapon() -> void:
	var weapons := {
		"paladin": "paperdoll/gear/oath_blade.png",
		"druid": "paperdoll/gear/sap_crook.png",
		"wizard": "paperdoll/gear/reed_staff.png",
		"barbarian": "paperdoll/gear/gravel_axe.png",
		"bard": "paperdoll/gear/road_lute.png",
		"ranger": "paperdoll/gear/thorn_bow.png",
		"cleric": "paperdoll/gear/chapel_mace.png",
		"rogue": "paperdoll/gear/pocket_knife.png",
	}
	for class_id in weapons.keys():
		var gear_path := str(weapons[class_id])
		var look := ArtPack.default_look(class_id)
		var unarmed := ArtPack.compose_doll("back", look, class_id).get_image()
		var stripped := ArtPack.compose_doll("back", look, class_id, {"main_weapon": true}).get_image()
		var armed := ArtPack.compose_doll("back", look, class_id, {
			"main": gear_path,
			"main_weapon": true,
		}).get_image()
		var gear := ArtPack.gear_image(gear_path, false)
		var class_pixels := 0
		var leaked := 0
		var covered := 0
		for y in unarmed.get_height():
			for x in unarmed.get_width():
				if unarmed.get_pixel(x, y) == stripped.get_pixel(x, y):
					continue
				class_pixels += 1
				if y < gear.get_height() and x < gear.get_width() and gear.get_pixel(x, y).a > 0.5:
					covered += 1
					continue
				if armed.get_pixel(x, y) != stripped.get_pixel(x, y):
					leaked += 1
		if class_id == "cleric" or class_id == "rogue":
			eq(class_pixels, 0, class_id + " has no baked weapon to double")
		else:
			check(class_pixels > 0, class_id + " baked weapon is visible when unarmed")
		eq(leaked, 0, class_id + " shows one weapon when one is equipped")
		check(not _same_image(stripped, armed), class_id + " still draws the equipped weapon")


func _same_image(a: Image, b: Image) -> bool:
	if a.get_width() != b.get_width() or a.get_height() != b.get_height():
		return false
	for y in a.get_height():
		for x in a.get_width():
			if a.get_pixel(x, y) != b.get_pixel(x, y):
				return false
	return true


func _gear_pixel_matches(base: Image, seated: Image, want: Image, other: Image) -> bool:
	var found := false
	for y in mini(want.get_height(), seated.get_height()):
		for x in mini(want.get_width(), seated.get_width()):
			var painted := want.get_pixel(x, y)
			var rival := other.get_pixel(x, y)
			if painted.a < 0.5 or base.get_pixel(x, y).a > 0.2:
				continue
			if rival == painted:
				continue
			found = true
			if seated.get_pixel(x, y) != painted:
				return false
	return found


func _test_quests() -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/quests.json"))
	var story: Array = QuestRules.steps(data)
	var rows: Array = QuestRules.board(data)
	check(story.size() >= 8 and story.size() <= 12, "story is 8 to 12 steps")
	eq(str(data["rules"]["refresh"]).find("Accepting"), 0, "the board rerolls a slot when a quest is accepted")
	var first := {}
	for i in story.size():
		var place := str(story[i].get("place", ""))
		if not first.has(place):
			first[place] = i
	check(int(first["candlewick"]) < int(first["millpond"]), "Candlewick comes before the meadow")
	check(int(first["millpond"]) < int(first["briar_cross"]), "the meadow comes before Briar Cross")
	check(int(first["briar_cross"]) < int(first["lantern_reach"]), "Briar Cross comes before the coast")
	check(int(first["lantern_reach"]) < int(first["howling_cleft"]), "the coast comes before the cave")
	check(int(first["howling_cleft"]) < int(first["gravel_keep"]), "the cave comes before the keep")
	eq(str(story[story.size() - 1].get("place", "")), "gravel_keep", "the chain ends at Gravel Keep")
	var toad := QuestRules.find_row(story, "the_wide_toad")
	eq(QuestRules.story_drop_item(toad, "millpond", ["grinmud_toad"]), "reed_tongue", "the toad leaves its tongue")
	eq(QuestRules.story_drop_item(toad, "millpond", ["puddleblob"]), "", "a different monster does not leave the tongue")
	var done: Array = []
	var inventory := {}
	for _guard in story.size() + 2:
		var step := QuestRules.current_step(story, done)
		if step.is_empty():
			break
		var place := str(step.get("place", ""))
		var kind := str(step.get("type", ""))
		var won := kind == "fight" or kind == "boss"
		var killed: Array = []
		if kind == "boss":
			killed = [str(step.get("monster", ""))]
		var drop := QuestRules.story_drop_item(step, place, killed)
		if drop != "":
			inventory[drop] = int(inventory.get(drop, 0)) + 1
		if kind == "deliver":
			inventory[str(step.get("item", ""))] = int(inventory.get(str(step.get("item", "")), 0)) + 1
		check(not QuestRules.step_ready(step, "gravel_keep" if place != "gravel_keep" else "candlewick", won, killed, inventory), str(step["id"]) + " ignores the wrong place")
		var before := done.size()
		var result: Dictionary = QuestRules.advance(story, done, place, won, killed, inventory)
		done = result["done"]
		eq(done.size(), before + 1, str(step["id"]) + " unlocks the next step")
		for taken in QuestRules.reward_takes(result["completed"]):
			inventory[str(taken)] = int(inventory.get(str(taken), 1)) - 1
	eq(done.size(), story.size(), "the story chain finishes")
	var early: Array = QuestRules.revealed_places(story, [str(story[0]["id"])])
	check(early.has("millpond"), "the first step reveals Millpond")
	check(not early.has("gravel_keep"), "the keep stays unrevealed at the start")
	var regions: Array = QuestRules.unlocked_regions(early)
	check(regions.has("meadow") and not regions.has("coast") and not regions.has("keep"), "only the meadow board is open")
	check(not QuestRules.blocks_travel("gravel_keep", []), "story does not hard-lock a road")
	var meadow := QuestRules.fill_offers(rows, ["meadow"], [], 1)
	eq(meadow.size(), 3, "the board posts three notices")
	for offer in meadow:
		var quest := QuestRules.find_row(rows, str(offer))
		eq(str(quest.get("region", "")), "meadow", "early notices stay in the meadow")
	var quiet := QuestRules.fill_offers(rows, [], [], 1)
	eq(quiet, ["", "", ""], "a locked board posts nothing")
	var active: Array = []
	var salt := 1
	var offers: Array = meadow.duplicate()
	for _slot in 3:
		var taken: Dictionary = QuestRules.accept(offers, 0, active, rows, ["meadow"], salt)
		check(bool(taken["ok"]), "a board notice can be accepted")
		offers = taken["offers"]
		active = taken["active"]
		salt = int(taken["salt"])
	eq(active.size(), 3, "three grind quests can be active")
	var blocked: Dictionary = QuestRules.accept(offers, 0, active, rows, ["meadow", "coast", "cave", "keep"], salt)
	check(not bool(blocked["ok"]), "a fourth grind quest is refused")
	eq(str(blocked["reason"]), "cap", "the cap is three active quests")
	var kill_quest: Dictionary = {}
	var collect_quest: Dictionary = {}
	for row in rows:
		if str(row.get("region", "")) != "meadow":
			continue
		if str(row.get("kind", "")) == "kill" and kill_quest.is_empty():
			kill_quest = row
		if str(row.get("kind", "")) == "collect" and collect_quest.is_empty():
			collect_quest = row
	var grind: Array = [{"id": str(kill_quest["id"]), "progress": 0}, {"id": str(collect_quest["id"]), "progress": 0}]
	var kill_lines := QuestRules.note_kill(grind, rows, str(kill_quest["monster"]))
	eq(int(grind[0]["progress"]), 1, "a kill advances that monster's quest")
	eq(str(kill_lines[0]), QuestRules.progress_line(kill_quest, 1), "kill progress reads as a counter")
	eq(QuestRules.note_kill(grind, rows, "cobble_rat").size(), 0, "another monster does not tick the quest")
	eq(QuestRules.collect_drop(grind, rows, str(collect_quest["monster"]), 0.0), str(collect_quest["item"]), "an active quest can drop its token")
	eq(QuestRules.collect_drop(grind, rows, str(collect_quest["monster"]), QuestRules.DROP_CHANCE), "", "the drop rate is strict")
	eq(QuestRules.collect_drop([], rows, str(collect_quest["monster"]), 0.0), str(collect_quest["item"]), "materials still drop at the base rate")
	eq(QuestRules.collect_drop([], rows, str(collect_quest["monster"]), QuestRules.BASE_DROP), "", "the base drop rate is strict")
	var farm := QuestRules.collect_result([], rows, str(collect_quest["monster"]), 0.0)
	check(not bool(farm["counts"]), "a farmed drop does not count toward a quest")
	var toast := QuestRules.bump_collect(grind, str(collect_quest["item"]), rows)
	eq(toast, "%s 1/%d" % [str(collect_quest["item_name"]), int(collect_quest["count"])], "a drop toasts the counter")
	eq(int(grind[1]["progress"]), 1, "the drop advances the collect quest")
	var early_turn: Dictionary = QuestRules.turn_in(grind, rows, str(collect_quest["id"]))
	check(not bool(early_turn["ok"]), "a short collect quest cannot be turned in")
	grind[1]["progress"] = int(collect_quest["count"])
	var paid: Dictionary = QuestRules.turn_in(grind, rows, str(collect_quest["id"]))
	check(bool(paid["ok"]), "a finished collect quest turns in")
	eq(int(paid["quest"]["gold"]), int(collect_quest["gold"]), "turn-in pays the posted gold")
	eq(int(paid["quest"]["xp"]), int(collect_quest["xp"]), "turn-in pays the posted xp")
	eq(QuestRules.turn_in_takes(paid["quest"]), int(collect_quest["count"]), "turn-in consumes the tokens")
	check(paid["active"].size() == 1, "turn-in clears that quest")
	var packed := QuestRules.pack_state({"story_done": done, "offers": offers, "active": grind, "salt": salt})
	var restored := QuestRules.unpack_state(packed)
	eq(JSON.stringify(QuestRules.pack_state(restored)), JSON.stringify(packed), "quest state survives a save round trip")


func _test_towns_and_craft() -> void:
	var region := _region()
	var places := {}
	for place in region["places"]:
		places[str(place["id"])] = place
	var items: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/items.json"))
	var by_id := {}
	for row in items:
		by_id[str(row["id"])] = row
	var quests: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/quests.json"))
	var story: Array = QuestRules.steps(quests)
	var craft: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/craft.json"))
	var classes: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/classes.json"))
	var towns := {
		1: "candlewick",
		2: "brinewick",
		3: "ashgate",
		4: "pebblegate",
	}
	for tier in towns.keys():
		var place: Dictionary = places[towns[tier]]
		eq(str(place["kind"]), "town", str(place["name"]) + " is a town")
		eq(int(place["shop_tier"]), int(tier), str(place["name"]) + " sells its tier")
		check((place["monsters"] as Array).is_empty(), str(place["name"]) + " has no fight table")
	var early := QuestRules.revealed_places(story, ["kettle_errand"])
	check(not early.has("brinewick") and not early.has("ashgate") and not early.has("pebblegate"), "later towns stay shut at the kettle")
	var coast := QuestRules.revealed_places(story, ["wolf_in_the_hedge"])
	check(coast.has("brinewick") and coast.has("lantern_reach"), "the coast step opens Brinewick")
	check(not coast.has("ashgate"), "Ashgate waits for the cave")
	var cave := QuestRules.revealed_places(story, ["snapper_tide"])
	check(cave.has("ashgate") and cave.has("howling_cleft"), "the cave step opens Ashgate")
	var keep := QuestRules.revealed_places(story, ["bones_in_the_drip"])
	check(keep.has("pebblegate") and keep.has("gravel_keep"), "the keep step opens Pebblegate")
	var starter := CraftRules.shop_ids(items, places["candlewick"], early)
	check(starter.has("oath_blade") and not starter.has("kiln_sword") and not starter.has("salt_mace"), "Candlewick sells tier 1 only")
	var barred := CraftRules.shop_ids(items, places["brinewick"], early)
	eq(barred.size(), 0, "a locked town sells nothing")
	var coast_stock := CraftRules.shop_ids(items, places["brinewick"], coast)
	check(coast_stock.has("salt_mace") and coast_stock.has("kiln_sword") and not coast_stock.has("oath_blade"), "Brinewick sells tier 2")
	for tier in [1, 2, 3, 4]:
		var stock := CraftRules.shop_ids(items, places[towns[tier]], keep if tier == 4 else (cave if tier == 3 else (coast if tier == 2 else early)))
		var rows: Array = []
		for item_id in stock:
			rows.append(by_id[str(item_id)])
		var trinket := false
		var usable := false
		for row in rows:
			if str(row["slot"]) == "trinket":
				trinket = true
			if str(row["slot"]) == "usable":
				usable = true
		check(trinket and usable, "tier %d sells a trinket and a usable" % tier)
		for cls in classes:
			var tags: Array = cls["tags"]
			var weights: Array = cls["weights"]
			var weapon := false
			var armor := false
			var off := false
			var wants_off := tags.has("shield") or tags.has("orb")
			for row in rows:
				var slot := str(row["slot"])
				var tag := str(row.get("tag", ""))
				if slot == "weapon" and tags.has(tag):
					weapon = true
				if slot == "armor" and weights.has(str(row.get("weight", ""))):
					armor = true
				if slot == "off" and tags.has(tag):
					off = true
				if slot == "weapon" and tag == "dagger" and bool(row.get("offhand", false)) and tags.has("dagger"):
					off = true
			check(weapon, str(cls["id"]) + " can buy a weapon at tier %d" % tier)
			check(armor, str(cls["id"]) + " can buy armor at tier %d" % tier)
			if wants_off or tags.has("dagger"):
				check(off, str(cls["id"]) + " can buy an off-hand at tier %d" % tier)
	var recipe := CraftRules.find_recipe(craft["recipes"], "gel_edge")
	var bag := {"slime_gel": 4, "toad_wart": 1, "tonic": 1}
	var short := CraftRules.apply_craft(recipe, {"slime_gel": 3, "toad_wart": 1}, 40, 9)
	check(not bool(short["ok"]) and str(short["reason"]) == "material", "crafting refuses a short pile")
	eq(int(short["inventory"]["slime_gel"]), 3, "a refused craft keeps the materials")
	var broke := CraftRules.apply_craft(recipe, bag, 10, 9)
	check(not bool(broke["ok"]) and str(broke["reason"]) == "gold", "crafting refuses short gold")
	var made := CraftRules.apply_craft(recipe, bag, 40, 9)
	check(bool(made["ok"]), "gel edge crafts")
	eq(int(made["inventory"].get("slime_gel", 0)), 0, "crafting consumes the gel")
	eq(int(made["inventory"].get("toad_wart", 0)), 0, "crafting consumes the wart")
	eq(int(made["inventory"]["gel_edge"]), 1, "crafting adds the blade")
	eq(int(made["inventory"]["tonic"]), 1, "crafting leaves the rest of the bag")
	eq(int(made["gold"]), 0, "crafting spends the gold")
	var peer: Dictionary = by_id["pocket_knife"]
	var crafted: Dictionary = by_id["gel_edge"]
	check(int(crafted["stats"]["attack"]) > int(peer["stats"]["attack"]), "crafted gel edge hits harder than the stall knife")
	for row in craft["recipes"]:
		var result: Dictionary = by_id[str(row["result"])]
		var shop_peer: Dictionary = by_id[str(row["peer"])]
		eq(int(result["tier"]), int(row["tier"]), str(row["id"]) + " matches its tier")
		check(not bool(result["shop"]), str(row["id"]) + " is forge work, not stall stock")
		check(_craft_beats(result, shop_peer), str(row["id"]) + " beats the stall piece")
	eq(CraftRules.scale_int(3, 1), 4, "+1 lifts an attack of 3 to 4")
	eq(CraftRules.scale_int(5, 1), 6, "+1 lifts an attack of 5 by a quarter")
	eq(CraftRules.scale_int(5, 3), 9, "+3 keeps scaling")
	near(CraftRules.scale_float(0.05, 1), 0.06, 0.001, "+1 scales a spell bonus")
	eq(CraftRules.display_name("Oath Blade", 2), "Oath Blade +2", "the plus shows in the name")
	eq(CraftRules.can_upgrade(by_id["oath_blade"], 3), "max", "a weapon stops at +3")
	eq(CraftRules.can_upgrade(by_id["bread_charm"], 0), "slot", "a trinket cannot be tempered")
	var tiers: Dictionary = craft["tiers"]
	var cost := CraftRules.upgrade_cost(1, 0, tiers)
	eq(int(cost["gold"]), 30, "+1 at tier 1 costs 30 gold")
	eq(int(cost["materials"]["slime_gel"]), 2, "+1 asks for two gels")
	var cost3 := CraftRules.upgrade_cost(2, 2, tiers)
	eq(int(cost3["gold"]), 180, "+3 at tier 2 costs 180 gold")
	eq(int(cost3["materials"]["crab_shell"]), 4, "+3 asks for four shells")
	eq(int(cost3["materials"]["gull_feather"]), 2, "+3 also asks for feathers")
	var sword := {"oath_blade": 1, "slime_gel": 2}
	var lifted := CraftRules.apply_upgrade("oath_blade", by_id["oath_blade"], sword, 30, tiers, 9)
	check(bool(lifted["ok"]), "a bag weapon can be tempered")
	eq(int(lifted["inventory"].get("oath_blade", 0)), 0, "the plain blade leaves the bag")
	eq(int(lifted["inventory"]["oath_blade@1"]), 1, "the bag keeps the +1")
	eq(int(lifted["inventory"].get("slime_gel", 0)), 0, "tempering spends the gel")
	eq(int(lifted["gold"]), 0, "tempering spends the gold")
	var worn := CraftRules.apply_worn_upgrade("oath_blade", by_id["oath_blade"], {"slime_gel": 2}, 30, tiers)
	check(bool(worn["ok"]), "a worn blade can be tempered")
	eq(str(worn["key"]), "oath_blade@1", "the worn key gains +1")
	eq(int(worn["inventory"].get("slime_gel", 0)), 0, "a worn temper still spends materials")
	var capped := CraftRules.apply_upgrade("oath_blade@3", by_id["oath_blade"], {"oath_blade@3": 1, "slime_gel": 9}, 500, tiers, 9)
	check(not bool(capped["ok"]) and str(capped["reason"]) == "max", "plus three is the limit")
	eq(CraftRules.sell_price(40, 0), 20, "a plain item still sells at half")
	eq(CraftRules.sell_price(40, 2), 60, "each plus raises the sell price")
	var preview := CraftRules.stat_preview({"attack": 3}, CraftRules.scaled_stats({"attack": 3}, 1))
	eq(preview, "Atk 3 to 4", "the temper preview shows the next swing")
	var packed := CraftRules.pack_bag({"oath_blade@2": 1, "gel_edge": 1, "oath_blade@4": 1, "empty": 0})
	eq(int(packed["oath_blade@2"]), 1, "a plus survives the save")
	eq(int(packed["gel_edge"]), 1, "a crafted item survives the save")
	eq(int(packed["oath_blade@3"]), 1, "a plus above the cap clamps")
	check(not packed.has("empty"), "an empty stack is dropped")
	var again := CraftRules.pack_bag(packed)
	eq(JSON.stringify(again), JSON.stringify(packed), "the bag save round-trips")
	var active: Array = [{"id": str(quests["board"][0]["id"]), "progress": int(quests["board"][0]["count"])}]
	var full := QuestRules.collect_result(active, quests["board"], str(quests["board"][0]["monster"]), 0.0)
	check(not bool(full["counts"]), "a finished quest does not count another drop")
	eq(str(full["item"]), str(quests["board"][0]["item"]), "a finished quest still farms at the base rate")
	eq(QuestRules.turn_in_takes(quests["board"][0]), int(quests["board"][0]["count"]), "turn-in still takes the posted count")


func _test_levels_and_pools() -> void:
	eq(Formulas.vital_text(40, 80), "40/80", "the chair reads current and max")
	check(Formulas.max_hp(2, 9, 4) > Formulas.max_hp(2, 8, 4), "a body point raises max health")
	check(Formulas.max_energy(2, 8, 5) > Formulas.max_energy(2, 8, 4), "a mind point raises max energy")
	var perk_hp := int(round(float(Formulas.max_hp(2, 8, 4)) * (1.0 + LevelRules.HP_PCT)))
	check(perk_hp > Formulas.max_hp(2, 8, 4), "a health perk raises max health")
	eq(Formulas.fit_pool(40, 100, 130, false), 70, "a higher max adds the difference to current health")
	eq(Formulas.fit_pool(40, 100, 30, false), 30, "a lower max clamps current health")
	eq(Formulas.fit_pool(0, 100, 130, false), 0, "a downed hero stays down when max health rises")
	eq(Formulas.fit_pool(0, 20, 40, true), 20, "empty energy fills when the max rises")
	eq(Formulas.fit_pool(12, 20, 8, true), 8, "energy clamps when the max drops")
	var base := Formulas.max_hp(1, 8, 4)
	eq(Formulas.tuned_max(base, 1, 8, 4, 0, 0, 0.0, true), base, "an unshifted pool keeps its max")
	var body_up := Formulas.tuned_max(base, 1, 8, 4, 1, 0, 0.0, true)
	check(body_up > base, "a body buff raises max health")
	var wilted := Formulas.tuned_max(base, 1, 8, 4, -2, 0, 0.0, true)
	check(wilted < base, "a body debuff lowers max health")
	eq(Formulas.fit_pool(base, base, wilted, false), wilted, "health clamps to the debuffed max")
	var energy := Formulas.max_energy(1, 8, 4)
	var mind_up := Formulas.tuned_max(energy, 1, 8, 4, 0, 1, 0.0, false)
	check(mind_up > energy, "a mind buff raises max energy")
	var gear_hp := base + 10
	var tempered := base + CraftRules.scale_int(10, 1)
	check(tempered > gear_hp, "tempering a health trinket raises the pool")
	eq(Formulas.fit_pool(gear_hp, gear_hp, tempered, false), tempered, "the temper fills the new health")
	var hero := {
		"level": 2,
		"growth": LevelRules.blank(),
		"class_id": "paladin",
	}
	var skills: Array = []
	var rows: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/skills.json"))
	var classes: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/classes.json"))
	var wanted: Array = []
	for cls in classes:
		if str(cls["id"]) == "paladin":
			wanted = cls["skills"]
	for skill_id in wanted:
		for row in rows:
			if str(row["id"]) == str(skill_id):
				skills.append(row)
	var options := LevelRules.offers(hero, skills)
	eq(options.size(), 3, "a level offers three choices")
	var kinds := {}
	for option in options:
		kinds[str(option["kind"])] = true
		check(str(option["title"]) != "" and str(option["detail"]) != "", "each choice has a title and a line")
	check(bool(kinds.get("skill", false)), "a rankable hero is offered a skill")
	check(bool(kinds.get("stat", false)), "a level offers a stat")
	check(bool(kinds.get("perk", false)), "a level offers a perk")
	var refused := LevelRules.commit([], hero, skills, "stat_body")
	check(not bool(refused["ok"]), "there is no choice when nobody leveled")
	var queued := LevelRules.enqueue([], 0, 1)
	queued = LevelRules.enqueue(queued, 1, 2)
	eq(queued.size(), 3, "two heroes queue one panel per level")
	var skipped := LevelRules.commit(queued, hero, skills, "nope")
	check(not bool(skipped["ok"]) and skipped["queue"].size() == 3, "a bad pick does not leave the queue")
	var taken := LevelRules.commit(queued, hero, skills, "stat_mind")
	check(bool(taken["ok"]), "mind is one of the level 2 offers")
	eq(int(hero["growth"]["mind"]), 1, "the stat choice sticks")
	eq(taken["queue"].size(), 2, "the next hero is still waiting")
	var skill_id := ""
	for option in options:
		if str(option["kind"]) == "skill":
			skill_id = str(option["skill"])
	var ranked := LevelRules.commit(taken["queue"], hero, skills, "skill_%s" % skill_id)
	check(bool(ranked["ok"]), "the skill rank is accepted")
	eq(LevelRules.choice_rank(hero, skill_id), 1, "the skill rank is stored")
	var skill: Dictionary = {}
	for row in skills:
		if str(row["id"]) == skill_id:
			skill = row
	var tuned := LevelRules.tune_skill(skill, 1)
	check(Formulas.skill_mana_cost(tuned, 1) < Formulas.skill_mana_cost(skill, 1) or Formulas.skill_cooldown_length(tuned) < int(skill.get("cooldown", 0)) or Formulas.skill_hp_cost(tuned) <= int(skill.get("hp_cost", 0)), "a rank lowers a cost or a cooldown")
	var perked := LevelRules.commit(ranked["queue"], hero, skills, "perk_hp")
	if not bool(perked["ok"]):
		perked = LevelRules.commit(ranked["queue"], hero, skills, str(options[2]["id"]))
	check(bool(perked["ok"]), "the third offer is taken")
	check(LevelRules.sheet_line(hero, {skill_id: "Named"}) != "", "the sheet lists the growth")
	var saved := LevelRules.normalize(hero["growth"])
	eq(JSON.stringify(saved), JSON.stringify(LevelRules.normalize(saved)), "growth survives a save")
	for _i in LevelRules.SKILL_CAP:
		LevelRules.apply(hero, {"kind": "skill", "skill": skill_id})
	var full := LevelRules.offers(hero, skills)
	var still := false
	for option in full:
		if str(option.get("skill", "")) == skill_id:
			still = true
	check(not still, "a capped skill leaves the offer list")
	check(full.size() == 3, "a capped hero still gets three choices")


func _craft_beats(result: Dictionary, peer: Dictionary) -> bool:
	var left: Dictionary = result.get("stats", {})
	var right: Dictionary = peer.get("stats", {})
	for key in ["attack", "dr", "crit", "max_hp", "senses", "mind", "spell_bonus"]:
		if float(left.get(key, 0.0)) > float(right.get(key, 0.0)):
			return true
	return false
