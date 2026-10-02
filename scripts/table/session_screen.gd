extends Control
class_name SessionScreen
## Table scene for the hub and for combat. Positions come from Layout.

const Pack := preload("res://scripts/core/packed_file.gd")

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
var _turn_name: TextureRect
var _caption: Label
var _caption_plate: Panel
var _initiative: Control
var _inspect: Panel
var _action_art: TextureRect
var _inspect_catcher: Control
var _slot_x: Dictionary = {}
var _banner: Label
var _banner_plate: Panel
var _modal: Control
var _dice: Control
var _dice_labels: Array = []
var _targeting := false
var _seats_front := false
var _flickers: Array = []
var _table: TextureRect
var _gm: TextureRect
var _table_props: Array = []
var _action_back: ColorRect
var _level_open := false
var _armed_action := ""
var _hold_id := ""
var _hold_spent := ""
var _freeze_bars := false
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
	_set_banner_shown(true)
	_apply_hub_plates()
	var place: Dictionary = ContentDB.place(GameState.place_id)
	_banner.text = "%s   %d gold" % [place["name"], GameState.gold]
	_fit_header_plate(_banner_plate, _banner, Layout.rect("hub", "banner"))
	_set_caption(str(place["description"]))
	_sync_party()
	var fight: bool = not ContentDB.place_monster_ids(GameState.place_id).is_empty()
	set_actions([
		{"id": "travel", "label": "Travel", "icon_path": "ui/hub/icon_travel.png", "hub": true},
		{"id": "fight", "label": "Fight", "icon_path": "ui/hub/icon_fight.png", "hub": true, "disabled": not fight},
		{"id": "rest", "label": "Rest", "icon_path": "ui/hub/icon_rest.png", "hub": true},
		{"id": "quest", "label": "Quest", "icon_path": "ui/hub/icon_quest.png", "hub": true},
		{"id": "party", "label": "Gear", "icon_path": "ui/hub/icon_gear.png", "hub": true},
	])
	_close_modal()
	close_stats_sheet()
	if not _level_open and GameState.peek_level() >= 0:
		resolve_level_ups()


func location_banner(text: String) -> void:
	_set_caption(text)
	await get_tree().create_timer(Timing.LOCATION_BANNER).timeout
	if is_instance_valid(self):
		var place: Dictionary = ContentDB.place(GameState.place_id)
		_set_caption(str(place.get("description", "")))


