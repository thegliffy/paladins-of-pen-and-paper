extends Node
class_name BattleFlow
## Turn loop, dice, and the timing table. The view is a SessionScreen.

var view
var rng := RandomNumberGenerator.new()
var units: Array = []
var order: Array = []
var turn_index := 0
var _action := ""
var _target := ""
var _listening := false
var hurry := false


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
			"crit_bonus": float(stats.get("crit", 0.0)),
			"gear_threat": int(stats.get("gear_threat", 0)),
			"threat": 0,
			"covering": false,
			"conditions": [],
			"skill_ranks": member["skill_ranks"].duplicate(true),
			"class_id": str(member["class_id"]),
			"cooldowns": {},
			"buildup": {},
			"ward": 0,
			"ward_turns": 0,
			"passives": _passive_effects(str(member["class_id"])),
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
			"size": Formulas.monster_size_tag(monster),
			"elite": bool(monster.get("elite", false)),
			"power": int(monster.get("power", 1)),
		})


func _roll_initiative() -> void:
	var rolls := {}
	for unit in units:
		if int(unit["hp"]) <= 0:
			continue
		rolls[str(unit["id"])] = _initiative_roll(unit)
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
			rolls[id] = _initiative_roll(unit)
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
	view.set_caption("")
	if str(unit["side"]) != "player":
		view.clear_actor_bar()
	_refresh_threat_debug()
	_tick_ward(unit)
	if str(unit["side"]) == "player":
		_ensure_resources(unit)
		var cooling: Dictionary = unit["cooldowns"]
		Formulas.tick_cooldowns(cooling)
		_apply_regen(unit)
		unit["covering"] = false
		unit["threat"] = 0
		view.set_cover(int(unit["member_index"]), false)
		view.raise_member(int(unit["member_index"]), true)
	if _has(unit, "stun"):
		if str(unit["side"]) == "player":
			view.clear_actor_bar()
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
	var armed := ""
	var picking := false
	while true:
		_present_turn(unit, armed, picking)
		var event: Dictionary = await _wait_turn_input()
		if str(event.get("kind", "")) == "target":
			var target_id := str(event.get("id", ""))
			if picking and _target_ok(armed, target_id):
				if await _resolve_player_action(unit, armed, target_id):
					return ""
				armed = ""
				picking = false
				continue
			if not picking and _target_ok("attack", target_id):
				if await _resolve_player_action(unit, "attack", target_id):
					return ""
			continue
		var action := str(event.get("id", ""))
		if action == "dismiss":
			armed = ""
			picking = false
			continue
		if action == "run":
			view.hide_inspect()
			view.clear_target_mode()
			await _run()
			return "flee"
		var step: Dictionary = Formulas.turn_tap(
			{"armed": armed, "picking": picking},
			action,
			_action_can_cast(unit, action),
			_action_needs_pick(action)
		)
		if bool(step.get("cast", false)):
			if await _resolve_player_action(unit, action, ""):
				return ""
			armed = ""
			picking = false
			continue
		armed = str(step.get("armed", ""))
		picking = bool(step.get("picking", false))
	return ""


func _present_turn(unit: Dictionary, armed: String, picking: bool) -> void:
	_show_actor_bar(unit, armed, false)
	if armed == "":
		view.hide_inspect()
		view.clear_target_mode()
		return
	var card := _inspect_card(unit, armed)
	if picking:
		card["hint"] = "Pick a target"
		view.set_target_mode(_ids_for(armed), "")
	else:
		view.clear_target_mode()
	view.show_inspect(card, armed)


func _resolve_player_action(unit: Dictionary, action: String, target_id: String) -> bool:
	view.hide_inspect()
	view.clear_target_mode()
	view.set_actions_enabled(false)
	if action == "attack":
		var foe := _unit(target_id)
		if foe.is_empty() or int(foe.get("hp", 0)) <= 0:
			return false
		await _player_basic(unit, foe, true)
		return true
	if action.begins_with("skill:"):
		return await _use_skill(unit, action.trim_prefix("skill:"), target_id)
	if action == "item":
		return await _choose_item(unit)
	if action == "cover":
		await _cover(unit)
		return true
	return false


