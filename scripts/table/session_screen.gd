extends Control
class_name SessionScreen
## Table scene for the hub and for combat. Positions come from Layout.

signal action_pressed(action_id: String)
signal target_pressed(target_id: String)
signal continue_pressed

var _monster_layer: Control
var _seat_layer: Control
var _seats: Array = []
var _monsters := {}
var _bars := {}
var _actions: Control
var _turn_tab: Panel
var _turn_name: Label
var _caption: Label
var _initiative: HBoxContainer
var _cards: HBoxContainer
var _banner: Label
var _modal: Control
var _dice: Control
var _dice_labels: Array = []
var _targeting := false
var _flickers: Array = []
var _table: TextureRect
var _gm: TextureRect
var _idle := 0.0
var _idle_frame := 0


func _ready() -> void:
	_build_chrome()
	show_hub()


func _process(delta: float) -> void:
	_idle += delta
	if _idle < 0.5:
		return
	_idle = 0.0
	_idle_frame = 1 - _idle_frame
	for id in _monsters.keys():
		var node: Control = _monsters[id]
		if not node.visible or bool(node.get_meta("acting", false)):
			continue
		_set_frame(node, _idle_frame)


func show_hub() -> void:
	clear_monsters()
	_set_table_visible(true)
	_initiative.visible = false
	_banner.visible = true
	var place: Dictionary = ContentDB.place(GameState.place_id)
	_banner.text = "%s   %d gold" % [place["name"], GameState.gold]
	_caption.text = str(place["description"])
	_sync_party()
	var fight: bool = (place.get("monsters", []) as Array).size() > 0
	set_actions([
		{"id": "travel", "label": "Travel", "icon": "icon_run"},
		{"id": "fight", "label": "Fight", "icon": "icon_attack", "disabled": not fight},
		{"id": "rest", "label": "Rest", "icon": "icon_cover"},
		{"id": "quest", "label": "Quest", "icon": "icon_skill"},
		{"id": "party", "label": "Party", "icon": "icon_item"},
	])
	_close_modal()


func location_banner(text: String) -> void:
	_caption.text = text
	await get_tree().create_timer(Timing.LOCATION_BANNER).timeout
	if is_instance_valid(self):
		var place: Dictionary = ContentDB.place(GameState.place_id)
		_caption.text = str(place.get("description", ""))


func stage_battle_preview() -> void:
	show_hub()
	_banner.visible = false
	_initiative.visible = true
	var rows := [
		{"id": "thicket_imp", "hp_ratio": 0.7},
		{"id": "cave_howler", "hp_ratio": 1.0},
		{"id": "puddleblob", "hp_ratio": 0.45},
	]
	var units := []
	for i in rows.size():
		var monster: Dictionary = ContentDB.monster(rows[i]["id"])
		var hp := Formulas.monster_max_hp(int(monster["level"]), int(monster["body"]), int(monster["mind"]))
		units.append({
			"id": "m%d" % i,
			"kind": rows[i]["id"],
			"name": monster["name"],
			"side": "monster",
			"hp": int(float(hp) * float(rows[i]["hp_ratio"])),
			"max_hp": hp,
			"mp": 0,
			"max_mp": 1,
			"back_row": bool(monster["back_row"]),
		})
	for unit in units:
		_add_monster(unit)
	_layout_monsters()
	_caption.text = "Mason's turn"
	var order := []
	order.append({"id": "p0", "side": "player", "index": 0})
	for unit in units:
		order.append({"id": unit["id"], "side": "monster", "kind": unit["kind"]})
	for index in range(1, GameState.party.size()):
		order.append({"id": "p%d" % index, "side": "player", "index": index})
	set_initiative(order, "p0")
	if GameState.party.size() > 1:
		GameState.party[1]["hp"] = int(int(GameState.combat_stats(GameState.party[1])["max_hp"]) * 0.62)
		_sync_party()
	_raise(0, true)
	show_member_bar(0, {}, "", {})


func intro(ambush: bool) -> void:
	set_actions([])
	clear_monsters()
	_set_table_visible(false)
	_initiative.visible = false
	_banner.visible = false
	_caption.text = "Ambush!" if ambush else "The table goes quiet."
	await get_tree().create_timer(Timing.BATTLE_INTRO).timeout
	_set_table_visible(true)
	_initiative.visible = true


func clear_monsters() -> void:
	for id in _monsters.keys():
		var node: Node = _monsters[id]
		if is_instance_valid(node):
			node.queue_free()
	_monsters.clear()
	for key in _bars.keys():
		if str(key).begins_with("m"):
			_bars.erase(key)


func present_units(units: Array) -> void:
	clear_monsters()
	for unit in units:
		if str(unit["side"]) == "monster":
			_add_monster(unit)
	_layout_monsters()
	_sync_from_units(units)


