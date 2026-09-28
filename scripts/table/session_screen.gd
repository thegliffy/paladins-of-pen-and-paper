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
var _inspect: Panel
var _action_art: TextureRect
var _inspect_catcher: Control
var _slot_x: Dictionary = {}
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
var _strip_panel: Panel
var _strip_frames := 1
var _strip_clock := 0.0


func _ready() -> void:
	_build_chrome()
	show_hub()


func _process(delta: float) -> void:
	_idle += delta
	_pulse_low_hp()
	_pulse_ready_strip(delta)
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
	hide_inspect()
	if _turn_tab:
		_turn_tab.visible = false
	if _action_art:
		_action_art.visible = false
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
	if _action_art:
		_action_art.visible = true
	_clear_action_buttons()
	var slots: Dictionary = Layout.cfg()["combat"]["action_slots"]
	var entries: Array = []
	entries.append({"id": "attack", "rect": slots["attack"], "file": "ui/portrait/ability_attack_active.png" if selected_id == "attack" else "ui/portrait/ability_attack.png", "state": "selected" if selected_id == "attack" else "ready", "badge": ""})
	entries.append({"id": "cover", "rect": slots["cover"], "file": "ui/portrait/ability_cover_active.png" if selected_id == "cover" else "ui/portrait/ability_cover.png", "state": "selected" if selected_id == "cover" else "ready", "badge": ""})
	var skill_rects: Array = slots["skills"]
	var skill_i := 0
	for skill in skills:
		if skill_i >= skill_rects.size():
			break
		var skill_id := str(skill.get("id", ""))
		var rank := int(ranks.get(skill_id, 0))
		var state := Formulas.skill_button_state(skill, rank, hp, mp, cooldowns, buildup, selected_id == "skill:%s" % skill_id)
		var badge := Formulas.skill_cost_badge(skill, rank, cooldowns, buildup)
		if state == "locked" or state == "passive":
			badge = ""
		entries.append({
			"id": "skill:%s" % skill_id,
			"rect": skill_rects[skill_i],
			"file": ArtPack.slot_file(state),
			"state": state,
			"badge": badge,
			"skill": skill,
		})
		skill_i += 1
	entries.append({"id": "item", "rect": slots["item"], "file": "ui/portrait/mini_item_active.png" if selected_id == "item" else "ui/portrait/mini_item.png", "state": "selected" if selected_id == "item" else "ready", "badge": ""})
	entries.append({"id": "run", "rect": slots["run"], "file": "ui/portrait/mini_run_active.png" if selected_id == "run" else "ui/portrait/mini_run.png", "state": "selected" if selected_id == "run" else "ready", "badge": ""})
	_slot_x.clear()
	var bar := Layout.rect("combat", "action_bar")
	for entry in entries:
		var raw: Array = entry["rect"]
		var local := Rect2(float(raw[0]) - bar.position.x, float(raw[1]) - bar.position.y, float(raw[2]), float(raw[3]))
		var action_id := str(entry["id"])
		_slot_x[action_id] = float(raw[0]) + local.size.x * 0.5
		var button_state := str(entry["state"])
		if button_state == "selected":
			var armed := FxStrip.new()
			armed.setup("ui/portrait/skill_slot_armed.png", Vector2(36, 36), 2, 4.0, true)
			armed.position = local.position + Vector2(-2, -2)
			_actions.add_child(armed)
		var button := Button.new()
		button.focus_mode = Control.FOCUS_NONE
		button.position = local.position
		button.size = local.size
		var empty := StyleBoxEmpty.new()
		button.add_theme_stylebox_override("normal", empty)
		button.add_theme_stylebox_override("hover", empty)
		button.add_theme_stylebox_override("pressed", empty)
		button.add_theme_stylebox_override("focus", empty)
		button.set_meta("action_id", action_id)
		var face := _icon_rect(str(entry["file"]))
		face.position = Vector2.ZERO
		face.size = local.size
		button.add_child(face)
		if entry.has("skill"):
			var icon := _icon_rect("")
			icon.texture = ArtPack.skill_icon(entry["skill"])
			icon.position = Vector2(6, 6)
			icon.size = Vector2(20, 20)
			button.add_child(icon)
			if button_state == "passive":
				var dim := _icon_rect("ui/portrait/passive_dim_mask.png")
				dim.position = Vector2(4, 4)
				dim.size = Vector2(24, 24)
				button.add_child(dim)
			elif button_state == "cooldown":
				var mask := _icon_rect("ui/skills/skill_cooldown_mask.png")
				mask.position = Vector2(4, 4)
				mask.size = Vector2(24, 24)
				button.add_child(mask)
			elif button_state == "locked":
				var mask_l := _icon_rect("ui/skills/skill_cooldown_mask.png")
				mask_l.position = Vector2(4, 4)
				mask_l.size = Vector2(24, 24)
				button.add_child(mask_l)
				var lock := _icon_rect("ui/portrait/lock_icon.png")
				lock.position = Vector2(11, 11)
				lock.size = Vector2(10, 10)
				button.add_child(lock)
			elif button_state == "disabled":
				button.modulate = Color(0.55, 0.55, 0.55)
		var badge_text := str(entry.get("badge", ""))
		if badge_text != "" and badge_text.is_valid_int():
			var pill := _icon_rect("ui/portrait/cost_badge.png")
			pill.position = Vector2(8, 34)
			pill.size = Vector2(16, 7)
			button.add_child(pill)
			var badge := DigitReadout.new()
			badge.sheet = "ui/portrait/digits_3x5.png"
			badge.cell = Vector2i(4, 5)
			badge.advance = 4
			badge.position = Vector2(6, 1)
			badge.size = Vector2(10, 5)
			badge.set_text(badge_text)
			pill.add_child(badge)
		var emit_id := action_id
		if cancel_selected and emit_id == selected_id:
			emit_id = "back"
		button.pressed.connect(_emit_action.bind(emit_id))
		_actions.add_child(button)


