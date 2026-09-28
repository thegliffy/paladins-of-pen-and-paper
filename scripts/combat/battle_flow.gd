extends Node
class_name BattleFlow
## Turn loop, dice, and the timing table. The view is a SessionScreen.

var view: SessionScreen
var rng := RandomNumberGenerator.new()
var units: Array = []
var order: Array = []
var turn_index := 0
var _action := ""
var _target := ""
var _listening := false


func _ready() -> void:
	rng.randomize()


func start(monster_rows: Array, kind: String) -> String:
	_listen(true)
	await view.intro(kind == "ambush")
	_build_units(monster_rows)
	_roll_initiative()
	view.present_units(units)
	view.set_initiative(_order_entries(), "")
	var result := await _loop()
	_write_party()
	if result == "victory":
		await _grant_victory()
	elif result == "defeat":
		_grant_defeat()
		view.set_caption("The session breaks up.")
		await view.show_end("Defeated", "You crawl back to the road with a scrap of health.", 0.0, 0.25)
	else:
		view.set_caption("The party slips away.")
		await get_tree().create_timer(0.6).timeout
	GameState.disarm_battle()
	_listen(false)
	return result


func measure_visible_attack() -> int:
	var attacker := {
		"id": "p0", "side": "player", "name": "Mason", "member_index": 0,
		"level": 1, "body": 8, "senses": 3, "mind": 4, "hp": 200, "max_hp": 200,
		"mp": 50, "max_mp": 50, "attack": 45, "dr": 0, "initiative": 0,
		"spell_bonus": 0.0, "threat": 0, "covering": false, "conditions": [],
		"skill_ranks": {}, "weakened": false,
	}
	var defender := {
		"id": "m0", "side": "monster", "name": "Puddleblob", "hp": 500, "max_hp": 500,
		"mp": 0, "max_mp": 1, "dr": 0, "body": 2, "senses": 1, "mind": 1,
		"conditions": [], "back_row": false, "boss": false,
	}
	var started := Time.get_ticks_msec()
	await _player_basic(attacker, defender, false)
	return Time.get_ticks_msec() - started


func _listen(on: bool) -> void:
	if on and not _listening:
		view.action_pressed.connect(_on_action)
		view.target_pressed.connect(_on_target)
		_listening = true
	elif not on and _listening:
		if view.action_pressed.is_connected(_on_action):
			view.action_pressed.disconnect(_on_action)
		if view.target_pressed.is_connected(_on_target):
			view.target_pressed.disconnect(_on_target)
		_listening = false


func _on_action(action_id: String) -> void:
	_action = action_id


func _on_target(target_id: String) -> void:
	_target = target_id


func _build_units(monster_rows: Array) -> void:
	units.clear()
	for index in GameState.party.size():
		var member: Dictionary = GameState.party[index]
		var stats := GameState.combat_stats(member)
		units.append({
			"id": "p%d" % index,
			"side": "player",
			"name": ContentDB.persona(str(member["persona"]))["name"],
			"member_index": index,
			"level": int(member["level"]),
			"body": stats["body"],
			"senses": stats["senses"],
			"mind": stats["mind"],
			"hp": int(member["hp"]),
			"max_hp": stats["max_hp"],
			"mp": int(member["mp"]),
			"max_mp": stats["max_mp"],
			"attack": stats["attack"],
			"dr": stats["dr"],
			"initiative": stats["initiative"],
			"spell_bonus": stats["spell_bonus"],
			"threat": 0,
			"covering": false,
			"conditions": [],
			"skill_ranks": member["skill_ranks"].duplicate(true),
			"class_id": str(member["class_id"]),
			"boss": false,
			"back_row": false,
		})
	for i in monster_rows.size():
		var row: Dictionary = monster_rows[i]
		var monster: Dictionary = ContentDB.monster(str(row["id"]))
		var hp := Formulas.monster_max_hp(int(monster["level"]), int(monster["body"]), int(monster["mind"]), bool(monster.get("elite", false)))
		var attack := Formulas.monster_attack(int(monster["level"]), int(monster["body"]), bool(monster.get("elite", false)))
		units.append({
			"id": "m%d" % i,
			"side": "monster",
			"kind": str(monster["id"]),
			"name": str(monster["name"]),
			"level": int(monster["level"]),
			"body": int(monster["body"]),
			"senses": int(monster["senses"]),
			"mind": int(monster["mind"]),
			"hp": hp,
			"max_hp": hp,
			"mp": 0,
			"max_mp": 1,
			"attack": attack,
			"dr": int(monster.get("dr", 0)),
			"initiative": 0,
			"spell_bonus": 0.0,
			"threat": 0,
			"covering": false,
			"conditions": [],
			"skills": monster.get("skills", []),
			"skill_turns": 0,
			"attacks": int(monster.get("attacks", 1)),
			"damage_frame": int(monster.get("damage_frame", 2)),
			"back_row": bool(monster.get("back_row", false)),
			"boss": bool(monster.get("boss", false)),
			"elite": bool(monster.get("elite", false)),
			"power": int(monster.get("power", 1)),
		})


