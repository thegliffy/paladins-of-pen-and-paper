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
	await _heal_on_cast(host, tree, failures)
	await _gear(host, tree, failures)
	await _map_bag(host, tree, failures)
	await _combat_item(host, tree, failures)
	await _builder(host, tree, failures)
	await _builder_space(host, tree, failures)
	await _row_fit(host, tree, failures)
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
	var seat := session._seats[1] as Control
	var digits := seat.get_node("BarHost/HpDigits") as DigitReadout
	if digits == null or digits.text != "20":
		failures.append("ally_digits_before")
		push_error("Touch check: the chair did not show 20 before the heal")
		session.queue_free()
		return
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
	var timing := session.find_child("HealTiming", true, false)
	if timing == null or str(timing.get_meta("caption", "")) != "IMMEDIATE":
		failures.append("ally_timing")
		push_error("Touch check: Rallying Brand was not labeled immediate")
	var at := Vector2(seat.get_global_rect().get_center().x, seat.get_global_rect().end.y - 6.0)
	await _tap(tree, at)
	var healed: bool = await _until(tree, func() -> bool: return _unit_hp(flow, "p1") > 20)
	if not healed:
		failures.append("ally_cast")
		push_error("Touch check: tapping an ally did not cast the heal")
	elif digits.text == "20" or int(digits.text) != _unit_hp(flow, "p1"):
		failures.append("ally_digits")
		push_error("Touch check: the chair still showed %s after HP became %d" % [digits.text, _unit_hp(flow, "p1")])
	if _unit_hp(flow, "m0") != 800:
		failures.append("ally_next")
		push_error("Touch check: the next actor acted before the heal finished")
	session.queue_free()
	await tree.process_frame


static func _heal_on_cast(host: Node, tree: SceneTree, failures: Array[String]) -> void:
	var pack: Dictionary = await _boot_turn(host, tree, [
		_hero("mason", "delver", "paladin"),
		_hero("nim", "glenfolk", "wizard"),
	], ["puddleblob"])
	var session := pack["session"] as SessionScreen
	var flow := pack["flow"] as BattleFlow
	flow.units[1]["hp"] = 20
	session.sync_unit(flow.units[1])
	var seat := session._seats[1] as Control
	var digits := seat.get_node("BarHost/HpDigits") as DigitReadout
	var skill: Dictionary = ContentDB.skill("rallying_brand")
	var turn_before := flow.turn_index
	flow._land_heal(flow.units[0], skill, flow.units[1], 1)
	var hp := _unit_hp(flow, "p1")
	var popup := false
	for child in session.get_children():
		if child is DigitReadout and str((child as DigitReadout).text).begins_with("+"):
			popup = true
	if hp <= 20 or digits == null or digits.text != str(hp) or not popup:
		failures.append("heal_now")
		push_error("Touch check: heal left HP %d chair %s popup %s" % [hp, digits.text if digits else "missing", popup])
	elif _unit_hp(flow, "m0") != 800 or flow.turn_index != turn_before:
		failures.append("heal_next")
		push_error("Touch check: the heal waited for another actor")
	session.queue_free()
	await tree.process_frame