func clear_actor_bar() -> void:
	hide_inspect()
	if _turn_tab:
		_turn_tab.visible = false
	_clear_action_buttons()


func present_inspect(member_index: int, action_id: String, cooldowns: Dictionary, ranks_override: Dictionary, mp_override: int = -1) -> void:
	if member_index < 0 or member_index >= GameState.party.size():
		hide_inspect()
		return
	var member: Dictionary = GameState.party[member_index]
	var ranks: Dictionary = member["skill_ranks"]
	if not ranks_override.is_empty():
		ranks = ranks_override
	var mp := int(member["mp"])
	if mp_override >= 0:
		mp = mp_override
	show_inspect(_inspect_card(action_id, ranks, int(member["hp"]), mp, cooldowns, {}), action_id)


func show_inspect(card: Dictionary, action_id: String) -> void:
	if _inspect == null:
		return
	var size_rect := Layout.rect("combat", "skill_card")
	var center := float(_slot_x.get(action_id, 135.0))
	var width := size_rect.size.x
	var height := Widgets.inspect_card_height(str(card.get("description", "")), width)
	var left := clampf(center - width * 0.5, 4.0, Layout.viewport_size().x - width - 4.0)
	var bar_top := 480.0
	for point in Layout.party_seat_points(maxi(1, _seats.size())):
		bar_top = minf(bar_top, point.y - 11.0)
	var top := bar_top - 14.0 - height
	_inspect.position = Vector2(left, top)
	_inspect.size = Vector2(width, height)
	_fill_inspect(card, action_id)
	_inspect.visible = true
	_inspect.mouse_filter = Control.MOUSE_FILTER_STOP
	if _inspect_catcher:
		_inspect_catcher.mouse_filter = Control.MOUSE_FILTER_STOP


func hide_inspect() -> void:
	if _inspect:
		_inspect.visible = false
		_inspect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if _inspect_catcher:
		_inspect_catcher.mouse_filter = Control.MOUSE_FILTER_IGNORE