func _roll_initiative() -> void:
	var rolls := {}
	for unit in units:
		if int(unit["hp"]) <= 0:
			continue
		rolls[str(unit["id"])] = int(unit["senses"]) + int(unit["initiative"]) + rng.randi_range(1, 12)
	for _attempt in 5:
		var groups := {}
		for id in rolls.keys():
			var key := str(int(rolls[id]))
			if not groups.has(key):
				groups[key] = []
			groups[key].append(id)
		var tied: Array = []
		for key in groups.keys():
			if groups[key].size() > 1:
				tied.append_array(groups[key])
		if tied.is_empty():
			break
		for id in tied:
			var unit := _unit(str(id))
			rolls[id] = int(unit["senses"]) + int(unit["initiative"]) + rng.randi_range(1, 12)
	var ids: Array = rolls.keys()
	ids.sort_custom(func(a, b): return int(rolls[a]) > int(rolls[b]))
	order.clear()
	for id in ids:
		order.append(_unit(str(id)))
	turn_index = 0


func _loop() -> String:
	while true:
		if not _side_alive("player"):
			return "defeat"
		if not _side_alive("monster"):
			return "victory"
		if turn_index >= order.size():
			turn_index = 0
		var unit: Dictionary = order[turn_index]
		turn_index += 1
		if int(unit["hp"]) <= 0:
			continue
		var outcome := await _take_turn(unit)
		if outcome == "flee":
			return "flee" if _side_alive("player") else "defeat"
	return "defeat"


func _take_turn(unit: Dictionary) -> String:
	view.set_initiative(_order_entries(), str(unit["id"]))
	view.set_caption("%s's turn" % unit["name"])
	if str(unit["side"]) == "player":
		unit["covering"] = false
		unit["threat"] = 0
		view.set_cover(int(unit["member_index"]), false)
		view.raise_member(int(unit["member_index"]), true)
	if _has(unit, "stun"):
		await _damage_conditions(unit)
		_decay_stun(unit)
		view.sync_unit(unit)
		await _gap(unit)
		if str(unit["side"]) == "player":
			view.raise_member(int(unit["member_index"]), false)
		return ""
	await _tick_conditions(unit)
	if int(unit["hp"]) <= 0:
		return ""
	var outcome := ""
	if str(unit["side"]) == "player":
		outcome = await _player_turn(unit)
	else:
		await _monster_turn(unit)
	if str(unit["side"]) == "player":
		view.raise_member(int(unit["member_index"]), false)
	if outcome == "":
		await _gap(unit)
	return outcome


func _player_turn(unit: Dictionary) -> String:
	while true:
		view.set_actions([
			{"id": "attack", "label": "Attack", "icon": "icon_attack"},
			{"id": "skill", "label": "Skill", "icon": "icon_skill"},
			{"id": "item", "label": "Item", "icon": "icon_item"},
			{"id": "cover", "label": "Cover", "icon": "icon_cover"},
			{"id": "run", "label": "Run", "icon": "icon_run"},
		])
		var action := await _wait_action()
		match action:
			"attack":
				var target := await _choose_enemy(unit, false)
				if target.is_empty():
					continue
				await _player_basic(unit, target, true)
				return ""
			"skill":
				var skill_id := await _choose_skill(unit)
				if skill_id == "":
					continue
				if not await _use_skill(unit, skill_id):
					continue
				return ""
			"item":
				if not await _choose_item(unit):
					continue
				return ""
			"cover":
				await _cover(unit)
				return ""
			"run":
				await _run()
				return "flee"
	return ""