static func _gear(host: Node, tree: SceneTree, failures: Array[String]) -> void:
	GameState.new_campaign([
		_hero("mason", "delver", "paladin"),
		_hero("nim", "glenfolk", "wizard"),
	])
	GameState.place_id = "candlewick"
	GameState.give_item("kiln_sword", 1)
	GameState.give_item("sunbrand", 1)
	var before := int(GameState.combat_stats(GameState.party[0])["attack"])
	var session := SessionScreen.new()
	await _mount(host, tree, session)
	session.show_hub()
	host.set("screen", session)
	host.set("_busy", false)
	var hub_action := Callable(host, "_on_hub_action")
	if not session.action_pressed.is_connected(hub_action):
		session.action_pressed.connect(hub_action)
	var opener := _find_button(session, "Gear")
	if opener == null:
		failures.append("gear_hub")
		push_error("Touch check: the hub has no Gear button")
		session.queue_free()
		return
	await _tap(tree, opener.get_global_rect().get_center())
	var opened: bool = await _until(tree, func() -> bool: return session.find_child("GearScreen", true, false) != null)
	if not opened or session.find_child("Item_tonic", true, false) == null:
		failures.append("gear_bag")
		push_error("Touch check: Gear did not open the shared bag")
		session.queue_free()
		return
	var sword := session.find_child("Item_kiln_sword", true, false) as Button
	if sword == null:
		failures.append("gear_row")
		session.queue_free()
		return
	await _tap(tree, sword.get_global_rect().get_center())
	var compared: bool = await _until(tree, func() -> bool:
		var line := session.find_child("Compare", true, false) as Label
		return line != null and line.text.contains(" to ")
	)
	if not compared:
		failures.append("gear_compare")
		push_error("Touch check: the item card did not compare stats")
		session.queue_free()
		return
	var equip := _find_button(session, "Equip")
	await _tap(tree, equip.get_global_rect().get_center())
	var worn: bool = await _until(tree, func() -> bool:
		var slot := session.find_child("Slot_main", true, false) as Button
		return slot != null and slot.text == "Main: Kiln Sword"
	)
	var geared := BattleFlow.new()
	geared._build_units([])
	var attack := int(geared.units[0]["attack"])
	if not worn or attack <= before or attack != int(GameState.combat_stats(GameState.party[0])["attack"]):
		failures.append("gear_equip")
		push_error("Touch check: Kiln Sword did not raise combat attack (%d to %d)" % [before, attack])
		session.queue_free()
		return
	var bag_tab := session.find_child("Tab_bag", true, false) as Button
	await _tap(tree, bag_tab.get_global_rect().get_center())
	var brand_ready: bool = await _until(tree, func() -> bool: return session.find_child("Item_sunbrand", true, false) != null)
	if not brand_ready:
		failures.append("gear_bag_back")
		session.queue_free()
		return
	var brand := session.find_child("Item_sunbrand", true, false) as Button
	await _tap(tree, brand.get_global_rect().get_center())
	var brand_card: bool = await _until(tree, func() -> bool:
		var name_label := session.find_child("DetailName", true, false) as Label
		return name_label != null and name_label.text == "Sunbrand"
	)
	if not brand_card:
		failures.append("gear_brand")
		session.queue_free()
		return
	equip = _find_button(session, "Equip")
	await _tap(tree, equip.get_global_rect().get_center())
	var two_hand: bool = await _until(tree, func() -> bool:
		var main := session.find_child("Slot_main", true, false) as Button
		var off := session.find_child("Slot_off", true, false) as Button
		return main != null and off != null and main.text == "Main: Sunbrand" and off.text == "Off: Empty"
	)
	if not two_hand:
		failures.append("gear_twohand")
		push_error("Touch check: Sunbrand did not clear the off hand")
		session.queue_free()
		return
	var hero_tab := session.find_child("Tab_hero", true, false) as Button
	await _tap(tree, hero_tab.get_global_rect().get_center())
	var wizard_ready: bool = await _until(tree, func() -> bool: return session.find_child("Hero_1", true, false) != null)
	if not wizard_ready:
		failures.append("gear_hero")
		session.queue_free()
		return
	var wizard := session.find_child("Hero_1", true, false) as Button
	await _tap(tree, wizard.get_global_rect().get_center())
	await _until(tree, func() -> bool: return session.find_child("Tab_bag", true, false) != null)
	bag_tab = session.find_child("Tab_bag", true, false) as Button
	await _tap(tree, bag_tab.get_global_rect().get_center())
	var sword_back: bool = await _until(tree, func() -> bool: return session.find_child("Item_kiln_sword", true, false) != null)
	if not sword_back:
		failures.append("gear_returned")
		session.queue_free()
		return
	sword = session.find_child("Item_kiln_sword", true, false) as Button
	await _tap(tree, sword.get_global_rect().get_center())
	var blocked: bool = await _until(tree, func() -> bool:
		var line := session.find_child("Compare", true, false) as Label
		return line != null and line.text == "This class cannot wield it"
	)
	if not blocked:
		failures.append("gear_restrict")
		push_error("Touch check: the wizard was offered a sword")
		session.queue_free()
		return
	equip = _find_button(session, "Equip")
	await _tap(tree, equip.get_global_rect().get_center())
	await tree.process_frame
	await tree.process_frame
	if str(GameState.party[1]["gear"]["main"]) != "reed_staff":
		failures.append("gear_restrict_equip")
		push_error("Touch check: the wizard equipped a sword")
		session.queue_free()
		return
	var shop_tab := session.find_child("Tab_shop", true, false) as Button
	if shop_tab == null:
		failures.append("gear_shop_tab")
		session.queue_free()
		return
	await _tap(tree, shop_tab.get_global_rect().get_center())
	var armor_ready: bool = await _until(tree, func() -> bool: return session.find_child("Filter_armor", true, false) != null)
	if not armor_ready:
		failures.append("gear_shop")
		session.queue_free()
		return
	var armor := session.find_child("Filter_armor", true, false) as Button
	await _tap(tree, armor.get_global_rect().get_center())
	var coat_ready: bool = await _until(tree, func() -> bool: return session.find_child("Item_travel_coat", true, false) != null)
	if not coat_ready:
		failures.append("gear_shop_row")
		session.queue_free()
		return
	var coat := session.find_child("Item_travel_coat", true, false) as Button
	await _tap(tree, coat.get_global_rect().get_center())
	var buy_ready: bool = await _until(tree, func() -> bool: return _find_button(session, "Buy 25") != null)
	if not buy_ready:
		failures.append("gear_buy_button")
		session.queue_free()
		return
	var gold_before := GameState.gold
	var buy := _find_button(session, "Buy 25")
	await _tap(tree, buy.get_global_rect().get_center())
	var bought: bool = await _until(tree, func() -> bool:
		return int(GameState.inventory.get("travel_coat", 0)) == 1 and _find_button(session, "Sell") != null
	)
	if not bought or GameState.gold != gold_before - 25:
		failures.append("gear_buy")
		push_error("Touch check: buying the coat left gold %d" % GameState.gold)
		session.queue_free()
		return
	var sell := _find_button(session, "Sell")
	if sell == null:
		failures.append("gear_sell_button")
		session.queue_free()
		return
	await _tap(tree, sell.get_global_rect().get_center())
	var sold: bool = await _until(tree, func() -> bool: return int(GameState.inventory.get("travel_coat", 0)) == 0)
	if not sold or GameState.gold != gold_before - 25 + 12:
		failures.append("gear_sell")
		push_error("Touch check: selling the coat left gold %d" % GameState.gold)
		session.queue_free()
		return
	var saved_main := str(GameState.party[0]["gear"]["main"])
	var saved_off := str(GameState.party[0]["gear"]["off"])
	var saved_tonic := int(GameState.inventory.get("tonic", 0))
	var saved_gold := GameState.gold
	GameState.save_game()
	GameState.party = []
	GameState.inventory = {}
	GameState.gold = 0
	if not GameState.load_game():
		failures.append("gear_load")
		session.queue_free()
		return
	if str(GameState.party[0]["gear"]["main"]) != saved_main or str(GameState.party[0]["gear"]["off"]) != saved_off:
		failures.append("gear_load_slots")
		push_error("Touch check: load did not restore equipment")
	elif int(GameState.inventory.get("tonic", 0)) != saved_tonic or GameState.gold != saved_gold:
		failures.append("gear_load_bag")
		push_error("Touch check: load did not restore the bag")
	elif str(GameState.party[1]["gear"]["main"]) != "reed_staff":
		failures.append("gear_load_kit")
		push_error("Touch check: load dropped the wizard's staff")
	var closer := session.find_child("CloseGear", true, false) as Button
	if closer != null:
		await _tap(tree, closer.get_global_rect().get_center())
		await _until(tree, func() -> bool: return session.find_child("GearScreen", true, false) == null)
	session.queue_free()
	await tree.process_frame