func _inspect_card(action_id: String, ranks: Dictionary, hp: int, mp: int, cooldowns: Dictionary, buildup: Dictionary) -> Dictionary:
	if action_id.begins_with("skill:"):
		var skill_id := action_id.trim_prefix("skill:")
		var skill: Dictionary = ContentDB.skill(skill_id)
		var rank := int(ranks.get(skill_id, 0))
		return Formulas.skill_inspect(skill, rank, hp, mp, cooldowns, buildup)
	return Formulas.basic_inspect(ContentDB.action_def(action_id))


func _fill_inspect(card: Dictionary, action_id: String = "") -> void:
	_strip_panel = null
	for child in _inspect.get_children():
		child.free()
	_inspect.add_theme_stylebox_override("panel", ArtPack.nine_slice("ui/portrait/skill_card_panel.png", 14, 10, 6, 6))
	var passive := str(card.get("tag", "")) == "Passive"
	var frame := _icon_rect("ui/portrait/skill_card_icon_frame_passive.png" if passive else "ui/portrait/skill_card_icon_frame.png")
	frame.position = Vector2(16, 12)
	frame.size = Vector2(44, 44)
	_inspect.add_child(frame)
	var icon := _icon_rect(str(card.get("icon", "")))
	if str(card.get("icon", "")).begins_with("ui/skills/"):
		icon.texture = ArtPack.texture(str(card.get("icon", "")))
	elif not str(card.get("icon", "")).contains("/"):
		var skill_tex := ArtPack.texture("ui/skills/%s.png" % str(card.get("icon", "")))
		if skill_tex:
			icon.texture = skill_tex
	icon.position = Vector2(18, 14)
	icon.size = Vector2(40, 40)
	_inspect.add_child(icon)
	var title := Widgets.label(str(card.get("name", "")), Layout.font_size(), SpriteCatalog.INK)
	title.position = Vector2(66, 12)
	title.size = Vector2(_inspect.size.x - 110, 16)
	title.clip_text = true
	_inspect.add_child(title)
	var tag_path := "ui/portrait/skill_tag_passive.png" if passive else "ui/portrait/skill_tag_active.png"
	var tag := _icon_rect(tag_path)
	var tag_tex := ArtPack.texture(tag_path)
	var tag_size := tag_tex.get_size() if tag_tex else Vector2(29, 9)
	tag.position = Vector2(_inspect.size.x - 8.0 - tag_size.x, 12)
	tag.size = tag_size
	_inspect.add_child(tag)
	_inspect_row("Cost", str(card.get("cost", "")), "", Vector2(66, 28))
	_inspect_row("Target", str(card.get("target", "")), _target_icon(str(card.get("target", ""))), Vector2(66, 38))
	_inspect_row("Cd", str(card.get("cooldown", "")), "ui/portrait/icon_cooldown.png", Vector2(66, 48))
	var body := Widgets.label(str(card.get("description", "")), Layout.font_size(), SpriteCatalog.INK)
	Widgets.enable_wrap(body)
	var body_size := Widgets.wrap_size(body.text, _inspect.size.x - 28.0, Layout.font_size())
	body.position = Vector2(16, 62)
	body.size = Vector2(_inspect.size.x - 28.0, body_size.y)
	_inspect.add_child(body)
	var hint := str(card.get("hint", ""))
	var strip_path := "ui/portrait/skill_card_strip_ready.png"
	var frames := 2
	if passive or hint == "Always on":
		strip_path = "ui/portrait/skill_card_strip_passive.png"
		frames = 1
	elif hint == "On cooldown":
		strip_path = "ui/portrait/skill_card_strip_cooldown.png"
		frames = 1
	elif hint.begins_with("Not enough") or hint == "Not learned yet":
		strip_path = "ui/portrait/skill_card_strip_nomp.png"
		frames = 1
	var strip := Panel.new()
	strip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	strip.position = Vector2(8, _inspect.size.y - 18)
	strip.size = Vector2(_inspect.size.x - 16, 14)
	var atlas := AtlasTexture.new()
	atlas.atlas = ArtPack.texture(strip_path)
	atlas.region = Rect2(0, 0, 24, 14)
	var box := StyleBoxTexture.new()
	box.texture = atlas
	box.texture_margin_left = 5
	box.texture_margin_right = 5
	box.axis_stretch_horizontal = StyleBoxTexture.AXIS_STRETCH_MODE_TILE
	box.axis_stretch_vertical = StyleBoxTexture.AXIS_STRETCH_MODE_STRETCH
	strip.add_theme_stylebox_override("panel", box)
	_inspect.add_child(strip)
	var hint_label := Widgets.label(hint.to_upper(), Layout.font_size(), Color("fcf0a0"))
	hint_label.set_anchors_preset(Control.PRESET_FULL_RECT)
	hint_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hint_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	strip.add_child(hint_label)
	_strip_panel = strip
	_strip_frames = frames
	_strip_clock = 0.0
	var tail := _icon_rect("ui/portrait/skill_card_tail.png")
	var center := float(_slot_x.get(action_id, _inspect.position.x + _inspect.size.x * 0.5))
	tail.position = Vector2(clampf(center - _inspect.position.x - 6.0, 8.0, _inspect.size.x - 20.0), _inspect.size.y - 2.0)
	tail.size = Vector2(13, 8)
	_inspect.add_child(tail)