func set_initiative(order: Array, current_id: String) -> void:
	for child in _initiative.get_children():
		child.free()
	var area := Layout.rect("combat", "initiative")
	var combat: Dictionary = Layout.cfg()["combat"]
	var designed := int(combat.get("initiative_slot", 24))
	var sep := 2
	var count := maxi(1, order.size())
	var fit := int(floor((area.size.x - float(sep * (count - 1))) / float(count)))
	var slot_px := mini(designed, maxi(14, fit))
	for entry in order:
		var slot := Panel.new()
		slot.custom_minimum_size = Vector2(slot_px, slot_px)
		var box := StyleBoxFlat.new()
		box.bg_color = Color(0.15, 0.1, 0.08)
		box.border_color = SpriteCatalog.HIGHLIGHT if str(entry["id"]) == current_id else Color(0.3, 0.22, 0.16)
		box.set_border_width_all(2 if str(entry["id"]) == current_id else 1)
		slot.add_theme_stylebox_override("panel", box)
		var portrait := _mini_portrait(entry)
		portrait.set_anchors_preset(Control.PRESET_FULL_RECT)
		slot.add_child(portrait)
		_initiative.add_child(slot)


func set_actions(entries: Array) -> void:
	if _turn_tab:
		_turn_tab.visible = false
	_clear_action_buttons()
	if entries.is_empty():
		return
	var bar := Layout.rect("combat", "action_bar")
	var gap := 3.0
	var count := entries.size()
	var width := (bar.size.x - 4.0 - gap * float(count - 1)) / float(count)
	var x := 2.0
	for entry in entries:
		var button := Widgets.make_button(str(entry["label"]), Vector2(width, bar.size.y - 8.0))
		button.position = Vector2(x, 4)
		button.size = Vector2(width, bar.size.y - 8.0)
		var icon_name := str(entry.get("icon", ""))
		if icon_name != "" and FileAccess.file_exists("res://art/ui/%s.png" % icon_name):
			button.icon = SpriteCatalog.ui(icon_name)
			button.expand_icon = true
			button.add_theme_constant_override("icon_max_width", 16)
		button.disabled = bool(entry.get("disabled", false))
		button.pressed.connect(_emit_action.bind(str(entry["id"])))
		_actions.add_child(button)
		x += width + gap


func show_member_bar(member_index: int, cooldowns: Dictionary, selected_id: String, ranks_override: Dictionary, mp_override: int = -1) -> void:
	if member_index < 0 or member_index >= GameState.party.size():
		clear_actor_bar()
		return
	var member: Dictionary = GameState.party[member_index]
	var ranks: Dictionary = member["skill_ranks"]
	if not ranks_override.is_empty():
		ranks = ranks_override
	var skills: Array = []
	var cls: Dictionary = ContentDB.class_def(str(member["class_id"]))
	for skill_id in cls["skills"]:
		skills.append(ContentDB.skill(str(skill_id)))
	var mp := int(member["mp"])
	if mp_override >= 0:
		mp = mp_override
	var persona_name := str(ContentDB.persona(str(member["persona"]))["name"])
	show_actor_bar(persona_name, skills, ranks, int(member["hp"]), mp, cooldowns, {}, selected_id, false)


func show_actor_bar(actor_name: String, skills: Array, ranks: Dictionary, hp: int, mp: int, cooldowns: Dictionary, buildup: Dictionary, selected_id: String, cancel_selected: bool = false) -> void:
	_turn_tab.visible = true
	_turn_name.text = actor_name
	_clear_action_buttons()
	var combat: Dictionary = Layout.cfg()["combat"]
	var main_px := int(combat.get("action_main", 32))
	var small_px := int(combat.get("action_small", 20))
	var gap := float(combat.get("action_gap", 0))
	var entries: Array = []
	entries.append({"id": "attack", "icon": "icon_attack", "width": main_px, "state": "selected" if selected_id == "attack" else "ready", "badge": ""})
	entries.append({"id": "cover", "icon": "icon_cover", "width": main_px, "state": "selected" if selected_id == "cover" else "ready", "badge": ""})
	for skill in skills:
		var skill_id := str(skill.get("id", ""))
		var rank := int(ranks.get(skill_id, 0))
		var state := Formulas.skill_button_state(skill, rank, hp, mp, cooldowns, buildup, selected_id == "skill:%s" % skill_id)
		var badge := Formulas.skill_cost_badge(skill, rank, cooldowns, buildup)
		if state == "locked":
			badge = "—"
		elif state == "passive":
			badge = ""
		entries.append({
			"id": "skill:%s" % skill_id,
			"icon": "icon_skill",
			"width": main_px,
			"state": state,
			"badge": badge,
		})
	entries.append({"id": "item", "icon": "icon_item", "width": small_px, "state": "selected" if selected_id == "item" else "ready", "badge": ""})
	entries.append({"id": "run", "icon": "icon_run", "width": small_px, "state": "selected" if selected_id == "run" else "ready", "badge": ""})
	var total := gap * float(maxi(0, entries.size() - 1))
	for entry in entries:
		total += float(entry["width"])
	var bar := Layout.rect("combat", "action_bar")
	var x := (bar.size.x - total) * 0.5
	for entry in entries:
		var width := float(entry["width"])
		var height := float(main_px if width >= float(main_px) else small_px)
		var button := Widgets.make_button("", Vector2(width, height))
		button.position = Vector2(x, (bar.size.y - height) * 0.5)
		button.size = Vector2(width, height)
		var icon_name := str(entry["icon"])
		if FileAccess.file_exists("res://art/ui/%s.png" % icon_name):
			button.icon = SpriteCatalog.ui(icon_name)
			button.expand_icon = true
			button.add_theme_constant_override("icon_max_width", int(mini(16, width - 4)))
		var button_state := str(entry["state"])
		var blocked := button_state == "passive" or button_state == "locked" or button_state == "cooldown" or button_state == "disabled"
		button.disabled = blocked
		if button_state == "selected":
			button.modulate = SpriteCatalog.HIGHLIGHT
		elif button_state == "locked":
			button.modulate = Color(0.28, 0.24, 0.2)
		elif button_state == "cooldown":
			button.modulate = Color(0.62, 0.5, 0.28)
		elif blocked:
			button.modulate = Color(0.45, 0.42, 0.38)
		var badge_text := str(entry.get("badge", ""))
		if badge_text != "":
			var badge_color := SpriteCatalog.GOLD if button_state == "cooldown" else SpriteCatalog.INK
			var badge := Widgets.label(badge_text, Layout.font_tiny(), badge_color)
			badge.position = Vector2(0, height - 11)
			badge.size = Vector2(width, 11)
			badge.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			badge.clip_text = true
			button.add_child(badge)
		var emit_id := str(entry["id"])
		if cancel_selected and emit_id == selected_id:
			emit_id = "back"
		if not blocked:
			button.pressed.connect(_emit_action.bind(emit_id))
		_actions.add_child(button)
		x += width + gap