func _action_needs_pick(action_id: String) -> bool:
	if not action_id.begins_with("skill:"):
		return false
	var skill: Dictionary = ContentDB.skill(action_id.trim_prefix("skill:"))
	return Formulas.needs_chosen_target(str(skill.get("target", "")), Formulas.is_passive(skill))


func _action_can_cast(unit: Dictionary, action_id: String) -> bool:
	if action_id == "attack" or action_id == "cover" or action_id == "item":
		return true
	if not action_id.begins_with("skill:"):
		return false
	var card: Dictionary = _inspect_card(unit, action_id)
	return bool(card.get("can_cast", false))


func _inspect_card(unit: Dictionary, action_id: String) -> Dictionary:
	_ensure_resources(unit)
	if action_id.begins_with("skill:"):
		var skill_id := action_id.trim_prefix("skill:")
		var skill: Dictionary = ContentDB.skill(skill_id)
		var ranks: Dictionary = unit.get("skill_ranks", {})
		var cds: Dictionary = unit.get("cooldowns", {})
		var stacks: Dictionary = unit.get("buildup", {})
		return Formulas.skill_inspect(skill, int(ranks.get(skill_id, 0)), int(unit.get("hp", 0)), int(unit.get("mp", 0)), cds, stacks)
	return Formulas.basic_inspect(ContentDB.action_def(action_id))


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
	var attacker_passives: Array = attacker.get("passives", [])
	raw *= Formulas.outgoing_damage_multiplier(int(attacker.get("hp", 0)), int(attacker.get("max_hp", 1)), attacker_passives)
	raw += float(Formulas.on_hit_bonus(attacker_passives))
	var crit := false
	if can_crit:
		var chance := Formulas.crit_chance(int(attacker["senses"]), Formulas.crit_flat_bonus(attacker_passives) + float(attacker.get("crit_bonus", 0.0)))
		crit = Formulas.is_crit(chance, rng.randi_range(1, 100))
		if crit:
			raw *= 2.0
	var dealt := Formulas.damage_taken(raw, _defender_dr(defender))
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
	else:
		await _reflect(defender, attacker)


func _use_skill(user: Dictionary, skill_id: String, preset_id: String = "") -> bool:
	var skill: Dictionary = ContentDB.skill(skill_id)
	var rank := int(user.get("skill_ranks", {}).get(skill_id, 1))
	_ensure_resources(user)
	var cds: Dictionary = user["cooldowns"]
	var stacks: Dictionary = user["buildup"]
	if not Formulas.skill_usable(skill, rank, int(user["hp"]), int(user["mp"]), cds, stacks):
		view.set_caption("Can't use that yet.")
		return false
	var preset: Dictionary = {}
	if preset_id != "":
		preset = _unit(preset_id)
		if preset.is_empty() or int(preset.get("hp", 0)) <= 0:
			return false
		if not _ids_for("skill:%s" % skill_id).has(preset_id):
			return false
	var before := {
		"hp": int(user["hp"]),
		"mp": int(user["mp"]),
		"cooldowns": (user["cooldowns"] as Dictionary).duplicate(true),
		"buildup": (user["buildup"] as Dictionary).duplicate(true),
	}
	var paid: Dictionary = Formulas.apply_skill_payment(skill, rank, int(user["hp"]), int(user["mp"]), cds, stacks)
	user["hp"] = int(paid["hp"])
	user["mp"] = int(paid["mp"])
	user["cooldowns"] = paid["cooldowns"]
	user["buildup"] = paid["buildup"]
	view.sync_unit(user)
	if Formulas.skill_resource(skill) == "hp":
		var spent := int(before["hp"]) - int(user["hp"])
		view.react_hit(str(user["id"]), [{"text": "-%d" % spent, "color": SpriteCatalog.HP}], _ratio(user, "hp"), _ratio(user, "mp"))
	var cancelled := false
	var kind := str(skill.get("kind", "spell"))
	var target_mode := str(skill.get("target", "enemy"))
	if not preset.is_empty():
		await _resolve_skill(user, skill, [preset], rank)
	elif target_mode == "self":
		await _resolve_skill(user, skill, [user], rank)
	elif kind == "heal" or kind == "cleanse" or target_mode == "ally":
		var ally := await _choose_ally(user, "skill:%s" % skill_id)
		if ally.is_empty():
			cancelled = true
		else:
			await _resolve_skill(user, skill, [ally], rank)
	elif target_mode == "enemies":
		var crowd: Array = _random_enemies(int(skill.get("max_targets", 1)), bool(skill.get("can_target_back_row", false)))
		if crowd.is_empty():
			cancelled = true
		else:
			await _resolve_skill(user, skill, crowd, rank)
	else:
		var picked := await _choose_enemy(user, bool(skill.get("can_target_back_row", false)), "skill:%s" % skill_id)
		if picked.is_empty():
			cancelled = true
		else:
			await _resolve_skill(user, skill, [picked], rank)
	if cancelled:
		user["hp"] = int(before["hp"])
		user["mp"] = int(before["mp"])
		user["cooldowns"] = before["cooldowns"]
		user["buildup"] = before["buildup"]
		view.sync_unit(user)
		return false
	var track := str(skill.get("buildup_id", ""))
	if track != "":
		view.set_caption("%s · %d %s" % [skill["name"], int(user["buildup"].get(track, 0)), str(skill.get("buildup_label", track))])
	_refresh_threat_debug()
	return true