func _icon_rect(rel: String) -> TextureRect:
	var rect := TextureRect.new()
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	rect.stretch_mode = TextureRect.STRETCH_SCALE
	if rel != "" and ArtPack.has(rel):
		rect.texture = ArtPack.texture(rel)
	return rect


func _inspect_row(label: String, value: String, icon_rel: String, at: Vector2) -> void:
	if icon_rel != "":
		var icon := _icon_rect(icon_rel)
		icon.position = at
		icon.size = Vector2(9, 7)
		_inspect.add_child(icon)
	var text := Widgets.label("%s %s" % [label, value], Layout.font_size(), SpriteCatalog.INK)
	text.position = at + Vector2(12 if icon_rel != "" else 0, -2)
	text.size = Vector2(_inspect.size.x - text.position.x - 8, 12)
	text.clip_text = true
	_inspect.add_child(text)


func _target_icon(label: String) -> String:
	if label == "Self":
		return "ui/portrait/target_self.png"
	if label == "One ally":
		return "ui/portrait/target_ally.png"
	if label == "Several foes":
		return "ui/portrait/target_all_enemies.png"
	if label.find("foe") >= 0:
		return "ui/portrait/target_enemy.png"
	return ""


func _on_dismiss_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		_emit_action("dismiss")


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
	for seat in _seats:
		var label: Label = seat.get_node_or_null("Threat") as Label
		if label == null:
			continue
		label.visible = false
		label.text = ""
	for row in rows:
		var id := str(row.get("id", ""))
		if not id.begins_with("p"):
			continue
		var index := int(id.trim_prefix("p"))
		if index < 0 or index >= _seats.size():
			continue
		var label: Label = _seats[index].get_node_or_null("Threat") as Label
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
		var seat: Control = _seats[i]
		var doll: Control = seat.get_node_or_null("Doll") as Control
		if doll == null:
			continue
		if valid_ids.has("p%d" % i):
			_flicker(doll)
		else:
			doll.modulate = Color(0.55, 0.55, 0.55)