func stage_battle_preview() -> void:
	_dress_reference_party()
	show_hub()
	_set_banner_shown(false)
	_initiative.visible = true
	var rows := [
		{"id": "cinder_mite", "hp_ratio": 1.0},
		{"id": "cave_howler", "hp_ratio": 0.6},
		{"id": "puddleblob", "hp_ratio": 0.85},
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
	_set_caption("")
	var order := [
		{"id": "p0", "side": "player", "index": 0},
		{"id": "m0", "side": "monster", "kind": "cinder_mite"},
		{"id": "p4", "side": "player", "index": 4},
		{"id": "p3", "side": "player", "index": 3},
		{"id": "m1", "side": "monster", "kind": "cave_howler"},
		{"id": "p2", "side": "player", "index": 2},
		{"id": "m2", "side": "monster", "kind": "puddleblob"},
		{"id": "p1", "side": "player", "index": 1},
	]
	set_initiative(order, "p0")
	_raise(0, true)
	_paint_reference_bars()
	_freeze_reference_fx()
	var preview_ranks: Dictionary = (GameState.party[0]["skill_ranks"] as Dictionary).duplicate(true)
	preview_ranks["rallying_brand"] = 0
	show_member_bar(0, {"shieldwall": 2}, "skill:oathstrike", preview_ranks)


func intro(ambush: bool) -> void:
	set_actions([])
	clear_monsters()
	_set_table_visible(false)
	_initiative.visible = false
	_set_banner_shown(false)
	_set_caption("Ambush!" if ambush else "The table goes quiet.")
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
		if str(child.name) == "Rail":
			continue
		child.free()
	var combat: Dictionary = Layout.cfg()["combat"]
	var origin_raw: Array = combat.get("initiative_origin", [4, 3])
	var origin := Vector2(float(origin_raw[0]), float(origin_raw[1]))
	var step := float(combat.get("initiative_step", 29))
	var clip := Control.new()
	clip.name = "Clip"
	clip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	clip.clip_contents = true
	clip.position = origin
	clip.size = Vector2(252.0, 24.0)
	_initiative.add_child(clip)
	for i in order.size():
		var entry: Dictionary = order[i]
		var slot := _initiative_slot(entry, str(entry["id"]) == current_id)
		slot.position = Vector2(step * float(i), 0)
		clip.add_child(slot)
	if not order.is_empty():
		var last_x := step * float(order.size() - 1)
		var divider := ColorRect.new()
		divider.color = Color("f8d040")
		divider.mouse_filter = Control.MOUSE_FILTER_IGNORE
		divider.position = Vector2(last_x + 26.0, 1.0)
		divider.size = Vector2(1, 22)
		clip.add_child(divider)
		var next := _initiative_slot(order[0], false)
		next.position = Vector2(step * float(order.size()) + 1.0, 0)
		clip.add_child(next)
	_initiative.add_child(_scroll_chevron())


func set_actions(entries: Array) -> void:
	hide_inspect()
	if _turn_tab:
		_turn_tab.visible = false
	if _action_back:
		_action_back.visible = true
	if _action_art:
		_action_art.visible = false
	_clear_action_buttons()
	if entries.is_empty():
		return
	var bar := Layout.rect("combat", "action_bar")
	var gap := 3.0
	var count := entries.size()
	var width := (bar.size.x - 4.0 - gap * float(count - 1)) / float(count)
	var height := bar.size.y - 8.0
	var labels := PackedStringArray()
	var want_icon := false
	for entry in entries:
		labels.append(str(entry["label"]))
		if str(entry.get("icon", "")) != "" or str(entry.get("icon_path", "")) != "":
			want_icon = true
	var fit: Dictionary = Widgets.action_row_fit(labels, width, height, want_icon)
	var icon_width := int(fit["icon_width"])
	var x := 2.0
	for entry in entries:
		var button := Widgets.make_button(str(entry["label"]), Vector2(width, height))
		if bool(entry.get("hub", false)):
			Widgets.skin_hub_button(button)
		button.position = Vector2(x, 4)
		button.size = Vector2(width, height)
		button.add_theme_font_size_override("font_size", int(fit["font_size"]))
		button.add_theme_constant_override("h_separation", int(fit["gap"]))
		var icon_path := str(entry.get("icon_path", ""))
		var icon_name := str(entry.get("icon", ""))
		if icon_width > 0 and icon_path != "" and ArtPack.has(icon_path):
			button.icon = ArtPack.texture(icon_path)
			button.expand_icon = true
			button.add_theme_constant_override("icon_max_width", icon_width)
		elif icon_width > 0 and icon_name != "" and Pack.exists("res://art/ui/%s.png" % icon_name):
			button.icon = SpriteCatalog.ui(icon_name)
			button.expand_icon = true
			button.add_theme_constant_override("icon_max_width", icon_width)
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
		var skill_key := str(skill_id)
		skills.append(LevelRules.tune_skill(ContentDB.skill(skill_key), LevelRules.choice_rank(member, skill_key)))
	var mp := int(member["mp"])
	if mp_override >= 0:
		mp = mp_override
	var class_label := str(cls.get("name", "")).to_upper()
	show_actor_bar(class_label, skills, ranks, int(member["hp"]), mp, cooldowns, {}, selected_id, false)


func show_actor_bar(actor_name: String, skills: Array, ranks: Dictionary, hp: int, mp: int, cooldowns: Dictionary, buildup: Dictionary, selected_id: String, cancel_selected: bool = false) -> void:
	_turn_tab.visible = true
	_set_turn_name(actor_name)
	if _action_back:
		_action_back.visible = false
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
		Widgets.bind_pointer(button)
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
				var left := int(entry.get("badge", "0")) if str(entry.get("badge", "0")).is_valid_int() else 0
				var total := int(entry["skill"].get("cooldown", left))
				var open_px := 0
				if total > 0:
					open_px = int(round((1.0 - float(left) / float(total)) * 24.0))
				open_px = clampi(open_px, 0, 23)
				var mask := _icon_rect("ui/skills/skill_cooldown_mask.png")
				var region := AtlasTexture.new()
				region.atlas = ArtPack.texture("ui/skills/skill_cooldown_mask.png")
				region.region = Rect2(0, open_px, 24, 24 - open_px)
				mask.texture = region
				mask.position = Vector2(4, 4 + open_px)
				mask.size = Vector2(24, 24 - open_px)
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
		if button_state == "passive":
			var plum := ColorRect.new()
			plum.color = Color("52288a")
			plum.mouse_filter = Control.MOUSE_FILTER_IGNORE
			plum.position = Vector2(24, 23)
			plum.size = Vector2(7, 8)
			button.add_child(plum)
			var tag := PixelFont.label("P", Color("fcf0a0"))
			tag.position = Vector2(26, 24)
			button.add_child(tag)
		elif button_state == "cooldown" and str(entry.get("badge", "")).is_valid_int():
			var box := ColorRect.new()
			box.color = Color("120c18")
			box.mouse_filter = Control.MOUSE_FILTER_IGNORE
			box.position = Vector2(12, 12)
			box.size = Vector2(8, 8)
			button.add_child(box)
			var turns := DigitReadout.new()
			turns.sheet = "ui/portrait/digits_3x5.png"
			turns.cell = Vector2i(4, 5)
			turns.advance = 4
			turns.position = Vector2(2, 2)
			turns.size = Vector2(6, 5)
			turns.set_text(str(entry.get("badge", "")))
			box.add_child(turns)
		var badge_text := str(entry.get("badge", ""))
		var show_cost := badge_text.is_valid_int() and button_state != "passive" and button_state != "cooldown" and button_state != "locked"
		if show_cost and badge_text.length() == 1:
			var pill := _icon_rect("ui/portrait/cost_badge_0_9.png")
			pill.texture = ArtPack.frame_texture("ui/portrait/cost_badge_0_9.png", int(badge_text), Vector2(16, 7))
			pill.position = Vector2(8, 34)
			pill.size = Vector2(16, 7)
			button.add_child(pill)
		elif show_cost:
			var pill_wide := _icon_rect("ui/portrait/cost_badge.png")
			pill_wide.position = Vector2(8, 34)
			pill_wide.size = Vector2(16, 7)
			button.add_child(pill_wide)
			var badge := DigitReadout.new()
			badge.sheet = "ui/portrait/digits_3x5.png"
			badge.cell = Vector2i(4, 5)
			badge.advance = 4
			var digit_w := badge_text.length() * 4
			badge.position = Vector2(float(16 - digit_w) * 0.5, 1)
			badge.size = Vector2(digit_w, 5)
			badge.set_text(badge_text)
			pill_wide.add_child(badge)
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
	show_inspect(_inspect_card(action_id, ranks, int(member["hp"]), mp, cooldowns, {}, member_index), action_id)


func show_inspect(card: Dictionary, action_id: String) -> void:
	if _inspect == null:
		return
	var size_rect := Layout.rect("combat", "skill_card")
	var center := float(_slot_x.get(action_id, 135.0))
	var width := size_rect.size.x
	var height := Widgets.pixel_card_height(str(card.get("description", "")), width)
	var left := clampf(center - width * 0.5, 4.0, Layout.viewport_size().x - width - 4.0)
	var bar_top := 480.0
	for point in Layout.party_seat_points(maxi(1, _seats.size())):
		bar_top = minf(bar_top, point.y - 11.0)
	var top := bar_top - 14.0 - height
	_inspect.position = Vector2(left, top)
	_inspect.size = Vector2(width, height)
	_fill_inspect(card, action_id)
	_dim_other_slots(action_id)
	_arm_slot(action_id)
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
	_clear_slot_dims()
	_clear_arm_glow()


func _inspect_card(action_id: String, ranks: Dictionary, hp: int, mp: int, cooldowns: Dictionary, buildup: Dictionary, member_index: int = -1) -> Dictionary:
	if action_id.begins_with("skill:"):
		var skill_id := action_id.trim_prefix("skill:")
		var skill: Dictionary = ContentDB.skill(skill_id)
		var rank := int(ranks.get(skill_id, 0))
		var extra := 0
		if member_index >= 0 and member_index < GameState.party.size():
			extra = LevelRules.choice_rank(GameState.party[member_index], skill_id)
		return Formulas.skill_inspect(LevelRules.tune_skill(skill, extra), rank, hp, mp, cooldowns, buildup)
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
	var title := PixelFont.label(str(card.get("name", "")), Color("120c18"), 2)
	title.position = Vector2(66, 13)
	_inspect.add_child(title)
	var tag_path := "ui/portrait/skill_tag_passive.png" if passive else "ui/portrait/skill_tag_active.png"
	var tag := _icon_rect(tag_path)
	var tag_tex := ArtPack.texture(tag_path)
	var tag_size := tag_tex.get_size() if tag_tex else Vector2(29, 9)
	tag.position = Vector2(_inspect.size.x - 8.0 - tag_size.x, 12)
	tag.size = tag_size
	_inspect.add_child(tag)
	_fill_cost_row(card, passive)
	var target_at := Vector2(66, 35)
	var target_icon := _target_icon(str(card.get("target", "")))
	if target_icon != "":
		var mark := _icon_rect(target_icon)
		mark.position = target_at
		mark.size = Vector2(9, 7)
		_inspect.add_child(mark)
	var target_label := PixelFont.label(str(card.get("target", "")), Color("744526"))
	target_label.position = target_at + Vector2(12, 1)
	_inspect.add_child(target_label)
	var cd_at := Vector2(66, 45)
	var cd_icon := _icon_rect("ui/portrait/icon_cooldown.png")
	cd_icon.position = cd_at
	cd_icon.size = Vector2(9, 7)
	_inspect.add_child(cd_icon)
	var cd_copy := "ALWAYS ON" if passive else _cooldown_line(str(card.get("cooldown", "")))
	var cd_label := PixelFont.label(cd_copy, Color("744526"))
	cd_label.position = cd_at + Vector2(12, 1)
	_inspect.add_child(cd_label)
	var timing := str(card.get("timing", ""))
	if timing != "":
		var timing_copy := "EACH TURN" if timing == "Each turn" else "IMMEDIATE"
		var timing_label := PixelFont.label(timing_copy, Color("3d7a4a"))
		timing_label.name = "HealTiming"
		timing_label.position = Vector2(_inspect.size.x - 8.0 - timing_label.size.x, cd_at.y + 1.0)
		timing_label.set_meta("caption", timing_copy)
		_inspect.add_child(timing_label)
	var chars := int((_inspect.size.x - 32.0 + 1.0) / 4.0)
	var lines := PixelFont.wrap(str(card.get("description", "")), chars)
	for i in lines.size():
		var line := PixelFont.label(lines[i], Color("2c1810"))
		line.position = Vector2(16, 62 + i * 8)
		_inspect.add_child(line)
	var hint := str(card.get("hint", ""))
	var strip_path := "ui/portrait/skill_card_strip_ready.png"
	var frames := 2
	var hint_copy := "TAP AGAIN TO CAST"
	var hint_color := Color("f8d040")
	if passive or hint == "Always on":
		strip_path = "ui/portrait/skill_card_strip_passive.png"
		frames = 1
		hint_copy = "PASSIVE: ALWAYS ACTIVE"
		hint_color = Color("fcb8d4")
	elif hint == "On cooldown":
		strip_path = "ui/portrait/skill_card_strip_cooldown.png"
		frames = 1
		hint_copy = "ON COOLDOWN: %d" % _first_int(str(card.get("cooldown", "")))
		hint_color = Color("cfd0d4")
	elif hint == "Pick a target":
		hint_copy = "PICK A TARGET"
		hint_color = Color("f8d040")
	elif hint.begins_with("Not enough") or hint == "Not learned yet":
		strip_path = "ui/portrait/skill_card_strip_nomp.png"
		frames = 1
		hint_copy = "NOT LEARNED YET" if hint == "Not learned yet" else "NOT ENOUGH MP"
		hint_color = Color("ec5a44")
	var strip := Panel.new()
	strip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	strip.position = Vector2(8, _inspect.size.y - 19)
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
	var hint_label := PixelFont.label(hint_copy, hint_color)
	hint_label.position = Vector2((strip.size.x - hint_label.size.x) * 0.5, 5)
	hint_label.name = "Hint"
	_inspect.set_meta("hint", hint_copy)
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
	if Widgets.is_press(event):
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
	_set_caption(text)


func _set_caption(text: String) -> void:
	_caption.text = text
	if _caption_plate:
		_caption_plate.visible = text != ""
		_fit_header_plate(_caption_plate, _caption, Layout.rect("combat", "caption"))


func _header_frame(plate: Panel) -> float:
	var style := plate.get_theme_stylebox("panel")
	if style is StyleBoxTexture:
		return (style as StyleBoxTexture).texture_margin_top
	if style is StyleBoxFlat:
		return float((style as StyleBoxFlat).get_border_width(SIDE_TOP))
	return 0.0


func _fit_header_plate(plate: Panel, label: Label, base: Rect2) -> void:
	if plate == null or label == null:
		return
	var frame := _header_frame(plate)
	var font_size := label.get_theme_font_size("font_size")
	var height := Widgets.fitted_header_height(label.text, base.size.x, font_size, base.size.y, frame)
	plate.position = base.position
	plate.size = Vector2(base.size.x, height)
	label.position = Vector2(frame, frame)
	label.size = Vector2(maxf(1.0, base.size.x - frame * 2.0), height - frame * 2.0)


func _apply_hub_plates() -> void:
	if _banner_plate:
		_banner_plate.add_theme_stylebox_override("panel", Widgets.hub_plate())
	if _caption_plate:
		_caption_plate.add_theme_stylebox_override("panel", Widgets.hub_plate())


func _set_banner_shown(shown: bool) -> void:
	if _banner_plate:
		_banner_plate.visible = shown


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
	var recovery := _floater_is_recovery(texts)
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
		var tint := Color(0.55, 1.0, 0.65, base.a) if recovery else Color(1, 0.3, 0.3, base.a)
		flash.tween_property(sprite, "modulate", tint, Timing.HIT_BLINK_IN)
		flash.tween_property(sprite, "modulate", base, Timing.HIT_BLINK_OUT)
	if _bars.has(id):
		if _bars[id].has("hp"):
			Widgets.tween_bar(_bars[id]["hp"], hp_ratio, Timing.HP_TWEEN)
		if _bars[id].has("hp_art"):
			_tween_clip(_bars[id]["hp_art"], hp_ratio, Timing.HP_TWEEN)
		if _bars[id].has("mp"):
			Widgets.tween_bar(_bars[id]["mp"], mp_ratio, Timing.HP_TWEEN)
	var delay := 0.0
	for entry in texts:
		_queue_floater(id, str(entry["text"]), entry["color"], delay)
		delay += Timing.FLOATER_QUEUE
	if not recovery:
		Sfx.play("hit")


func _floater_is_recovery(texts: Array) -> bool:
	for entry in texts:
		if str(entry.get("text", "")).begins_with("+"):
			return true
	return false


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


func set_target_mode(valid_ids: Array, _hint: String) -> void:
	_targeting = true
	_stop_flickers()
	var allies := false
	for id in valid_ids:
		if str(id).begins_with("p"):
			allies = true
	if allies and _seat_layer:
		move_child(_seat_layer, get_child_count() - 1)
		_seats_front = true
	elif _seats_front:
		_restore_seat_layer()
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
	if _seats_front:
		_restore_seat_layer()
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
	Widgets.place_wrapped(copy, Vector2(8, 36), Vector2(230, 120))
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
	if get_node_or_null("QuestScreen"):
		return
	_close_modal()
	var log := QuestScreen.new()
	log.setup("log")
	add_child(log)
	log.move_to_front()
	log.closed.connect(func():
		if is_instance_valid(log):
			log.queue_free()
		if is_instance_valid(self):
			show_hub()
	)


func sync_unit(unit: Dictionary) -> void:
	var id := str(unit["id"])
	if not _bars.has(id):
		return
	var hp_ratio := 0.0 if int(unit["max_hp"]) <= 0 else float(unit["hp"]) / float(unit["max_hp"])
	var mp_ratio := 0.0 if int(unit.get("max_mp", 1)) <= 0 else float(unit.get("mp", 0)) / float(unit["max_mp"])
	var info: Dictionary = _bars[id]
	if info.has("hp"):
		Widgets.set_bar(info["hp"], hp_ratio)
	if info.has("hp_art"):
		var art: Dictionary = info["hp_art"]
		art["clip"].size.x = float(int(30.0 * clampf(hp_ratio, 0.0, 1.0)))
	if info.has("mp"):
		Widgets.set_bar(info["mp"], mp_ratio)
	if info.has("hp_fill"):
		_set_clip_ratio(info["hp_fill"], hp_ratio)
		info["hp_ratio"] = hp_ratio
	if info.has("mp_fill"):
		_set_clip_ratio(info["mp_fill"], mp_ratio)
	if info.has("hp_text"):
		var digits: DigitReadout = info["hp_text"]
		digits.set_text(Formulas.vital_text(int(unit["hp"]), int(unit["max_hp"])))
	if info.has("mp_text"):
		var mp_digits: DigitReadout = info["mp_text"]
		mp_digits.set_text(Formulas.vital_text(int(unit.get("mp", 0)), int(unit.get("max_mp", 0))))
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
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bg)
	_apply_backdrop()
	_inspect_catcher = Control.new()
	_inspect_catcher.set_anchors_preset(Control.PRESET_FULL_RECT)
	_inspect_catcher.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_inspect_catcher.gui_input.connect(_on_dismiss_input)
	add_child(_inspect_catcher)
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
	_gm.position = gm_feet - Vector2(22, 45)
	add_child(_gm)
	_table = TextureRect.new()
	_table.texture = ArtPack.texture("combat/table_portrait.png")
	_table.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_table.stretch_mode = TextureRect.STRETCH_SCALE
	_table.mouse_filter = Control.MOUSE_FILTER_IGNORE
	Layout.place(_table, Layout.rect("combat", "table"))
	add_child(_table)
	_add_table_props()
	_seat_layer = Control.new()
	_seat_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_seat_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_seat_layer)
	_initiative = Control.new()
	_initiative.mouse_filter = Control.MOUSE_FILTER_IGNORE
	Layout.place(_initiative, Layout.rect("combat", "initiative"))
	add_child(_initiative)
	var rail := Panel.new()
	rail.name = "Rail"
	rail.mouse_filter = Control.MOUSE_FILTER_IGNORE
	rail.set_anchors_preset(Control.PRESET_FULL_RECT)
	rail.offset_left = 0
	rail.offset_top = 0
	rail.offset_right = 0
	rail.offset_bottom = 0
	rail.add_theme_stylebox_override("panel", ArtPack.nine_slice("ui/panel_dark.png", 6, 6, 6, 6))
	_initiative.add_child(rail)
	var banner_rect := Layout.rect("hub", "banner")
	_banner_plate = Widgets.header_plate()
	_banner_plate.name = "BannerPlate"
	Layout.place(_banner_plate, banner_rect)
	add_child(_banner_plate)
	_banner = Widgets.label("", Layout.font_small(), Widgets.header_ink())
	Widgets.enable_wrap(_banner)
	_banner.position = Vector2(4, 1)
	_banner.size = Vector2(banner_rect.size.x - 8.0, banner_rect.size.y - 2.0)
	_banner.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_banner_plate.add_child(_banner)
	var caption_rect := Layout.rect("combat", "caption")
	_caption_plate = Widgets.header_plate()
	_caption_plate.name = "CaptionPlate"
	Layout.place(_caption_plate, caption_rect)
	add_child(_caption_plate)
	_caption = Widgets.label("", Layout.font_tiny(), Widgets.header_ink())
	Widgets.enable_wrap(_caption)
	_caption.position = Vector2(4, 1)
	_caption.size = Vector2(caption_rect.size.x - 8.0, caption_rect.size.y - 2.0)
	_caption.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_caption.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_caption_plate.add_child(_caption)
	_turn_tab = Panel.new()
	var tab_box := StyleBoxTexture.new()
	tab_box.texture = ArtPack.texture("ui/portrait/name_tab.png")
	tab_box.content_margin_left = 0
	tab_box.content_margin_right = 0
	tab_box.content_margin_top = 0
	tab_box.content_margin_bottom = 0
	_turn_tab.add_theme_stylebox_override("panel", tab_box)
	_turn_tab.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_turn_tab.visible = false
	Layout.place(_turn_tab, Layout.rect("combat", "name_tab"))
	add_child(_turn_tab)
	_turn_name = TextureRect.new()
	_turn_name.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_turn_name.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_turn_name.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_turn_name.stretch_mode = TextureRect.STRETCH_SCALE
	_turn_name.position = Vector2(5, 2)
	_turn_tab.add_child(_turn_name)
	_action_back = ColorRect.new()
	_action_back.color = Color(0.12, 0.08, 0.05, 0.92)
	_action_back.mouse_filter = Control.MOUSE_FILTER_IGNORE
	Layout.place(_action_back, Layout.rect("combat", "action_bar"))
	add_child(_action_back)
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
			aura.position = Vector2(-4, 65)
			seat.add_child(aura)
			var badge := FxStrip.new()
			badge.name = "TauntBadge"
			badge.setup("fx/taunt_badge.png", Vector2(12, 13), 2, 3.0, true)
			badge.position = Vector2(30, -7)
			seat.add_child(badge)
		var doll := PaperDoll.new()
		doll.name = "Doll"
		var class_id := str(member["class_id"])
		var seat_gear := PaperDoll.seat_spec(member)
		var armed := bool(seat_gear.get("main_weapon", false))
		var main_tag := str(seat_gear.get("main_tag", ""))
		if ArtPack.seat_is_default(class_id, member["look"]):
			doll.show_sheet(ArtPack.seat_idle(class_id, armed, main_tag), canvas)
		else:
			doll.set_look(member["look"], class_id, str(member["race"]), "back")
		doll.show_gear(member)
		seat.add_child(doll)
		if _class_regens_mp(class_id):
			var plus := FxStrip.new()
			plus.name = "MpPlus"
			plus.setup("fx/mp_plus.png", Vector2(19, 14), 4, 8.0, true)
			plus.position = Vector2(13, -16)
			seat.add_child(plus)
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
	_order_seats(points)
	_apply_backdrop()


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
	hp_label.set_text(Formulas.vital_text(int(member["hp"]), int(stats["max_hp"])))
	host.add_child(hp_label)
	var mp_text: Array = spec.get("mp_text", [0, 11, 44, 7])
	var mp_label := DigitReadout.new()
	mp_label.sheet = "ui/portrait/digits_3x5_outlined.png"
	mp_label.cell = Vector2i(5, 7)
	mp_label.advance = 4
	mp_label.position = Vector2(float(mp_text[0]), float(mp_text[1]))
	mp_label.size = Vector2(float(mp_text[2]), float(mp_text[3]))
	mp_label.name = "MpDigits"
	mp_label.set_text(Formulas.vital_text(int(member["mp"]), int(stats["max_mp"])))
	host.add_child(mp_label)
	var threat_rect: Array = spec["threat"]
	var threat_label := Widgets.label("", Layout.font_tiny(), SpriteCatalog.GOLD)
	threat_label.name = "Threat"
	threat_label.position = Vector2(float(threat_rect[0]), float(threat_rect[1]))
	threat_label.size = Vector2(float(threat_rect[2]), float(threat_rect[3]))
	threat_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	threat_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	threat_label.visible = false
	seat.add_child(threat_label)
	_bars[pid] = {
		"hp_fill": hp_fill,
		"mp_fill": mp_fill,
		"hp_text": hp_label,
		"mp_text": mp_label,
		"hp_ratio": float(member["hp"]) / float(maxi(1, int(stats["max_hp"]))),
		"frame": frame,
	}