func _resolve_skill(user: Dictionary, skill: Dictionary, targets: Array, rank: int) -> void:
	var kind := str(skill.get("kind", "spell"))
	if kind == "heal":
		await _heal(user, skill, targets[0], rank)
		_grant_threat(user, skill)
		return
	if kind == "cleanse":
		await _cleanse(user, skill, targets[0], rank)
		return
	if kind == "buff":
		await _buff(user, skill, targets[0], rank)
		return
	await _cast(user, skill, targets)


func _grant_threat(user: Dictionary, skill: Dictionary) -> void:
	var bonus := int(skill.get("threat", 0))
	if bonus > 0:
		user["threat"] = int(user.get("threat", 0)) + bonus


func _buff(user: Dictionary, skill: Dictionary, target: Dictionary, rank: int) -> void:
	view.set_caption("%s uses %s" % [user["name"], skill["name"]])
	var ward := int(skill.get("grant_dr", 0))
	if ward > 0:
		target["ward"] = ward
		target["ward_turns"] = int(skill.get("ward_turns", 2))
		view.react_hit(str(target["id"]), [{"text": "WARD", "color": SpriteCatalog.SAFE}], _ratio(target, "hp"), _ratio(target, "mp"))
	if bool(skill.get("grant_cover", false)) and target.has("member_index"):
		target["covering"] = true
		view.set_cover(int(target["member_index"]), true)
	_grant_threat(user, skill)
	if int(skill.get("heal", 0)) > 0:
		await _heal(user, skill, target, rank)
	else:
		Sfx.play("good")
		await _wait(0.35)
	view.sync_unit(target)


func _cleanse(user: Dictionary, skill: Dictionary, target: Dictionary, rank: int) -> void:
	target["conditions"] = []
	view.sync_unit(target)
	view.set_caption("%s clears %s" % [user["name"], target["name"]])
	if int(skill.get("heal", 0)) > 0:
		await _heal(user, skill, target, rank)
	else:
		await _wait(0.3)


func _tick_ward(unit: Dictionary) -> void:
	var turns := int(unit.get("ward_turns", 0))
	if turns <= 0:
		return
	unit["ward_turns"] = turns - 1
	if int(unit["ward_turns"]) <= 0:
		unit["ward"] = 0