func clear_target_mode() -> void:
	_targeting = false
	_stop_flickers()
	for id in _monsters.keys():
		var visual := _visual(_monsters[id])
		if visual:
			visual.modulate = Color.WHITE
	for seat in _seats:
		var doll: Control = seat.get_node_or_null("Doll") as Control
		if doll:
			doll.modulate = Color.WHITE


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
	var info: Dictionary = _bars[id]
	if info.has("hp"):
		Widgets.set_bar(info["hp"], hp_ratio)
	if info.has("mp"):
		Widgets.set_bar(info["mp"], mp_ratio)
	if info.has("hp_fill"):
		_set_clip_ratio(info["hp_fill"], hp_ratio)
		info["hp_ratio"] = hp_ratio
	if info.has("mp_fill"):
		_set_clip_ratio(info["mp_fill"], mp_ratio)
	if info.has("hp_text"):
		var digits: DigitReadout = info["hp_text"]
		digits.set_text(str(maxi(0, int(unit["hp"]))))
	if int(unit.get("threat", 0)) > 0:
		_ensure_taunt(id)
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
	bg.texture = ArtPack.texture("combat/bg_forest_portrait.png")
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bg)
	_monster_layer = Control.new()
	_monster_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_monster_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_monster_layer)
	_gm = TextureRect.new()
	_gm.texture = ArtPack.texture("combat/gm_idle.png")
	_gm.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var gm_size := Vector2(44, 46)
	_gm.size = gm_size
	var gm_feet := Layout.vec("combat", "gm")
	_gm.position = gm_feet - Vector2(gm_size.x * 0.5, gm_size.y)
	add_child(_gm)
	_table = TextureRect.new()
	_table.texture = ArtPack.texture("combat/table_portrait.png")
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
	_inspect_catcher = Control.new()
	_inspect_catcher.set_anchors_preset(Control.PRESET_FULL_RECT)
	_inspect_catcher.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_inspect_catcher.gui_input.connect(_on_dismiss_input)
	add_child(_inspect_catcher)
	_turn_tab = Panel.new()
	var tab_box := StyleBoxTexture.new()
	tab_box.texture = ArtPack.texture("ui/portrait/name_tab.png")
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
	_action_art = TextureRect.new()
	_action_art.texture = ArtPack.texture("ui/portrait/action_bar_v2.png")
	_action_art.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_action_art.stretch_mode = TextureRect.STRETCH_SCALE
	_action_art.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_action_art.visible = false
	Layout.place(_action_art, Layout.rect("combat", "action_bar"))
	add_child(_action_art)
	_actions = Control.new()
	Layout.place(_actions, Layout.rect("combat", "action_bar"))
	add_child(_actions)
	_inspect = Widgets.panel()
	_inspect.visible = false
	_inspect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_inspect)


func _sync_party() -> void:
	for child in _seat_layer.get_children():
		child.free()
	_seats.clear()
	var stale: Array = []
	for key in _bars.keys():
		if str(key).begins_with("p"):
			stale.append(key)
	for key in stale:
		_bars.erase(key)
	var points := Layout.party_seat_points(GameState.party.size())
	for index in GameState.party.size():
		var member: Dictionary = GameState.party[index]
		var stats := GameState.combat_stats(member)
		var seat := Control.new()
		var point: Vector2 = points[index]
		var anchor := Layout.vec("combat", "seat_anchor")
		var canvas := Layout.vec("combat", "seat_canvas")
		seat.position = Vector2(point.x - anchor.x, point.y - anchor.y)
		seat.size = canvas
		seat.mouse_filter = Control.MOUSE_FILTER_STOP
		var bracket := Panel.new()
		bracket.name = "Bracket"
		bracket.visible = false
		bracket.mouse_filter = Control.MOUSE_FILTER_IGNORE
		bracket.position = Vector2(-2, -2)
		bracket.size = Layout.vec("combat", "seat_canvas") + Vector2(4, 4)
		var border := StyleBoxFlat.new()
		border.bg_color = Color(0, 0, 0, 0)
		border.border_color = SpriteCatalog.HIGHLIGHT
		border.set_border_width_all(2)
		bracket.add_theme_stylebox_override("panel", border)
		seat.add_child(bracket)
		if _class_has_threat_passive(str(member["class_id"])):
			var aura := FxStrip.new()
			aura.name = "TauntAura"
			aura.setup("fx/taunt_aura.png", Vector2(56, 16), 3, 6.0, true)
			aura.position = Vector2(24, 77) - Vector2(28, 8)
			seat.add_child(aura)
			var badge := FxStrip.new()
			badge.name = "TauntBadge"
			badge.setup("fx/taunt_badge.png", Vector2(12, 13), 2, 3.0, true)
			badge.position = Vector2(18, -14)
			seat.add_child(badge)
		var doll := PaperDoll.new()
		doll.name = "Doll"
		doll.set_look(member["look"], str(member["class_id"]), str(member["race"]), "back")
		seat.add_child(doll)
		if seat.has_node("TauntAura"):
			seat.move_child(seat.get_node("TauntAura"), 1)
		if seat.has_node("TauntBadge"):
			seat.move_child(seat.get_node("TauntBadge"), seat.get_child_count() - 1)
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
		seat.gui_input.connect(_card_input.bind(pid))
		_attach_chair_bars(seat, member, stats, pid)
	var bg := get_child(0) as TextureRect
	if bg:
		bg.texture = ArtPack.texture("combat/bg_forest_portrait.png")


