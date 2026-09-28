extends Control
class_name CreatorScreen
## Portrait creator: doll on top, tabs and option rows under it, confirm in thumb reach.

signal finished(members: Array)
signal cancelled

var preview_mode := false
var _index := 0
var _members: Array = []
var _persona := "mason"
var _race := "hearthborn"
var _class := "paladin"
var _look := {"skin": 0, "head": 0, "hair": 1, "hair_color": 2, "outfit_color": 0}
var _tab := "look"
var _look_row := "head"
var _doll: PaperDoll
var _name_label: Label
var _stats: Label
var _options: GridContainer
var _row_bar: HBoxContainer
var _next_button: Button
var _begin_button: Button
var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	_rng.randomize()
	_build()
	if preview_mode:
		_apply_preview()
	else:
		_randomize()
	_refresh()


func stage_preview() -> void:
	preview_mode = true
	_persona = "mason"
	_race = "delver"
	_class = "paladin"
	_look = {"skin": 4, "head": 3, "hair": 4, "hair_color": 1, "outfit_color": 0}
	_tab = "look"
	_look_row = "head"
	_index = 0
	if is_node_ready():
		_refresh()


func _apply_preview() -> void:
	_persona = "nim"
	_race = "glenfolk"
	_class = "wizard"
	_look = {"skin": 1, "head": 5, "hair": 3, "hair_color": 6, "outfit_color": 1}
	_tab = "class"
	_look_row = "hair"


func _build() -> void:
	var bg := ColorRect.new()
	bg.color = SpriteCatalog.CREAM
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	var frame := Widgets.panel()
	frame.set_anchors_preset(Control.PRESET_FULL_RECT)
	frame.offset_left = 2
	frame.offset_top = 2
	frame.offset_right = -2
	frame.offset_bottom = -2
	add_child(frame)

	var header := Layout.rect("creator", "header")
	var header_row := HBoxContainer.new()
	Layout.place(header_row, header)
	add_child(header_row)
	var back := Widgets.make_button("Back", Vector2(52, header.size.y))
	back.pressed.connect(_on_back)
	header_row.add_child(back)
	_name_label = Widgets.label("Recruit 1/%d" % Layout.party_max(), Layout.font_small())
	_name_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header_row.add_child(_name_label)

	var doll_rect := Layout.rect("creator", "doll")
	var doll_host := Control.new()
	Layout.place(doll_host, doll_rect)
	doll_host.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(doll_host)
	_doll = PaperDoll.new()
	doll_host.add_child(_doll)
	var scale := Layout.num("doll_scale")
	_doll.scale = Vector2(scale, scale)
	var left := Widgets.make_button("<", Vector2(36, 44))
	left.position = Vector2(4, doll_rect.size.y * 0.5 - 22)
	left.pressed.connect(func(): _nudge(-1))
	doll_host.add_child(left)
	var right := Widgets.make_button(">", Vector2(36, 44))
	right.position = Vector2(doll_rect.size.x - 40, doll_rect.size.y * 0.5 - 22)
	right.pressed.connect(func(): _nudge(1))
	doll_host.add_child(right)

	var tabs := HBoxContainer.new()
	Layout.place(tabs, Layout.rect("creator", "tabs"))
	tabs.add_theme_constant_override("separation", 4)
	add_child(tabs)
	for pair in [["who", "Who"], ["look", "Look"], ["class", "Class"]]:
		var button := Widgets.make_button(pair[1], Vector2(80, 28))
		button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		button.pressed.connect(_set_tab.bind(pair[0]))
		button.set_meta("tab", pair[0])
		tabs.add_child(button)

	_row_bar = HBoxContainer.new()
	_row_bar.position = Layout.rect("creator", "options").position
	_row_bar.size = Vector2(Layout.rect("creator", "options").size.x, 26)
	_row_bar.add_theme_constant_override("separation", 3)
	add_child(_row_bar)

	_options = GridContainer.new()
	var options_rect := Layout.rect("creator", "options")
	_options.position = options_rect.position + Vector2(0, 28)
	_options.size = options_rect.size - Vector2(0, 28)
	_options.columns = 4
	_options.add_theme_constant_override("h_separation", 4)
	_options.add_theme_constant_override("v_separation", 4)
	add_child(_options)

	_stats = Widgets.label("", Layout.font_tiny())
	Layout.place(_stats, Layout.rect("creator", "stats"))
	add_child(_stats)

	var actions := HBoxContainer.new()
	Layout.place(actions, Layout.rect("creator", "actions"))
	actions.add_theme_constant_override("separation", 6)
	add_child(actions)
	var randomize := Widgets.make_button("Random", Vector2(80, 56))
	randomize.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	randomize.icon = SpriteCatalog.ui("icon_die")
	randomize.pressed.connect(_randomize_and_refresh)
	actions.add_child(randomize)
	_next_button = Widgets.make_button("Next", Vector2(80, 56))
	_next_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_next_button.pressed.connect(_confirm)
	actions.add_child(_next_button)
	_begin_button = Widgets.make_button("Begin", Vector2(80, 56))
	_begin_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_begin_button.icon = SpriteCatalog.ui("icon_check")
	_begin_button.pressed.connect(_begin)
	actions.add_child(_begin_button)


