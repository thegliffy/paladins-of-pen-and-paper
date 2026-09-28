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