func clear_actor_bar() -> void:
	if _turn_tab:
		_turn_tab.visible = false
	_clear_action_buttons()


func _clear_action_buttons() -> void:
	if _actions == null:
		return
	for child in _actions.get_children():
		child.free()


func _emit_action(action_id: String) -> void:
	Sfx.play("tap")
	action_pressed.emit(action_id)


func set_actions_enabled(enabled: bool) -> void:
	for child in _actions.get_children():
		if child is Button:
			child.disabled = not enabled


func set_caption(text: String) -> void:
	_caption.text = text


func raise_member(index: int, up: bool) -> void:
	_raise(index, up)


func set_threat_debug(rows: Array) -> void:
	for card in _cards.get_children():
		var label := card.get_node_or_null("Threat")
		if label == null:
			continue
		label.visible = false
		label.text = ""
	for row in rows:
		var id := str(row.get("id", ""))
		if not id.begins_with("p"):
			continue
		var index := int(id.trim_prefix("p"))
		if index < 0 or index >= _cards.get_child_count():
			continue
		var label := _cards.get_child(index).get_node_or_null("Threat")
		if label == null:
			continue
		var text := str(row.get("text", ""))
		label.text = text
		label.visible = text != ""


func set_cover(index: int, on: bool) -> void:
	if index < 0 or index >= _seats.size():
		return
	var seat: Control = _seats[index]
	seat.modulate = Color(0.5, 0.5, 0.5, 0.8) if on else Color.WHITE


func lunge(id: String, delta_y: float, duration: float) -> void:
	var node := _node_for(id)
	if node == null:
		return
	var origin: Vector2 = node.position
	var tween := create_tween()
	tween.tween_property(node, "position", origin + Vector2(0, delta_y), duration * 0.45)
	tween.tween_property(node, "position", origin, duration * 0.55)


func monster_pose(id: String, pose: String) -> void:
	var node := _node_for(id)
	if node == null:
		return
	match pose:
		"windup", "attack":
			node.set_meta("acting", true)
			_set_frame(node, 2 if pose == "windup" else 3)
		_:
			node.set_meta("acting", false)
			_set_frame(node, _idle_frame)


func react_hit(id: String, texts: Array, hp_ratio: float, mp_ratio: float) -> void:
	var node := _node_for(id)
	if node == null:
		return
	var visual := node.get_node_or_null("Sprite")
	if visual == null:
		visual = node.get_node_or_null("Doll")
	if visual is Control:
		var sprite := visual as Control
		var origin_x := sprite.position.x
		var tween := create_tween()
		tween.tween_property(sprite, "position:x", origin_x + Timing.PUNCH_PIXELS, 0.08)
		tween.tween_property(sprite, "position:x", origin_x - 3.0, 0.08)
		tween.tween_property(sprite, "position:x", origin_x, 0.14)
		var flash := create_tween()
		var base := sprite.modulate
		flash.tween_property(sprite, "modulate", Color(1, 0.3, 0.3, base.a), Timing.HIT_BLINK_IN)
		flash.tween_property(sprite, "modulate", base, Timing.HIT_BLINK_OUT)
	if _bars.has(id):
		Widgets.tween_bar(_bars[id]["hp"], hp_ratio, Timing.HP_TWEEN)
		if _bars[id].has("mp"):
			Widgets.tween_bar(_bars[id]["mp"], mp_ratio, Timing.HP_TWEEN)
	var delay := 0.0
	for entry in texts:
		_queue_floater(id, str(entry["text"]), entry["color"], delay)
		delay += Timing.FLOATER_QUEUE
	Sfx.play("hit")