func _sync_from_units(units: Array) -> void:
	for unit in units:
		sync_unit(unit)


func _add_monster(unit: Dictionary) -> void:
	var sprite_name := ArtPack.monster_sprite(str(unit["kind"]))
	var frame_size := ArtPack.monster_size(sprite_name)
	var node := Control.new()
	node.clip_contents = true
	node.mouse_filter = Control.MOUSE_FILTER_STOP
	node.set_meta("back", bool(unit.get("back_row", false)))
	node.set_meta("kind", str(unit["kind"]))
	node.set_meta("size", _monster_size_tag(unit))
	node.set_meta("sprite", sprite_name)
	node.set_meta("frame", frame_size)
	node.set_meta("hp_anchor", ArtPack.monster_hp_anchor(sprite_name))
	var trough := _icon_rect("ui/enemy_bar_bg.png")
	trough.name = "Trough"
	trough.size = Vector2(32, 5)
	node.add_child(trough)
	var hp_fill := _clipped_fill("ui/enemy_bar_hp.png", Vector2.ZERO, Vector2(30, 3))
	hp_fill["clip"].name = "HpClip"
	node.add_child(hp_fill["clip"])
	var ratio := float(unit["hp"]) / float(maxi(1, int(unit["max_hp"])))
	hp_fill["clip"].size.x = float(int(30.0 * clampf(ratio, 0.0, 1.0)))
	_bars[str(unit["id"])] = {"hp_art": hp_fill}
	var sprite := TextureRect.new()
	sprite.name = "Sprite"
	sprite.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	sprite.stretch_mode = TextureRect.STRETCH_SCALE
	sprite.mouse_filter = Control.MOUSE_FILTER_IGNORE
	sprite.texture = ArtPack.monster_frame(sprite_name, "idle", 0)
	node.add_child(sprite)
	node.move_child(sprite, 0)
	var conds := Widgets.label("", Layout.font_tiny(), SpriteCatalog.LIGHT)
	conds.name = "Conds"
	conds.mouse_filter = Control.MOUSE_FILTER_IGNORE
	node.add_child(conds)
	var uid := str(unit["id"])
	node.gui_input.connect(_pointer_input.bind(uid))
	_monster_layer.add_child(node)
	_monsters[uid] = node


