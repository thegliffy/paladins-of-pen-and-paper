extends Control
class_name BattleBuilder
## Pick who stands across the table. One to five foes, mixed types, remembered per place.

signal closed(rows: Array)

var _place_id := ""
var _order: Array = []
var _counts := {}
var _gold: Label
var _xp: Label
var _difficulty: Label
var _start: Button


func setup(place_id: String) -> void:
	_place_id = place_id
	_order = ContentDB.region_monster_ids()
	_counts = GameState.lineup_counts(place_id, _order)
	_build()


func _build() -> void:
	for child in get_children():
		child.free()
	name = "BattleBuilder"
	mouse_filter = Control.MOUSE_FILTER_STOP
	var backdrop := TextureRect.new()
	backdrop.set_anchors_preset(Control.PRESET_FULL_RECT)
	backdrop.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	backdrop.stretch_mode = TextureRect.STRETCH_SCALE
	backdrop.texture = ArtPack.texture("combat/bg_forest_portrait.png")
	backdrop.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(backdrop)
	var sheet := Widgets.panel()
	sheet.position = Vector2(6, 6)
	sheet.size = Vector2(258, 468)
	sheet.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(sheet)
	var place: Dictionary = ContentDB.place(_place_id) if ContentDB.places.has(_place_id) else {}
	var title := PixelFont.label("SET THE FIGHT", Color("120c18"))
	title.position = Vector2(16, 14)
	add_child(title)
	var where := PixelFont.label(str(place.get("name", "Here")).to_upper(), Color("744526"))
	where.position = Vector2(16, 24)
	add_child(where)
	var list := Control.new()
	list.name = "List"
	list.position = Vector2(0, 36)
	list.size = Vector2(270, 300)
	list.clip_contents = true
	list.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(list)
	var y := 4.0
	for monster_id in _order:
		_add_row(list, str(monster_id), y)
		y += 36.0
	var cap := PixelFont.label("UP TO FIVE ACROSS THE TABLE", Color("744526"))
	cap.position = Vector2(16, 348)
	add_child(cap)
	_difficulty = Widgets.label("", Layout.font_tiny(), SpriteCatalog.INK)
	_difficulty.name = "Difficulty"
	_difficulty.position = Vector2(16, 364)
	_difficulty.size = Vector2(238, 18)
	add_child(_difficulty)
	_gold = Widgets.label("", Layout.font_tiny(), SpriteCatalog.INK)
	_gold.name = "Gold"
	_gold.position = Vector2(16, 386)
	_gold.size = Vector2(116, 18)
	add_child(_gold)
	_xp = Widgets.label("", Layout.font_tiny(), SpriteCatalog.INK)
	_xp.name = "Xp"
	_xp.position = Vector2(136, 386)
	_xp.size = Vector2(116, 18)
	add_child(_xp)
	var back := Widgets.make_button("Back", Vector2(116, 40))
	back.position = Vector2(16, 416)
	back.size = Vector2(116, 40)
	back.pressed.connect(_on_back)
	add_child(back)
	_start = Widgets.make_button("Start", Vector2(116, 40))
	_start.position = Vector2(138, 416)
	_start.size = Vector2(116, 40)
	_start.pressed.connect(_on_start)
	add_child(_start)
	_refresh()


func _add_row(list: Control, monster_id: String, y: float) -> void:
	var monster: Dictionary = ContentDB.monster(monster_id)
	var row := Control.new()
	row.position = Vector2(14, y)
	row.size = Vector2(242, 32)
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	list.add_child(row)
	var portrait := TextureRect.new()
	portrait.mouse_filter = Control.MOUSE_FILTER_IGNORE
	portrait.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	portrait.stretch_mode = TextureRect.STRETCH_SCALE
	portrait.texture = ArtPack.monster_portrait(ArtPack.monster_sprite(monster_id))
	portrait.position = Vector2(0, 4)
	portrait.size = Vector2(24, 24)
	row.add_child(portrait)
	var name_label := PixelFont.label(str(monster.get("name", monster_id)).to_upper(), Color("2c1810"))
	name_label.position = Vector2(28, 4)
	row.add_child(name_label)
	var level_label := PixelFont.label("LV %d" % int(monster.get("level", 1)), Color("744526"))
	level_label.position = Vector2(28, 14)
	row.add_child(level_label)
	var minus := Widgets.make_button("-", Vector2(28, 28))
	minus.name = "Minus_%s" % monster_id
	minus.position = Vector2(150, 2)
	minus.size = Vector2(28, 28)
	minus.pressed.connect(_bump.bind(monster_id, -1))
	row.add_child(minus)
	var count := Widgets.label("0", Layout.font_tiny(), SpriteCatalog.INK)
	count.name = "Count_%s" % monster_id
	count.position = Vector2(180, 8)
	count.size = Vector2(20, 16)
	count.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	row.add_child(count)
	var plus := Widgets.make_button("+", Vector2(28, 28))
	plus.name = "Plus_%s" % monster_id
	plus.position = Vector2(202, 2)
	plus.size = Vector2(28, 28)
	plus.pressed.connect(_bump.bind(monster_id, 1))
	row.add_child(plus)


func _bump(monster_id: String, delta: int) -> void:
	_counts = Formulas.adjust_count(_order, _counts, monster_id, delta)
	GameState.remember_lineup(_place_id, _counts)
	_refresh()


func _refresh() -> void:
	var total := 0
	for monster_id in _order:
		var copies := int(_counts.get(str(monster_id), 0))
		total += copies
		var count := find_child("Count_%s" % monster_id, true, false) as Label
		if count:
			count.text = str(copies)
		var minus := find_child("Minus_%s" % monster_id, true, false) as Button
		if minus:
			minus.disabled = copies <= 0
		var plus := find_child("Plus_%s" % monster_id, true, false) as Button
		if plus:
			plus.disabled = total >= Formulas.LINEUP_CAP and copies >= 0
	# Plus stays available on a type only while the table has room.
	# The loop above saw a running total, so recompute once the sum is known.
	for monster_id in _order:
		var plus := find_child("Plus_%s" % monster_id, true, false) as Button
		if plus:
			plus.disabled = total >= Formulas.LINEUP_CAP
	var preview := _preview()
	if _difficulty:
		_difficulty.text = "Difficulty  %s" % str(preview["difficulty"])
	if _gold:
		_gold.text = "Gold %d" % int(preview["gold"])
	if _xp:
		_xp.text = "XP %d" % int(preview["xp"])
	if _start:
		_start.disabled = total < 1 or total > Formulas.LINEUP_CAP


func _preview() -> Dictionary:
	var monsters: Array = []
	for monster_id in Formulas.lineup_from_counts(_order, _counts):
		var monster: Dictionary = ContentDB.monster(str(monster_id))
		monsters.append({
			"id": str(monster_id),
			"level": int(monster.get("level", 1)),
			"elite": bool(monster.get("elite", false)),
			"boss": bool(monster.get("boss", false)),
		})
	return Formulas.expected_battle_rewards(monsters, GameState.party_average())


func _rows() -> Array:
	var rows: Array = []
	for monster_id in Formulas.lineup_from_counts(_order, _counts):
		rows.append({"id": str(monster_id)})
	return rows


func _on_back() -> void:
	GameState.remember_lineup(_place_id, _counts)
	closed.emit([])


func _on_start() -> void:
	var rows := _rows()
	if rows.is_empty() or rows.size() > Formulas.LINEUP_CAP:
		return
	GameState.remember_lineup(_place_id, _counts)
	closed.emit(rows)
