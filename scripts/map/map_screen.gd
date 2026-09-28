extends Control
class_name MapScreen
## Vertical node map. Drag to scroll. Tap a place, tap again or press Travel.
## Stop sits in the bottom thumb bar during a multi-hop trip.

signal closed
signal arrived(place_id: String, ambush: bool)

var _cam := Vector2.ZERO
var _drag := false
var _moved := 0.0
var _selected := ""
var _traveling := false
var _stop := false
var _content: Control
var _places: Control
var _select_mark: ColorRect
var _pawn: TextureRect
var _info: Label
var _travel_button: Button
var _stop_button: Button
var _back_button: Button
var _die: Label
var _rng := RandomNumberGenerator.new()
var _preview := false


func _ready() -> void:
	_rng.randomize()
	_build()
	if _preview:
		_selected = "briar_cross"
		_focus_on(Vector2(150, 370), false)
	else:
		_focus_on(_place_pos(GameState.place_id), false)
	_refresh_hud()
	queue_redraw()


func stage_preview() -> void:
	_preview = true
	_selected = "briar_cross"


func _build() -> void:
	var parchment := ColorRect.new()
	parchment.color = SpriteCatalog.CREAM_DARK
	parchment.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(parchment)

	var top := Layout.rect("map", "top_bar")
	var gold := Widgets.label("", Layout.font_small(), SpriteCatalog.INK)
	gold.name = "Gold"
	Layout.place(gold, top)
	add_child(gold)

	var view_rect := Layout.rect("map", "view")
	var clip := Control.new()
	clip.name = "Clip"
	Layout.place(clip, view_rect)
	clip.clip_contents = true
	add_child(clip)

	var content_size := Layout.vec("map", "content")
	_content = Control.new()
	_content.name = "Content"
	_content.set_script(load("res://scripts/map/map_canvas.gd"))
	_content.size = content_size
	_content.custom_minimum_size = content_size
	clip.add_child(_content)
	_spawn_places(content_size)
	_pawn = TextureRect.new()
	_pawn.texture = ArtPack.frame_texture("map/pawn_walk.png", 0, Vector2(24, 20))
	_pawn.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_pawn.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_pawn.stretch_mode = TextureRect.STRETCH_SCALE
	_pawn.size = Vector2(24, 20)
	_content.add_child(_pawn)
	_pawn.position = _place_pos(GameState.place_id) - Vector2(12, 19)

	var controls := Widgets.panel()
	Layout.place(controls, Layout.rect("map", "controls"))
	add_child(controls)
	_info = Widgets.label("Pick a place.", Layout.font_tiny())
	Widgets.enable_wrap(_info)
	var info_rect := Layout.rect("map", "info")
	_info.position = info_rect.position
	_info.size = info_rect.size
	controls.add_child(_info)
	_die = Widgets.label("", Layout.font_small())
	_die.position = Vector2(8, 4)
	_die.size = Vector2(controls.size.x - 16, 48)
	_die.visible = false
	controls.add_child(_die)
	var row := HBoxContainer.new()
	var row_rect := Layout.rect("map", "travel_row")
	row.position = row_rect.position
	row.size = row_rect.size
	row.add_theme_constant_override("separation", 6)
	controls.add_child(row)
	_back_button = Widgets.make_button("Back", Vector2(70, 46))
	_back_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_back_button.pressed.connect(func(): closed.emit())
	row.add_child(_back_button)
	_travel_button = Widgets.make_button("Travel", Vector2(110, 46))
	_travel_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_travel_button.pressed.connect(_on_travel_pressed)
	row.add_child(_travel_button)
	_stop_button = Widgets.make_button("Stop", Vector2(180, 46))
	_stop_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_stop_button.visible = false
	_stop_button.pressed.connect(func(): _stop = true)
	row.add_child(_stop_button)
	clip.gui_input.connect(_on_clip_input)


func _on_clip_input(event: InputEvent) -> void:
	if _traveling:
		return
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		if event.pressed:
			_drag = true
			_moved = 0.0
		else:
			_drag = false
			if _moved < 8.0:
				_tap(event.position)
	elif event is InputEventMouseMotion and _drag:
		_moved += event.relative.length()
		if _moved >= 8.0:
			_pan(-event.relative)


