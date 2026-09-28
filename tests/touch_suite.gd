extends RefCounted
## Finger taps, with mouse emulation turned off.
## Run from the game with: godot --path . -- --touch-check


static func run(host: Node) -> int:
	Input.set_emulate_mouse_from_touch(false)
	Input.set_emulate_touch_from_mouse(false)
	var tree := host.get_tree()
	var failures: Array[String] = []
	await _title(host, tree, failures)
	await _creator(host, tree, failures)
	await _hub(host, tree, failures)
	await _map(host, tree, failures)
	await _combat(host, tree, failures)
	await _tap_attack(host, tree, failures)
	await _tap_skill(host, tree, failures)
	await _tap_cancel(host, tree, failures)
	await _tap_ally(host, tree, failures)
	await _builder(host, tree, failures)
	if failures.is_empty():
		print("TOUCH_CHECK_OK")
		return 0
	push_error("TOUCH_CHECK_FAIL %s" % ", ".join(failures))
	return 1


static func _title(host: Node, tree: SceneTree, failures: Array[String]) -> void:
	var title := TitleScreen.new()
	var started := {"ok": false}
	title.new_game.connect(func(): started["ok"] = true)
	await _mount(host, tree, title)
	var button := _find_button(title, "New game")
	if button == null:
		failures.append("title_button")
		title.queue_free()
		return
	await _tap(tree, button.get_global_rect().get_center())
	if not bool(started["ok"]):
		failures.append("title")
		push_error("Touch check: title New game did not fire")
	title.queue_free()
	await tree.process_frame


static func _creator(host: Node, tree: SceneTree, failures: Array[String]) -> void:
	var creator := CreatorScreen.new()
	var began := {"ok": false}
	creator.finished.connect(func(_members: Array): began["ok"] = true)
	await _mount(host, tree, creator)
	var button := _find_button(creator, "Begin")
	if button == null:
		failures.append("creator_button")
		creator.queue_free()
		return
	await _tap(tree, button.get_global_rect().get_center())
	if not bool(began["ok"]):
		failures.append("creator")
		push_error("Touch check: creator Begin did not fire")
	creator.queue_free()
	await tree.process_frame


static func _hub(host: Node, tree: SceneTree, failures: Array[String]) -> void:
	var session := SessionScreen.new()
	var action := {"id": ""}
	session.action_pressed.connect(func(id: String): action["id"] = id)
	await _mount(host, tree, session)
	session.show_hub()
	await tree.process_frame
	var button := _find_button(session, "Travel")
	if button == null:
		failures.append("hub_button")
		session.queue_free()
		return
	await _tap(tree, button.get_global_rect().get_center())
	if str(action["id"]) != "travel":
		failures.append("hub")
		push_error("Touch check: hub Travel did not fire")
	session.queue_free()
	await tree.process_frame


static func _map(host: Node, tree: SceneTree, failures: Array[String]) -> void:
	var map := MapScreen.new()
	await _mount(host, tree, map)
	var place_id := _visible_place(map)
	if place_id == "":
		failures.append("map_place")
		push_error("Touch check: no tappable place was on screen")
		map.queue_free()
		return
	var node := map.get_node("Clip/Content/Places/%s" % place_id) as Control
	var at := node.get_global_rect().get_center()
	await _tap(tree, at)
	if str(map._selected) != place_id:
		failures.append("map_select")
		push_error("Touch check: tap did not select %s" % place_id)
		map.queue_free()
		return
	var pawn_before: Vector2 = map._pawn.position
	await _tap(tree, at)
	await tree.create_timer(0.35).timeout
	if not map._traveling:
		failures.append("map_walk")
		push_error("Touch check: second tap did not start the walk")
	elif map._pawn.position.distance_to(pawn_before) < 1.0:
		failures.append("map_pawn")
		push_error("Touch check: pawn did not move")
	map.queue_free()
	await tree.process_frame