func _player_basic(attacker: Dictionary, defender: Dictionary, can_crit: bool) -> void:
	view.set_caption("%s attacks %s" % [attacker["name"], defender["name"]])
	view.lunge(str(attacker["id"]), -8.0, Timing.PLAYER_ATTACK_WINDUP + Timing.PLAYER_ATTACK_TO_HIT)
	await _wait(Timing.PLAYER_ATTACK_WINDUP + Timing.PLAYER_ATTACK_TO_HIT)
	await _strike(attacker, defender, float(attacker["attack"]), 0.25, can_crit, 0)
	await _wait(Timing.HP_TWEEN)


func _monster_turn(unit: Dictionary) -> void:
	unit["skill_turns"] = int(unit.get("skill_turns", 0)) + 1
	var skills: Array = unit.get("skills", [])
	var use_skill := false
	if not skills.is_empty():
		var chance := 0.25 * float(unit["skill_turns"])
		if rng.randf() > 1.0 - chance:
			use_skill = true
			unit["skill_turns"] = 0
	if use_skill:
		var skill: Dictionary = ContentDB.skill(str(skills[rng.randi() % skills.size()]))
		var target := _pick_player()
		if target.is_empty():
			return
		await _cast(unit, skill, [target])
		return
	var swings := maxi(1, int(unit.get("attacks", 1)))
	for swing in swings:
		var target := _pick_player()
		if target.is_empty() or int(target["hp"]) <= 0:
			break
		view.monster_pose(str(unit["id"]), "windup")
		await _wait(Timing.MONSTER_WINDUP)
		view.monster_pose(str(unit["id"]), "attack")
		await _wait(Timing.monster_time_to_damage(int(unit.get("damage_frame", 2))))
		await _strike(unit, target, float(unit["attack"]), 0.25, true, 0)
		await _wait(Timing.HP_TWEEN)
		view.monster_pose(str(unit["id"]), "idle")
		if swing + 1 < swings and int(target["hp"]) > 0:
			await _wait(Timing.FLOATER_QUEUE)


func _strike(attacker: Dictionary, defender: Dictionary, base: float, variance: float, can_crit: bool, flat_bonus: int) -> void:
	var weakened := _has(attacker, "weakness")
	if weakened:
		base *= 0.5
		can_crit = false
	var span := variance * 2.0
	var mult := (1.0 - variance) + rng.randf() * span
	var raw := float(int(round(base * mult))) + float(flat_bonus)
	var crit := false
	if can_crit:
		var chance := Formulas.crit_chance(int(attacker["senses"]))
		crit = Formulas.is_crit(chance, rng.randi_range(1, 100))
		if crit:
			raw *= 2.0
	var dealt := Formulas.damage_taken(raw, int(defender["dr"]))
	defender["hp"] = maxi(0, int(defender["hp"]) - dealt)
	var texts: Array = []
	if crit:
		texts.append({"text": "CRITICAL", "color": SpriteCatalog.FREE})
	texts.append({"text": "-%d" % dealt, "color": SpriteCatalog.HP})
	view.react_hit(str(defender["id"]), texts, _ratio(defender, "hp"), _ratio(defender, "mp"))
	if crit:
		await _wait(Timing.CRIT_HOLD)
	if int(defender["hp"]) <= 0:
		var stamp := Time.get_ticks_msec()
		await view.death_blink(str(defender["id"]))
		defender["death_ms"] = Time.get_ticks_msec() - stamp