func _tap(local_pos: Vector2) -> void:
	var map_pos: Vector2 = local_pos - _content.position
	var hit := ""
	var best := 24.0
	for place_id in ContentDB.places.keys():
		var dist: float = map_pos.distance_to(_place_pos(str(place_id)))
		if dist < best:
			best = dist
			hit = str(place_id)
	if hit == "":
		return
	Sfx.play("tap")
	if hit == _selected and hit != GameState.place_id:
		_begin_travel()
		return
	_selected = hit
	_refresh_hud()
	_content.queue_redraw()


func _on_travel_pressed() -> void:
	if _selected == "" or _selected == GameState.place_id:
		return
	_begin_travel()


func _begin_travel() -> void:
	if _traveling:
		return
	var path: Array = RouteFinder.fewest_hops(GameState.place_id, _selected, ContentDB.edges)
	if path.size() < 2:
		_info.text = "No road goes there."
		return
	_stop = false
	_traveling = true
	_set_travel_buttons(true)
	_run_route(path)


func _run_route(path: Array) -> void:
	var ambush := false
	for hop in range(1, path.size()):
		if _stop:
			break
		var origin := str(path[hop - 1])
		var dest := str(path[hop])
		var cost := Formulas.hop_gold(int(ContentDB.place(origin)["level"]), int(ContentDB.place(dest)["level"]))
		if GameState.gold < cost:
			_info.text = "Not enough gold for the next road."
			break
		GameState.gold -= cost
		_refresh_gold()
		var kind: String = await _hop(origin, dest, cost)
		GameState.place_id = dest
		GameState.hops += 1
		GameState.save_game()
		if kind == "ambush" or kind == "lost":
			ambush = true
			break
	_traveling = false
	_set_travel_buttons(false)
	_die.visible = false
	_info.visible = true
	_pawn.position = _place_pos(GameState.place_id) - Vector2(12, 19)
	_content.set_meta("route", PackedVector2Array())
	_refresh_hud()
	arrived.emit(GameState.place_id, ambush)


func _hop(origin: String, dest: String, cost: int) -> String:
	var points := RouteFinder.edge_points(origin, dest, ContentDB.edges, ContentDB.places)
	var length := RouteFinder.polyline_length(points)
	_content.set_meta("route", points)
	_content.queue_redraw()
	var midpoint: Vector2 = RouteFinder.point_along(points, length * 0.5)
	_spring_to(midpoint)
	var needs_roll: bool = (ContentDB.place(dest).get("monsters", []) as Array).size() > 0
	var approach := create_tween()
	approach.tween_method(_set_hop_alpha.bind(points, length), 0.0, 0.5, Timing.HOP_APPROACH)
	var kind := "safe"
	if needs_roll:
		await _wait(Timing.travel_roll_lead())
		kind = await _travel_roll(int(ContentDB.place(dest)["level"]))
		if approach.is_running():
			await approach.finished
	else:
		await approach.finished
	if kind == "ambush" or kind == "lost":
		await _show_bang(midpoint)
		_pawn.visible = false
		return kind
	if kind == "free":
		GameState.gold += cost
		_refresh_gold()
	var sprint := create_tween()
	sprint.tween_method(_set_hop_alpha.bind(points, length), 0.5, 1.0, Timing.HOP_SPRINT)
	await sprint.finished
	_die.visible = false
	_info.visible = true
	return kind


func _set_hop_alpha(alpha: float, points: PackedVector2Array, length: float) -> void:
	var pos := RouteFinder.point_along(points, length * alpha)
	_pawn.visible = true
	_pawn.position = pos - Vector2(12, 19)
	if points.size() >= 2:
		var ahead := RouteFinder.point_along(points, minf(length, length * alpha + 4.0))
		_pawn.flip_h = ahead.x < pos.x


