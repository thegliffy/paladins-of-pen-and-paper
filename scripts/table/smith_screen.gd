extends Control
class_name SmithScreen
## Town forge. Craft recipes and weapon or armor upgrades on one parchment sheet.


signal closed

const TEXT_W := 246.0
const CARD_W := 222.0

var _tab := "craft"
var _sheet: Panel
var _header: VBoxContainer
var _tabs: HBoxContainer
var _body: VBoxContainer
var _covering := false


func _ready() -> void:
	_cover()
	_build_chrome()
	_refresh()


func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED and is_inside_tree():
		var view := Vector2(Layout.viewport_size())
		if size.x < view.x * 0.5 or size.y < view.y * 0.5:
			_cover()


func _cover() -> void:
	if _covering:
		return
	_covering = true
	name = "SmithScreen"
	mouse_filter = Control.MOUSE_FILTER_STOP
	var view := Vector2(Layout.viewport_size())
	set_anchors_preset(Control.PRESET_TOP_LEFT)
	position = Vector2.ZERO
	size = view
	custom_minimum_size = view
	_covering = false


func _build_chrome() -> void:
	var veil := ColorRect.new()
	veil.name = "Veil"
	veil.color = Color("e8d6b0")
	veil.mouse_filter = Control.MOUSE_FILTER_STOP
	veil.position = Vector2.ZERO
	veil.size = Vector2(Layout.viewport_size())
	add_child(veil)
	_sheet = Panel.new()
	_sheet.name = "Sheet"
	var parchment := StyleBoxFlat.new()
	parchment.bg_color = Color("e8d6b0")
	parchment.border_color = Color("5a4028")
	parchment.set_border_width_all(4)
	parchment.set_content_margin_all(0)
	_sheet.add_theme_stylebox_override("panel", parchment)
	_sheet.mouse_filter = Control.MOUSE_FILTER_STOP
	_sheet.clip_contents = true
	_sheet.position = Vector2(4, 4)
	_sheet.size = Vector2(262, 472)
	add_child(_sheet)
	var column := VBoxContainer.new()
	column.name = "Column"
	column.position = Vector2(8, 8)
	column.size = Vector2(TEXT_W, 456)
	column.custom_minimum_size = column.size
	column.add_theme_constant_override("separation", 6)
	_sheet.add_child(column)
	_header = VBoxContainer.new()
	_header.name = "Header"
	_header.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_header.add_theme_constant_override("separation", 2)
	column.add_child(_header)
	_tabs = HBoxContainer.new()
	_tabs.name = "Tabs"
	_tabs.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_tabs.add_theme_constant_override("separation", 4)
	column.add_child(_tabs)
	var scroll := ScrollContainer.new()
	scroll.name = "Scroll"
	scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.custom_minimum_size = Vector2(TEXT_W, 340)
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO
	column.add_child(scroll)
	_body = VBoxContainer.new()
	_body.name = "Body"
	_body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_body.add_theme_constant_override("separation", 6)
	scroll.add_child(_body)


func _refresh() -> void:
	if _body == null:
		return
	_clear(_header)
	_clear(_tabs)
	_clear(_body)
	var place: Dictionary = ContentDB.place(GameState.place_id) if ContentDB.places.has(GameState.place_id) else {}
	var title := Widgets.wrapped_label("%s Smith" % str(place.get("name", "Town")), TEXT_W, Layout.font_size(), SpriteCatalog.INK)
	_header.add_child(title)
	var row := HBoxContainer.new()
	row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_theme_constant_override("separation", 6)
	_header.add_child(row)
	var gold := Widgets.wrapped_label("Gold %d" % GameState.gold, 160.0, Layout.font_tiny(), SpriteCatalog.INK)
	gold.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(gold)
	var close := Widgets.make_button("Close", Vector2(64, 28))
	close.name = "CloseSmith"
	close.pressed.connect(func(): closed.emit())
	row.add_child(close)
	_tabs.add_child(_tab_button("Craft", "craft"))
	_tabs.add_child(_tab_button("Upgrade", "upgrade"))
	if not CraftRules.town_unlocked(GameState.place_id, GameState.revealed_places()):
		_body.add_child(_line("The forge is still barred. Finish the road that opens this town."))
		return
	if _tab == "upgrade":
		_build_upgrades()
	else:
		_build_craft()