func _use_skill(user: Dictionary, skill_id: String) -> bool:
	var skill: Dictionary = ContentDB.skill(skill_id)
	var rank := int(user.get("skill_ranks", {}).get(skill_id, 1))
	var cost := Formulas.mp_cost(int(skill.get("mp_base", 0)), rank)
	if str(user["side"]) == "player" and int(user["mp"]) < cost:
		view.set_caption("Not enough energy.")
		return false
	if str(user["side"]) == "player":
		user["mp"] = int(user["mp"]) - cost
		view.sync_unit(user)
	var kind := str(skill.get("kind", "spell"))
	if kind == "heal":
		var target := await _choose_ally()
		if target.is_empty():
			user["mp"] = int(user["mp"]) + cost
			view.sync_unit(user)
			return false
		await _heal(user, skill, target, rank)
		return true
	var allow_back := bool(skill.get("can_target_back_row", false))
	var targets: Array = []
	if str(skill.get("target", "enemy")) == "enemies":
		targets = _random_enemies(int(skill.get("max_targets", 1)), allow_back)
	else:
		var picked := await _choose_enemy(user, allow_back)
		if picked.is_empty():
			user["mp"] = int(user["mp"]) + cost
			view.sync_unit(user)
			return false
		targets = [picked]
	await _cast(user, skill, targets)
	return true


func _cast(user: Dictionary, skill: Dictionary, targets: Array) -> void:
	var lead := float(skill.get("time_before_damage", 0.0))
	if lead > 0.0:
		await _wait(lead)
	var rank := int(user.get("skill_ranks", {}).get(str(skill["id"]), 1))
	for i in targets.size():
		if i > 0:
			await _wait(Timing.MULTI_TARGET_GAP)
		var target: Dictionary = targets[i]
		if int(target["hp"]) <= 0:
			continue
		view.set_caption("%s uses %s" % [user["name"], skill["name"]])
		if str(skill.get("kind", "")) == "weapon":
			var bonus := 0
			if int(skill.get("later_init_bonus", 0)) > 0 and _later(user, target):
				bonus = int(skill["later_init_bonus"])
			await _strike(user, target, float(user["attack"]) * float(skill.get("attack_mult", 1.0)), float(skill.get("variance", 0.25)), true, bonus)
		else:
			var flat := Formulas.spell_flat(skill, int(user["mind"]), int(user["senses"]), rank, float(user.get("spell_bonus", 0.0)))
			if int(skill.get("later_init_bonus", 0)) > 0 and _later(user, target):
				flat += int(skill["later_init_bonus"])
			await _strike(user, target, float(flat), float(skill.get("variance", 0.1)), false, 0)
			var splash := float(skill.get("splash", 0.0))
			if splash > 0.0:
				for other in _neighbors(target):
					await _wait(Timing.MULTI_TARGET_GAP)
					await _strike(user, other, float(flat) * splash, float(skill.get("variance", 0.1)), false, 0)
					await _try_condition(skill, other)
		await _try_condition(skill, target)
		await _wait(Timing.HP_TWEEN)
	if int(skill.get("threat", 0)) > 0:
		user["threat"] = int(user.get("threat", 0)) + int(skill["threat"])


func _heal(user: Dictionary, skill: Dictionary, target: Dictionary, rank: int) -> void:
	var amount := Formulas.heal_amount(skill, int(user["mind"]), rank)
	target["hp"] = mini(int(target["max_hp"]), int(target["hp"]) + amount)
	view.react_hit(str(target["id"]), [{"text": "+%d" % amount, "color": Color("3dba6a")}], _ratio(target, "hp"), _ratio(target, "mp"))
	Sfx.play("heal")
	var self_heal := int(skill.get("self_heal", 0))
	if self_heal > 0 and str(target["id"]) != str(user["id"]):
		await _wait(Timing.FLOATER_QUEUE)
		user["hp"] = mini(int(user["max_hp"]), int(user["hp"]) + self_heal)
		view.react_hit(str(user["id"]), [{"text": "+%d" % self_heal, "color": Color("3dba6a")}], _ratio(user, "hp"), _ratio(user, "mp"))
	await _wait(0.4)


func _try_condition(skill: Dictionary, target: Dictionary) -> void:
	var cond := str(skill.get("condition", ""))
	if cond == "":
		return
	var save := str(skill.get("condition_save", ""))
	if save != "":
		var roll := rng.randi_range(1, 20)
		var ok := Formulas.saving_throw_succeeds(roll, int(target[save]), 0, _has(target, "stun"), bool(target.get("boss", false)))
		view.react_hit(str(target["id"]), [{"text": "SAVE" if ok else "FAIL", "color": SpriteCatalog.SAFE if ok else SpriteCatalog.HP}], _ratio(target, "hp"), _ratio(target, "mp"))
		await _wait(Timing.SAVING_THROW)
		if ok:
			return
	var kept: Array = []
	for existing in target["conditions"]:
		if str(existing["id"]) != cond:
			kept.append(existing)
	kept.append({
		"id": cond,
		"timer": int(skill.get("condition_timer", 2)),
		"damage": int(skill.get("condition_damage", 0)),
		"save": save,
	})
	target["conditions"] = kept
	view.sync_unit(target)


