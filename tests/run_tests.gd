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


func _test_route_and_encounter() -> void:
	var text := FileAccess.get_file_as_string("res://data/region.json")
	var region: Dictionary = JSON.parse_string(text)
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
	var region: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/region.json"))
	eq(personas.size(), 5, "5 personas")
	eq(races.size(), 3, "3 races")
	eq(classes.size(), 8, "8 classes")
	check(monsters.size() >= 6 and monsters.size() <= 8, "6–8 monsters")
	var places: Array = region["places"]
	check(places.size() >= 5 and places.size() <= 6, "5–6 places")
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
	eq(monster_skills, 5, "monster skills stay")


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
	var region: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/region.json"))
	eq(int(region["map_size"][0]), int(content[0]), "region width matches layout")
	eq(int(region["map_size"][1]), int(content[1]), "region height matches layout")
	var actions: Array = layout["portrait"]["combat"]["action_bar"]
	eq(int(actions[0]), 0, "action bar x")
	eq(int(actions[1]), 430, "action bar y")
	eq(int(actions[2]), 270, "action bar width")
	eq(int(actions[3]), 50, "action bar height")
	check(int(actions[1]) + int(actions[3]) >= 460, "action bar sits in the bottom thumb zone")
	var chair: Dictionary = layout["portrait"]["combat"]["chair_bars"]
	check(chair.has("hp") and chair.has("mp") and chair.has("hp_text"), "chair bars are data")
	var hp_text: Array = chair["hp_text"]
	var mp_bar: Array = chair["mp"]
	check(int(hp_text[2]) >= 13 and int(hp_text[3]) >= 7, "hp number box fits three outlined digits")
	check(int(hp_text[1]) + int(hp_text[3]) <= int(mp_bar[1]), "hp number sits above the mp bar")
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
		check(FileAccess.file_exists("res://art/monsters/%s.png" % monster["id"]), monster["id"] + " sprite")
	check(FileAccess.file_exists("res://art/map/greenmere.png"), "region map")
	check(FileAccess.file_exists("res://art/ui/table.png"), "table")
	check(FileAccess.file_exists("res://art/ui/gm.png"), "gm")
	check(FileAccess.file_exists("res://art_source/phase0/manifest.json"), "production manifest")
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
	var region: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/region.json"))
	for place in region["places"]:
		var blurb := Widgets.place_blurb(place, 4, 99, false)
		var wrapped := Widgets.wrap_size(blurb, info.size.x, font_size)
		check(wrapped.x <= info.size.x + 0.01, str(place["id"]) + " description stays inside the panel")
		check(wrapped.y <= info.size.y + 0.01, str(place["id"]) + " description wraps inside the panel")