func _monster_size_tag(unit: Dictionary) -> String:
	var tagged := str(unit.get("size", ""))
	if tagged == "large" or tagged == "regular":
		return tagged
	var kind := str(unit.get("kind", ""))
	if ContentDB.monsters.has(kind):
		return Formulas.monster_size_tag(ContentDB.monster(kind))
	return "regular"


func _layout_monsters() -> void:
	var ids: Array = _monsters.keys()
	var entries: Array = []
	for id in ids:
		var node: Control = _monsters[id]
		entries.append({
			"size": str(node.get_meta("size", "regular")),
			"back": bool(node.get_meta("back", false)),
		})
	var rects: Array = Formulas.enemy_layout(entries)
	for i in ids.size():
		_place_monster(_monsters[ids[i]], rects[i])


func _place_monster(node: Control, rect: Rect2) -> void:
	node.position = rect.position
	node.size = rect.size
	var sprite := node.get_node_or_null("Sprite") as TextureRect
	if sprite:
		sprite.position = Vector2.ZERO
		sprite.size = rect.size
	var frame: Vector2 = node.get_meta("frame", Vector2(Formulas.FRAME_W, Formulas.FRAME_H))
	var scale := Vector2(rect.size.x / maxf(frame.x, 1.0), rect.size.y / maxf(frame.y, 1.0))
	var anchor: Vector2 = node.get_meta("hp_anchor", Vector2(frame.x * 0.5, 12.0))
	var bar_pos := anchor * scale - Vector2(16, 4)
	bar_pos.x = clampf(bar_pos.x, 0.0, maxf(0.0, rect.size.x - 32.0))
	bar_pos.y = clampf(bar_pos.y, 0.0, maxf(0.0, rect.size.y - 5.0))
	var trough := node.get_node_or_null("Trough") as Control
	if trough:
		trough.position = bar_pos
	var clip := node.get_node_or_null("HpClip") as Control
	if clip:
		clip.position = bar_pos + Vector2(1, 1)
	var conds := node.get_node_or_null("Conds") as Control
	if conds:
		conds.position = Vector2(0, maxf(0.0, rect.size.y - 10.0))
		conds.size = Vector2(rect.size.x, 10)


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
		var bars: Dictionary = Layout.cfg()["combat"]["chair_bars"]
		var hp_home := float(bars["hp_text"][1])
		var mp_home := float(bars["mp_text"][1])
		var digits: DigitReadout = seat.get_node_or_null("BarHost/HpDigits") as DigitReadout
		if digits:
			digits.position.y = hp_home - (1.0 if raised else 0.0)
		var mp_digits: DigitReadout = seat.get_node_or_null("BarHost/MpDigits") as DigitReadout
		if mp_digits:
			mp_digits.position.y = mp_home - (1.0 if raised else 0.0)
		var doll := seat.get_node_or_null("Doll") as PaperDoll
		if doll:
			doll.set_raised(raised)
		if seat.has_node("TauntAura"):
			seat.get_node("TauntAura").position = Vector2(-4, 68 if raised else 65)
		if seat.has_node("TauntBadge"):
			seat.get_node("TauntBadge").position = Vector2(30, -4 if raised else -7)
		seat.get_node("Bracket").visible = false
		seat.get_node("Arrow").visible = false