func _schedule_refresh() -> void:
	call_deferred("_refresh")


func _build_craft() -> void:
	_body.add_child(_line("Drops and gold become gear a step past the stall."))
	var place: Dictionary = ContentDB.place(GameState.place_id) if ContentDB.places.has(GameState.place_id) else {}
	var tier := CraftRules.shop_tier(place)
	for recipe in ContentDB.recipes():
		if int(recipe.get("tier", 1)) > tier:
			continue
		var result_id := str(recipe.get("result", ""))
		if not ContentDB.has_item(result_id):
			continue
		var item: Dictionary = ContentDB.item(result_id)
		var lines: Array = [
			_card_line(str(item.get("name", result_id)), Layout.font_size()),
			_card_line(_gear_line(item), Layout.font_tiny()),
		]
		var materials: Dictionary = recipe.get("materials", {})
		for mat_id in materials.keys():
			lines.append(_card_line(_have_need(str(mat_id), int(materials[mat_id])), Layout.font_tiny()))
		lines.append(_card_line("Gold %d" % int(recipe.get("gold", 0)), Layout.font_tiny()))
		var button := Widgets.make_button("Craft", Vector2(72, 26))
		button.name = "Craft_%s" % str(recipe.get("id", ""))
		var recipe_id := str(recipe.get("id", ""))
		button.disabled = not _can_craft(recipe)
		button.pressed.connect(func():
			GameState.craft_recipe(recipe_id)
			_schedule_refresh()
		)
		_body.add_child(_card(lines, button))


func _can_craft(recipe: Dictionary) -> bool:
	if GameState.gold < int(recipe.get("gold", 0)):
		return false
	var materials: Dictionary = recipe.get("materials", {})
	for mat_id in materials.keys():
		if int(GameState.inventory.get(str(mat_id), 0)) < int(materials[mat_id]):
			return false
	var result_id := str(recipe.get("result", ""))
	if not ContentDB.has_item(result_id):
		return false
	return int(GameState.inventory.get(result_id, 0)) < Formulas.stack_cap(ContentDB.item(result_id))


func _build_upgrades() -> void:
	_body.add_child(_line("Temper a weapon or armor, +1 through +3."))
	var found := false
	for entry in _upgrade_rows():
		found = true
		var key := str(entry["key"])
		var item: Dictionary = ContentDB.resolve(key)
		var plus := int(item.get("plus", 0))
		var base_stats: Dictionary = ContentDB.item(CraftRules.base_id(key)).get("stats", {})
		var preview := CraftRules.stat_preview(CraftRules.scaled_stats(base_stats, plus), CraftRules.scaled_stats(base_stats, plus + 1))
		var cost := CraftRules.upgrade_cost(int(item.get("tier", 1)), plus, ContentDB.tier_mats())
		var lines: Array = [
			_card_line(str(entry["label"]), Layout.font_size()),
			_card_line(preview, Layout.font_tiny()),
		]
		var materials: Dictionary = cost.get("materials", {})
		for mat_id in materials.keys():
			lines.append(_card_line(_have_need(str(mat_id), int(materials[mat_id])), Layout.font_tiny()))
		lines.append(_card_line("Gold %d" % int(cost.get("gold", 0)), Layout.font_tiny()))
		var button := Widgets.make_button("Upgrade", Vector2(88, 26))
		button.name = "Upgrade_%s_%s" % [str(entry["where"]), key.replace("@", "_")]
		var where := str(entry["where"])
		var member_index := int(entry["member"])
		var slot := str(entry["slot"])
		button.disabled = not _can_pay(cost)
		button.pressed.connect(func():
			if where == "bag":
				GameState.upgrade_item(key)
			else:
				GameState.upgrade_worn(member_index, slot)
				var host := get_parent()
				if host is GearScreen:
					host = host.get_parent()
				if host is SessionScreen:
					(host as SessionScreen).push_vitals(member_index)
			_schedule_refresh()
		)
		_body.add_child(_card(lines, button))
	if not found:
		_body.add_child(_line("No weapon or armor to temper."))