func _attach_chair_bars(seat: Control, member: Dictionary, stats: Dictionary, pid: String) -> void:
	var spec: Dictionary = Layout.cfg()["combat"]["chair_bars"]
	var offset: Array = spec["offset"]
	var host := Control.new()
	host.name = "BarHost"
	host.mouse_filter = Control.MOUSE_FILTER_IGNORE
	host.position = Vector2(float(offset[0]), float(offset[1]))
	seat.add_child(host)
	var frame := _icon_rect(str(spec.get("frame", "ui/portrait/seat_bars_frame.png")))
	frame.name = "Frame"
	frame.size = Vector2(float(spec["size"][0]), float(spec["size"][1]))
	host.add_child(frame)
	var hp_rect: Array = spec["hp"]
	var hp_fill := _clipped_fill("ui/portrait/seat_bar_hp.png", Vector2(float(hp_rect[0]), float(hp_rect[1])), Vector2(float(hp_rect[2]), float(hp_rect[3])))
	host.add_child(hp_fill["clip"])
	var mp_rect: Array = spec["mp"]
	var mp_fill := _clipped_fill("ui/portrait/seat_bar_mp.png", Vector2(float(mp_rect[0]), float(mp_rect[1])), Vector2(float(mp_rect[2]), float(mp_rect[3])))
	host.add_child(mp_fill["clip"])
	_set_clip_ratio(hp_fill, float(member["hp"]) / float(maxi(1, int(stats["max_hp"]))))
	_set_clip_ratio(mp_fill, float(member["mp"]) / float(maxi(1, int(stats["max_mp"]))))
	var text_rect: Array = spec["hp_text"]
	var hp_label := DigitReadout.new()
	hp_label.sheet = "ui/portrait/digits_3x5_outlined.png"
	hp_label.cell = Vector2i(5, 7)
	hp_label.advance = 4
	hp_label.position = Vector2(float(text_rect[0]), float(text_rect[1]))
	hp_label.size = Vector2(float(text_rect[2]), float(text_rect[3]))
	hp_label.name = "HpDigits"
	hp_label.set_text(str(int(member["hp"])))
	host.add_child(hp_label)
	var threat_rect: Array = spec["threat"]
	var threat_label := Widgets.label("", Layout.font_tiny(), SpriteCatalog.GOLD)
	threat_label.name = "Threat"
	threat_label.position = Vector2(float(threat_rect[0]), float(threat_rect[1]))
	threat_label.size = Vector2(float(threat_rect[2]), float(threat_rect[3]))
	threat_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	threat_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	threat_label.visible = false
	seat.add_child(threat_label)
	_bars[pid] = {"hp_fill": hp_fill, "mp_fill": mp_fill, "hp_text": hp_label, "hp_ratio": float(member["hp"]) / float(maxi(1, int(stats["max_hp"]))), "frame": frame}


func _sync_from_units(units: Array) -> void:
	for unit in units:
		sync_unit(unit)