func _set_table_visible(show_table: bool) -> void:
	_gm.visible = show_table
	_table.visible = show_table
	for prop in _table_props:
		var node := prop as CanvasItem
		if node:
			node.visible = show_table
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


func set_armed_action(action_id: String) -> void:
	_armed_action = action_id


func _pointer_input(event: InputEvent, unit_id: String) -> void:
	if Widgets.is_press(event):
		_begin_hold(unit_id)
	elif Widgets.is_release(event):
		_end_hold(unit_id)


func _card_input(event: InputEvent, pid: String) -> void:
	_pointer_input(event, pid)


func _begin_hold(unit_id: String) -> void:
	_hold_spent = ""
	_hold_id = unit_id
	var timer := get_tree().create_timer(0.45)
	timer.timeout.connect(_complete_hold.bind(unit_id), CONNECT_ONE_SHOT)


func _complete_hold(unit_id: String) -> void:
	if _hold_id != unit_id:
		return
	_hold_id = ""
	_hold_spent = unit_id
	if unit_id.begins_with("m"):
		show_enemy_sheet(unit_id)


func _end_hold(unit_id: String) -> void:
	var spent := _hold_spent == unit_id
	var holding := _hold_id == unit_id
	_hold_id = ""
	_hold_spent = ""
	if spent or not holding:
		return
	if get_node_or_null("LevelPanel") != null:
		return
	_pulse_node(_node_for(unit_id))
	if unit_id.begins_with("p"):
		if _ally_tap_targets():
			target_pressed.emit(unit_id)
		else:
			show_hero_sheet(int(unit_id.trim_prefix("p")))
	else:
		target_pressed.emit(unit_id)


func _ally_tap_targets() -> bool:
	if _targeting:
		return true
	if _armed_action.begins_with("skill:"):
		return true
	if _armed_action == "item" or _armed_action.begins_with("item:"):
		return true
	return false


func show_hero_sheet(index: int) -> void:
	if index < 0 or index >= GameState.party.size():
		return
	var member: Dictionary = GameState.party[index]
	var stats := GameState.combat_stats(member)
	var unit := _battle_unit("p%d" % index)
	var hp := int(member["hp"])
	var max_hp := int(stats["max_hp"])
	var mp := int(member["mp"])
	var max_mp := int(stats["max_mp"])
	var body := int(stats["body"])
	var senses := int(stats["senses"])
	var mind := int(stats["mind"])
	var attack := int(stats["attack"])
	var dr := int(stats["dr"])
	var crit := float(stats["crit"])
	var spell := float(stats["spell_bonus"])
	var flat_threat := int(stats["gear_threat"])
	if not unit.is_empty():
		hp = int(unit.get("hp", hp))
		max_hp = int(unit.get("max_hp", max_hp))
		mp = int(unit.get("mp", mp))
		max_mp = int(unit.get("max_mp", max_mp))
		body = int(unit.get("body", body)) + int(unit.get("body_shift", 0))
		senses = int(unit.get("senses", senses))
		mind = int(unit.get("mind", mind)) + int(unit.get("mind_shift", 0))
		attack = int(unit.get("attack", attack))
		dr = int(unit.get("dr", dr))
		crit = float(unit.get("crit_bonus", crit))
		spell = float(unit.get("spell_bonus", spell))
		flat_threat = int(unit.get("gear_threat", flat_threat))
	var persona := str(ContentDB.persona(str(member["persona"])).get("name", "Hero"))
	var role_name := str(ContentDB.class_def(str(member["class_id"])).get("name", ""))
	var level := int(member["level"])
	var rules: Dictionary = ContentDB.threat_rules()
	var cls: Dictionary = ContentDB.class_def(str(member["class_id"]))
	var threat := Formulas.member_threat(
		int(cls.get("base_threat", 0)), body, dr, flat_threat,
		1.0, 1.0, float(rules.get("body_per", 0.0)), float(rules.get("armor_per", 0.0))
	)
	var lines: PackedStringArray = []
	lines.append(persona)
	lines.append("%s    Level %d" % [role_name, level])
	lines.append("XP %d / %d to next" % [int(member["xp"]), Formulas.xp_to_next(level)])
	lines.append("HP %s" % Formulas.vital_text(hp, max_hp))
	lines.append("MP %s" % Formulas.vital_text(mp, max_mp))
	lines.append("Body %d    Senses %d    Mind %d" % [body, senses, mind])
	lines.append("Attack %d    Defense %d" % [attack, dr])
	lines.append("Crit %d    Threat %d    Spell %.2f" % [int(round(crit)), threat, spell])
	lines.append("Gear")
	var worn := 0
	for item_id in Formulas.gear_ids(Formulas.normalize_gear(member.get("gear", {}))):
		var item := ContentDB.resolve(str(item_id))
		if item.is_empty():
			continue
		lines.append(str(item.get("name", item_id)))
		worn += 1
	if worn == 0:
		lines.append("Nothing worn")
	lines.append("Skills")
	var names := {}
	for skill_id in cls.get("skills", []):
		var skill: Dictionary = ContentDB.skill(str(skill_id))
		var rank := int(member.get("skill_ranks", {}).get(str(skill_id), 1))
		var pick := LevelRules.choice_rank(member, str(skill_id))
		var skill_name := str(skill.get("name", skill_id))
		names[str(skill_id)] = skill_name
		if pick > 0:
			lines.append("%s rank %d, pick +%d" % [skill_name, rank, pick])
		else:
			lines.append("%s rank %d" % [skill_name, rank])
	var grown := LevelRules.sheet_line(member, names)
	lines.append("Picks")
	lines.append(grown if grown != "" else "No level-up picks yet")
	_open_stats_sheet(lines)