func _damage_conditions(unit: Dictionary) -> void:
	for cond in unit["conditions"]:
		if int(cond.get("damage", 0)) > 0:
			await _apply_condition_damage(unit, cond)


func _decay_stun(unit: Dictionary) -> void:
	var kept: Array = []
	for cond in unit["conditions"]:
		if str(cond["id"]) == "stun":
			cond["timer"] = int(cond["timer"]) - 1
			if int(cond["timer"]) > 0:
				kept.append(cond)
		else:
			kept.append(cond)
	unit["conditions"] = kept
	view.sync_unit(unit)


func _tick_conditions(unit: Dictionary) -> void:
	var kept: Array = []
	for cond in unit["conditions"]:
		var save := str(cond.get("save", ""))
		if save != "" and str(cond["id"]) != "stun":
			var roll := rng.randi_range(1, 20)
			var ok := Formulas.saving_throw_succeeds(roll, int(unit[save]), 0, false, bool(unit.get("boss", false)))
			if ok:
				view.set_caption("%s shakes off %s" % [unit["name"], cond["id"]])
				await _wait(Timing.SAVING_THROW)
				continue
		if int(cond.get("damage", 0)) > 0:
			await _apply_condition_damage(unit, cond)
			await _wait(Timing.CONDITION_DAMAGE)
		cond["timer"] = int(cond["timer"]) - 1
		if int(cond["timer"]) > 0:
			kept.append(cond)
		await _wait(Timing.CONDITION_GAP)
		if int(unit["hp"]) <= 0:
			break
	unit["conditions"] = kept
	view.sync_unit(unit)


func _apply_condition_damage(unit: Dictionary, cond: Dictionary) -> void:
	var amount := int(cond["damage"])
	if str(cond["id"]) == "poison" and int(unit.get("mp", 0)) > 0:
		var taken := mini(int(unit["mp"]), amount)
		unit["mp"] = int(unit["mp"]) - taken
		amount -= taken
		view.react_hit(str(unit["id"]), [{"text": "-%d" % taken, "color": SpriteCatalog.MP}], _ratio(unit, "hp"), _ratio(unit, "mp"))
		if amount > 0:
			await _wait(Timing.FLOATER_QUEUE)
	if amount > 0:
		unit["hp"] = maxi(0, int(unit["hp"]) - amount)
		view.react_hit(str(unit["id"]), [{"text": "-%d" % amount, "color": SpriteCatalog.HP}], _ratio(unit, "hp"), _ratio(unit, "mp"))
		if int(unit["hp"]) <= 0:
			await view.death_blink(str(unit["id"]))


func _cover(unit: Dictionary) -> void:
	unit["covering"] = true
	view.set_cover(int(unit["member_index"]), true)
	view.set_caption("%s takes cover." % unit["name"])
	Sfx.play("tap")
	await _wait(0.35)


func _choose_item(user: Dictionary) -> bool:
	var entries: Array = []
	for item_id in GameState.inventory.keys():
		var item: Dictionary = ContentDB.item(str(item_id))
		entries.append({
			"id": "item:%s" % item_id,
			"text": "%s x%d" % [item["name"], int(GameState.inventory[item_id])],
		})
	if entries.is_empty():
		view.set_caption("The pouch is empty.")
		await _wait(0.4)
		return false
	view.show_choices(entries, "back")
	var choice := await _wait_action()
	view.hide_choices()
	if not choice.begins_with("item:"):
		return false
	var item_id := choice.trim_prefix("item:")
	var target := await _choose_ally()
	if target.is_empty():
		return false
	if not GameState.take_item(item_id):
		return false
	var item := ContentDB.item(item_id)
	var amount := int(item.get("amount", 0))
	if str(item.get("kind", "")) == "heal_mp":
		target["mp"] = mini(int(target["max_mp"]), int(target["mp"]) + amount)
		view.react_hit(str(target["id"]), [{"text": "+%d" % amount, "color": SpriteCatalog.MP}], _ratio(target, "hp"), _ratio(target, "mp"))
	else:
		target["hp"] = mini(int(target["max_hp"]), int(target["hp"]) + amount)
		view.react_hit(str(target["id"]), [{"text": "+%d" % amount, "color": Color("3dba6a")}], _ratio(target, "hp"), _ratio(target, "mp"))
	Sfx.play("heal")
	await _wait(0.35)
	return true


