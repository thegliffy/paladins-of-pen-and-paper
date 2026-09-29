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
	await _quest_panel(host, tree, failures)
	await _town_services(host, tree, failures)
	await _bottom_and_levels(host, tree, failures)
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
	if digits == null or digits.text != _vital(20, int(flow.units[1]["max_hp"])):
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
	elif digits.text != _vital(_unit_hp(flow, "p1"), int(flow.units[1]["max_hp"])):
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
	if hp <= 20 or digits == null or digits.text != _vital(hp, int(flow.units[1]["max_hp"])) or not popup:
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
	if item == null or digits == null or digits.text != _vital(20, int(flow.units[1]["max_hp"])):
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
	if not healed or digits.text != _vital(hp, int(flow.units[1]["max_hp"])):
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


static func _quest_panel(host: Node, tree: SceneTree, failures: Array[String]) -> void:
	GameState.new_campaign([_hero("mason", "delver", "paladin")])
	GameState.place_id = "candlewick"
	var session := SessionScreen.new()
	await _mount(host, tree, session)
	session.show_hub()
	host.set("screen", session)
	host.set("_busy", false)
	var hub_action := Callable(host, "_on_hub_action")
	if not session.action_pressed.is_connected(hub_action):
		session.action_pressed.connect(hub_action)
	await tree.process_frame
	_assert_hub_buttons(session, failures)
	await _assert_header_plates(session, tree, failures)
	if session._caption.autowrap_mode == TextServer.AUTOWRAP_OFF:
		failures.append("hub_caption_wrap")
	var quest := _find_button(session, "Quest")
	if quest == null:
		failures.append("quest_button")
		session.queue_free()
		return
	await _tap(tree, quest.get_global_rect().get_center())
	await _assert_quest_sheet(session, tree, failures, "hub")
	await _tap_quest(session, tree, "Notice board")
	await _assert_quest_sheet(session, tree, failures, "board")
	await _tap_quest(session, tree, "Log")
	await _assert_quest_sheet(session, tree, failures, "board_back")
	for i in 3:
		await _tap_quest(session, tree, "Close")
		await tree.process_frame
		await tree.process_frame
		if session.get_node_or_null("QuestScreen") != null:
			failures.append("quest_close")
			break
		var again := _find_button(session, "Quest")
		if again == null:
			failures.append("quest_reopen_button")
			break
		await _tap(tree, again.get_global_rect().get_center())
		await _assert_quest_sheet(session, tree, failures, "reopen_%d" % i)
	session.queue_free()
	await tree.process_frame
	var map := MapScreen.new()
	await _mount(host, tree, map)
	var story_bar := map.get_node_or_null("StoryBar")
	var story_track := map.get_node_or_null("StoryBar/StoryTrack")
	if story_bar == null or story_track == null or story_track.get_parent() != story_bar:
		failures.append("story_track_parent")
		push_error("Touch check: the story tracker is not parented to its parchment")
	var log := _find_button(map, "Log")
	if log == null:
		failures.append("map_log_button")
		map.queue_free()
		return
	await _tap(tree, log.get_global_rect().get_center())
	await _assert_quest_sheet(map, tree, failures, "map")
	await _tap_quest(map, tree, "Notice board")
	await _assert_quest_sheet(map, tree, failures, "map_board")
	await _tap_quest(map, tree, "Log")
	await _assert_quest_sheet(map, tree, failures, "map_back")
	await _tap_quest(map, tree, "Close")
	await tree.process_frame
	await tree.process_frame
	log = _find_button(map, "Log")
	if log == null:
		failures.append("map_log_again")
	else:
		await _tap(tree, log.get_global_rect().get_center())
		await _assert_quest_sheet(map, tree, failures, "map_reopen")
		await _tap_quest(map, tree, "Close")
		await tree.process_frame
	map.queue_free()
	await tree.process_frame


static func _assert_header_plates(session: SessionScreen, tree: SceneTree, failures: Array[String]) -> void:
	await RenderingServer.frame_post_draw
	var image := tree.root.get_viewport().get_texture().get_image()
	for plate_name in ["BannerPlate", "CaptionPlate"]:
		var plate := session.get_node_or_null(plate_name) as Panel
		if plate == null or not plate.visible or plate.get_child_count() < 1:
			failures.append("hub_plate_%s" % plate_name)
			push_error("Touch check: %s is missing" % plate_name)
			continue
		var label := plate.get_child(0) as Label
		if label == null or label.get_parent() != plate:
			failures.append("hub_plate_label_%s" % plate_name)
			push_error("Touch check: %s text is not on the plate" % plate_name)
			continue
		var style := plate.get_theme_stylebox("panel") as StyleBoxFlat
		var fg := label.get_theme_color("font_color")
		if style == null or style.bg_color.a < 0.99 or Widgets.contrast_ratio(fg, style.bg_color) < 4.5:
			failures.append("hub_contrast_%s" % plate_name)
			push_error("Touch check: %s text does not contrast with its backing" % plate_name)
		var at := plate.get_global_rect().position + Vector2(6, 6)
		if at.x < 0.0 or at.y < 0.0 or at.x >= image.get_width() or at.y >= image.get_height():
			failures.append("hub_plate_pixel_%s" % plate_name)
			continue
		var pixel := image.get_pixel(int(at.x), int(at.y))
		if pixel.b > pixel.r or pixel.a < 0.95:
			failures.append("hub_plate_sky_%s" % plate_name)
			push_error("Touch check: %s still shows the sky %s" % [plate_name, pixel])