func _travel_roll(dest_level: int) -> String:
	var p := Formulas.travel_p(dest_level, GameState.party_average())
	_info.visible = false
	_die.visible = true
	_die.text = "Road roll\nNeed %d+" % (p + 1)
	_die.add_theme_color_override("font_color", SpriteCatalog.INK)
	Sfx.play("dice")
	await _wait(Timing.TRAVEL_ROLL_SPIN)
	var faced := clampi(_rng.randi_range(1, 20) + GameState.travel_bonus(), 1, 20)
	var branch := _rng.randi_range(2, 4)
	var kind := Formulas.classify_travel_roll(faced, p, branch)
	match kind:
		"lost":
			_die.text = "Got lost"
			_die.add_theme_color_override("font_color", SpriteCatalog.HP)
			Sfx.play("bad")
		"ambush":
			_die.text = "Ambush!"
			_die.add_theme_color_override("font_color", SpriteCatalog.HP)
			Sfx.play("ambush")
		"safe":
			_die.text = "Safe travel"
			_die.add_theme_color_override("font_color", SpriteCatalog.SAFE)
			Sfx.play("good")
		"free":
			_die.text = "Free travel"
			_die.add_theme_color_override("font_color", SpriteCatalog.FREE)
			Sfx.play("good")
		_:
			_die.text = "Found a Hearth Tonic"
			_die.add_theme_color_override("font_color", SpriteCatalog.GOLD)
			GameState.give_item("tonic", 1)
			Sfx.play("good")
	var remain := Timing.TRAVEL_ROLL_VISIBLE - Timing.TRAVEL_ROLL_SPIN
	await _wait(remain)
	return kind


func _show_bang(at: Vector2) -> void:
	var bang := TextureRect.new()
	bang.texture = SpriteCatalog.ui("bang")
	bang.size = Vector2(16, 16)
	bang.position = at + Vector2(-8, 8)
	_content.add_child(bang)
	await _wait(0.8)
	bang.queue_free()


func _spring_to(focus: Vector2) -> void:
	var view := Layout.rect("map", "view").size
	var content := Layout.vec("map", "content")
	var target := RouteFinder.spring_offset(view, content, focus)
	var tween := create_tween()
	tween.tween_method(_set_cam, _cam, target, 0.55).set_trans(Tween.TRANS_SPRING).set_ease(Tween.EASE_OUT)


func _focus_on(focus: Vector2, animate: bool) -> void:
	var view := Layout.rect("map", "view").size
	var content := Layout.vec("map", "content")
	var target := RouteFinder.spring_offset(view, content, focus)
	if animate:
		_spring_to(focus)
	else:
		_set_cam(target)


func _set_cam(cam: Vector2) -> void:
	_cam = cam
	var view := Layout.rect("map", "view").size
	var content := Layout.vec("map", "content")
	var x := (view.x - content.x) * 0.5 - cam.x
	_content.position = Vector2(x, -cam.y)


func _pan(delta: Vector2) -> void:
	var view := Layout.rect("map", "view").size
	var content := Layout.vec("map", "content")
	var next := _cam + delta
	var max_x := maxf(0.0, content.x - view.x)
	var max_y := maxf(0.0, content.y - view.y)
	next.x = clampf(next.x, 0.0, max_x)
	next.y = clampf(next.y, 0.0, max_y)
	_set_cam(next)


func paint_route(canvas: Control) -> void:
	var grass := ArtPack.texture("map/tile_grass.png")
	var content := Layout.vec("map", "content")
	if grass:
		var y := 0.0
		while y < content.y:
			var x := 0.0
			while x < content.x:
				var tile := grass
				if int(x / 16.0 + y / 16.0) % 7 == 0:
					var flowers := ArtPack.texture("map/tile_grass_flowers.png")
					if flowers:
						tile = flowers
				canvas.draw_texture(tile, Vector2(x, y))
				x += 16.0
			y += 16.0
	var points: PackedVector2Array = _content.get_meta("route", PackedVector2Array())
	if points.is_empty() and _selected != "" and not _traveling:
		var path: Array = RouteFinder.fewest_hops(GameState.place_id, _selected, ContentDB.edges)
		points = PackedVector2Array()
		for i in range(1, path.size()):
			var hop: PackedVector2Array = RouteFinder.edge_points(str(path[i - 1]), str(path[i]), ContentDB.edges, ContentDB.places)
			for point in hop:
				points.append(point)
	if not points.is_empty():
		var length := RouteFinder.polyline_length(points)
		var dist := 0.0
		while dist < length:
			var point := RouteFinder.point_along(points, dist)
			canvas.draw_rect(Rect2(point - Vector2(1, 1), Vector2(2, 2)), Color("5a3a18"))
			dist += 8.0