func _choose_skill(user: Dictionary) -> String:
	var entries: Array = []
	var cls: Dictionary = ContentDB.class_def(str(user["class_id"]))
	for skill_id in cls["skills"]:
		var skill: Dictionary = ContentDB.skill(str(skill_id))
		var rank := int(user["skill_ranks"].get(str(skill_id), 1))
		var cost := Formulas.mp_cost(int(skill.get("mp_base", 0)), rank)
		entries.append({
			"id": "skill:%s" % skill_id,
			"text": "%s  %d EN" % [skill["name"], cost],
			"disabled": int(user["mp"]) < cost,
		})
	view.show_choices(entries, "back")
	var choice := await _wait_action()
	view.hide_choices()
	if choice.begins_with("skill:"):
		return choice.trim_prefix("skill:")
	return ""


func _choose_enemy(user: Dictionary, allow_back: bool) -> Dictionary:
	var valid: Array = []
	var front := false
	for unit in units:
		if str(unit["side"]) == "monster" and int(unit["hp"]) > 0 and not bool(unit["back_row"]):
			front = true
	for unit in units:
		if str(unit["side"]) != "monster" or int(unit["hp"]) <= 0:
			continue
		if bool(unit["back_row"]) and front and not allow_back:
			continue
		valid.append(unit)
	if valid.is_empty():
		return {}
	if valid.size() == 1:
		return valid[0]
	var ids: Array = []
	for unit in valid:
		ids.append(str(unit["id"]))
	view.set_target_mode(ids, "Choose a foe")
	view.set_actions([{"id": "back", "label": "Back", "icon": ""}])
	var picked := await _wait_target()
	view.clear_target_mode()
	if picked == "":
		return {}
	return _unit(picked)


func _choose_ally() -> Dictionary:
	var ids: Array = []
	for unit in units:
		if str(unit["side"]) == "player":
			ids.append(str(unit["id"]))
	view.set_target_mode(ids, "Choose an ally")
	view.set_actions([{"id": "back", "label": "Back", "icon": ""}])
	var picked := await _wait_target()
	view.clear_target_mode()
	if picked == "":
		return {}
	return _unit(picked)


func _run() -> void:
	view.set_caption("The party runs.")
	view.set_actions([])
	await view.play_chicken()
	var living: Array = []
	for unit in units:
		if str(unit["side"]) == "player" and int(unit["hp"]) > 0:
			living.append(unit)
	var results: Array = await _party_roll(living, "body", true)
	for i in results.size():
		if bool(results[i]):
			continue
		var monster := _random_monster()
		if monster.is_empty():
			continue
		view.set_caption("%s strikes as you flee." % monster["name"])
		await _monster_swing(monster, living[i])
	view.close_dice()


func _monster_swing(monster: Dictionary, target: Dictionary) -> void:
	view.monster_pose(str(monster["id"]), "windup")
	await _wait(Timing.MONSTER_WINDUP)
	view.monster_pose(str(monster["id"]), "attack")
	await _wait(Timing.monster_time_to_damage(int(monster.get("damage_frame", 2))))
	await _strike(monster, target, float(monster["attack"]), 0.25, true, 0)
	await _wait(Timing.HP_TWEEN)
	view.monster_pose(str(monster["id"]), "idle")