func death_blink(id: String) -> void:
	var node := _node_for(id)
	if node == null:
		return
	var visual := node.get_node_or_null("Sprite")
	if visual == null:
		visual = node.get_node_or_null("Doll")
	if visual == null:
		return
	for step in range(6, 0, -1):
		visual.visible = false
		await get_tree().create_timer(Timing.DEATH_BLINK_OFF).timeout
		visual.visible = true
		await get_tree().create_timer(Timing.DEATH_BLINK_OFF * float(step)).timeout
	if str(id).begins_with("m"):
		node.visible = false
	else:
		visual.modulate = Color(1, 1, 1, 0.35)


func set_target_mode(valid_ids: Array, hint: String) -> void:
	_targeting = true
	_caption.text = hint
	_stop_flickers()
	for id in _monsters.keys():
		var visual := _visual(_monsters[id])
		if visual == null:
			continue
		if valid_ids.has(str(id)):
			_flicker(visual)
		else:
			var tween := create_tween()
			tween.tween_property(visual, "modulate", Color(0.45, 0.45, 0.45), Timing.UNTARGET_GREY)
	for i in _seats.size():
		var card := _cards.get_child(i) if i < _cards.get_child_count() else null
		if card == null:
			continue
		if valid_ids.has("p%d" % i):
			_flicker(card)
		else:
			card.modulate = Color.WHITE


func clear_target_mode() -> void:
	_targeting = false
	_stop_flickers()
	for id in _monsters.keys():
		var visual := _visual(_monsters[id])
		if visual:
			visual.modulate = Color.WHITE
	for card in _cards.get_children():
		card.modulate = Color.WHITE


func show_choices(entries: Array, back_id: String) -> void:
	_close_modal()
	_modal = Widgets.panel()
	_modal.position = Vector2(8, 210)
	_modal.size = Vector2(254, 180)
	add_child(_modal)
	var box := VBoxContainer.new()
	box.position = Vector2(6, 6)
	box.size = Vector2(242, 168)
	box.add_theme_constant_override("separation", 4)
	_modal.add_child(box)
	for entry in entries:
		var button := Widgets.make_button(str(entry["text"]), Vector2(230, 32))
		button.disabled = bool(entry.get("disabled", false))
		if button.disabled:
			button.modulate = Color(0.45, 0.42, 0.38)
		var choice_id := str(entry["id"])
		button.pressed.connect(func(): action_pressed.emit(choice_id))
		box.add_child(button)
	set_actions([{"id": back_id, "label": "Back", "icon": ""}])


func hide_choices() -> void:
	_close_modal()


func open_dice(count: int, stat_name: String) -> void:
	_close_dice()
	_dice = Widgets.panel("res://art/ui/panel_dark.png")
	_dice.position = Vector2(12, 250)
	_dice.size = Vector2(246, 90)
	add_child(_dice)
	var row := HBoxContainer.new()
	row.set_anchors_preset(Control.PRESET_FULL_RECT)
	row.offset_left = 6
	row.offset_top = 8
	row.offset_right = -6
	row.offset_bottom = -8
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	_dice.add_child(row)
	_dice_labels.clear()
	var tint := SpriteCatalog.HP if stat_name == "body" else SpriteCatalog.SAFE if stat_name == "senses" else SpriteCatalog.MP
	for _i in count:
		var col := VBoxContainer.new()
		col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		col.alignment = BoxContainer.ALIGNMENT_CENTER
		var face := TextureRect.new()
		face.texture = SpriteCatalog.ui("die")
		face.custom_minimum_size = Vector2(16, 16)
		face.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
		face.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		face.modulate = tint
		var number := Widgets.label("?", Layout.font_small(), SpriteCatalog.LIGHT)
		number.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		var tag := Widgets.label("", Layout.font_tiny(), SpriteCatalog.LIGHT)
		tag.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		col.add_child(face)
		col.add_child(number)
		col.add_child(tag)
		row.add_child(col)
		_dice_labels.append({"face": face, "number": number, "tag": tag})


func set_die(index: int, label_text: String, number: String, success: int) -> void:
	if index < 0 or index >= _dice_labels.size():
		return
	var row: Dictionary = _dice_labels[index]
	var tag: Label = row["tag"]
	var num: Label = row["number"]
	var face: TextureRect = row["face"]
	tag.text = label_text
	num.text = number
	if success == 0:
		face.texture = SpriteCatalog.ui("die_fail")
	elif success == 1:
		face.texture = SpriteCatalog.ui("die")


func close_dice() -> void:
	_close_dice()