func _add_monster(unit: Dictionary) -> void:
	var sprite_name := ArtPack.monster_sprite(str(unit["kind"]))
	var frame_size := ArtPack.monster_size(sprite_name)
	var node := Control.new()
	node.size = frame_size
	node.set_meta("back", bool(unit.get("back_row", false)))
	node.set_meta("kind", str(unit["kind"]))
	node.set_meta("sprite", sprite_name)
	var bar := Widgets.bar(mini(48, int(frame_size.x)), 6, SpriteCatalog.HP, SpriteCatalog.HP_BACK)
	bar["root"].position = Vector2((frame_size.x - bar["root"].size.x) * 0.5, 0)
	node.add_child(bar["root"])
	Widgets.set_bar(bar, float(unit["hp"]) / float(maxi(1, int(unit["max_hp"]))))
	_bars[str(unit["id"])] = {"hp": bar}
	var sprite := TextureRect.new()
	sprite.name = "Sprite"
	sprite.position = Vector2.ZERO
	sprite.size = frame_size
	sprite.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	sprite.stretch_mode = TextureRect.STRETCH_SCALE
	sprite.mouse_filter = Control.MOUSE_FILTER_IGNORE
	sprite.texture = ArtPack.monster_frame(sprite_name, "idle", 0)
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
	var ids: Array = _monsters.keys()
	var count := maxi(1, ids.size())
	var span := 168.0
	var origin_x := 135.0 - span * 0.5
	for i in ids.size():
		var node: Control = _monsters[ids[i]]
		var sprite_name := str(node.get_meta("sprite"))
		var feet := ArtPack.monster_feet(sprite_name)
		var feet_x := origin_x + span * (float(i) + 0.5) / float(count)
		var feet_y := 222.0 if bool(node.get_meta("back", false)) else 262.0
		node.position = Vector2(feet_x, feet_y) - feet


func _raise(index: int, up: bool) -> void:
	var points := Layout.party_seat_points(_seats.size())
	for i in _seats.size():
		var seat: Control = _seats[i]
		var point: Vector2 = points[i]
		var anchor := Layout.vec("combat", "seat_anchor")
		var base := Vector2(point.x - anchor.x, point.y - anchor.y)
		var raised := up and i == index
		seat.position = base + Vector2(0, -Timing.PLAYER_RISE_PX if raised else 0)
		var host := seat.get_node_or_null("BarHost/Frame") as TextureRect
		if host:
			host.texture = ArtPack.texture("ui/portrait/seat_bars_frame_active.png" if raised else "ui/portrait/seat_bars_frame.png")
			host.position = Vector2(-1, -1) if raised else Vector2.ZERO
			host.size = Vector2(46, 12) if raised else Vector2(44, 10)
		var digits: DigitReadout = seat.get_node_or_null("BarHost/HpDigits") as DigitReadout
		if digits:
			digits.position.y = -7.0 if raised else -6.0
		seat.get_node("Bracket").visible = up and i == index
		seat.get_node("Arrow").visible = up and i == index


func _set_table_visible(show_table: bool) -> void:
	_gm.visible = show_table
	_table.visible = show_table
	_seat_layer.visible = show_table


func _set_frame(node: Control, frame: int) -> void:
	var sprite := node.get_node_or_null("Sprite")
	if sprite is TextureRect and node.has_meta("sprite"):
		var anim := "attack" if frame >= 2 else "idle"
		var index := frame - 2 if frame >= 2 else frame
		(sprite as TextureRect).texture = ArtPack.monster_frame(str(node.get_meta("sprite")), anim, index)


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


func _clipped_fill(rel: String, at: Vector2, full_size: Vector2) -> Dictionary:
	var clip := Control.new()
	clip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	clip.clip_contents = true
	clip.position = at
	clip.size = full_size
	var tex := TextureRect.new()
	tex.texture = ArtPack.texture(rel)
	tex.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	tex.stretch_mode = TextureRect.STRETCH_SCALE
	tex.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tex.size = full_size
	clip.add_child(tex)
	return {"clip": clip, "full": full_size.x}


func _set_clip_ratio(fill: Dictionary, ratio: float) -> void:
	var clip: Control = fill["clip"]
	clip.size.x = float(fill["full"]) * clampf(ratio, 0.0, 1.0)


func _pulse_ready_strip(delta: float) -> void:
	if _strip_panel == null or not is_instance_valid(_strip_panel) or _strip_frames < 2:
		return
	_strip_clock += delta
	var frame := int(_strip_clock * 3.0) % _strip_frames
	var box := _strip_panel.get_theme_stylebox("panel") as StyleBoxTexture
	if box == null or not (box.texture is AtlasTexture):
		return
	var atlas := box.texture as AtlasTexture
	var next := Rect2(float(frame) * 24.0, 0, 24, 14)
	if atlas.region != next:
		atlas.region = next
		_strip_panel.queue_redraw()