func show_enemy_sheet(unit_id: String) -> void:
	var unit := _battle_unit(unit_id)
	if unit.is_empty():
		return
	var kind := str(unit.get("kind", ""))
	var monster: Dictionary = ContentDB.monster(kind) if ContentDB.monsters.has(kind) else {}
	var lines: PackedStringArray = []
	lines.append(str(unit.get("name", monster.get("name", "Foe"))))
	lines.append("Level %d" % int(unit.get("level", monster.get("level", 1))))
	lines.append("HP %s" % Formulas.vital_text(int(unit.get("hp", 0)), int(unit.get("max_hp", 0))))
	lines.append("Attack %d" % int(unit.get("attack", 0)))
	_open_stats_sheet(lines)


func _battle_unit(unit_id: String) -> Dictionary:
	for child in get_children():
		if child is BattleFlow:
			for unit in (child as BattleFlow).units:
				if str(unit.get("id", "")) == unit_id:
					return unit
	return {}


func _open_stats_sheet(lines: PackedStringArray) -> void:
	close_stats_sheet()
	var root := Control.new()
	root.name = "StatsSheet"
	root.mouse_filter = Control.MOUSE_FILTER_STOP
	root.position = Vector2.ZERO
	root.size = Layout.viewport_size()
	add_child(root)
	var veil := ColorRect.new()
	veil.color = Color(0.08, 0.05, 0.03, 0.55)
	veil.mouse_filter = Control.MOUSE_FILTER_STOP
	veil.position = Vector2.ZERO
	veil.size = root.size
	veil.gui_input.connect(func(event: InputEvent) -> void:
		if Widgets.is_press(event):
			close_stats_sheet()
	)
	root.add_child(veil)
	var sheet := Panel.new()
	sheet.name = "Sheet"
	var plate := StyleBoxFlat.new()
	plate.bg_color = Color("e8d6b0")
	plate.border_color = Color("5a4028")
	plate.set_border_width_all(2)
	sheet.add_theme_stylebox_override("panel", plate)
	sheet.position = Vector2(8, 8)
	sheet.size = Vector2(254, 464)
	sheet.mouse_filter = Control.MOUSE_FILTER_STOP
	root.add_child(sheet)
	var scroll := ScrollContainer.new()
	scroll.name = "Body"
	scroll.position = Vector2(8, 8)
	scroll.size = Vector2(238, 400)
	scroll.mouse_filter = Control.MOUSE_FILTER_STOP
	sheet.add_child(scroll)
	var column := VBoxContainer.new()
	column.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	column.custom_minimum_size = Vector2(230, 0)
	column.add_theme_constant_override("separation", 4)
	scroll.add_child(column)
	for line in lines:
		var label := Widgets.wrapped_label(line, 230.0, Layout.font_tiny(), SpriteCatalog.INK)
		column.add_child(label)
	var close := Widgets.make_button("Close", Vector2(238, 44))
	close.name = "CloseStats"
	close.position = Vector2(8, 412)
	close.size = Vector2(238, 44)
	close.pressed.connect(close_stats_sheet)
	sheet.add_child(close)
	move_child(root, get_child_count() - 1)


func close_stats_sheet() -> void:
	var panel := get_node_or_null("StatsSheet")
	if panel and is_instance_valid(panel):
		panel.queue_free()


func _pulse_node(node: Control) -> void:
	var visual := _visual(node)
	if visual == null:
		return
	visual.modulate = Color(1.45, 1.22, 0.55)
	var tween := create_tween()
	tween.tween_property(visual, "modulate", Color.WHITE, 0.16)


func _restore_seat_layer() -> void:
	_seats_front = false
	if _seat_layer == null or _initiative == null:
		return
	move_child(_seat_layer, _initiative.get_index())


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
	var frame := 0 if _freeze_bars else int(Time.get_ticks_msec() / 180) % 2
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
	badge.position = Vector2(30, -7)
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


func _apply_backdrop() -> void:
	if get_child_count() == 0:
		return
	var bg := get_child(0) as TextureRect
	if bg == null:
		return
	bg.texture = ArtPack.texture(ContentDB.combat_backdrop_path(GameState.place_id))


func _dress_reference_party() -> void:
	var classes: Array = ["paladin", "cleric", "rogue", "druid", "wizard"]
	for i in mini(classes.size(), GameState.party.size()):
		var member: Dictionary = GameState.party[i]
		var class_id := str(classes[i])
		member["class_id"] = class_id
		member["look"] = ArtPack.default_look(class_id)


func _paint_reference_bars() -> void:
	var numbers: Array = [50, 28, 16, 34, 6]
	var ratios: Array = [1.0, 28.0 / 40.0, 16.0 / 36.0, 34.0 / 38.0, 6.0 / 30.0]
	var mp_ratios: Array = [0.5, 1.0, 0.6, 0.8, 0.35]
	for i in mini(numbers.size(), _seats.size()):
		var seat: Control = _seats[i]
		var digits := seat.get_node_or_null("BarHost/HpDigits") as DigitReadout
		if digits:
			digits.set_text(Formulas.vital_text(int(numbers[i]), int(numbers[i])))
		var mp_digits := seat.get_node_or_null("BarHost/MpDigits") as DigitReadout
		if mp_digits:
			mp_digits.set_text(Formulas.vital_text(int(round(float(mp_ratios[i]) * 20.0)), 20))
		var info: Dictionary = _bars.get("p%d" % i, {})
		if info.has("hp_fill"):
			var hp_px := maxi(1, int(round(42.0 * float(ratios[i]))))
			info["hp_fill"]["clip"].size.x = float(hp_px)
			info["hp_ratio"] = float(ratios[i])
		if info.has("mp_fill"):
			var mp_px := maxi(1, int(round(42.0 * float(mp_ratios[i]))))
			info["mp_fill"]["clip"].size.x = float(mp_px)
	if _seats.size() > 4:
		var tick := FxStrip.new()
		tick.name = "ManaTick"
		tick.setup("fx/mana_tick.png", Vector2(16, 28), 6, 10.0, true)
		tick.position = Vector2(float(int(round(42.0 * 0.35))) - 5.0, 48.0)
		_seats[4].add_child(tick)