func play_chicken() -> void:
	var chick := TextureRect.new()
	chick.texture = SpriteCatalog.ui("chicken")
	chick.size = Vector2(16, 16)
	chick.position = Vector2(180, 300)
	add_child(chick)
	var tween := create_tween()
	tween.tween_property(chick, "position", Vector2(40, 250), Timing.CHICKEN_MOVE)
	await get_tree().create_timer(Timing.CHICKEN_SFX_AT).timeout
	Sfx.play("chicken")
	if tween.is_valid() and tween.is_running():
		await tween.finished
	else:
		await get_tree().create_timer(0.2).timeout
	if is_instance_valid(chick):
		chick.queue_free()


func show_end(title: String, body: String, from_ratio: float, to_ratio: float) -> void:
	_close_modal()
	_modal = Widgets.panel()
	_modal.position = Vector2(12, 168)
	_modal.size = Vector2(246, 230)
	add_child(_modal)
	var heading := Widgets.label(title, Layout.font_size())
	heading.position = Vector2(8, 8)
	heading.size = Vector2(230, 24)
	_modal.add_child(heading)
	var copy := Widgets.label(body, Layout.font_tiny())
	copy.position = Vector2(8, 36)
	copy.size = Vector2(230, 120)
	copy.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_modal.add_child(copy)
	var bar := Widgets.bar(220, 10, SpriteCatalog.GOLD, SpriteCatalog.HP_BACK)
	bar["root"].position = Vector2(12, 164)
	_modal.add_child(bar["root"])
	Widgets.set_bar(bar, from_ratio)
	Widgets.tween_bar(bar, to_ratio, Timing.XP_TWEEN)
	await get_tree().create_timer(Timing.XP_TWEEN).timeout
	var button := Widgets.make_button("Continue", Vector2(220, 44))
	button.position = Vector2(12, 180)
	button.pressed.connect(func(): continue_pressed.emit())
	_modal.add_child(button)
	await continue_pressed
	_close_modal()


func open_party() -> void:
	_open_text_modal("Party", "%d / %d heroes" % [GameState.party.size(), Layout.party_max()], _party_buttons())


func open_quest() -> void:
	var quest: Dictionary = ContentDB.quest("reed_trouble")
	var done := GameState.quests_done.has("reed_trouble")
	var body := "%s\n\n%s\n\n%s" % [quest.get("name", "Quest"), quest.get("description", ""), "Done." if done else "Still open."]
	_open_text_modal("Quest", body, [])


func sync_unit(unit: Dictionary) -> void:
	var id := str(unit["id"])
	if not _bars.has(id):
		return
	var hp_ratio := 0.0 if int(unit["max_hp"]) <= 0 else float(unit["hp"]) / float(unit["max_hp"])
	var mp_ratio := 0.0 if int(unit.get("max_mp", 1)) <= 0 else float(unit.get("mp", 0)) / float(unit["max_mp"])
	Widgets.set_bar(_bars[id]["hp"], hp_ratio)
	if _bars[id].has("mp"):
		Widgets.set_bar(_bars[id]["mp"], mp_ratio)
	var node := _node_for(id)
	if node and node.has_node("Conds"):
		var names: Array = []
		for cond in unit.get("conditions", []):
			names.append(str(cond["id"]))
		node.get_node("Conds").text = " ".join(names)


func _build_chrome() -> void:
	var bg := TextureRect.new()
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	bg.stretch_mode = TextureRect.STRETCH_SCALE
	bg.texture = SpriteCatalog.background("meadow")
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bg)
	_monster_layer = Control.new()
	_monster_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_monster_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_monster_layer)
	_gm = TextureRect.new()
	_gm.texture = SpriteCatalog.ui("gm")
	_gm.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var gm_size := Vector2(72, 80)
	_gm.size = gm_size
	var gm_feet := Layout.vec("combat", "gm")
	_gm.position = gm_feet - Vector2(gm_size.x * SpriteCatalog.GM_ANCHOR.x, gm_size.y * SpriteCatalog.GM_ANCHOR.y)
	add_child(_gm)
	_table = TextureRect.new()
	_table.texture = SpriteCatalog.ui("table")
	_table.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_table.stretch_mode = TextureRect.STRETCH_SCALE
	_table.mouse_filter = Control.MOUSE_FILTER_IGNORE
	Layout.place(_table, Layout.rect("combat", "table"))
	add_child(_table)
	_seat_layer = Control.new()
	_seat_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_seat_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_seat_layer)
	_initiative = HBoxContainer.new()
	Layout.place(_initiative, Layout.rect("combat", "initiative"))
	_initiative.alignment = BoxContainer.ALIGNMENT_CENTER
	_initiative.add_theme_constant_override("separation", 2)
	add_child(_initiative)
	_banner = Widgets.label("", Layout.font_small())
	Layout.place(_banner, Layout.rect("hub", "banner"))
	add_child(_banner)
	_caption = Widgets.label("", Layout.font_tiny(), SpriteCatalog.LIGHT)
	var caption_rect := Layout.rect("combat", "caption")
	Layout.place(_caption, caption_rect)
	_caption.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_caption.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	add_child(_caption)
	_cards = HBoxContainer.new()
	Layout.place(_cards, Layout.rect("combat", "cards"))
	_cards.alignment = BoxContainer.ALIGNMENT_CENTER
	_cards.add_theme_constant_override("separation", 0)
	add_child(_cards)
	_turn_tab = Panel.new()
	var tab_box := StyleBoxFlat.new()
	tab_box.bg_color = Color(0.93, 0.86, 0.7, 0.96)
	tab_box.border_color = Color(0.45, 0.32, 0.18)
	tab_box.set_border_width_all(1)
	_turn_tab.add_theme_stylebox_override("panel", tab_box)
	_turn_tab.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_turn_tab.visible = false
	Layout.place(_turn_tab, Layout.rect("combat", "name_tab"))
	add_child(_turn_tab)
	_turn_name = Widgets.label("", Layout.font_tiny(), SpriteCatalog.INK)
	_turn_name.set_anchors_preset(Control.PRESET_FULL_RECT)
	_turn_name.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_turn_name.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_turn_name.clip_text = true
	_turn_tab.add_child(_turn_name)
	var action_back := ColorRect.new()
	action_back.color = Color(0.12, 0.08, 0.05, 0.92)
	Layout.place(action_back, Layout.rect("combat", "action_bar"))
	add_child(action_back)
	_actions = Control.new()
	Layout.place(_actions, Layout.rect("combat", "action_bar"))
	add_child(_actions)