func _pulse_low_hp() -> void:
	var frame := int(Time.get_ticks_msec() / 180) % 2
	for id in _bars.keys():
		var info: Dictionary = _bars[id]
		if not info.has("hp_fill"):
			continue
		var clip: Control = info["hp_fill"]["clip"]
		if clip.get_child_count() == 0:
			continue
		var tex: TextureRect = clip.get_child(0)
		if float(info.get("hp_ratio", 1.0)) < 0.25:
			tex.texture = ArtPack.frame_texture("ui/portrait/seat_bar_hp_lowflash.png", frame, Vector2(42, 4))
		else:
			tex.texture = ArtPack.texture("ui/portrait/seat_bar_hp.png")


func _class_has_threat_passive(class_id: String) -> bool:
	var cls: Dictionary = ContentDB.class_def(class_id)
	for skill_id in cls.get("skills", []):
		var skill: Dictionary = ContentDB.skill(str(skill_id))
		if not Formulas.is_passive(skill):
			continue
		for effect in skill.get("effects", []):
			if float(effect.get("threat_mult", 1.0)) > 1.01 or int(effect.get("threat_add", 0)) > 0:
				return true
	return false


func _ensure_taunt(id: String) -> void:
	if not str(id).begins_with("p"):
		return
	var index := int(str(id).substr(1))
	if index < 0 or index >= _seats.size():
		return
	var seat: Control = _seats[index]
	if seat.has_node("TauntBadge"):
		seat.get_node("TauntBadge").visible = true
		return
	var badge := FxStrip.new()
	badge.name = "TauntBadge"
	badge.setup("fx/taunt_badge.png", Vector2(12, 13), 2, 3.0, true)
	badge.position = Vector2(18, -14)
	seat.add_child(badge)


func play_regen_fx(id: String) -> void:
	var node := _node_for(id)
	if node == null:
		return
	var tick := FxStrip.new()
	tick.setup("fx/mana_tick.png", Vector2(16, 28), 6, 10.0, false)
	tick.position = Vector2(24, 77) - Vector2(8, 27)
	node.add_child(tick)
	var plus := FxStrip.new()
	plus.setup("fx/mp_plus.png", Vector2(19, 14), 4, 8.0, false)
	plus.position = Vector2(15, 4)
	node.add_child(plus)


func _numeric_text(text: String) -> bool:
	var body := text.replace("+", "").replace("-", "").replace(" ", "")
	return body.is_valid_int()


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
	var floater: Control
	if _numeric_text(text):
		var digits := DigitReadout.new()
		digits.cell = Vector2i(7, 9)
		digits.advance = 6
		digits.glyph_order = "0123456789+-"
		digits.sheet = "ui/dmg_font_hp.png"
		if color.is_equal_approx(SpriteCatalog.MP):
			digits.sheet = "ui/dmg_font_mp.png"
			digits.letters_sheet = "ui/dmg_font_mp_letters.png"
			digits.letters_order = "MP"
			if not text.contains("M"):
				text = text + " MP"
		elif color.g > color.r and color.g > 0.4:
			digits.sheet = "ui/dmg_font_heal.png"
		digits.size = Vector2(96, 9)
		digits.set_text(text)
		floater = digits
	else:
		floater = Widgets.label(text, Layout.font_size(), color)
	floater.position = node.global_position - global_position + Vector2(8, 0)
	add_child(floater)
	var tween := create_tween()
	tween.tween_property(floater, "position:y", floater.position.y - 18, 0.6)
	tween.parallel().tween_property(floater, "modulate:a", 0.0, 0.6)
	tween.finished.connect(floater.queue_free)


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
		rect.texture = ArtPack.monster_frame(ArtPack.monster_sprite(str(entry.get("kind", "puddleblob"))), "idle", 0)
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