static func _map_bag(host: Node, tree: SceneTree, failures: Array[String]) -> void:
	GameState.new_campaign([_hero("mason", "delver", "paladin")])
	GameState.place_id = "candlewick"
	var map := MapScreen.new()
	await _mount(host, tree, map)
	var bag := map.get_node_or_null("Bag") as Button
	if bag == null or not bag.visible:
		failures.append("map_bag")
		push_error("Touch check: the map has no Bag button")
		map.queue_free()
		return
	await _tap(tree, bag.get_global_rect().get_center())
	var opened: bool = await _until(tree, func() -> bool: return map.find_child("GearScreen", true, false) != null)
	if not opened:
		failures.append("map_bag_open")
		push_error("Touch check: Bag did not open the inventory")
		map.queue_free()
		return
	var closer := map.find_child("CloseGear", true, false) as Button
	await _tap(tree, closer.get_global_rect().get_center())
	var gone: bool = await _until(tree, func() -> bool: return map.find_child("GearScreen", true, false) == null)
	if not gone:
		failures.append("map_bag_close")
		push_error("Touch check: Close did not leave the bag")
	map._set_travel_buttons(true)
	if bag.visible:
		failures.append("map_bag_travel")
		push_error("Touch check: Bag stayed up while walking")
	map.queue_free()
	await tree.process_frame