func _sync_party() -> void:
	for child in _seat_layer.get_children():
		child.free()
	for child in _cards.get_children():
		child.free()
	_seats.clear()
	var points := Layout.party_seat_points(GameState.party.size())
	var card_raw: Array = Layout.cfg()["combat"]["card_size"]
	var card_size := Vector2(float(card_raw[0]), float(card_raw[1]))
	for index in GameState.party.size():
		var member: Dictionary = GameState.party[index]
		var stats := GameState.combat_stats(member)
		var seat := Control.new()
		var point: Vector2 = points[index]
		seat.position = Vector2(point.x - SpriteCatalog.BACK_SIZE.x * 0.5, point.y)
		seat.size = SpriteCatalog.BACK_SIZE
		seat.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var bracket := Panel.new()
		bracket.name = "Bracket"
		bracket.visible = false
		bracket.mouse_filter = Control.MOUSE_FILTER_IGNORE
		bracket.position = Vector2(-3, -8)
		bracket.size = SpriteCatalog.BACK_SIZE + Vector2(6, 10)
		var border := StyleBoxFlat.new()
		border.bg_color = Color(0, 0, 0, 0)
		border.border_color = SpriteCatalog.HIGHLIGHT
		border.set_border_width_all(2)
		bracket.add_theme_stylebox_override("panel", border)
		seat.add_child(bracket)
		var doll := PaperDoll.new()
		doll.name = "Doll"
		doll.set_look(member["look"], str(member["class_id"]), str(member["race"]), "back")
		seat.add_child(doll)
		var arrow := TextureRect.new()
		arrow.name = "Arrow"
		arrow.texture = SpriteCatalog.ui("arrow")
		arrow.visible = false
		arrow.position = Vector2(14, -16)
		arrow.size = Vector2(12, 12)
		arrow.mouse_filter = Control.MOUSE_FILTER_IGNORE
		seat.add_child(arrow)
		_seat_layer.add_child(seat)
		_seats.append(seat)
		var pid := "p%d" % index
		var card := Panel.new()
		card.custom_minimum_size = card_size
		card.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
		card.mouse_filter = Control.MOUSE_FILTER_STOP
		card.gui_input.connect(_card_input.bind(pid))
		var card_box := StyleBoxFlat.new()
		card_box.bg_color = Color(0.16, 0.1, 0.07, 0.92)
		card_box.border_color = Color(0.45, 0.32, 0.18)
		card_box.set_border_width_all(1)
		card_box.content_margin_left = 3
		card_box.content_margin_right = 3
		card_box.content_margin_top = 2
		card_box.content_margin_bottom = 2
		card.add_theme_stylebox_override("panel", card_box)
		var name := Widgets.label(ContentDB.persona(str(member["persona"]))["name"], Layout.font_tiny(), SpriteCatalog.LIGHT)
		name.position = Vector2(2, 1)
		name.size = Vector2(card_size.x - 24, 12)
		name.clip_text = true
		card.add_child(name)
		var bar_w := card_size.x - 6.0
		var hp := Widgets.bar(bar_w, 6, SpriteCatalog.HP, SpriteCatalog.HP_BACK)
		hp["root"].position = Vector2(3, 14)
		card.add_child(hp["root"])
		var mp := Widgets.bar(bar_w, 6, SpriteCatalog.MP, SpriteCatalog.MP_BACK)
		mp["root"].position = Vector2(3, 24)
		card.add_child(mp["root"])
		Widgets.set_bar(hp, float(member["hp"]) / float(stats["max_hp"]))
		Widgets.set_bar(mp, float(member["mp"]) / float(stats["max_mp"]))
		var threat_label := Widgets.label("", Layout.font_tiny(), SpriteCatalog.GOLD)
		threat_label.name = "Threat"
		threat_label.position = Vector2(card_size.x - 24, 1)
		threat_label.size = Vector2(22, 12)
		threat_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		threat_label.visible = false
		card.add_child(threat_label)
		_bars[pid] = {"hp": hp, "mp": mp}
		_cards.add_child(card)
	var kind := str(ContentDB.place(GameState.place_id).get("kind", "meadow"))
	var bg := get_child(0) as TextureRect
	if bg:
		bg.texture = SpriteCatalog.background(kind)


