extends Control
class_name GearScreen
## Shared bag, hero slots, and the town shop. Portrait, tap first.

signal closed

var _mode := "bag"
var _filter := "all"
var _hero := 0
var _selected := ""
var _from_shop := false


func setup(mode: String) -> void:
	_mode = mode if mode != "" else "bag"
	if _mode == "shop" and not _town():
		_mode = "bag"
	_rebuild()


func show_hero(index: int) -> void:
	_hero = index
	_mode = "hero"
	_selected = ""
	_rebuild()


func show_shop() -> void:
	_mode = "shop" if _town() else "bag"
	_selected = ""
	_from_shop = _mode == "shop"
	_rebuild()


func _town() -> bool:
	if not ContentDB.places.has(GameState.place_id):
		return false
	var place: Dictionary = ContentDB.place(GameState.place_id)
	return str(place.get("kind", "")) == "town" or bool(place.get("has_inn", false))


func _rebuild() -> void:
	for child in get_children():
		child.free()
	name = "GearScreen"
	mouse_filter = Control.MOUSE_FILTER_STOP
	var backdrop := TextureRect.new()
	backdrop.set_anchors_preset(Control.PRESET_FULL_RECT)
	backdrop.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	backdrop.stretch_mode = TextureRect.STRETCH_SCALE
	backdrop.texture = ArtPack.texture(ContentDB.combat_backdrop_path(GameState.place_id))
	backdrop.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(backdrop)
	var sheet := Widgets.panel()
	sheet.position = Vector2(4, 4)
	sheet.size = Vector2(262, 472)
	sheet.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(sheet)
	var title := PixelFont.label("PARTY GEAR", Color("120c18"), 2)
	title.position = Vector2(12, 10)
	add_child(title)
	var gold_text := "Gold %d" % GameState.gold
	if _town() and ContentDB.places.has(GameState.place_id):
		gold_text += "   Tier %d" % CraftRules.shop_tier(ContentDB.place(GameState.place_id))
	var gold := Widgets.label(gold_text, Layout.font_tiny(), SpriteCatalog.INK)
	gold.position = Vector2(12, 24)
	gold.size = Vector2(140, 14)
	add_child(gold)
	var close := Widgets.make_button("Close", Vector2(64, 28))
	close.name = "CloseGear"
	close.position = Vector2(196, 8)
	close.pressed.connect(func(): closed.emit())
	add_child(close)
	_tab("Bag", "bag", Vector2(12, 40))
	_tab("Hero", "hero", Vector2(70, 40))
	if _town():
		_tab("Shop", "shop", Vector2(128, 40))
		_tab("Smith", "smith", Vector2(186, 40))
	if _mode == "hero":
		_build_hero()
	else:
		_build_list()
	_build_detail()


func _tab(label: String, mode: String, at: Vector2) -> void:
	var button := Widgets.make_button(label, Vector2(54, 26))
	button.position = at
	button.name = "Tab_%s" % mode
	if _mode == mode:
		button.modulate = Color(1, 0.92, 0.6)
	button.pressed.connect(_set_mode.bind(mode))
	add_child(button)


func _set_mode(mode: String) -> void:
	if mode == "smith":
		_open_smith()
		return
	_mode = mode
	if mode != "shop":
		_from_shop = false
	_refresh()


func _open_smith() -> void:
	if get_node_or_null("SmithScreen") != null:
		return
	var smith := SmithScreen.new()
	add_child(smith)
	smith.move_to_front()
	smith.closed.connect(func():
		if is_instance_valid(smith):
			smith.queue_free()
	)


func _filters() -> void:
	var labels := ["All", "Weapons", "Armor", "Trinkets", "Usables"]
	var keys := ["all", "weapon", "armor", "trinket", "usable"]
	for i in labels.size():
		var button := Widgets.make_button(labels[i], Vector2(48, 22))
		button.position = Vector2(8 + i * 51, 70)
		button.name = "Filter_%s" % keys[i]
		if _filter == keys[i]:
			button.modulate = Color(1, 0.92, 0.6)
		button.pressed.connect(_set_filter.bind(keys[i]))
		add_child(button)


func _set_filter(key: String) -> void:
	_filter = key
	_refresh()