func _party_roll(group: Array, stat_name: String, flee: bool) -> Array:
	view.open_dice(group.size(), stat_name)
	var results: Array = []
	for i in group.size():
		var unit: Dictionary = group[i]
		var stat := int(unit[stat_name])
		view.set_die(i, "%d-20" % Formulas.party_die_target(stat), "", -1)
		Sfx.play("dice")
		await _wait(Timing.PARTY_DIE_SPIN_FLEE if flee else Timing.PARTY_DIE_SPIN)
		var roll := rng.randi_range(1, 20)
		var ok := Formulas.party_die_succeeds(roll, stat, 0)
		view.set_die(i, "OK!" if ok else "MISS", str(roll), 1 if ok else 0)
		Sfx.play("good" if ok else "bad")
		await _wait(Timing.PARTY_DIE_AFTER)
		await _wait(Timing.PARTY_DIE_GAP)
		results.append(ok)
	await _wait(Timing.PARTY_ROLL_END_HOLD)
	return results


func _grant_victory() -> void:
	var last_death := 0
	for unit in units:
		if str(unit["side"]) == "monster":
			last_death = maxi(last_death, int(unit.get("death_ms", 0)))
	var remain := Timing.VICTORY_DELAY - float(last_death) / 1000.0
	if remain > 0.0:
		await _wait(remain)
	var entries: Array = []
	var gold_sum := 0
	for unit in units:
		if str(unit["side"]) != "monster":
			continue
		entries.append({"level": int(unit["level"]), "boss": bool(unit.get("boss", false)), "type_id": str(unit["kind"])})
		var gap := Formulas.level_gap(GameState.party_average(), int(unit["level"]))
		var gold := Formulas.gold_per_kill(int(unit["level"]), gap, bool(unit.get("elite", false)) or bool(unit.get("boss", false)))
		if rng.randf() < 0.2:
			gold += Formulas.bonus_gold_amount(int(unit["level"]), rng.randf())
		gold_sum += gold
	var xp := Formulas.battle_xp(entries, GameState.party_average())
	var gold_total := Formulas.battle_gold(gold_sum, entries.size())
	var living: Array = []
	for unit in units:
		if str(unit["side"]) == "player" and int(unit["hp"]) > 0:
			living.append(unit)
	if living.is_empty():
		living = units
	var share := 0 if living.is_empty() else int(xp / living.size())
	var rem := 0 if living.is_empty() else xp % living.size()
	var notes: PackedStringArray = []
	var leveled := false
	for i in living.size():
		if str(living[i]["side"]) != "player":
			continue
		var member: Dictionary = GameState.party[int(living[i]["member_index"])]
		var gain := share + (1 if i < rem else 0)
		if GameState.apply_xp(member, gain):
			leveled = true
			notes.append("%s reaches level %d." % [member_name(member), int(member["level"])])
	GameState.gold += gold_total
	var quest_note := ""
	if GameState.place_id == "millpond" and not GameState.quests_done.has("reed_trouble"):
		var quest: Dictionary = ContentDB.quest("reed_trouble")
		GameState.quests_done.append("reed_trouble")
		GameState.gold += int(quest.get("gold", 0))
		for unit in living:
			if str(unit.get("side", "")) == "player":
				GameState.apply_xp(GameState.party[int(unit["member_index"])], int(quest.get("xp", 0)) / maxi(1, living.size()))
		quest_note = "\nReed Trouble is settled. +%d gold." % int(quest.get("gold", 0))
	if leveled:
		Sfx.play("level")
	else:
		Sfx.play("victory")
	var body := "XP %d, split across the table.\nGold +%d. Purse %d.%s\n%s" % [
		xp, gold_total, GameState.gold, quest_note, "\n".join(notes)
	]
	await view.show_end("Victory", body, 0.15, 0.95)


func _grant_defeat() -> void:
	var cost := 0
	for member in GameState.party:
		cost += Formulas.resurrect_cost(int(member["level"]))
	if GameState.gold >= cost:
		GameState.gold -= cost
	for member in GameState.party:
		var stats := GameState.combat_stats(member)
		member["hp"] = maxi(1, int(stats["max_hp"] * 0.25))
		member["mp"] = maxi(1, int(stats["max_mp"] * 0.25))


func _write_party() -> void:
	for unit in units:
		if str(unit["side"]) != "player":
			continue
		var member: Dictionary = GameState.party[int(unit["member_index"])]
		member["hp"] = maxi(0, int(unit["hp"]))
		member["mp"] = maxi(0, int(unit["mp"]))