static func _combat(host: Node, tree: SceneTree, failures: Array[String]) -> void:
	var session := SessionScreen.new()
	var action := {"id": ""}
	session.action_pressed.connect(func(id: String): action["id"] = id)
	await _mount(host, tree, session)
	GameState.new_campaign([
		GameState.make_member("mason", "delver", "paladin", {"skin": 4, "head": 2, "hair": 1, "hair_color": 0, "outfit_color": 0}),
		GameState.make_member("nim", "glenfolk", "wizard", {"skin": 1, "head": 5, "hair": 3, "hair_color": 6, "outfit_color": 1}),
		GameState.make_member("pip", "hearthborn", "ranger", {"skin": 2, "head": 0, "hair": 6, "hair_color": 2, "outfit_color": 2}),
		GameState.make_member("sable", "hearthborn", "cleric", {"skin": 3, "head": 4, "hair": 2, "hair_color": 4, "outfit_color": 1}),
		GameState.make_member("holt", "glenfolk", "bard", {"skin": 0, "head": 6, "hair": 5, "hair_color": 5, "outfit_color": 2}),
	])
	session.stage_battle_preview()
	await tree.process_frame
	var button := _find_action(session, "attack")
	if button == null:
		failures.append("combat_button")
		session.queue_free()
		return
	await _tap(tree, button.get_global_rect().get_center())
	if str(action["id"]) != "attack":
		failures.append("combat")
		push_error("Touch check: combat Attack did not fire")
	session.queue_free()
	await tree.process_frame


static func _hero(persona: String, race: String, class_id: String) -> Dictionary:
	return GameState.make_member(persona, race, class_id, {
		"skin": 0, "head": 0, "hair": 0, "hair_color": 0, "outfit_color": 0,
	})


static func _boot_turn(host: Node, tree: SceneTree, members: Array, monster_ids: Array) -> Dictionary:
	var session := SessionScreen.new()
	await _mount(host, tree, session)
	GameState.new_campaign(members)
	session._sync_party()
	for member in GameState.party:
		member["mp"] = 500
	var flow := BattleFlow.new()
	flow.hurry = true
	flow.view = session
	session.add_child(flow)
	flow._listen(true)
	var rows: Array = []
	for monster_id in monster_ids:
		rows.append({"id": monster_id})
	flow._build_units(rows)
	for unit in flow.units:
		if str(unit["side"]) == "monster":
			unit["hp"] = 800
			unit["max_hp"] = 800
		else:
			unit["mp"] = 500
	session.present_units(flow.units)
	if not flow.units.is_empty():
		session.raise_member(0, true)
		flow._player_turn(flow.units[0])
	await tree.process_frame
	await tree.process_frame
	return {"session": session, "flow": flow}


static func _unit_hp(flow: BattleFlow, unit_id: String) -> int:
	for unit in flow.units:
		if str(unit["id"]) == unit_id:
			return int(unit["hp"])
	return -1


static func _unit_mp(flow: BattleFlow, unit_id: String) -> int:
	for unit in flow.units:
		if str(unit["id"]) == unit_id:
			return int(unit["mp"])
	return -1


static func _until(tree: SceneTree, cond: Callable, frames: int = 90) -> bool:
	for _i in frames:
		if bool(cond.call()):
			return true
		await tree.process_frame
	return false


static func _tap_attack(host: Node, tree: SceneTree, failures: Array[String]) -> void:
	var pack: Dictionary = await _boot_turn(host, tree, [_hero("mason", "delver", "paladin")], ["puddleblob", "thicket_imp"])
	var session := pack["session"] as SessionScreen
	var flow := pack["flow"] as BattleFlow
	var node := session._monsters["m1"] as Control
	if node == null or node.size.x < 24.0 or node.size.y < 24.0:
		failures.append("hitbox")
		push_error("Touch check: enemy hitbox is under 24px")
		session.queue_free()
		return
	var before := _unit_hp(flow, "m1")
	await _tap(tree, node.get_global_rect().get_center())
	var hit: bool = await _until(tree, func() -> bool: return _unit_hp(flow, "m1") < before)
	if not hit:
		failures.append("tap_attack")
		push_error("Touch check: tapping an enemy did not attack it")
	elif _unit_hp(flow, "m0") != 800:
		failures.append("tap_attack_target")
		push_error("Touch check: the tap hit the wrong enemy")
	session.queue_free()
	await tree.process_frame