func _sync_from_units(units: Array) -> void:
	for unit in units:
		sync_unit(unit)


func _add_monster(unit: Dictionary) -> void:
	var node := Control.new()
	node.size = Vector2(64, 64)
	node.set_meta("back", bool(unit.get("back_row", false)))
	node.set_meta("kind", str(unit["kind"]))
	node.set_meta("strip", SpriteCatalog.monster_strip(str(unit["kind"])))
	var bar := Widgets.bar(48, 6, SpriteCatalog.HP, SpriteCatalog.HP_BACK)
	bar["root"].position = Vector2(8, 0)
	node.add_child(bar["root"])
	Widgets.set_bar(bar, float(unit["hp"]) / float(maxi(1, int(unit["max_hp"]))))
	_bars[str(unit["id"])] = {"hp": bar}
	var sprite := TextureRect.new()
	sprite.name = "Sprite"
	sprite.position = Vector2(8, 8)
	sprite.size = Vector2(48, 48)
	sprite.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	sprite.stretch_mode = TextureRect.STRETCH_SCALE
	sprite.mouse_filter = Control.MOUSE_FILTER_IGNORE
	sprite.texture = SpriteCatalog.monster_frame(node.get_meta("strip"), 0)
	node.add_child(sprite)
	var conds := Widgets.label("", Layout.font_tiny(), SpriteCatalog.LIGHT)
	conds.name = "Conds"
	conds.position = Vector2(0, 56)
	conds.size = Vector2(64, 12)
	node.add_child(conds)
	var uid := str(unit["id"])
	node.gui_input.connect(func(event: InputEvent):
		if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
			target_pressed.emit(uid)
	)
	_monster_layer.add_child(node)
	_monsters[uid] = node


func _layout_monsters() -> void:
	var area := Layout.rect("combat", "monsters")
	var ids: Array = _monsters.keys()
	var count := maxi(1, ids.size())
	for i in ids.size():
		var node: Control = _monsters[ids[i]]
		var slot_w := area.size.x / float(count)
		var x := area.position.x + slot_w * float(i) + (slot_w - node.size.x) * 0.5
		var y := area.position.y + Layout.num("monster_front_drop")
		if bool(node.get_meta("back", false)):
			y -= Layout.num("monster_back_lift")
		node.position = Vector2(x, y)


func _raise(index: int, up: bool) -> void:
	var points := Layout.party_seat_points(_seats.size())
	for i in _seats.size():
		var seat: Control = _seats[i]
		var point: Vector2 = points[i]
		var base := Vector2(point.x - SpriteCatalog.BACK_SIZE.x * 0.5, point.y)
		seat.position = base + Vector2(0, -Timing.PLAYER_RISE_PX if up and i == index else 0)
		seat.get_node("Bracket").visible = up and i == index
		seat.get_node("Arrow").visible = up and i == index


func _set_table_visible(show_table: bool) -> void:
	_gm.visible = show_table
	_table.visible = show_table
	_seat_layer.visible = show_table


func _set_frame(node: Control, frame: int) -> void:
	var sprite := node.get_node_or_null("Sprite")
	if sprite is TextureRect and node.has_meta("strip"):
		(sprite as TextureRect).texture = SpriteCatalog.monster_frame(node.get_meta("strip"), frame)


func _node_for(id: String) -> Control:
	if _monsters.has(id):
		return _monsters[id]
	if id.begins_with("p"):
		var index := int(id.substr(1))
		if index >= 0 and index < _seats.size():
			return _seats[index]
	return null


func _visual(node: Control) -> Control:
	var sprite := node.get_node_or_null("Sprite")
	if sprite:
		return sprite
	return node.get_node_or_null("Doll")


func _card_input(event: InputEvent, pid: String) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		target_pressed.emit(pid)


func _queue_floater(id: String, text: String, color: Color, delay: float) -> void:
	if delay <= 0.0:
		_spawn_floater(id, text, color)
		return
	var timer := get_tree().create_timer(delay)
	timer.timeout.connect(func(): _spawn_floater(id, text, color))


func _spawn_floater(id: String, text: String, color: Color) -> void:
	var node := _node_for(id)
	if node == null:
		return
	var label := Widgets.label(text, Layout.font_small(), color)
	label.position = node.global_position - global_position + Vector2(8, 0)
	add_child(label)
	var tween := create_tween()
	tween.tween_property(label, "position:y", label.position.y - 18, 0.6)
	tween.parallel().tween_property(label, "modulate:a", 0.0, 0.6)
	tween.finished.connect(label.queue_free)