func _set_tab(tab: String) -> void:
	_tab = tab
	_refresh()


func _nudge(direction: int) -> void:
	if _tab == "who":
		_cycle_persona(direction)
	elif _tab == "class":
		_cycle_class(direction)
	else:
		_cycle_look(direction)
	_refresh()


func _cycle_persona(direction: int) -> void:
	var ids := _available("persona")
	if ids.is_empty():
		return
	var at := ids.find(_persona)
	_persona = ids[(at + direction + ids.size()) % ids.size()]


func _cycle_class(direction: int) -> void:
	var ids := _available("class")
	if ids.is_empty():
		return
	var at := ids.find(_class)
	_class = ids[(at + direction + ids.size()) % ids.size()]


func _cycle_look(direction: int) -> void:
	var count := _row_count(_look_row)
	var key := _look_key(_look_row)
	_look[key] = (int(_look[key]) + direction + count) % count


func _randomize_and_refresh() -> void:
	_randomize()
	_refresh()
	Sfx.play("dice")


func _randomize() -> void:
	var personas := _available("persona")
	var classes := _available("class")
	if not personas.is_empty():
		_persona = personas[_rng.randi() % personas.size()]
	var race_ids := ContentDB.races.keys()
	_race = str(race_ids[_rng.randi() % race_ids.size()])
	if not classes.is_empty():
		_class = classes[_rng.randi() % classes.size()]
	var appearance := SpriteCatalog.appearance()
	_look = {
		"skin": _rng.randi() % appearance["skins"].size(),
		"head": _rng.randi() % int(appearance["head_count"]),
		"hair": _rng.randi() % int(appearance["hair_count"]),
		"hair_color": _rng.randi() % appearance["hairs"].size(),
		"outfit_color": _rng.randi() % appearance["outfits"].size(),
	}


func _available(kind: String) -> Array:
	var taken := {}
	for member in _members:
		taken[str(member["persona" if kind == "persona" else "class_id"])] = true
	var source: Array = ContentDB.personas.keys() if kind == "persona" else ContentDB.classes.keys()
	var open: Array = []
	for id in source:
		if not taken.has(str(id)):
			open.append(str(id))
	return open


func _confirm() -> void:
	Sfx.play("tap")
	if not _seat_current():
		return
	if _members.size() >= Layout.party_max():
		finished.emit(_members)
		return
	_index = _members.size()
	_randomize()
	_refresh()


func _begin() -> void:
	Sfx.play("tap")
	if not _seat_current():
		return
	if _members.size() < Layout.party_min():
		return
	finished.emit(_members)


func _seat_current() -> bool:
	if _available("persona").find(_persona) < 0 or _available("class").find(_class) < 0:
		return false
	_members.append(GameState.make_member(_persona, _race, _class, _look))
	return true


func _on_back() -> void:
	if _index == 0:
		cancelled.emit()
		return
	_index -= 1
	_members.pop_back()
	_refresh()


func _refresh() -> void:
	_doll.set_look(_look, _class, _race, "front")
	var scale := Layout.num("doll_scale")
	var host: Control = _doll.get_parent()
	_doll.position = (host.size - _doll.size * scale) * 0.5
	var persona := ContentDB.persona(_persona)
	var race := ContentDB.race(_race)
	var cls := ContentDB.class_def(_class)
	_name_label.text = "Recruit %d/%d" % [_index + 1, Layout.party_max()]
	var last_slot := _index + 1 >= Layout.party_max()
	if _next_button:
		_next_button.visible = not last_slot
	var stats := Formulas.compose_stats(
		int(cls["body"]), int(cls["senses"]), int(cls["mind"]),
		int(persona["body"]), int(persona["senses"]), int(persona["mind"]),
		int(race["body"]), int(race["senses"]), int(race["mind"])
	)
	var hp := Formulas.max_hp(1, stats["body"], stats["mind"])
	var energy := Formulas.max_energy(1, stats["body"], stats["mind"]) + int(race.get("energy", 0))
	var attack := Formulas.player_attack(1, stats["body"])
	var attack_range := Formulas.damage_range(attack)
	_stats.text = "%s the %s %s\nB%d S%d M%d  HP %d  EN %d  Atk %d-%d" % [
		persona["name"], race["name"], cls["name"],
		stats["body"], stats["senses"], stats["mind"], hp, energy, attack_range.x, attack_range.y
	]
	_fill_rows()
	_fill_options()


func _fill_rows() -> void:
	var stale: Array = _row_bar.get_children()
	for child in stale:
		child.free()
	if _tab == "class":
		_row_bar.visible = true
		var passive := Widgets.label(_passive_line(), Layout.font_tiny())
		passive.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		passive.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		_row_bar.add_child(passive)
		return
	if _tab != "look":
		_row_bar.visible = false
		return
	_row_bar.visible = true
	for pair in [["head", "Head"], ["hair", "Hair"], ["skin", "Skin"], ["dye", "Dye"], ["cloth", "Cloth"]]:
		var button := Widgets.make_button(pair[1], Vector2(48, 24))
		button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		button.pressed.connect(_set_row.bind(pair[0]))
		if pair[0] == _look_row:
			button.modulate = SpriteCatalog.HIGHLIGHT
		_row_bar.add_child(button)