func _build_list() -> void:
	_filters()
	var scroll := ScrollContainer.new()
	scroll.position = Vector2(8, 96)
	scroll.size = Vector2(254, 200)
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	add_child(scroll)
	var box := VBoxContainer.new()
	box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	box.add_theme_constant_override("separation", 3)
	scroll.add_child(box)
	var rows: Array = _rows()
	if rows.is_empty():
		var empty_text := "Nothing in this tab."
		if _mode == "shop" and not _shop_open():
			empty_text = "The stall is still barred."
		var empty := Widgets.label(empty_text, Layout.font_tiny(), SpriteCatalog.INK)
		empty.custom_minimum_size = Vector2(230, 24)
		box.add_child(empty)
		return
	for row in rows:
		var item: Dictionary = row["item"]
		var count := int(row["count"])
		var button := Widgets.make_button("%s  x%d" % [item["name"], count], Vector2(236, 28))
		button.name = "Item_%s" % str(item["id"])
		button.alignment = HORIZONTAL_ALIGNMENT_LEFT
		button.add_theme_constant_override("h_separation", 6)
		var icon_path := str(item.get("icon", ""))
		if icon_path != "" and ArtPack.has(icon_path):
			button.icon = ArtPack.texture(icon_path)
			button.expand_icon = false
		button.add_theme_color_override("font_color", Color(Formulas.rarity_hex(str(item.get("rarity", "common")))))
		var item_id := str(item["id"])
		var from_shop := bool(row["shop"])
		button.pressed.connect(_select.bind(item_id, from_shop))
		box.add_child(button)


func _rows() -> Array:
	var rows: Array = []
	if _mode == "shop":
		if not _shop_open():
			return rows
		var place: Dictionary = ContentDB.place(GameState.place_id)
		for item_id in CraftRules.shop_ids(ContentDB.item_rows(), place, GameState.revealed_places()):
			var item: Dictionary = ContentDB.item(str(item_id))
			if not _matches(item):
				continue
			rows.append({"item": item, "count": 1, "shop": true})
		return rows
	for item_id in GameState.inventory.keys():
		var item: Dictionary = ContentDB.resolve(str(item_id))
		if item.is_empty() or not _matches(item):
			continue
		rows.append({"item": item, "count": int(GameState.inventory[item_id]), "shop": false})
	return rows


func _shop_open() -> bool:
	if not _town() or not ContentDB.places.has(GameState.place_id):
		return false
	return CraftRules.town_unlocked(GameState.place_id, GameState.revealed_places())


func _matches(item: Dictionary) -> bool:
	if _filter == "all":
		return true
	var slot := str(item.get("slot", ""))
	if _filter == "weapon":
		return slot == "weapon" or slot == "off"
	return slot == _filter


func _select(item_id: String, from_shop: bool) -> void:
	_selected = item_id
	_from_shop = from_shop
	_refresh()


func _build_hero() -> void:
	if GameState.party.is_empty():
		return
	_hero = clampi(_hero, 0, GameState.party.size() - 1)
	var row := 0
	for index in GameState.party.size():
		var member: Dictionary = GameState.party[index]
		var persona: Dictionary = ContentDB.persona(str(member["persona"]))
		var button := Widgets.make_button(str(persona["name"]), Vector2(48, 22))
		button.position = Vector2(8 + row * 51, 70)
		button.name = "Hero_%d" % index
		if index == _hero:
			button.modulate = Color(1, 0.92, 0.6)
		button.pressed.connect(_pick_hero.bind(index))
		add_child(button)
		row += 1
	var member: Dictionary = GameState.party[_hero]
	var doll := PaperDoll.new()
	doll.set_look(member["look"], str(member["class_id"]), str(member["race"]), "front")
	doll.position = Vector2(10, 98)
	doll.show_gear(member)
	add_child(doll)
	var gear := Formulas.normalize_gear(member.get("gear", {}))
	_slot_button("Main", "main", str(gear["main"]), Vector2(78, 96))
	_slot_button("Off", "off", str(gear["off"]), Vector2(78, 120))
	_slot_button("Armor", "armor", str(gear["armor"]), Vector2(78, 144))
	var trinkets: Array = gear["trinkets"]
	for i in 3:
		_slot_button("Trinket %d" % (i + 1), "trinket:%d" % i, str(trinkets[i]), Vector2(78, 168 + i * 24))
	var stats := GameState.combat_stats(member)
	var line := Widgets.label("B%d S%d M%d  Atk %d  DR %d\nHP %d/%d  EN %d/%d" % [
		stats["body"], stats["senses"], stats["mind"], stats["attack"], stats["dr"],
		int(member["hp"]), stats["max_hp"], int(member["mp"]), stats["max_mp"],
	], Layout.font_tiny(), SpriteCatalog.INK)
	line.position = Vector2(10, 246)
	line.size = Vector2(160, 28)
	add_child(line)
	var names := {}
	for skill_id in ContentDB.class_def(str(member["class_id"])).get("skills", []):
		names[str(skill_id)] = str(ContentDB.skill(str(skill_id)).get("name", skill_id))
	var grown := LevelRules.sheet_line(member, names)
	if grown != "":
		var growth := Widgets.wrapped_label(grown, 160.0, Layout.font_tiny(), SpriteCatalog.INK)
		growth.position = Vector2(10, 276)
		add_child(growth)
	var skills := Widgets.make_button("Skills", Vector2(70, 24))
	skills.position = Vector2(184, 248)
	skills.pressed.connect(_open_skills)
	add_child(skills)