func place_node_count() -> int:
	if _places == null:
		return 0
	var count := 0
	for child in _places.get_children():
		if child is TextureRect and (child as TextureRect).texture != null:
			count += 1
	return count


func backdrop_ready() -> bool:
	var grass := ArtPack.texture("map/tile_grass.png")
	return grass != null and grass.get_width() > 0


func _spawn_places(content_size: Vector2) -> void:
	_places = Control.new()
	_places.name = "Places"
	_places.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_places.position = Vector2.ZERO
	_places.size = content_size
	_content.add_child(_places)
	for place_id in ContentDB.places.keys():
		var id := str(place_id)
		var place: Dictionary = ContentDB.place(id)
		var sprite_name := str(place.get("sprite", "village"))
		var loc := ArtPack.texture("map/loc_%s.png" % sprite_name)
		if loc == null:
			push_error("Map place %s has no sprite map/loc_%s.png" % [id, sprite_name])
			continue
		var node := TextureRect.new()
		node.name = id
		node.texture = loc
		node.mouse_filter = Control.MOUSE_FILTER_IGNORE
		node.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		node.stretch_mode = TextureRect.STRETCH_SCALE
		node.position = _place_pos(id) - Vector2(16, 28)
		node.size = loc.get_size()
		_places.add_child(node)
	_select_mark = ColorRect.new()
	_select_mark.name = "SelectMark"
	_select_mark.color = SpriteCatalog.HIGHLIGHT
	_select_mark.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_select_mark.size = Vector2(6, 8)
	_select_mark.visible = false
	_content.add_child(_select_mark)


func _sync_select_mark() -> void:
	if _select_mark == null:
		return
	if _selected == "":
		_select_mark.visible = false
		return
	_select_mark.visible = true
	_select_mark.position = _place_pos(_selected) + Vector2(-3, -18)


func _refresh_hud() -> void:
	_sync_select_mark()
	_refresh_gold()
	if _selected == "":
		_info.text = "Tap a place.\nTap again to walk."
		_travel_button.disabled = true
		return
	var place: Dictionary = ContentDB.place(_selected)
	var here := _selected == GameState.place_id
	if here:
		_info.text = Widgets.place_blurb(place, 0, 0, true)
		_travel_button.disabled = true
		return
	var path: Array = RouteFinder.fewest_hops(GameState.place_id, _selected, ContentDB.edges)
	var hops := maxi(0, path.size() - 1)
	var cost := 0
	for i in range(1, path.size()):
		cost += Formulas.hop_gold(int(ContentDB.place(str(path[i - 1]))["level"]), int(ContentDB.place(str(path[i]))["level"]))
	_info.text = Widgets.place_blurb(place, hops, cost, false)
	_travel_button.disabled = hops <= 0
	_travel_button.text = "Travel %d" % cost


func _refresh_gold() -> void:
	var gold: Label = get_node("Gold")
	gold.text = "Gold %d   %s" % [GameState.gold, ContentDB.region.get("name", "")]


func _set_travel_buttons(traveling: bool) -> void:
	_travel_button.visible = not traveling
	_back_button.visible = not traveling
	_stop_button.visible = traveling
	_info.visible = not traveling


func _place_pos(id: String) -> Vector2:
	var place: Dictionary = ContentDB.place(id)
	return Vector2(float(place["x"]), float(place["y"]))


func _wait(seconds: float) -> void:
	if seconds <= 0.0:
		return
	await get_tree().create_timer(seconds).timeout