func _wait_action() -> String:
	_action = ""
	while _action == "":
		await get_tree().process_frame
	var chosen := _action
	_action = ""
	return chosen


func _wait_target() -> String:
	_target = ""
	_action = ""
	while _target == "" and _action != "back":
		await get_tree().process_frame
	if _action == "back":
		_action = ""
		return ""
	var chosen := _target
	_target = ""
	return chosen


func _gap(unit: Dictionary) -> void:
	await _wait(Timing.PLAYER_NEXT_TURN if str(unit["side"]) == "player" else Timing.MONSTER_NEXT_TURN)


func _wait(seconds: float) -> void:
	if seconds <= 0.0:
		return
	await get_tree().create_timer(seconds).timeout


func _unit(id: String) -> Dictionary:
	for unit in units:
		if str(unit["id"]) == id:
			return unit
	return {}


func _has(unit: Dictionary, cond_id: String) -> bool:
	for cond in unit.get("conditions", []):
		if str(cond["id"]) == cond_id:
			return true
	return false


func _side_alive(side: String) -> bool:
	for unit in units:
		if str(unit["side"]) == side and int(unit["hp"]) > 0:
			return true
	return false


func _pick_player() -> Dictionary:
	var bag: Array = []
	var total := 0
	for unit in units:
		if str(unit["side"]) != "player" or int(unit["hp"]) <= 0:
			continue
		var weight := Formulas.aggro_weight(int(unit["body"]), int(unit.get("threat", 0)), bool(unit.get("covering", false)))
		if weight > 0:
			bag.append({"unit": unit, "weight": weight})
			total += weight
	if bag.is_empty():
		for unit in units:
			if str(unit["side"]) == "player" and int(unit["hp"]) > 0:
				return unit
		return {}
	var roll := rng.randi_range(1, total)
	var cursor := 0
	for entry in bag:
		cursor += int(entry["weight"])
		if roll <= cursor:
			return entry["unit"]
	return bag[0]["unit"]


func _random_monster() -> Dictionary:
	var living: Array = []
	for unit in units:
		if str(unit["side"]) == "monster" and int(unit["hp"]) > 0 and not _has(unit, "stun"):
			living.append(unit)
	if living.is_empty():
		return {}
	return living[rng.randi() % living.size()]


func _random_enemies(count: int, allow_back: bool) -> Array:
	var pool: Array = []
	for unit in units:
		if str(unit["side"]) == "monster" and int(unit["hp"]) > 0:
			if bool(unit["back_row"]) and not allow_back:
				continue
			pool.append(unit)
	pool.shuffle()
	return pool.slice(0, mini(count, pool.size()))


func _neighbors(target: Dictionary) -> Array:
	var row: Array = []
	for unit in units:
		if str(unit["side"]) == "monster" and int(unit["hp"]) > 0:
			row.append(unit)
	row.sort_custom(func(a, b): return str(a["id"]) < str(b["id"]))
	var index := -1
	for i in row.size():
		if str(row[i]["id"]) == str(target["id"]):
			index = i
	var found: Array = []
	if index > 0:
		found.append(row[index - 1])
	if index >= 0 and index + 1 < row.size():
		found.append(row[index + 1])
	return found


func _later(attacker: Dictionary, target: Dictionary) -> bool:
	var ai := -1
	var ti := -1
	for i in order.size():
		if str(order[i]["id"]) == str(attacker["id"]):
			ai = i
		if str(order[i]["id"]) == str(target["id"]):
			ti = i
	return ti > ai


func _ratio(unit: Dictionary, key: String) -> float:
	var max_key := "max_%s" % key
	var denom := int(unit.get(max_key, 1))
	if denom <= 0:
		return 0.0
	return float(unit.get(key, 0)) / float(denom)


func _order_entries() -> Array:
	var entries: Array = []
	for unit in order:
		if int(unit["hp"]) <= 0:
			continue
		var entry := {"id": str(unit["id"]), "side": str(unit["side"])}
		if str(unit["side"]) == "player":
			entry["index"] = int(unit["member_index"])
		else:
			entry["kind"] = str(unit["kind"])
		entries.append(entry)
	return entries


func member_name(member: Dictionary) -> String:
	return ContentDB.persona(str(member["persona"]))["name"]