func _pick_hero(index: int) -> void:
	_hero = index
	_refresh()


func _slot_button(label: String, slot: String, item_id: String, at: Vector2) -> void:
	var worn := "Empty"
	if item_id != "" and ContentDB.has_item(item_id):
		worn = str(ContentDB.resolve(item_id)["name"])
	var button := Widgets.make_button("%s: %s" % [label, worn], Vector2(176, 22))
	button.position = at
	button.name = "Slot_%s" % slot.replace(":", "_")
	button.pressed.connect(_tap_slot.bind(slot))
	add_child(button)


func _tap_slot(slot: String) -> void:
	if _selected != "" and not _from_shop:
		var reason := GameState.equip_item(_hero, _selected, slot)
		if reason == "":
			_selected = ""
			_push_chair()
		_refresh()
		return
	GameState.unequip_slot(_hero, slot)
	_push_chair()
	_refresh()


func _push_chair() -> void:
	var parent := get_parent()
	if parent is SessionScreen:
		(parent as SessionScreen).push_vitals(_hero)


func _open_skills() -> void:
	if get_parent() is SessionScreen:
		(get_parent() as SessionScreen).open_party()


func _build_detail() -> void:
	var panel := Widgets.panel("res://art/ui/panel_dark.png")
	panel.position = Vector2(8, 318)
	panel.size = Vector2(254, 150)
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(panel)
	if _selected == "" or not ContentDB.has_item(_selected):
		var hint := Widgets.label("Tap an item.", Layout.font_tiny(), SpriteCatalog.LIGHT)
		hint.position = Vector2(16, 330)
		add_child(hint)
		return
	var item: Dictionary = ContentDB.resolve(_selected) if not _from_shop else ContentDB.item(_selected)
	var icon_path := str(item.get("icon", ""))
	if icon_path != "" and ArtPack.has(icon_path):
		var icon := TextureRect.new()
		icon.name = "DetailIcon"
		icon.texture = ArtPack.texture(icon_path)
		icon.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		icon.stretch_mode = TextureRect.STRETCH_KEEP
		icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
		icon.position = Vector2(16, 326)
		icon.size = Vector2(16, 16)
		add_child(icon)
	var name_label := Widgets.label(str(item["name"]), Layout.font_size(), Color(Formulas.rarity_hex(str(item.get("rarity", "common")))))
	name_label.name = "DetailName"
	name_label.position = Vector2(36, 324)
	name_label.size = Vector2(140, 18)
	add_child(name_label)
	var rarity := Widgets.label(str(item.get("rarity", "common")).to_upper(), Layout.font_tiny(), Color(Formulas.rarity_hex(str(item.get("rarity", "common")))))
	rarity.position = Vector2(180, 326)
	rarity.size = Vector2(74, 14)
	add_child(rarity)
	var stats := Widgets.label(_stat_line(item), Layout.font_tiny(), SpriteCatalog.LIGHT)
	stats.position = Vector2(16, 344)
	stats.size = Vector2(230, 28)
	add_child(stats)
	var price := int(item.get("price", 0))
	var cost := Widgets.label("Price %d   Sell %d" % [price, Formulas.sell_value(price)], Layout.font_tiny(), SpriteCatalog.GOLD)
	cost.position = Vector2(16, 372)
	cost.size = Vector2(230, 14)
	add_child(cost)
	var blurb := Widgets.label(str(item.get("description", "")), Layout.font_tiny(), SpriteCatalog.LIGHT)
	blurb.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	blurb.position = Vector2(16, 386)
	blurb.size = Vector2(230, 28)
	add_child(blurb)
	var compare := Widgets.label(_compare_line(item), Layout.font_tiny(), SpriteCatalog.SAFE)
	compare.name = "Compare"
	compare.position = Vector2(16, 412)
	compare.size = Vector2(230, 14)
	add_child(compare)
	if _from_shop:
		var buy := Widgets.make_button("Buy %d" % price, Vector2(100, 28))
		buy.name = "Buy"
		buy.position = Vector2(16, 430)
		buy.disabled = GameState.gold < price
		buy.pressed.connect(_buy)
		add_child(buy)
		return
	var equip := Widgets.make_button("Equip", Vector2(70, 28))
	equip.name = "Equip"
	equip.position = Vector2(16, 430)
	var quest_item := str(item.get("slot", "")) == "quest"
	equip.disabled = quest_item or str(item.get("slot", "")) == "usable"
	equip.pressed.connect(_equip)
	add_child(equip)
	var use := Widgets.make_button("Use", Vector2(60, 28))
	use.name = "Use"
	use.position = Vector2(92, 430)
	use.disabled = str(item.get("slot", "")) != "usable"
	use.pressed.connect(_use)
	add_child(use)
	var sell := Widgets.make_button("Sell", Vector2(60, 28))
	sell.name = "Sell"
	sell.position = Vector2(158, 430)
	sell.disabled = quest_item
	sell.pressed.connect(_sell)
	add_child(sell)