func _freeze_reference_fx() -> void:
	_freeze_bars = true
	_pulse_low_hp()
	for seat in _seats:
		var node := seat as Node
		if node.has_node("TauntAura"):
			(node.get_node("TauntAura") as FxStrip).freeze(1)
		if node.has_node("TauntBadge"):
			(node.get_node("TauntBadge") as FxStrip).freeze(0)
		if node.has_node("MpPlus"):
			(node.get_node("MpPlus") as FxStrip).freeze(1)
		if node.has_node("ManaTick"):
			(node.get_node("ManaTick") as FxStrip).freeze(3)
	for id in _monsters.keys():
		var monster: Control = _monsters[id]
		monster.set_meta("acting", true)
		_set_frame(monster, 0)


func _order_seats(points: Array) -> void:
	var order: Array = []
	for i in _seats.size():
		order.append(i)
	for a in order.size():
		for b in range(a + 1, order.size()):
			var ia: int = order[a]
			var ib: int = order[b]
			var pa: Vector2 = points[ia]
			var pb: Vector2 = points[ib]
			var swap := pb.y < pa.y or (pb.y == pa.y and ib < ia)
			if swap:
				order[a] = ib
				order[b] = ia
	for step in order.size():
		_seat_layer.move_child(_seats[order[step]], step)


func _add_table_props() -> void:
	_table_props.clear()
	var screen := _icon_rect("combat/gm_screen.png")
	screen.position = Vector2(83, 329)
	screen.size = Vector2(35, 30)
	add_child(screen)
	_table_props.append(screen)
	var die := _icon_rect("combat/d20_roll.png")
	die.texture = ArtPack.frame_texture("combat/d20_roll.png", 3, Vector2(24, 24))
	die.position = Vector2(152, 333)
	die.size = Vector2(24, 24)
	add_child(die)
	_table_props.append(die)
	var blue := _icon_rect("combat/d6_blue.png")
	blue.texture = ArtPack.frame_texture("combat/d6_blue.png", 4, Vector2(8, 8))
	blue.position = Vector2(210, 345)
	blue.size = Vector2(8, 8)
	add_child(blue)
	_table_props.append(blue)
	var red := _icon_rect("combat/d6_red.png")
	red.texture = ArtPack.frame_texture("combat/d6_red.png", 2, Vector2(8, 8))
	red.position = Vector2(220, 347)
	red.size = Vector2(8, 8)
	add_child(red)
	_table_props.append(red)


func _set_turn_name(text: String) -> void:
	if _turn_name == null:
		return
	var label := text.to_upper()
	_turn_name.texture = PixelFont.texture(label, Color("120c18"))
	_turn_name.size = Vector2(PixelFont.width(label), 5)


func push_vitals(index: int) -> void:
	if index < 0 or index >= GameState.party.size():
		return
	var member: Dictionary = GameState.party[index]
	var stats := GameState.combat_stats(member)
	sync_unit({
		"id": "p%d" % index,
		"hp": int(member["hp"]),
		"max_hp": int(stats["max_hp"]),
		"mp": int(member["mp"]),
		"max_mp": int(stats["max_mp"]),
	})


func push_party_vitals() -> void:
	for index in GameState.party.size():
		push_vitals(index)


func bar_fill_width(unit_id: String) -> float:
	return _pool_fill_width(unit_id, "hp_fill")


func mp_bar_fill_width(unit_id: String) -> float:
	return _pool_fill_width(unit_id, "mp_fill")


func _pool_fill_width(unit_id: String, key: String) -> float:
	if not _bars.has(unit_id):
		return -1.0
	var info: Dictionary = _bars[unit_id]
	if not info.has(key):
		return -1.0
	var clip: Control = info[key]["clip"]
	return clip.size.x


func show_level_panel(member_index: int) -> void:
	close_level_panel()
	if member_index < 0 or member_index >= GameState.party.size():
		return
	var member: Dictionary = GameState.party[member_index]
	var skills: Array = []
	for skill_id in ContentDB.class_def(str(member["class_id"])).get("skills", []):
		skills.append(ContentDB.skill(str(skill_id)))
	var options := LevelRules.offers(member, skills)
	var root := Control.new()
	root.name = "LevelPanel"
	root.mouse_filter = Control.MOUSE_FILTER_STOP
	root.position = Vector2.ZERO
	root.size = Layout.viewport_size()
	add_child(root)
	var veil := ColorRect.new()
	veil.color = Color(0.08, 0.05, 0.03, 0.72)
	veil.mouse_filter = Control.MOUSE_FILTER_STOP
	veil.position = Vector2.ZERO
	veil.size = root.size
	root.add_child(veil)
	var sheet := Panel.new()
	sheet.name = "Sheet"
	var plate := StyleBoxFlat.new()
	plate.bg_color = Color("e8d6b0")
	plate.border_color = Color("5a4028")
	plate.set_border_width_all(2)
	plate.set_content_margin_all(6)
	sheet.add_theme_stylebox_override("panel", plate)
	sheet.position = Vector2(8, 78)
	sheet.size = Vector2(254, 360)
	sheet.mouse_filter = Control.MOUSE_FILTER_STOP
	root.add_child(sheet)
	var text_w := 222.0
	var persona_row: Dictionary = ContentDB.persona(str(member["persona"]))
	var persona := str(persona_row.get("name", "Hero"))
	var title := Widgets.wrapped_label("%s reaches level %d" % [persona, int(member["level"])], text_w, Layout.font_size(), SpriteCatalog.INK)
	var hint := Widgets.wrapped_label("Choose one. The road waits.", text_w, Layout.font_tiny(), SpriteCatalog.INK)
	var y := 8.0
	_place_block(sheet, title, Vector2(12, y), text_w)
	y += title.size.y + 4.0
	_place_block(sheet, hint, Vector2(12, y), text_w)
	y += hint.size.y + 8.0
	for option in options:
		var card := Panel.new()
		var card_box := StyleBoxFlat.new()
		card_box.bg_color = Color("f3e6c8")
		card_box.border_color = Color("5a4028")
		card_box.set_border_width_all(1)
		card.add_theme_stylebox_override("panel", card_box)
		card.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var heading := Widgets.wrapped_label(str(option.get("title", "")), text_w, Layout.font_size(), SpriteCatalog.INK)
		var detail := Widgets.wrapped_label(str(option.get("detail", "")), text_w, Layout.font_tiny(), SpriteCatalog.INK)
		var inner_y := 6.0
		_place_block(card, heading, Vector2(8, inner_y), text_w)
		inner_y += heading.size.y + 4.0
		_place_block(card, detail, Vector2(8, inner_y), text_w)
		inner_y += detail.size.y + 6.0
		var button := Widgets.make_button("Take", Vector2(text_w, 44))
		button.name = "Level_%s" % str(option.get("id", ""))
		button.position = Vector2(8, inner_y)
		button.size = Vector2(text_w, 44)
		var option_id := str(option.get("id", ""))
		button.pressed.connect(_emit_action.bind("level:%s" % option_id))
		card.add_child(button)
		inner_y += 44.0 + 6.0
		card.position = Vector2(8, y)
		card.size = Vector2(238, inner_y)
		sheet.add_child(card)
		y += inner_y + 6.0
	var sheet_h := minf(y + 8.0, 464.0)
	sheet.position = Vector2(8, maxf(8.0, (480.0 - sheet_h) * 0.5))
	sheet.size = Vector2(254, sheet_h)
	move_child(root, get_child_count() - 1)