static func _assert_hub_buttons(session: SessionScreen, failures: Array[String]) -> void:
	var bar := Layout.rect("combat", "action_bar")
	var gap := 3.0
	var width := (bar.size.x - 4.0 - gap * 4.0) / 5.0
	var labels := PackedStringArray(["Travel", "Fight", "Rest", "Quest", "Gear"])
	var font := Widgets.ui_font()
	for label in labels:
		var button := _find_button(session, label)
		if button == null:
			failures.append("hub_label_%s" % label)
			push_error("Touch check: hub is missing the %s button" % label)
			continue
		var font_size := button.get_theme_font_size("font_size")
		var text_w := font.get_string_size(button.text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x
		var icon_w := 0.0
		if button.icon != null:
			icon_w = float(button.get_theme_constant("icon_max_width")) + float(button.get_theme_constant("h_separation"))
		var style := button.get_theme_stylebox("normal")
		var inner := button.size.x - style.content_margin_left - style.content_margin_right
		if text_w + icon_w > inner + 0.5:
			failures.append("hub_clip_%s" % label)
			push_error("Touch check: %s text %.1f icon %.1f inner %.1f" % [label, text_w, icon_w, inner])
		if button.text != label:
			failures.append("hub_word_%s" % label)
	if width < 40.0:
		failures.append("hub_button_width")


static func _tap_quest(root: Node, tree: SceneTree, text: String) -> void:
	var screen := root.get_node_or_null("QuestScreen")
	if screen == null:
		return
	var button := _find_button(screen, text)
	if button == null:
		push_error("Touch check: quest screen has no %s button" % text)
		return
	await _tap(tree, button.get_global_rect().get_center())


static func _assert_quest_sheet(root: Node, tree: SceneTree, failures: Array[String], tag: String) -> void:
	await tree.process_frame
	await RenderingServer.frame_post_draw
	var screen := root.get_node_or_null("QuestScreen") as Control
	if screen == null or not screen.visible:
		failures.append("quest_screen_%s" % tag)
		push_error("Touch check: quest screen missing on %s" % tag)
		return
	var view := Vector2(Layout.viewport_size())
	if screen.size.x < view.x - 1.0 or screen.size.y < view.y - 1.0:
		failures.append("quest_cover_%s" % tag)
		push_error("Touch check: quest screen size %s on %s" % [screen.size, tag])
	var sheet := screen.get_node_or_null("Sheet") as Control
	if sheet == null or not sheet.visible or sheet.size.x < 250.0 or sheet.size.y < 400.0:
		failures.append("quest_sheet_%s" % tag)
		push_error("Touch check: parchment missing on %s" % tag)
		return
	var image := tree.root.get_viewport().get_texture().get_image()
	var origin := sheet.get_global_rect().position
	var sample_at := Vector2i(int(origin.x + 12), int(origin.y + sheet.size.y - 14))
	if sample_at.x < 0 or sample_at.y < 0 or sample_at.x >= image.get_width() or sample_at.y >= image.get_height():
		failures.append("quest_pixel_%s" % tag)
		push_error("Touch check: parchment sample %s outside %s on %s" % [sample_at, image.get_size(), tag])
	else:
		var pixel := image.get_pixelv(sample_at)
		if not _parchment(pixel):
			failures.append("quest_parchment_%s" % tag)
			push_error("Touch check: sheet pixel %s at %s on %s" % [pixel, sample_at, tag])
	var labels: Array[Label] = []
	_collect_labels(sheet, labels)
	var seen: Array[Rect2] = []
	var story := false
	var posted := false
	for label in labels:
		if label.get_parent() == null or not _parented_to(label, sheet):
			failures.append("quest_parent_%s" % tag)
			push_error("Touch check: '%s' escaped the sheet on %s" % [label.text, tag])
			return
		if label.text == "On the board" or label.text.begins_with("The road is quiet"):
			story = true
		if label.text == "Posted":
			posted = true
		var rect := _clipped_rect(label)
		if rect.size.x <= 0.5 or rect.size.y <= 0.5:
			continue
		var sheet_rect := sheet.get_global_rect().grow(1.0)
		if not sheet_rect.encloses(rect):
			failures.append("quest_overflow_%s" % tag)
			push_error("Touch check: '%s' %s outside sheet %s on %s" % [label.text, rect, sheet.get_global_rect(), tag])
		var raw := label.get_global_rect()
		var bounds := sheet.get_global_rect()
		if raw.position.x < bounds.position.x - 1.0 or raw.end.x > bounds.end.x + 1.0:
			failures.append("quest_wide_%s" % tag)
			push_error("Touch check: '%s' %s wider than the sheet %s on %s" % [label.text, raw, bounds, tag])
		for other in seen:
			var hit := rect.intersection(other)
			if hit.size.x > 1.0 and hit.size.y > 1.0:
				failures.append("quest_overlap_%s" % tag)
				push_error("Touch check: '%s' overlaps another label on %s" % [label.text, tag])
				break
		seen.append(rect)
	var wants_story := tag == "hub" or tag.begins_with("reopen") or tag == "board_back" or tag == "map" or tag == "map_back" or tag == "map_reopen"
	var wants_board := tag == "board" or tag.ends_with("_board")
	if wants_story and not story:
		failures.append("quest_story_%s" % tag)
		push_error("Touch check: story copy missing on %s" % tag)
	if wants_board and not posted:
		failures.append("quest_board_%s" % tag)
		push_error("Touch check: notice board copy missing on %s" % tag)


static func _town_services(host: Node, tree: SceneTree, failures: Array[String]) -> void:
	GameState.new_campaign([_hero("mason", "delver", "paladin")])
	GameState.story_done.append("wolf_in_the_hedge")
	GameState.place_id = "brinewick"
	var session := SessionScreen.new()
	await _mount(host, tree, session)
	session.show_hub()
	host.set("screen", session)
	host.set("_busy", false)
	var hub_action := Callable(host, "_on_hub_action")
	if not session.action_pressed.is_connected(hub_action):
		session.action_pressed.connect(hub_action)
	await tree.process_frame
	var fight := _find_button(session, "Fight")
	if fight == null or not fight.disabled:
		failures.append("town_fight")
		push_error("Touch check: Brinewick still offers a fight")
	var gear_button := _find_button(session, "Gear")
	if gear_button == null:
		failures.append("town_gear")
		session.queue_free()
		return
	await _tap(tree, gear_button.get_global_rect().get_center())
	var opened: bool = await _until(tree, func() -> bool: return session.find_child("Tab_shop", true, false) != null)
	if not opened:
		failures.append("town_shop_tab")
		session.queue_free()
		return
	var shop := session.find_child("Tab_shop", true, false) as Button
	await _tap(tree, shop.get_global_rect().get_center())
	var tier_ready: bool = await _until(tree, func() -> bool:
		return session.find_child("Item_salt_mace", true, false) != null and session.find_child("Item_travel_coat", true, false) == null
	)
	if not tier_ready:
		failures.append("town_shop_tier")
		push_error("Touch check: Brinewick shop did not keep tier 2 stock")
		session.queue_free()
		return
	var mace := session.find_child("Item_salt_mace", true, false) as Button
	var scroller := mace.get_parent()
	while scroller and not scroller is ScrollContainer:
		scroller = scroller.get_parent()
	if scroller is ScrollContainer:
		(scroller as ScrollContainer).scroll_vertical = int(mace.position.y)
		await tree.process_frame
		await tree.process_frame
	await _tap(tree, mace.get_global_rect().get_center())
	var compared: bool = await _until(tree, func() -> bool:
		var line := session.find_child("Compare", true, false) as Label
		return line != null and line.text.contains(" to ")
	)
	if not compared:
		failures.append("town_shop_compare")
		session.queue_free()
		return
	var smith := session.find_child("Tab_smith", true, false) as Button
	if smith == null:
		failures.append("town_smith_tab")
		session.queue_free()
		return
	await _tap(tree, smith.get_global_rect().get_center())
	var smith_open: bool = await _until(tree, func() -> bool: return session.find_child("SmithScreen", true, false) != null)
	if not smith_open:
		failures.append("town_smith")
		session.queue_free()
		return
	await _assert_smith(session, tree, failures, "craft")
	var upgrade := session.find_child("Tab_upgrade", true, false) as Button
	if upgrade == null:
		failures.append("town_upgrade_tab")
		session.queue_free()
		return
	await _tap(tree, upgrade.get_global_rect().get_center())
	var upgrade_ready: bool = await _until(tree, func() -> bool:
		var labels: Array[Label] = []
		var screen := session.find_child("SmithScreen", true, false)
		if screen == null:
			return false
		_collect_labels(screen, labels)
		for label in labels:
			if label.text.contains("Atk") and label.text.contains(" to "):
				return true
		return false
	)
	if not upgrade_ready:
		failures.append("town_upgrade_preview")
		session.queue_free()
		return
	await _assert_smith(session, tree, failures, "upgrade")
	session.queue_free()


static func _assert_smith(root: Node, tree: SceneTree, failures: Array[String], tag: String) -> void:
	await tree.process_frame
	await RenderingServer.frame_post_draw
	var screen := root.find_child("SmithScreen", true, false) as Control
	if screen == null or not screen.visible:
		failures.append("smith_screen_%s" % tag)
		return
	var view := Vector2(Layout.viewport_size())
	if screen.size.x < view.x - 1.0 or screen.size.y < view.y - 1.0:
		failures.append("smith_cover_%s" % tag)
		push_error("Touch check: smith size %s on %s" % [screen.size, tag])
	var sheet := screen.get_node_or_null("Sheet") as Panel
	if sheet == null or not sheet.visible or sheet.size.x < 250.0 or sheet.size.y < 400.0:
		failures.append("smith_sheet_%s" % tag)
		return
	var style := sheet.get_theme_stylebox("panel") as StyleBoxFlat
	if style == null or style.bg_color.a < 0.99:
		failures.append("smith_backing_%s" % tag)
		return
	var image := tree.root.get_viewport().get_texture().get_image()
	var origin := sheet.get_global_rect().position
	var sample_at := Vector2i(int(origin.x + 12), int(origin.y + 12))
	if sample_at.x < 0 or sample_at.y < 0 or sample_at.x >= image.get_width() or sample_at.y >= image.get_height():
		failures.append("smith_pixel_%s" % tag)
	else:
		var pixel := image.get_pixelv(sample_at)
		if not _parchment(pixel):
			failures.append("smith_parchment_%s" % tag)
			push_error("Touch check: smith pixel %s on %s" % [pixel, tag])
	var labels: Array[Label] = []
	_collect_labels(sheet, labels)
	var seen: Array[Rect2] = []
	var wanted := false
	for label in labels:
		if not _parented_to(label, sheet):
			failures.append("smith_parent_%s" % tag)
			return
		var fg := label.get_theme_color("font_color")
		var bg := _label_back(label, style.bg_color)
		if bg.a < 0.99 or Widgets.contrast_ratio(fg, bg) < 4.5:
			failures.append("smith_contrast_%s" % tag)
			push_error("Touch check: '%s' contrast on %s" % [label.text, tag])
		if tag == "craft" and label.text == "Gel Edge":
			wanted = true
		if tag == "upgrade" and label.text.contains("Oath Blade"):
			wanted = true
		var rect := _clipped_rect(label)
		if rect.size.x <= 0.5 or rect.size.y <= 0.5:
			continue
		var sheet_rect := sheet.get_global_rect().grow(1.0)
		if not sheet_rect.encloses(rect):
			failures.append("smith_overflow_%s" % tag)
			push_error("Touch check: '%s' outside the smith sheet on %s" % [label.text, tag])
		var raw := label.get_global_rect()
		var bounds := sheet.get_global_rect()
		if raw.position.x < bounds.position.x - 1.0 or raw.end.x > bounds.end.x + 1.0:
			failures.append("smith_wide_%s" % tag)
			push_error("Touch check: '%s' wider than the smith sheet on %s" % [label.text, tag])
		for other in seen:
			var hit := rect.intersection(other)
			if hit.size.x > 1.0 and hit.size.y > 1.0:
				failures.append("smith_overlap_%s" % tag)
				push_error("Touch check: '%s' overlaps another line on %s" % [label.text, tag])
				break
		seen.append(rect)
	if not wanted:
		failures.append("smith_copy_%s" % tag)
		push_error("Touch check: smith %s copy missing" % tag)


static func _label_back(label: Label, fallback: Color) -> Color:
	var cursor: Node = label
	while cursor:
		if cursor is Panel:
			var box := (cursor as Panel).get_theme_stylebox("panel") as StyleBoxFlat
			if box != null:
				return box.bg_color
		cursor = cursor.get_parent()
	return fallback


static func _parchment(color: Color) -> bool:
	return color.a > 0.95 and color.r > 0.75 and color.g > 0.6 and color.b > 0.45 and color.b < color.r


static func _parented_to(node: Node, ancestor: Node) -> bool:
	var cursor := node.get_parent()
	while cursor:
		if cursor == ancestor:
			return true
		cursor = cursor.get_parent()
	return false


static func _clipped_rect(control: Control) -> Rect2:
	var rect := control.get_global_rect()
	var node: Node = control
	while node:
		if node is Control and (node as Control).clip_contents:
			rect = rect.intersection((node as Control).get_global_rect())
		node = node.get_parent()
	return rect


static func _collect_labels(node: Node, into: Array[Label]) -> void:
	if node is Label:
		into.append(node)
	for child in node.get_children():
		_collect_labels(child, into)


static func _vital(current: int, maximum: int) -> String:
	return Formulas.vital_text(current, maximum)


static func _bottom_and_levels(host: Node, tree: SceneTree, failures: Array[String]) -> void:
	GameState.new_campaign([
		_hero("mason", "delver", "paladin"),
		_hero("nim", "glenfolk", "cleric"),
	])
	GameState.place_id = "candlewick"
	var session := SessionScreen.new()
	await _mount(host, tree, session)
	session.show_hub()
	await tree.process_frame
	await tree.process_frame
	_assert_bottom(session, failures, "hub")
	session.show_hub()
	await tree.process_frame
	_assert_bottom(session, failures, "hub_again")
	if _count_named(session, "HpDigits") != GameState.party.size():
		failures.append("hub_hp_dup")
		push_error("Touch check: chair health numbers were rebuilt on top of the old ones")
	session.visible = false
	var map := MapScreen.new()
	host.add_child(map)
	map.set_anchors_preset(Control.PRESET_FULL_RECT)
	await tree.process_frame
	await tree.process_frame
	_assert_bottom(map, failures, "map")
	map.queue_free()
	var quest := QuestScreen.new()
	quest.setup("log")
	host.add_child(quest)
	quest.set_anchors_preset(Control.PRESET_FULL_RECT)
	await tree.process_frame
	_assert_bottom(quest, failures, "quest")
	quest.queue_free()
	session.visible = true
	await tree.process_frame
	var member: Dictionary = GameState.party[0]
	var before := GameState.combat_stats(member)
	member["hp"] = maxi(1, int(before["max_hp"]) / 2)
	member["mp"] = maxi(0, int(before["max_mp"]) / 2)
	session.push_vitals(0)
	await tree.process_frame
	var hp_digits := _chair_digits(session, 0, "HpDigits")
	var mp_digits := _chair_digits(session, 0, "MpDigits")
	if hp_digits == null or hp_digits.text != _vital(int(member["hp"]), int(before["max_hp"])):
		failures.append("pool_half")
		push_error("Touch check: half health did not reach the chair")
	var half_fill := session.bar_fill_width("p0")
	if half_fill < 1.0 or half_fill > 30.0:
		failures.append("pool_half_fill")
		push_error("Touch check: half health fill is %s" % half_fill)
	if not GameState.give_item("bread_charm", 1) or GameState.equip_item(0, "bread_charm", "trinket") != "":
		failures.append("pool_charm")
		push_error("Touch check: bread charm did not equip")
	else:
		session.push_vitals(0)
		var charmed := GameState.combat_stats(member)
		if int(charmed["max_hp"]) != int(before["max_hp"]) + 10:
			failures.append("pool_charm_max")
			push_error("Touch check: bread charm max is %s" % charmed["max_hp"])
		if hp_digits.text != _vital(int(member["hp"]), int(charmed["max_hp"])):
			failures.append("pool_charm_text")
			push_error("Touch check: bread charm chair reads %s" % hp_digits.text)
		if int(member["hp"]) <= int(before["max_hp"]) / 2:
			failures.append("pool_charm_current")
			push_error("Touch check: bread charm did not raise current health")
	if not GameState.give_item("wick_ring", 1) or GameState.equip_item(0, "wick_ring", "trinket") != "":
		failures.append("pool_ring")
	else:
		session.push_vitals(0)
		var ringed := GameState.combat_stats(member)
		if int(ringed["max_mp"]) <= int(before["max_mp"]) or mp_digits == null or mp_digits.text != _vital(int(member["mp"]), int(ringed["max_mp"])):
			failures.append("pool_ring_text")
			push_error("Touch check: wick ring did not refresh energy")
	var armed := GameState.combat_stats(member)
	if GameState.unequip_slot(0, "trinket:0") != "":
		failures.append("pool_unequip")
	else:
		session.push_vitals(0)
		var dropped := GameState.combat_stats(member)
		if int(dropped["max_hp"]) >= int(armed["max_hp"]) or int(member["hp"]) > int(dropped["max_hp"]):
			failures.append("pool_clamp")
			push_error("Touch check: unequip left health at %s/%s" % [member["hp"], dropped["max_hp"]])
		elif hp_digits.text != _vital(int(member["hp"]), int(dropped["max_hp"])):
			failures.append("pool_clamp_text")
	if not GameState.give_item("silk_mail", 1) or GameState.equip_item(0, "silk_mail", "armor") != "":
		failures.append("pool_mail")
	else:
		var mailed := GameState.combat_stats(member)
		GameState.gold = 400
		GameState.give_item("bat_ear", 2)
		var worn_max := int(mailed["max_hp"])
		if GameState.upgrade_worn(0, "armor") != "":
			failures.append("pool_upgrade")
			push_error("Touch check: silk mail did not temper")
		else:
			session.push_vitals(0)
			var tempered := GameState.combat_stats(member)
			if int(tempered["max_hp"]) <= worn_max or hp_digits.text != _vital(int(member["hp"]), int(tempered["max_hp"])):
				failures.append("pool_upgrade_text")
				push_error("Touch check: tempered mail reads %s" % hp_digits.text)
	session.sync_unit({"id": "p0", "hp": 40, "max_hp": 100, "mp": 10, "max_mp": 20})
	var wide := session.bar_fill_width("p0")
	var wide_mp := session.mp_bar_fill_width("p0")
	session.sync_unit({"id": "p0", "hp": 40, "max_hp": 200, "mp": 10, "max_mp": 40})
	if session.bar_fill_width("p0") >= wide or session.mp_bar_fill_width("p0") >= wide_mp:
		failures.append("pool_max_fill")
		push_error("Touch check: a higher max did not shrink the fill")
	if hp_digits.text != "40/200" or mp_digits.text != "10/40":
		failures.append("pool_max_text")
		push_error("Touch check: max-only sync reads %s %s" % [hp_digits.text, mp_digits.text])
	var clamped_hp := Formulas.fit_pool(40, 200, 30, false)
	var clamped_mp := Formulas.fit_pool(10, 40, 8, true)
	session.sync_unit({"id": "p0", "hp": clamped_hp, "max_hp": 30, "mp": clamped_mp, "max_mp": 8})
	if clamped_hp != 30 or clamped_mp != 8 or hp_digits.text != "30/30" or mp_digits.text != "8/8":
		failures.append("pool_drop_text")
		push_error("Touch check: a lower max reads %s %s" % [hp_digits.text, mp_digits.text])
	session.show_hub()
	await tree.process_frame
	var flow := BattleFlow.new()
	flow.hurry = true
	flow.view = session
	session.add_child(flow)
	flow._build_units([{"id": "puddleblob"}])
	var unit: Dictionary = flow.units[0]
	unit["hp"] = mini(40, int(unit["max_hp"]))
	session.present_units(flow.units)
	session.show_member_bar(0, {}, "", {})
	await tree.process_frame
	_assert_bottom(session, failures, "combat")
	session.show_member_bar(0, {}, "", {})
	await tree.process_frame
	_assert_bottom(session, failures, "combat_again")
	var buff_max := int(unit["max_hp"])
	var buff_mp := int(unit["max_mp"])
	unit["conditions"] = [{"id": "bulk", "timer": 3, "body": 2, "mind": 1, "hp_pct": 0.1, "mp_pct": 0.1}]
	flow._apply_condition_shifts(unit)
	hp_digits = _chair_digits(session, 0, "HpDigits")
	mp_digits = _chair_digits(session, 0, "MpDigits")
	if int(unit["max_hp"]) <= buff_max or int(unit["max_mp"]) <= buff_mp:
		failures.append("pool_buff")
		push_error("Touch check: the buff left pools at %s/%s" % [unit["max_hp"], unit["max_mp"]])
	elif hp_digits == null or hp_digits.text != _vital(int(unit["hp"]), int(unit["max_hp"])) or mp_digits.text != _vital(int(unit["mp"]), int(unit["max_mp"])):
		failures.append("pool_buff_text")
		push_error("Touch check: buff chair reads %s %s" % [hp_digits.text, mp_digits.text])
	var debuff_hp := int(unit["hp"])
	unit["conditions"] = [{"id": "wilt", "timer": 2, "body": -6}]
	flow._apply_condition_shifts(unit)
	if int(unit["max_hp"]) >= buff_max or int(unit["hp"]) > int(unit["max_hp"]):
		failures.append("pool_debuff")
		push_error("Touch check: the wilt left health at %s/%s" % [unit["hp"], unit["max_hp"]])
	elif _chair_digits(session, 0, "HpDigits").text != _vital(int(unit["hp"]), int(unit["max_hp"])):
		failures.append("pool_debuff_text")
	elif int(unit["hp"]) > debuff_hp and int(unit["max_hp"]) < debuff_hp:
		failures.append("pool_debuff_clamp")
	session.show_hub()
	await tree.process_frame
	var body_before := GameState.combat_stats(member)
	member["growth"]["body"] = int(member["growth"].get("body", 0)) + 1
	GameState._fit_pools(member, body_before, GameState.combat_stats(member))
	session.push_vitals(0)
	var body_after := GameState.combat_stats(member)
	hp_digits = _chair_digits(session, 0, "HpDigits")
	if int(body_after["max_hp"]) <= int(body_before["max_hp"]) or hp_digits == null or hp_digits.text != _vital(int(member["hp"]), int(body_after["max_hp"])):
		failures.append("pool_body")
		push_error("Touch check: body did not refresh health, reads %s" % (hp_digits.text if hp_digits else ""))
	var mind_before := body_after
	member["growth"]["mind"] = int(member["growth"].get("mind", 0)) + 1
	GameState._fit_pools(member, mind_before, GameState.combat_stats(member))
	session.push_vitals(0)
	var mind_after := GameState.combat_stats(member)
	mp_digits = _chair_digits(session, 0, "MpDigits")
	if int(mind_after["max_mp"]) <= int(mind_before["max_mp"]) or mp_digits == null or mp_digits.text != _vital(int(member["mp"]), int(mind_after["max_mp"])):
		failures.append("pool_mind")
		push_error("Touch check: mind did not refresh energy")
	for hero in GameState.party:
		hero["xp"] = Formulas.xp_to_next(int(hero["level"])) - 1
	GameState.level_queue.clear()
	GameState.arm_battle()
	var victory = flow._grant_victory()
	var continued: bool = await _until(tree, func() -> bool: return _find_button(session, "Continue") != null, 180)
	if not continued:
		failures.append("victory_continue")
		push_error("Touch check: victory did not offer Continue")
		session.queue_free()
		return
	await _tap(tree, _find_button(session, "Continue").get_global_rect().get_center())
	await victory
	GameState.disarm_battle()
	flow._listen(false)
	if GameState.peek_level() < 0:
		failures.append("victory_level")
		push_error("Touch check: victory did not queue a level choice")
		session.queue_free()
		return
	var queued := GameState.level_queue.size()
	if queued < 2:
		failures.append("victory_queue")
		push_error("Touch check: both heroes should choose, queue is %s" % queued)
	var resolving = session.resolve_level_ups()
	var picks := 0
	while picks < 6 and GameState.peek_level() >= 0:
		var shown: bool = await _until(tree, func() -> bool: return session.get_node_or_null("LevelPanel") != null)
		if not shown:
			failures.append("level_panel")
			break
		_assert_level_panel(session, tree, failures, "level_%d" % picks)
		var outside := GameState.level_queue.size()
		await _tap(tree, Vector2(4, 4))
		await tree.process_frame
		if GameState.level_queue.size() != outside or session.get_node_or_null("LevelPanel") == null:
			failures.append("level_skip")
			push_error("Touch check: the level choice closed without a pick")
			break
		var take := _first_take(session)
		if take == null:
			failures.append("level_take")
			break
		var taken_name := str(take.name)
		await _tap(tree, take.get_global_rect().get_center())
		picks += 1
		var advanced: bool = await _until(tree, func() -> bool:
			return session.find_child(taken_name, true, false) == null or GameState.peek_level() < 0
		)
		if not advanced:
			failures.append("level_commit")
			break
	await resolving
	if GameState.peek_level() >= 0 or picks < 2:
		failures.append("level_remaining")
		push_error("Touch check: level choices left %s after %s picks" % [GameState.level_queue.size(), picks])
	var grown := false
	for hero in GameState.party:
		if LevelRules.sheet_line(hero, {}) != "":
			grown = true
	if not grown:
		failures.append("level_growth")
	GameState.save_game()
	var kept_growth: Dictionary = LevelRules.read(GameState.party[0])
	var kept_queue: Array = GameState.level_queue.duplicate()
	GameState.party[0]["growth"] = LevelRules.blank()
	GameState.level_queue = [0]
	if not GameState.load_game():
		failures.append("level_load")
	elif JSON.stringify(LevelRules.read(GameState.party[0])) != JSON.stringify(kept_growth) or GameState.level_queue.size() != kept_queue.size():
		failures.append("level_save")
		push_error("Touch check: growth or the queue did not survive the save")
	session.show_hub()
	await tree.process_frame
	_assert_bottom(session, failures, "after_level")
	var gear := GearScreen.new()
	gear.setup("hero")
	session.add_child(gear)
	gear.set_anchors_preset(Control.PRESET_FULL_RECT)
	await tree.process_frame
	await tree.process_frame
	_assert_bottom(gear, failures, "gear")
	var sheet_hit := false
	var labels: Array[Label] = []
	_collect_labels(gear, labels)
	for label in labels:
		if label.text.begins_with("Grown:"):
			sheet_hit = true
	if not sheet_hit:
		failures.append("level_sheet")
		push_error("Touch check: the character sheet does not list the growth")
	var smith_tab := gear.find_child("Tab_smith", true, false) as Button
	if smith_tab != null:
		await _tap(tree, smith_tab.get_global_rect().get_center())
		var smith_open: bool = await _until(tree, func() -> bool: return session.find_child("SmithScreen", true, false) != null)
		if smith_open:
			_assert_bottom(session.find_child("SmithScreen", true, false), failures, "smith")
	gear.queue_free()
	await tree.process_frame
	session.show_member_bar(0, {}, "", {})
	await tree.process_frame
	_assert_bottom(session, failures, "combat_after_level")
	flow._build_units([{"id": "puddleblob"}])
	var learned: Dictionary = flow.units[0].get("choice_ranks", {})
	var expected: Dictionary = LevelRules.read(GameState.party[0])["skills"]
	if not expected.is_empty() and learned.is_empty():
		failures.append("level_combat")
		push_error("Touch check: the skill rank did not reach the battle")
	session.queue_free()
	await tree.process_frame


static func _chair_digits(session: SessionScreen, index: int, node_name: String) -> DigitReadout:
	if index < 0 or index >= session._seats.size():
		return null
	return session._seats[index].get_node_or_null("BarHost/%s" % node_name) as DigitReadout


static func _count_named(node: Node, node_name: String) -> int:
	var count := 0
	if str(node.name) == node_name:
		count += 1
	for child in node.get_children():
		count += _count_named(child, node_name)
	return count


static func _first_take(session: Node) -> Button:
	var found: Array[Button] = []
	_collect_buttons(session.get_node_or_null("LevelPanel"), found)
	for button in found:
		if str(button.name).begins_with("Level_") and button.text == "Take":
			return button
	return null


static func _assert_level_panel(session: Node, tree: SceneTree, failures: Array[String], tag: String) -> void:
	var panel := session.get_node_or_null("LevelPanel") as Control
	if panel == null:
		failures.append("level_missing_%s" % tag)
		return
	var sheet := panel.get_node_or_null("Sheet") as Panel
	if sheet == null or sheet.size.x < 240.0 or sheet.size.y < 200.0:
		failures.append("level_sheet_size_%s" % tag)
		return
	var style := sheet.get_theme_stylebox("panel") as StyleBoxFlat
	if style == null or style.bg_color.a < 0.99:
		failures.append("level_opaque_%s" % tag)
		return
	var image := tree.root.get_viewport().get_texture().get_image()
	var origin := sheet.get_global_rect().position
	var sample_at := Vector2i(int(origin.x + 14), int(origin.y + 14))
	if sample_at.x < 0 or sample_at.y < 0 or sample_at.x >= image.get_width() or sample_at.y >= image.get_height():
		failures.append("level_pixel_%s" % tag)
	else:
		var pixel := image.get_pixelv(sample_at)
		if not _parchment(pixel):
			failures.append("level_parchment_%s" % tag)
			push_error("Touch check: level sheet pixel %s on %s" % [pixel, tag])
	var takes := 0
	var buttons: Array[Button] = []
	_collect_buttons(panel, buttons)
	for button in buttons:
		var word := button.text.to_lower()
		if word == "close" or word == "skip" or word == "later" or word == "back":
			failures.append("level_dismiss_%s" % tag)
			push_error("Touch check: level panel offers %s" % button.text)
		if button.text == "Take":
			takes += 1
			if button.size.y < 40.0:
				failures.append("level_touch_%s" % tag)
	if takes != 3:
		failures.append("level_choices_%s" % tag)
		push_error("Touch check: level panel has %s choices on %s" % [takes, tag])
	var labels: Array[Label] = []
	_collect_labels(panel, labels)
	var seen: Array[Rect2] = []
	var view := Rect2(Vector2.ZERO, Layout.viewport_size())
	for label in labels:
		if label.text == "":
			continue
		var fg := label.get_theme_color("font_color")
		var bg := _label_back(label, style.bg_color)
		if Widgets.contrast_ratio(fg, bg) < 4.5:
			failures.append("level_contrast_%s" % tag)
			push_error("Touch check: '%s' contrast on %s" % [label.text, tag])
		if label.autowrap_mode == TextServer.AUTOWRAP_OFF:
			failures.append("level_wrap_%s" % tag)
		var rect := _clipped_rect(label)
		if not view.grow(1.0).encloses(rect) or not sheet.get_global_rect().grow(1.0).encloses(rect):
			failures.append("level_overflow_%s" % tag)
			push_error("Touch check: '%s' %s leaves the sheet on %s" % [label.text, rect, tag])
		for other in seen:
			var hit := rect.intersection(other)
			if hit.size.x > 1.0 and hit.size.y > 1.0:
				failures.append("level_overlap_%s" % tag)
				push_error("Touch check: '%s' overlaps another line on %s" % [label.text, tag])
				break
		seen.append(rect)
	for button in buttons:
		var rect := _clipped_rect(button)
		for other in seen:
			var hit := rect.intersection(other)
			if hit.size.x > 1.0 and hit.size.y > 1.0:
				failures.append("level_button_overlap_%s" % tag)
				push_error("Touch check: '%s' covers a line on %s" % [button.text, tag])
				break


static func _assert_bottom(root: Node, failures: Array[String], tag: String) -> void:
	var band := Rect2(0, 390, 270, 90)
	var marks: Array = []
	_gather_marks(root, marks)
	var in_band: Array = []
	for mark in marks:
		var caption := str(mark["text"])
		if caption.to_upper() == "ATTACK" or caption.to_upper() == "COVER" or caption.to_upper() == "PAS":
			failures.append("bottom_doubled_%s" % tag)
			push_error("Touch check: '%s' is painted twice on %s" % [caption, tag])
		var rect: Rect2 = mark["rect"]
		var hit := rect.intersection(band)
		if hit.size.x > 0.5 and hit.size.y > 0.5:
			in_band.append(mark)
	for i in in_band.size():
		for j in range(i + 1, in_band.size()):
			var left: Rect2 = in_band[i]["rect"]
			var right: Rect2 = in_band[j]["rect"]
			var overlap := left.intersection(right)
			if overlap.size.x > 1.0 and overlap.size.y > 1.0:
				failures.append("bottom_overlap_%s" % tag)
				push_error("Touch check: '%s' overlaps '%s' on %s" % [in_band[i]["text"], in_band[j]["text"], tag])
				return


static func _gather_marks(node: Node, into: Array) -> void:
	if node == null:
		return
	if node is CanvasItem and not (node as CanvasItem).visible:
		return
	if node is Label:
		var label := node as Label
		if label.text != "":
			var rect := _clipped_rect(label)
			if rect.size.x > 0.5 and rect.size.y > 0.5:
				into.append({"text": label.text, "rect": rect})
	elif node is Button:
		var button := node as Button
		if button.text != "":
			var button_rect := _clipped_rect(button)
			if button_rect.size.x > 0.5 and button_rect.size.y > 0.5:
				into.append({"text": button.text, "rect": button_rect})
	elif node is TextureRect and node.has_meta("caption"):
		var caption := str(node.get_meta("caption"))
		if caption != "":
			var caption_rect := _clipped_rect(node as Control)
			if caption_rect.size.x > 0.5 and caption_rect.size.y > 0.5:
				into.append({"text": caption, "rect": caption_rect})
	elif node is DigitReadout:
		var digits := node as DigitReadout
		if digits.text != "":
			var digit_rect := _clipped_rect(digits)
			if digit_rect.size.x > 0.5 and digit_rect.size.y > 0.5:
				into.append({"text": digits.text, "rect": digit_rect})
	for child in node.get_children():
		_gather_marks(child, into)