func _upgrade_rows() -> Array:
	var rows: Array = []
	for item_id in GameState.inventory.keys():
		var item := ContentDB.resolve(str(item_id))
		if item.is_empty() or CraftRules.can_upgrade(item, int(item.get("plus", 0))) != "":
			continue
		rows.append({
			"key": str(item_id),
			"label": str(item["name"]),
			"where": "bag",
			"member": -1,
			"slot": "",
		})
	for index in GameState.party.size():
		var member: Dictionary = GameState.party[index]
		var gear := Formulas.normalize_gear(member.get("gear", {}))
		var persona := str(ContentDB.persona(str(member.get("persona", ""))).get("name", "Hero"))
		for slot in ["main", "armor"]:
			var key := str(gear.get(slot, ""))
			var item := ContentDB.resolve(key)
			if item.is_empty() or CraftRules.can_upgrade(item, int(item.get("plus", 0))) != "":
				continue
			rows.append({
				"key": key,
				"label": "%s (%s)" % [str(item["name"]), persona],
				"where": "worn",
				"member": index,
				"slot": slot,
			})
	return rows


func _can_pay(cost: Dictionary) -> bool:
	if GameState.gold < int(cost.get("gold", 0)):
		return false
	var materials: Dictionary = cost.get("materials", {})
	for mat_id in materials.keys():
		if int(GameState.inventory.get(str(mat_id), 0)) < int(materials[mat_id]):
			return false
	return true


func _have_need(item_id: String, need: int) -> String:
	var name := item_id
	if ContentDB.has_item(item_id):
		name = str(ContentDB.item(item_id).get("name", item_id))
	return "%s %d/%d" % [name, int(GameState.inventory.get(item_id, 0)), need]


func _gear_line(item: Dictionary) -> String:
	var parts: PackedStringArray = []
	var stats: Dictionary = item.get("stats", {})
	if int(stats.get("attack", 0)) != 0:
		parts.append("Atk %d" % int(stats["attack"]))
	if int(stats.get("dr", 0)) != 0:
		parts.append("DR %d" % int(stats["dr"]))
	if int(stats.get("crit", 0)) != 0:
		parts.append("Crit %d" % int(stats["crit"]))
	if int(stats.get("body", 0)) != 0:
		parts.append("Body %d" % int(stats["body"]))
	if int(stats.get("senses", 0)) != 0:
		parts.append("Senses %d" % int(stats["senses"]))
	if int(stats.get("mind", 0)) != 0:
		parts.append("Mind %d" % int(stats["mind"]))
	if int(stats.get("max_hp", 0)) != 0:
		parts.append("HP %d" % int(stats["max_hp"]))
	if int(stats.get("max_mp", 0)) != 0:
		parts.append("EN %d" % int(stats["max_mp"]))
	if float(stats.get("spell_bonus", 0.0)) > 0.0:
		parts.append("Spell %.2f" % float(stats["spell_bonus"]))
	if parts.is_empty():
		return str(item.get("description", ""))
	return "  ".join(parts)


func _tab_button(label: String, tab: String) -> Button:
	var button := Widgets.make_button(label, Vector2(88, 26))
	button.name = "Tab_%s" % tab
	if _tab == tab:
		button.modulate = Color(1, 0.92, 0.6)
	button.pressed.connect(func():
		_tab = tab
		_schedule_refresh()
	)
	return button


func _line(text: String) -> Label:
	return Widgets.wrapped_label(text, TEXT_W, Layout.font_tiny(), SpriteCatalog.INK)


func _card_line(text: String, font_size: int) -> Label:
	return Widgets.wrapped_label(text, CARD_W, font_size, SpriteCatalog.INK)


func _card(lines: Array, button: Button) -> PanelContainer:
	var card := PanelContainer.new()
	card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var style := StyleBoxFlat.new()
	style.bg_color = Color("f3e6c8")
	style.border_color = Color("8a6840")
	style.set_border_width_all(2)
	style.set_content_margin_all(4)
	card.add_theme_stylebox_override("panel", style)
	var box := VBoxContainer.new()
	box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	box.add_theme_constant_override("separation", 2)
	card.add_child(box)
	for line in lines:
		box.add_child(line)
	if button != null:
		box.add_child(button)
	return card


func _clear(node: Node) -> void:
	for child in node.get_children():
		node.remove_child(child)
		child.queue_free()