func _stat_line(item: Dictionary) -> String:
	var stats: Dictionary = item.get("stats", {})
	var parts: PackedStringArray = []
	_add_part(parts, "Body", int(stats.get("body", 0)))
	_add_part(parts, "Senses", int(stats.get("senses", 0)))
	_add_part(parts, "Mind", int(stats.get("mind", 0)))
	_add_part(parts, "Atk", int(stats.get("attack", 0)))
	_add_part(parts, "DR", int(stats.get("dr", 0)))
	_add_part(parts, "HP", int(stats.get("max_hp", 0)))
	_add_part(parts, "EN", int(stats.get("max_mp", 0)))
	_add_part(parts, "Crit", int(stats.get("crit", 0)))
	_add_part(parts, "Threat", int(stats.get("threat", 0)))
	if str(item.get("slot", "")) == "usable":
		if str(item.get("kind", "")) == "heal_hp":
			parts.append("Heal %d" % int(item.get("amount", 0)))
		elif str(item.get("kind", "")) == "heal_mp":
			parts.append("Energy %d" % int(item.get("amount", 0)))
		elif str(item.get("kind", "")) == "heal_both":
			parts.append("Heal %d / EN %d" % [int(item.get("amount", 0)), int(item.get("mp_amount", 0))])
	if int(item.get("hands", 1)) >= 2:
		parts.append("Two hands")
	var weight := str(item.get("weight", ""))
	if weight != "":
		parts.append(weight)
	if parts.is_empty():
		return str(item.get("slot", ""))
	return "  ".join(parts)


func _add_part(parts: PackedStringArray, label: String, amount: int) -> void:
	if amount == 0:
		return
	parts.append("%s %d" % [label, amount])


func _compare_line(item: Dictionary) -> String:
	if GameState.party.is_empty() or str(item.get("slot", "")) == "usable":
		return ""
	var member: Dictionary = GameState.party[_hero]
	var block := Formulas.wear_block(item, ContentDB.class_def(str(member["class_id"])))
	if block == "weight":
		return "Too heavy for this class"
	if block == "tag":
		return "This class cannot wield it"
	if block != "":
		return ""
	var before := GameState.combat_stats(member)
	var trial: Dictionary = member.duplicate(true)
	var gear := Formulas.normalize_gear(member.get("gear", {}))
	var main_hands := 1
	if str(gear["main"]) != "" and ContentDB.has_item(str(gear["main"])):
		main_hands = int(ContentDB.resolve(str(gear["main"])).get("hands", 1))
	var plan: Dictionary = Formulas.equip_plan(gear, item, "", main_hands)
	if not bool(plan.get("ok", false)):
		return ""
	trial["gear"] = plan["gear"]
	var after := GameState.combat_stats(trial)
	return "Atk %d to %d   DR %d to %d   HP %d to %d" % [
		before["attack"], after["attack"], before["dr"], after["dr"], before["max_hp"], after["max_hp"],
	]


func _equip() -> void:
	var reason := GameState.equip_item(_hero, _selected, "")
	if reason == "":
		_selected = ""
		_mode = "hero"
	_refresh()


func _use() -> void:
	if GameState.use_on(_hero, _selected) == "":
		_selected = ""
	_refresh()


func _buy() -> void:
	if GameState.buy_item(_selected) == "":
		_from_shop = false
		_mode = "bag"
	_refresh()


func _sell() -> void:
	if GameState.sell_item(_selected) == "":
		_selected = ""
	_refresh()


func _refresh() -> void:
	call_deferred("_rebuild")