func _place_block(parent: Control, node: Control, at: Vector2, width: float) -> void:
	var height := maxf(node.custom_minimum_size.y, node.size.y)
	node.position = at
	node.size = Vector2(width, height)
	node.size_flags_horizontal = Control.SIZE_FILL
	parent.add_child(node)


func close_level_panel() -> void:
	var panel := get_node_or_null("LevelPanel")
	if panel and is_instance_valid(panel):
		panel.queue_free()


func resolve_level_ups() -> void:
	if _level_open:
		return
	if GameState.peek_level() < 0:
		return
	_level_open = true
	while GameState.peek_level() >= 0:
		var index := GameState.peek_level()
		show_level_panel(index)
		var picked := ""
		while picked == "":
			var action: String = await action_pressed
			if not str(action).begins_with("level:"):
				continue
			if GameState.commit_level(str(action).trim_prefix("level:")) == "":
				picked = str(action)
				push_vitals(index)
		close_level_panel()
		await get_tree().process_frame
	_level_open = false


func _scroll_chevron() -> TextureRect:
	var image := Image.create(3, 5, false, Image.FORMAT_RGBA8)
	image.fill(Color(0, 0, 0, 0))
	var cream := Color("fcf0a0")
	image.set_pixel(0, 0, cream)
	image.set_pixel(0, 2, cream)
	image.set_pixel(0, 4, cream)
	image.set_pixel(1, 1, cream)
	image.set_pixel(1, 3, cream)
	image.set_pixel(2, 2, cream)
	var rect := TextureRect.new()
	rect.name = "Chevron"
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	rect.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	rect.stretch_mode = TextureRect.STRETCH_SCALE
	rect.texture = ImageTexture.create_from_image(image)
	rect.position = Vector2(264, 11)
	rect.size = Vector2(3, 5)
	return rect


func _initiative_slot(entry: Dictionary, active: bool) -> TextureRect:
	var image := Image.create(24, 24, false, Image.FORMAT_RGBA8)
	var frame_rel := "ui/portrait_frame_active.png" if active else "ui/portrait_frame.png"
	var frame := ArtPack.texture(frame_rel)
	if frame and frame.get_image():
		image.blit_rect(frame.get_image(), Rect2i(0, 0, 24, 24), Vector2i.ZERO)
	var face := _initiative_face(entry)
	image.blend_rect(face, Rect2i(0, 0, mini(20, face.get_width()), mini(20, face.get_height())), Vector2i(2, 2))
	var slot := TextureRect.new()
	slot.mouse_filter = Control.MOUSE_FILTER_IGNORE
	slot.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	slot.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	slot.stretch_mode = TextureRect.STRETCH_SCALE
	slot.texture = ImageTexture.create_from_image(image)
	slot.size = Vector2(24, 24)
	return slot


func _initiative_face(entry: Dictionary) -> Image:
	if str(entry.get("side", "")) == "player":
		var index := int(entry.get("index", 0))
		if index >= 0 and index < GameState.party.size():
			var member: Dictionary = GameState.party[index]
			return ArtPack.front_portrait(member["look"], str(member["class_id"]))
	var sprite := ArtPack.monster_sprite(str(entry.get("kind", "puddleblob")))
	var portrait := ArtPack.monster_portrait(sprite)
	if portrait and portrait.get_image():
		return portrait.get_image()
	return Image.create(20, 20, false, Image.FORMAT_RGBA8)


func _fill_cost_row(card: Dictionary, passive: bool) -> void:
	var at := Vector2(66, 25)
	if passive:
		var none := PixelFont.label("NO COST", Color("9c6636"))
		none.position = at + Vector2(0, 1)
		_inspect.add_child(none)
		return
	var cost := str(card.get("cost", ""))
	var amount := _first_int(cost)
	if cost.find("energy") >= 0 and cost != "Free":
		var words := PixelFont.label("MP COST", Color("243a8a"))
		if amount <= 9:
			var pill := _icon_rect("ui/portrait/cost_badge_0_9.png")
			pill.texture = ArtPack.frame_texture("ui/portrait/cost_badge_0_9.png", amount, Vector2(16, 7))
			pill.position = at
			pill.size = Vector2(16, 7)
			_inspect.add_child(pill)
			words.position = at + Vector2(19, 1)
		else:
			var number := PixelFont.label(str(amount), Color("243a8a"))
			number.position = at + Vector2(0, 1)
			_inspect.add_child(number)
			words.position = at + Vector2(number.size.x + 3.0, 1)
		_inspect.add_child(words)
		return
	var line := PixelFont.label(cost, Color("243a8a") if cost.find("energy") >= 0 else Color("9c6636"))
	line.position = at + Vector2(0, 1)
	_inspect.add_child(line)


func _cooldown_line(text: String) -> String:
	if text == "None" or text == "":
		return "NO COOLDOWN"
	var n := _first_int(text)
	if text.find("left") >= 0:
		return "COOLDOWN %d LEFT" % n
	if n == 1:
		return "COOLDOWN 1 TURN"
	return "COOLDOWN %d TURNS" % n


func _first_int(text: String) -> int:
	var digits := ""
	for i in text.length():
		var ch := text.substr(i, 1)
		if ch >= "0" and ch <= "9":
			digits += ch
		elif digits != "":
			break
	if digits == "":
		return 0
	return int(digits)


func _dim_other_slots(selected_id: String) -> void:
	_clear_slot_dims()
	if _actions == null:
		return
	for child in _actions.get_children():
		if not (child is Button):
			continue
		var button := child as Button
		if str(button.get_meta("action_id", "")) == selected_id:
			continue
		if button.size.x < 30.0:
			continue
		var dim := _icon_rect("ui/portrait/bar_dim_mask.png")
		dim.name = "Dim"
		dim.position = button.position
		dim.size = button.size
		_actions.add_child(dim)


func _arm_slot(action_id: String) -> void:
	_clear_arm_glow()
	if _actions == null:
		return
	for child in _actions.get_children():
		if not (child is Button):
			continue
		var button := child as Button
		if str(button.get_meta("action_id", "")) != action_id:
			continue
		var armed := FxStrip.new()
		armed.name = "ArmedGlow"
		armed.setup("ui/portrait/skill_slot_armed.png", Vector2(36, 36), 2, 4.0, true)
		armed.position = button.position + Vector2(-2, -2)
		armed.freeze(0)
		_actions.add_child(armed)
		_actions.move_child(armed, button.get_index())
		return


func _clear_arm_glow() -> void:
	if _actions == null:
		return
	var glow := _actions.get_node_or_null("ArmedGlow")
	if glow:
		glow.free()


func _clear_slot_dims() -> void:
	if _actions == null:
		return
	var stale: Array = []
	for child in _actions.get_children():
		if str(child.name) == "Dim":
			stale.append(child)
	for child in stale:
		(child as Node).free()


func _tween_clip(fill: Dictionary, ratio: float, duration: float) -> void:
	var clip: Control = fill["clip"]
	var tween := clip.create_tween()
	tween.tween_property(clip, "size:x", float(int(30.0 * clampf(ratio, 0.0, 1.0))), duration)


func _class_regens_mp(class_id: String) -> bool:
	var cls: Dictionary = ContentDB.class_def(class_id)
	for skill_id in cls.get("skills", []):
		var skill: Dictionary = ContentDB.skill(str(skill_id))
		if not Formulas.is_passive(skill):
			continue
		for effect in skill.get("effects", []):
			if float(effect.get("mp_regen_pct", 0.0)) > 0.0:
				return true
	return false