static func _combat_item(host: Node, tree: SceneTree, failures: Array[String]) -> void:
	var pack: Dictionary = await _boot_turn(host, tree, [
		_hero("mason", "delver", "paladin"),
		_hero("nim", "glenfolk", "wizard"),
	], ["puddleblob"])
	var session := pack["session"] as SessionScreen
	var flow := pack["flow"] as BattleFlow
	GameState.give_item("kiln_sword", 1)
	flow.units[1]["hp"] = 20
	session.sync_unit(flow.units[1])
	var seat := session._seats[1] as Control
	var digits := seat.get_node("BarHost/HpDigits") as DigitReadout
	var item := _find_action(session, "item")
	if item == null or digits == null or digits.text != "20":
		failures.append("item_button")
		push_error("Touch check: the item slot or the chair was not ready")
		session.queue_free()
		return
	await _tap(tree, item.get_global_rect().get_center())
	var armed: bool = await _until(tree, func() -> bool: return session._inspect.visible)
	if not armed:
		failures.append("item_arm")
		session.queue_free()
		return
	item = _find_action(session, "item")
	await _tap(tree, item.get_global_rect().get_center())
	var listed: bool = await _until(tree, func() -> bool: return _find_button(session, "Hearth Tonic x3") != null)
	if not listed or _find_button(session, "Kiln Sword  x1") != null:
		failures.append("item_list")
		push_error("Touch check: the pouch did not list only usables")
		session.queue_free()
		return
	var tonic := _find_button(session, "Hearth Tonic x3")
	await _tap(tree, tonic.get_global_rect().get_center())
	var aiming: bool = await _until(tree, func() -> bool: return session._targeting)
	if not aiming:
		failures.append("item_aim")
		push_error("Touch check: the tonic did not ask for an ally")
		session.queue_free()
		return
	var at := Vector2(seat.get_global_rect().get_center().x, seat.get_global_rect().end.y - 6.0)
	await _tap(tree, at)
	var healed: bool = await _until(tree, func() -> bool: return _unit_hp(flow, "p1") > 20)
	var hp := _unit_hp(flow, "p1")
	if not healed or digits.text != str(hp):
		failures.append("item_heal")
		push_error("Touch check: the tonic left HP %d chair %s" % [hp, digits.text])
	elif int(GameState.inventory.get("tonic", 0)) != 2:
		failures.append("item_spent")
		push_error("Touch check: the tonic was not spent")
	elif _unit_hp(flow, "m0") != 800:
		failures.append("item_turn")
		push_error("Touch check: the foe acted before the tonic finished")
	else:
		var foe := session._monsters["m0"] as Control
		await _tap(tree, foe.get_global_rect().get_center())
		for _i in 12:
			await tree.process_frame
		if _unit_hp(flow, "m0") != 800:
			failures.append("item_turn")
			push_error("Touch check: the tonic did not end the turn")
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
	if builder.find_child("Count_gravel_brute", true, false) != null or builder.find_child("Count_grinmud_toad", true, false) == null or builder.find_child("Count_kelpback", true, false) != null:
		failures.append("builder_place")
		push_error("Touch check: Millpond did not list the meadow table")
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


static func _builder_space(host: Node, tree: SceneTree, failures: Array[String]) -> void:
	GameState.new_campaign([_hero("mason", "delver", "paladin")])
	GameState.place_id = "gravel_keep"
	GameState.lineups = {}
	var builder := BattleBuilder.new()
	builder.setup("gravel_keep")
	await _mount(host, tree, builder)
	var space := builder.find_child("Space", true, false)
	var howler := builder.find_child("Count_cave_howler", true, false) as Label
	var brute := builder.find_child("Count_gravel_brute", true, false) as Label
	if space == null or howler == null or brute == null or str(space.get_meta("caption")) != "SPACE 12 LEFT":
		failures.append("space_label")
		push_error("Touch check: the builder did not show table space")
		builder.queue_free()
		return
	if builder.find_child("Count_puddleblob", true, false) != null:
		failures.append("space_place")
		push_error("Touch check: Gravel Keep listed a marsh blob")
	if builder.find_child("Size_gravel_brute", true, false) == null or builder.find_child("Size_cave_howler", true, false) != null:
		failures.append("size_tag")
		push_error("Touch check: large foes were not marked")
	var minus_howler := builder.find_child("Minus_cave_howler", true, false) as Button
	await _tap(tree, minus_howler.get_global_rect().get_center())
	var plus_brute := builder.find_child("Plus_gravel_brute", true, false) as Button
	for _i in 5:
		await _tap(tree, plus_brute.get_global_rect().get_center())
	if brute.text != "3" or int(space.get_meta("left")) != 0 or not plus_brute.disabled:
		failures.append("space_large")
		push_error("Touch check: three larges did not fill the table (count %s space %s)" % [brute.text, space.get_meta("left")])
	var plus_howler := builder.find_child("Plus_cave_howler", true, false) as Button
	await _tap(tree, plus_howler.get_global_rect().get_center())
	if howler.text != "0" or not plus_howler.disabled:
		failures.append("space_full")
		push_error("Touch check: a full large table accepted a regular foe")
	var minus_brute := builder.find_child("Minus_gravel_brute", true, false) as Button
	for _i in 3:
		await _tap(tree, minus_brute.get_global_rect().get_center())
	await _tap(tree, plus_brute.get_global_rect().get_center())
	await _tap(tree, plus_brute.get_global_rect().get_center())
	await _tap(tree, plus_howler.get_global_rect().get_center())
	await _tap(tree, plus_howler.get_global_rect().get_center())
	await _tap(tree, plus_brute.get_global_rect().get_center())
	if brute.text != "2" or howler.text != "1" or int(space.get_meta("left")) != 2:
		failures.append("space_mix")
		push_error("Touch check: two large plus one regular landed on %s / %s space %s" % [brute.text, howler.text, space.get_meta("left")])
	for _i in 2:
		await _tap(tree, minus_brute.get_global_rect().get_center())
	await _tap(tree, minus_howler.get_global_rect().get_center())
	await _tap(tree, plus_brute.get_global_rect().get_center())
	for _i in 4:
		await _tap(tree, plus_howler.get_global_rect().get_center())
	if brute.text != "1" or howler.text != "3" or int(space.get_meta("left")) != 1 or not plus_howler.disabled or not plus_brute.disabled:
		failures.append("space_one_large")
		push_error("Touch check: one large plus three regular landed on %s / %s space %s" % [brute.text, howler.text, space.get_meta("left")])
	builder.queue_free()
	await tree.process_frame