func _flicker(node: Control) -> void:
	var tween := create_tween()
	tween.set_loops()
	tween.tween_property(node, "modulate", Color(1, 1, 1, 0.45), Timing.TARGET_FLICKER_OFF)
	tween.tween_property(node, "modulate", Color.WHITE, Timing.TARGET_FLICKER_ON)
	_flickers.append(tween)


func _stop_flickers() -> void:
	for tween in _flickers:
		if tween is Tween and (tween as Tween).is_valid():
			(tween as Tween).kill()
	_flickers.clear()


func _mini_portrait(entry: Dictionary) -> Control:
	var clip := Control.new()
	clip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	clip.clip_contents = true
	if str(entry.get("side", "")) == "player":
		var index := int(entry.get("index", 0))
		if index < GameState.party.size():
			var member: Dictionary = GameState.party[index]
			var doll := PaperDoll.new()
			doll.set_look(member["look"], str(member["class_id"]), str(member["race"]), "front")
			doll.scale = Vector2(0.4, 0.4)
			clip.add_child(doll)
	else:
		var rect := TextureRect.new()
		rect.texture = SpriteCatalog.monster_frame(SpriteCatalog.monster_strip(str(entry.get("kind", "puddleblob"))), 0)
		rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		rect.set_anchors_preset(Control.PRESET_FULL_RECT)
		clip.add_child(rect)
	return clip


func _close_modal() -> void:
	if _modal and is_instance_valid(_modal):
		_modal.queue_free()
	_modal = null


func _close_dice() -> void:
	if _dice and is_instance_valid(_dice):
		_dice.queue_free()
	_dice = null
	_dice_labels.clear()


func _open_text_modal(title: String, body: String, extra: Array) -> void:
	_close_modal()
	_modal = Widgets.panel()
	_modal.position = Vector2(10, 70)
	_modal.size = Vector2(250, 320)
	add_child(_modal)
	var heading := Widgets.label(title, Layout.font_size())
	heading.position = Vector2(8, 6)
	_modal.add_child(heading)
	var copy := Widgets.label(body, Layout.font_tiny())
	copy.position = Vector2(8, 28)
	copy.size = Vector2(234, 200 if extra.is_empty() else 88)
	copy.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_modal.add_child(copy)
	if not extra.is_empty():
		var scroll := ScrollContainer.new()
		scroll.position = Vector2(6, 120)
		scroll.size = Vector2(238, 148)
		scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
		var box := VBoxContainer.new()
		box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		box.add_theme_constant_override("separation", 4)
		scroll.add_child(box)
		for entry in extra:
			if bool(entry.get("info", false)):
				var info := Widgets.label(str(entry["text"]), Layout.font_tiny())
				var info_h := 48 if str(entry["text"]).contains("\n") else 36
				info.custom_minimum_size = Vector2(220, info_h)
				info.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
				box.add_child(info)
				continue
			var button := Widgets.make_button(str(entry["text"]), Vector2(220, 32))
			var skill_id := str(entry["id"])
			var member_index := int(entry["member"])
			button.pressed.connect(_spend.bind(member_index, skill_id))
			box.add_child(button)
		_modal.add_child(scroll)
	var close := Widgets.make_button("Close", Vector2(230, 40))
	close.position = Vector2(8, 272)
	close.pressed.connect(_close_modal)
	_modal.add_child(close)


func _party_buttons() -> Array:
	var buttons: Array = []
	for index in GameState.party.size():
		var member: Dictionary = GameState.party[index]
		var stats := GameState.combat_stats(member)
		var cls: Dictionary = ContentDB.class_def(str(member["class_id"]))
		buttons.append({
			"text": "%s · %s  Lv%d  HP %d/%d\nB%d S%d M%d  Atk %d  DR %d  SP %d" % [
				ContentDB.persona(str(member["persona"]))["name"], cls["name"],
				int(member["level"]), int(member["hp"]), stats["max_hp"],
				stats["body"], stats["senses"], stats["mind"], stats["attack"], stats["dr"],
				GameState.unspent_points(member),
			],
			"info": true,
			"id": "member",
			"member": index,
		})
		for skill_id in cls["skills"]:
			var skill: Dictionary = ContentDB.skill(str(skill_id))
			if not Formulas.is_passive(skill):
				continue
			buttons.append({
				"text": "Passive  %s — %s" % [skill["name"], skill.get("description", "")],
				"info": true,
				"id": str(skill_id),
				"member": index,
			})
		if GameState.unspent_points(member) <= 0:
			continue
		for skill_id in member["skill_ranks"].keys():
			var ranked: Dictionary = ContentDB.skill(str(skill_id))
			if Formulas.is_passive(ranked):
				continue
			buttons.append({
				"text": "+ %s (%s)" % [ranked["name"], ContentDB.persona(str(member["persona"]))["name"]],
				"id": str(skill_id),
				"member": index,
			})
	return buttons


func _spend(member_index: int, skill_id: String) -> void:
	var member: Dictionary = GameState.party[member_index]
	if GameState.spend_point(member, skill_id):
		Sfx.play("good")
		open_party()


func _backdrop_kind() -> void:
	pass