func _ensure_resources(user: Dictionary) -> void:
	if typeof(user.get("cooldowns", null)) != TYPE_DICTIONARY:
		user["cooldowns"] = {}
	if typeof(user.get("buildup", null)) != TYPE_DICTIONARY:
		user["buildup"] = {}


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
			var weapon_power := float(user["attack"]) * float(skill.get("attack_mult", 1.0))
			await _strike(user, target, weapon_power, float(skill.get("variance", 0.25)), true, bonus)
			var weapon_splash := float(skill.get("splash", 0.0))
			if weapon_splash > 0.0:
				for neighbor in _neighbors(target):
					await _wait(Timing.MULTI_TARGET_GAP)
					await _strike(user, neighbor, weapon_power * weapon_splash, float(skill.get("variance", 0.25)), false, 0)
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
	_land_heal(user, skill, target, rank)
	var self_heal := int(skill.get("self_heal", 0))
	if self_heal > 0 and str(target["id"]) != str(user["id"]):
		_land_flat_heal(user, self_heal)
	await _wait(0.4)


func _land_heal(user: Dictionary, skill: Dictionary, target: Dictionary, rank: int) -> void:
	var healed := Formulas.heal_amount(skill, int(user["mind"]), rank)
	var amount := Formulas.boost_heal(healed, user.get("passives", []))
	_land_flat_heal(target, amount)
	Sfx.play("heal")


func _land_flat_heal(target: Dictionary, amount: int) -> void:
	## Writes HP and refreshes the chair before this function returns, so the next actor has not moved yet.
	target["hp"] = mini(int(target["max_hp"]), int(target["hp"]) + amount)
	view.sync_unit(target)
	view.react_hit(str(target["id"]), [{"text": "+%d" % amount, "color": Color("3dba6a")}], _ratio(target, "hp"), _ratio(target, "mp"))


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
	view.set_caption("%s ducks, but foes can still reach them." % unit["name"])
	_refresh_threat_debug()
	Sfx.play("tap")
	await _wait(0.35)


func _keep_drop(item_id: String, found: PackedStringArray) -> void:
	if item_id == "" or not ContentDB.items.has(item_id):
		return
	if GameState.give_item(item_id, 1):
		found.append(str(ContentDB.item(item_id)["name"]))
	else:
		found.append("the bag is full")


func _choose_item(user: Dictionary) -> bool:
	var entries: Array = []
	for item_id in GameState.inventory.keys():
		var item: Dictionary = ContentDB.item(str(item_id))
		if str(item.get("slot", "")) != "usable":
			continue
		entries.append({
			"id": "item:%s" % item_id,
			"text": "%s x%d" % [item["name"], int(GameState.inventory[item_id])],
		})
	if entries.is_empty():
		view.set_caption("No usables in the pouch.")
		await _wait(0.4)
		return false
	view.show_choices(entries, "back")
	var choice := await _wait_action()
	view.hide_choices()
	if not choice.begins_with("item:"):
		return false
	var item_id := choice.trim_prefix("item:")
	var target := await _choose_ally(user, "item")
	if target.is_empty():
		return false
	if not GameState.take_item(item_id):
		return false
	var item := ContentDB.item(item_id)
	var amount := int(item.get("amount", 0))
	var kind := str(item.get("kind", ""))
	if kind == "heal_mp":
		target["mp"] = mini(int(target["max_mp"]), int(target["mp"]) + amount)
		view.sync_unit(target)
		view.react_hit(str(target["id"]), [{"text": "+%d" % amount, "color": SpriteCatalog.MP}], _ratio(target, "hp"), _ratio(target, "mp"))
	elif kind == "heal_both":
		_land_flat_heal(target, amount)
		var mp_amount := int(item.get("mp_amount", 0))
		target["mp"] = mini(int(target["max_mp"]), int(target["mp"]) + mp_amount)
		view.sync_unit(target)
		view.react_hit(str(target["id"]), [{"text": "+%d" % mp_amount, "color": SpriteCatalog.MP}], _ratio(target, "hp"), _ratio(target, "mp"))
	else:
		_land_flat_heal(target, amount)
	Sfx.play("heal")
	await _wait(0.35)
	return true