static func _row_fit(host: Node, tree: SceneTree, failures: Array[String]) -> void:
	var session := SessionScreen.new()
	await _mount(host, tree, session)
	var packs := [
		["regular", "regular", "regular", "regular", "regular"],
		["large", "large", "large"],
		["large", "regular", "regular", "regular"],
		["large", "large", "regular"],
	]
	for sizes in packs:
		var units: Array = []
		var entries: Array = []
		for i in sizes.size():
			var large := str(sizes[i]) == "large"
			var back: bool = i == 0 and sizes.size() == 3 and large
			units.append({
				"id": "m%d" % i,
				"side": "monster",
				"kind": "gravel_brute" if large else "puddleblob",
				"size": "large" if large else "regular",
				"back_row": back,
				"hp": 10,
				"max_hp": 10,
				"mp": 0,
				"max_mp": 1,
			})
			entries.append({"size": "large" if large else "regular", "back": back})
		session.present_units(units)
		await tree.process_frame
		var expected: Array = Formulas.enemy_layout(entries)
		var ids: Array = session._monsters.keys()
		if ids.size() != expected.size():
			failures.append("row_count")
			push_error("Touch check: the row did not spawn the lineup")
			continue
		var seen: Array = []
		var large_w := 0.0
		var regular_w := 0.0
		for i in ids.size():
			var node: Control = session._monsters[ids[i]]
			var rect := Rect2(node.position, node.size)
			var want: Rect2 = expected[i]
			if rect.position.distance_to(want.position) > 0.5 or rect.size.distance_to(want.size) > 0.5:
				failures.append("row_layout")
				push_error("Touch check: foe %s sat at %s, wanted %s" % [ids[i], rect, want])
			var card_top := Layout.rect("combat", "skill_card").position.y
			if rect.position.x < -0.01 or rect.position.y < 30.0 or rect.end.x > 270.01 or rect.end.y > card_top + 0.01:
				failures.append("row_bounds")
				push_error("Touch check: foe rect %s left the meadow" % rect)
			if rect.size.x < 24.0 or rect.size.y < 24.0:
				failures.append("row_hit")
				push_error("Touch check: foe hitbox %s is under 24px" % rect.size)
			var sprite := node.get_node_or_null("Sprite") as Control
			if sprite == null or absf(sprite.size.x - rect.size.x) > 0.5 or absf(sprite.size.y - rect.size.y) > 0.5:
				failures.append("row_sprite")
				push_error("Touch check: the sprite did not fill its footprint")
			if str(node.get_meta("size")) == "large":
				large_w = rect.size.x
			else:
				regular_w = rect.size.x
			for other in seen:
				var hit: Rect2 = rect.intersection(other)
				if hit.size.x > 0.05 and hit.size.y > 0.05:
					failures.append("row_overlap")
					push_error("Touch check: foe rects overlap %s and %s" % [rect, other])
			seen.append(rect)
		if large_w > 0.0 and regular_w > 0.0 and large_w <= regular_w:
			failures.append("row_scale")
			push_error("Touch check: large footprint %s was not wider than regular %s" % [large_w, regular_w])
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