static func _tap_skill(host: Node, tree: SceneTree, failures: Array[String]) -> void:
	var pack: Dictionary = await _boot_turn(host, tree, [_hero("mason", "delver", "paladin")], ["puddleblob", "thicket_imp"])
	var session := pack["session"] as SessionScreen
	var flow := pack["flow"] as BattleFlow
	var button := _find_action(session, "skill:oathstrike")
	if button == null:
		failures.append("skill_button")
		session.queue_free()
		return
	await _tap(tree, button.get_global_rect().get_center())
	var armed: bool = await _until(tree, func() -> bool:
		return session._targeting and str(session._inspect.get_meta("hint", "")) == "PICK A TARGET"
	)
	if not armed:
		failures.append("skill_arm")
		push_error("Touch check: Oathstrike did not enter targeting")
		session.queue_free()
		return
	if session._caption.text == "Pick a target" or session._caption.text == "Choose a foe":
		failures.append("skill_hint")
		push_error("Touch check: the target hint floated instead of staying on the card")
	var before_hp := _unit_hp(flow, "m0")
	var before_mp := _unit_mp(flow, "p0")
	var node := session._monsters["m0"] as Control
	await _tap(tree, node.get_global_rect().get_center())
	var cast: bool = await _until(tree, func() -> bool:
		return _unit_hp(flow, "m0") < before_hp and _unit_mp(flow, "p0") < before_mp
	)
	if not cast:
		failures.append("skill_cast")
		push_error("Touch check: tapping the enemy did not cast the armed skill")
	session.queue_free()
	await tree.process_frame


static func _tap_cancel(host: Node, tree: SceneTree, failures: Array[String]) -> void:
	var pack: Dictionary = await _boot_turn(host, tree, [_hero("mason", "delver", "paladin")], ["puddleblob", "thicket_imp"])
	var session := pack["session"] as SessionScreen
	var flow := pack["flow"] as BattleFlow
	var strike := _find_action(session, "skill:oathstrike")
	if strike == null:
		failures.append("cancel_button")
		session.queue_free()
		return
	await _tap(tree, strike.get_global_rect().get_center())
	var armed: bool = await _until(tree, func() -> bool: return session._targeting)
	if not armed:
		failures.append("cancel_arm")
		session.queue_free()
		return
	var before := _unit_hp(flow, "m0")
	await _tap(tree, Vector2(135, 120))
	var cleared: bool = await _until(tree, func() -> bool: return not session._targeting and not session._inspect.visible)
	if not cleared or _unit_hp(flow, "m0") != before:
		failures.append("cancel_empty")
		push_error("Touch check: an empty tap did not cancel targeting")
		session.queue_free()
		return
	strike = _find_action(session, "skill:oathstrike")
	if strike == null:
		failures.append("cancel_rearm")
		session.queue_free()
		return
	await _tap(tree, strike.get_global_rect().get_center())
	var rearmed: bool = await _until(tree, func() -> bool: return session._targeting)
	if not rearmed:
		failures.append("cancel_rearm")
		session.queue_free()
		return
	var wall := _find_action(session, "skill:shieldwall")
	if wall == null:
		failures.append("cancel_switch")
		session.queue_free()
		return
	await _tap(tree, wall.get_global_rect().get_center())
	var switched: bool = await _until(tree, func() -> bool:
		return not session._targeting and session._inspect.visible and str(session._inspect.get_meta("hint", "")) != "PICK A TARGET"
	)
	if not switched:
		failures.append("cancel_switch")
		push_error("Touch check: another skill did not leave targeting")
	session.queue_free()
	await tree.process_frame


static func _tap_ally(host: Node, tree: SceneTree, failures: Array[String]) -> void:
	var pack: Dictionary = await _boot_turn(host, tree, [
		_hero("mason", "delver", "paladin"),
		_hero("nim", "glenfolk", "wizard"),
	], ["puddleblob"])
	var session := pack["session"] as SessionScreen
	var flow := pack["flow"] as BattleFlow
	flow.units[1]["hp"] = 20
	session.sync_unit(flow.units[1])
	var button := _find_action(session, "skill:rallying_brand")
	if button == null:
		failures.append("ally_button")
		session.queue_free()
		return
	await _tap(tree, button.get_global_rect().get_center())
	var armed: bool = await _until(tree, func() -> bool: return session._targeting)
	if not armed:
		failures.append("ally_arm")
		push_error("Touch check: Rallying Brand did not ask for an ally")
		session.queue_free()
		return
	var seat := session._seats[1] as Control
	var at := Vector2(seat.get_global_rect().get_center().x, seat.get_global_rect().end.y - 6.0)
	await _tap(tree, at)
	var healed: bool = await _until(tree, func() -> bool: return _unit_hp(flow, "p1") > 20)
	if not healed:
		failures.append("ally_cast")
		push_error("Touch check: tapping an ally did not cast the heal")
	session.queue_free()
	await tree.process_frame