func _passive_line() -> String:
	var cls: Dictionary = ContentDB.class_def(_class)
	var names: PackedStringArray = PackedStringArray()
	for skill_id in cls["skills"]:
		var skill: Dictionary = ContentDB.skill(str(skill_id))
		if Formulas.is_passive(skill):
			names.append(str(skill["name"]))
	if names.is_empty():
		return ""
	return "Passive  " + ", ".join(names)


func _set_row(row: String) -> void:
	_look_row = row
	_refresh()


func _fill_options() -> void:
	for child in _options.get_children():
		child.queue_free()
	if _tab == "who":
		_options.columns = 2
		for id in ContentDB.personas.keys():
			_options.add_child(_choice_button(ContentDB.persona(str(id))["name"], str(id) == _persona, _available("persona").find(str(id)) >= 0, _pick_persona.bind(str(id))))
		for id in ContentDB.races.keys():
			_options.add_child(_choice_button(ContentDB.race(str(id))["name"], str(id) == _race, true, _pick_race.bind(str(id))))
	elif _tab == "class":
		_options.columns = 2
		for id in ContentDB.classes.keys():
			var cls: Dictionary = ContentDB.class_def(str(id))
			var text := "%s  B%d/S%d/M%d" % [cls["name"], int(cls["body"]), int(cls["senses"]), int(cls["mind"])]
			_options.add_child(_choice_button(text, str(id) == _class, _available("class").find(str(id)) >= 0, _pick_class.bind(str(id))))
	else:
		_options.columns = 4
		_add_look_choices()


func _add_look_choices() -> void:
	var appearance := SpriteCatalog.appearance()
	if _look_row == "head":
		for i in int(appearance["head_count"]):
			_options.add_child(_swatch_button("H%d" % (i + 1), Color.WHITE, i == int(_look["head"]), _pick_look.bind("head", i)))
	elif _look_row == "hair":
		for i in int(appearance["hair_count"]):
			_options.add_child(_swatch_button("Y%d" % (i + 1), Color.WHITE, i == int(_look["hair"]), _pick_look.bind("hair", i)))
	elif _look_row == "skin":
		for i in appearance["skins"].size():
			_options.add_child(_swatch_button("", SpriteCatalog.color_at("skins", i), i == int(_look["skin"]), _pick_look.bind("skin", i)))
	elif _look_row == "dye":
		for i in appearance["hairs"].size():
			_options.add_child(_swatch_button("", SpriteCatalog.color_at("hairs", i), i == int(_look["hair_color"]), _pick_look.bind("hair_color", i)))
	else:
		for i in appearance["outfits"].size():
			_options.add_child(_swatch_button("", SpriteCatalog.color_at("outfits", i), i == int(_look["outfit_color"]), _pick_look.bind("outfit_color", i)))


func _choice_button(text: String, selected: bool, enabled: bool, callback: Callable) -> Button:
	var button := Widgets.make_button(text, Vector2(120, 36))
	button.disabled = not enabled
	button.pressed.connect(callback)
	if selected:
		button.modulate = SpriteCatalog.HIGHLIGHT
	return button


func _swatch_button(text: String, color: Color, selected: bool, callback: Callable) -> Button:
	var button := Widgets.make_button(text, Vector2(58, 36))
	button.pressed.connect(callback)
	if text == "":
		var swatch := ColorRect.new()
		swatch.color = color
		swatch.mouse_filter = Control.MOUSE_FILTER_IGNORE
		swatch.set_anchors_preset(Control.PRESET_FULL_RECT)
		swatch.offset_left = 6
		swatch.offset_top = 6
		swatch.offset_right = -6
		swatch.offset_bottom = -6
		button.add_child(swatch)
	if selected:
		button.modulate = SpriteCatalog.HIGHLIGHT
	return button


func _pick_persona(id: String) -> void:
	if _available("persona").find(id) < 0:
		return
	_persona = id
	_refresh()


func _pick_race(id: String) -> void:
	_race = id
	_refresh()


func _pick_class(id: String) -> void:
	if _available("class").find(id) < 0:
		return
	_class = id
	_refresh()


func _pick_look(key: String, index: int) -> void:
	_look[key] = index
	_refresh()


func _look_key(row: String) -> String:
	match row:
		"head": return "head"
		"hair": return "hair"
		"skin": return "skin"
		"dye": return "hair_color"
		_: return "outfit_color"


func _row_count(row: String) -> int:
	var appearance := SpriteCatalog.appearance()
	match row:
		"head": return int(appearance["head_count"])
		"hair": return int(appearance["hair_count"])
		"skin": return appearance["skins"].size()
		"dye": return appearance["hairs"].size()
		_: return appearance["outfits"].size()