func _choose_skill(user: Dictionary) -> String:
	var entries: Array = []
	var cls: Dictionary = ContentDB.class_def(str(user["class_id"]))
	_ensure_resources(user)
	var cds: Dictionary = user["cooldowns"]
	var stacks: Dictionary = user["buildup"]
	for skill_id in cls["skills"]:
		var skill: Dictionary = ContentDB.skill(str(skill_id))
		if Formulas.is_passive(skill):
			continue
		var rank := int(user["skill_ranks"].get(str(skill_id), 1))
		var usable := Formulas.skill_usable(skill, rank, int(user["hp"]), int(user["mp"]), cds, stacks)
		entries.append({
			"id": "skill:%s" % skill_id,
			"text": Formulas.skill_cost_label(skill, rank, cds, stacks),
			"disabled": not usable,
		})
	view.show_choices(entries, "back")
	var choice := await _wait_action()
	view.hide_choices()
	if choice.begins_with("skill:"):
		return choice.trim_prefix("skill:")
	return ""


func _show_actor_bar(unit: Dictionary, selected_id: String, cancel_selected: bool) -> void:
	var cls: Dictionary = ContentDB.class_def(str(unit.get("class_id", "")))
	var skills: Array = []
	for skill_id in cls.get("skills", []):
		skills.append(ContentDB.skill(str(skill_id)))
	_ensure_resources(unit)
	var ranks: Dictionary = unit.get("skill_ranks", {})
	var cds: Dictionary = unit.get("cooldowns", {})
	var stacks: Dictionary = unit.get("buildup", {})
	view.show_actor_bar(
		str(cls.get("name", unit.get("name", ""))).to_upper(),
		skills,
		ranks,
		int(unit.get("hp", 0)),
		int(unit.get("mp", 0)),
		cds,
		stacks,
		selected_id,
		cancel_selected
	)


func _enemy_ids(allow_back: bool) -> Array:
	var front := false
	for unit in units:
		if str(unit["side"]) == "monster" and int(unit["hp"]) > 0 and not bool(unit["back_row"]):
			front = true
	var ids: Array = []
	for unit in units:
		if str(unit["side"]) != "monster" or int(unit["hp"]) <= 0:
			continue
		if bool(unit["back_row"]) and front and not allow_back:
			continue
		ids.append(str(unit["id"]))
	return ids


func _ally_ids() -> Array:
	var ids: Array = []
	for unit in units:
		if str(unit["side"]) == "player" and int(unit["hp"]) > 0:
			ids.append(str(unit["id"]))
	return ids


func _ids_for(action_id: String) -> Array:
	if action_id == "attack":
		return _enemy_ids(false)
	if not action_id.begins_with("skill:"):
		return []
	var skill: Dictionary = ContentDB.skill(action_id.trim_prefix("skill:"))
	var mode := str(skill.get("target", "enemy"))
	if mode == "ally":
		return _ally_ids()
	if mode == "enemy":
		return _enemy_ids(bool(skill.get("can_target_back_row", false)))
	return []


func _target_ok(action_id: String, target_id: String) -> bool:
	return _ids_for(action_id).has(target_id)


func _choose_enemy(user: Dictionary, allow_back: bool, selected_id: String) -> Dictionary:
	var ids := _enemy_ids(allow_back)
	if ids.is_empty():
		return {}
	if ids.size() == 1:
		return _unit(str(ids[0]))
	_show_actor_bar(user, selected_id, true)
	view.set_target_mode(ids, "")
	var card := _inspect_card(user, selected_id)
	card["hint"] = "Pick a target"
	view.show_inspect(card, selected_id)
	var picked := await _wait_target()
	view.clear_target_mode()
	view.hide_inspect()
	if picked == "":
		return {}
	return _unit(picked)