static func _builder(host: Node, tree: SceneTree, failures: Array[String]) -> void:
	GameState.new_campaign([_hero("mason", "delver", "paladin")])
	GameState.place_id = "millpond"
	GameState.lineups = {}
	var builder := BattleBuilder.new()
	builder.setup("millpond")
	await _mount(host, tree, builder)
	var blob := builder.find_child("Count_puddleblob", true, false) as Label
	var imp := builder.find_child("Count_thicket_imp", true, false) as Label
	var gold := builder.find_child("Gold", true, false) as Label
	if blob == null or imp == null or gold == null or blob.text != "1":
		failures.append("builder_default")
		push_error("Touch check: the builder did not start with one foe")
		builder.queue_free()
		return
	var gold_one := int(gold.text.trim_prefix("Gold "))
	var plus_blob := builder.find_child("Plus_puddleblob", true, false) as Button
	for _i in 8:
		await _tap(tree, plus_blob.get_global_rect().get_center())
	if blob.text != "5":
		failures.append("builder_cap")
		push_error("Touch check: the lineup did not cap at 5 (got %s)" % blob.text)
	var plus_imp := builder.find_child("Plus_thicket_imp", true, false) as Button
	await _tap(tree, plus_imp.get_global_rect().get_center())
	if imp.text != "0":
		failures.append("builder_cap_mix")
		push_error("Touch check: a full table accepted another monster")
	var gold_five := int(gold.text.trim_prefix("Gold "))
	var xp := builder.find_child("Xp", true, false) as Label
	var xp_five := int(xp.text.trim_prefix("XP "))
	if gold_five <= gold_one:
		failures.append("builder_gold")
		push_error("Touch check: expected gold did not rise with more foes")
	var minus_blob := builder.find_child("Minus_puddleblob", true, false) as Button
	await _tap(tree, minus_blob.get_global_rect().get_center())
	await _tap(tree, plus_imp.get_global_rect().get_center())
	if blob.text != "4" or imp.text != "1":
		failures.append("builder_mix")
		push_error("Touch check: mixed steppers landed on %s and %s" % [blob.text, imp.text])
	var xp_mix := int(xp.text.trim_prefix("XP "))
	if xp_mix <= 0 or xp_five <= 0:
		failures.append("builder_xp")
		push_error("Touch check: expected xp was empty")
	var one: Dictionary = Formulas.expected_battle_rewards([{"id": "a", "level": 1}], 1.0)
	var two: Dictionary = Formulas.expected_battle_rewards([
		{"id": "a", "level": 1}, {"id": "a", "level": 1},
	], 1.0)
	var high: Dictionary = Formulas.expected_battle_rewards([{"id": "b", "level": 4}], 1.0)
	if int(two["xp"]) <= int(one["xp"]) or int(two["gold"]) <= int(one["gold"]) or int(high["xp"]) <= int(one["xp"]) or int(high["gold"]) <= int(one["gold"]):
		failures.append("builder_scale")
		push_error("Touch check: rewards did not scale with count and level")
	var started := {"rows": []}
	builder.closed.connect(func(rows: Array): started["rows"] = rows)
	var start := _find_button(builder, "Start")
	await _tap(tree, start.get_global_rect().get_center())
	await tree.process_frame
	await tree.process_frame
	var rows: Array = started["rows"]
	var wanted := ["puddleblob", "puddleblob", "puddleblob", "puddleblob", "thicket_imp"]
	var got: Array = []
	for row in rows:
		got.append(str(row.get("id", "")))
	if got != wanted:
		failures.append("builder_rows")
		push_error("Touch check: start rows %s" % str(got))
	var flow := BattleFlow.new()
	flow._build_units(rows)
	var kinds: Array = []
	for unit in flow.units:
		if str(unit["side"]) == "monster":
			kinds.append(str(unit["kind"]))
	if kinds != wanted:
		failures.append("builder_spawn")
		push_error("Touch check: spawned %s" % str(kinds))
	builder.queue_free()
	await tree.process_frame
	var again := BattleBuilder.new()
	again.setup("millpond")
	await _mount(host, tree, again)
	var remembered := again.find_child("Count_thicket_imp", true, false) as Label
	var remembered_blob := again.find_child("Count_puddleblob", true, false) as Label
	if remembered == null or remembered.text != "1" or remembered_blob == null or remembered_blob.text != "4":
		failures.append("builder_memory")
		push_error("Touch check: the lineup was not remembered")
	again.queue_free()
	await tree.process_frame
	var session := SessionScreen.new()
	await _mount(host, tree, session)
	GameState.place_id = "briar_cross"
	session.show_hub()
	host.set("screen", session)
	host.set("_busy", false)
	var fight_action := Callable(host, "_on_hub_action")
	if not session.action_pressed.is_connected(fight_action):
		session.action_pressed.connect(fight_action)
	var fight := _find_button(session, "Fight")
	if fight == null or fight.disabled:
		failures.append("builder_fight")
		push_error("Touch check: Fight was not available")
		session.queue_free()
		return
	await _tap(tree, fight.get_global_rect().get_center())
	var opened: bool = await _until(tree, func() -> bool: return session.find_child("BattleBuilder", true, false) != null)
	if not opened:
		failures.append("builder_open")
		push_error("Touch check: Fight did not open the builder")
		session.queue_free()
		return
	var back := _find_button(session, "Back")
	await _tap(tree, back.get_global_rect().get_center())
	var gone: bool = await _until(tree, func() -> bool: return session.find_child("BattleBuilder", true, false) == null)
	if not gone:
		failures.append("builder_back")
		push_error("Touch check: Back did not leave the builder")
	session.queue_free()
	await tree.process_frame