func _choose_ally(user: Dictionary, selected_id: String) -> Dictionary:
	var ids: Array = []
	for unit in units:
		if str(unit["side"]) == "player":
			ids.append(str(unit["id"]))
	_show_actor_bar(user, selected_id, true)
	view.set_target_mode(ids, "")
	var card := _inspect_card(user, selected_id)
	card["hint"] = "Pick a target"
	view.show_inspect(card, selected_id)
	var picked := await _wait_target()
	view.clear_target_mode()
	view.hide_inspect()
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
	var found: PackedStringArray = []
	for unit in units:
		if str(unit.get("side", "")) != "monster":
			continue
		var monster: Dictionary = ContentDB.monster(str(unit.get("kind", "")))
		var categories: Array = Formulas.loot_categories(int(unit["level"]), bool(unit.get("boss", false)), rng.randf(), rng.randf(), rng.randf())
		for category in categories:
			var drop_id := Formulas.pick_loot(ContentDB.item_rows(), str(category), int(unit["level"]), rng.randi())
			_keep_drop(drop_id, found)
		_keep_drop(Formulas.unique_drop(str(monster.get("unique", "")), bool(unit.get("boss", false)), rng.randf()), found)
	var killed: Array = []
	for unit in units:
		if str(unit.get("side", "")) == "monster":
			killed.append(str(unit.get("kind", "")))
	var quest_lines := GameState.settle_quests(true, killed)
	var quest_note := ""
	if not quest_lines.is_empty():
		quest_note = "\n" + "\n".join(quest_lines)
	if leveled:
		Sfx.play("level")
	else:
		Sfx.play("victory")
	var loot_note := ""
	if not found.is_empty():
		loot_note = "\nFound %s." % ", ".join(found)
	var body := "XP %d, split across the table.\nGold +%d. Purse %d.%s%s\n%s" % [
		xp, gold_total, GameState.gold, quest_note, loot_note, "\n".join(notes)
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


func _wait_turn_input() -> Dictionary:
	_action = ""
	_target = ""
	while _action == "" and _target == "":
		await get_tree().process_frame
	if _target != "":
		var target_id := _target
		_target = ""
		_action = ""
		return {"kind": "target", "id": target_id}
	var chosen := _action
	_action = ""
	return {"kind": "action", "id": chosen}


func _wait_target() -> String:
	_target = ""
	_action = ""
	while _target == "" and _action != "back" and _action != "dismiss":
		await get_tree().process_frame
	if _action == "back" or _action == "dismiss":
		_action = ""
		_target = ""
		return ""
	var chosen := _target
	_target = ""
	return chosen


func _gap(unit: Dictionary) -> void:
	await _wait(Timing.PLAYER_NEXT_TURN if str(unit["side"]) == "player" else Timing.MONSTER_NEXT_TURN)


func _wait(seconds: float) -> void:
	if hurry or seconds <= 0.0:
		await get_tree().process_frame
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


func _passive_effects(class_id: String) -> Array:
	var effects: Array = []
	var cls: Dictionary = ContentDB.class_def(class_id)
	for skill_id in cls["skills"]:
		var skill: Dictionary = ContentDB.skill(str(skill_id))
		if not Formulas.is_passive(skill):
			continue
		var listed: Array = skill.get("effects", [])
		for effect in listed:
			effects.append(effect)
	return effects


func _initiative_roll(unit: Dictionary) -> int:
	var effects: Array = unit.get("passives", [])
	return int(unit["senses"]) + int(unit.get("initiative", 0)) + Formulas.initiative_bonus(effects) + rng.randi_range(1, 12)


func _apply_regen(unit: Dictionary) -> void:
	var effects: Array = unit.get("passives", [])
	var mp_gain := Formulas.mp_regen_amount(int(unit.get("max_mp", 0)), effects)
	if mp_gain > 0:
		var room := int(unit["max_mp"]) - int(unit["mp"])
		var gained := mini(mp_gain, maxi(0, room))
		if gained > 0:
			unit["mp"] = int(unit["mp"]) + gained
			view.react_hit(str(unit["id"]), [{"text": "+%d" % gained, "color": SpriteCatalog.MP}], _ratio(unit, "hp"), _ratio(unit, "mp"))
			if view.has_method("play_regen_fx"):
				view.play_regen_fx(str(unit["id"]))
	var hp_gain := Formulas.hp_regen_amount(int(unit.get("max_hp", 0)), effects)
	if hp_gain > 0:
		var room_hp := int(unit["max_hp"]) - int(unit["hp"])
		var gained_hp := mini(hp_gain, maxi(0, room_hp))
		if gained_hp > 0:
			unit["hp"] = int(unit["hp"]) + gained_hp
			view.react_hit(str(unit["id"]), [{"text": "+%d" % gained_hp, "color": Color("3dba6a")}], _ratio(unit, "hp"), _ratio(unit, "mp"))
	view.sync_unit(unit)


func _defender_dr(defender: Dictionary) -> int:
	var dr := int(defender.get("dr", 0)) + int(defender.get("ward", 0))
	if str(defender.get("side", "")) == "player":
		dr += _living_party_dr()
	return dr


func _living_party_dr() -> int:
	var extra := 0
	for unit in units:
		if str(unit.get("side", "")) != "player" or int(unit.get("hp", 0)) <= 0:
			continue
		var effects: Array = unit.get("passives", [])
		extra += Formulas.party_dr_aura(effects)
	return extra


func _reflect(defender: Dictionary, attacker: Dictionary) -> void:
	if str(attacker.get("id", "")) == str(defender.get("id", "")):
		return
	var effects: Array = defender.get("passives", [])
	var reflect := Formulas.on_damaged_reflect(effects)
	if reflect <= 0 or int(attacker.get("hp", 0)) <= 0:
		return
	attacker["hp"] = maxi(0, int(attacker["hp"]) - reflect)
	view.react_hit(str(attacker["id"]), [{"text": "-%d" % reflect, "color": SpriteCatalog.HP}], _ratio(attacker, "hp"), _ratio(attacker, "mp"))
	if int(attacker["hp"]) <= 0:
		await view.death_blink(str(attacker["id"]))


func _unit_threat(unit: Dictionary) -> int:
	var rules: Dictionary = ContentDB.threat_rules()
	var cls: Dictionary = ContentDB.class_def(str(unit.get("class_id", "paladin")))
	var effects: Array = unit.get("passives", [])
	var cover := 1.0
	if bool(unit.get("covering", false)):
		cover = float(rules.get("cover_mult", 1.0))
	var flat := int(unit.get("threat", 0)) + int(unit.get("gear_threat", 0)) + Formulas.threat_flat(effects)
	return Formulas.member_threat(
		int(cls.get("base_threat", 1)),
		int(unit.get("body", 0)),
		int(unit.get("dr", 0)),
		flat,
		Formulas.threat_multiplier(effects),
		cover,
		float(rules.get("body_per", 0.0)),
		float(rules.get("armor_per", 0.0))
	)


func _refresh_threat_debug() -> void:
	if not ContentDB.threat_debug():
		view.set_threat_debug([])
		return
	var rows: Array = []
	var total := 0
	var pending: Array = []
	for unit in units:
		if str(unit.get("side", "")) != "player":
			continue
		if int(unit.get("hp", 0)) <= 0:
			pending.append({"id": str(unit["id"]), "threat": 0})
			continue
		var threat := _unit_threat(unit)
		total += threat
		pending.append({"id": str(unit["id"]), "threat": threat})
	for row in pending:
		var threat := int(row["threat"])
		var text := ""
		if threat > 0 and total > 0:
			var pct := int(round(100.0 * float(threat) / float(total)))
			text = "%d%%" % pct
		rows.append({"id": str(row["id"]), "text": text})
	view.set_threat_debug(rows)


func _pick_player() -> Dictionary:
	var living: Array = []
	var weights: Array = []
	for unit in units:
		if str(unit["side"]) != "player" or int(unit["hp"]) <= 0:
			continue
		living.append(unit)
		weights.append(_unit_threat(unit))
	if living.is_empty():
		return {}
	var total := 0
	for weight in weights:
		total += int(weight)
	var idx := Formulas.raffle_index(weights, rng.randi_range(1, maxi(1, total)))
	if idx < 0 or idx >= living.size():
		return living[0]
	return living[idx]


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