static func _mount(host: Node, tree: SceneTree, screen: Control) -> void:
	host.add_child(screen)
	screen.set_anchors_preset(Control.PRESET_FULL_RECT)
	screen.offset_left = 0
	screen.offset_top = 0
	screen.offset_right = 0
	screen.offset_bottom = 0
	await tree.process_frame
	await tree.process_frame


static func _tap(tree: SceneTree, at: Vector2) -> void:
	# parse_input_event takes window coordinates. Stretch mode "viewport" then
	# maps them into the 270×480 canvas. Control rects are already in canvas space.
	var screen_at: Vector2 = tree.root.get_screen_transform() * at
	var down := InputEventScreenTouch.new()
	down.index = 0
	down.pressed = true
	down.position = screen_at
	Input.parse_input_event(down)
	await tree.process_frame
	var up := InputEventScreenTouch.new()
	up.index = 0
	up.pressed = false
	up.position = screen_at
	Input.parse_input_event(up)
	await tree.process_frame
	await tree.process_frame


static func _visible_place(map: MapScreen) -> String:
	var neighbors := {}
	for edge in ContentDB.edges:
		var a := str(edge.get("a", ""))
		var b := str(edge.get("b", ""))
		if a == GameState.place_id:
			neighbors[b] = true
		elif b == GameState.place_id:
			neighbors[a] = true
	var clip := map.get_node("Clip") as Control
	var clip_rect := clip.get_global_rect().grow(-4.0)
	var places := map.get_node("Clip/Content/Places")
	for child in places.get_children():
		if not child is Control:
			continue
		var place_id := str(child.name)
		if place_id == GameState.place_id or not neighbors.has(place_id):
			continue
		var center := (child as Control).get_global_rect().get_center()
		if clip_rect.has_point(center):
			return place_id
	return ""


static func _find_button(root: Node, text: String) -> Button:
	var found: Array[Button] = []
	_collect_buttons(root, found)
	for button in found:
		if button.text == text and button.visible:
			return button
	return null


static func _find_action(root: Node, action_id: String) -> Button:
	var found: Array[Button] = []
	_collect_buttons(root, found)
	for button in found:
		if str(button.get_meta("action_id", "")) == action_id and button.visible:
			return button
	return null


static func _collect_buttons(node: Node, into: Array[Button]) -> void:
	if node is Button:
		into.append(node)
	for child in node.get_children():
		_collect_buttons(child, into)
