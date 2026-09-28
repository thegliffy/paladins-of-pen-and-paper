extends Control
class_name PaperDoll
## Front creator doll or back seat doll, baked from the production pack.


var _sprite: TextureRect
var _base: Texture2D
var _face := ""
var _look: Dictionary = {}
var _class_id := ""


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_sprite = TextureRect.new()
	_sprite.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_sprite.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_sprite.stretch_mode = TextureRect.STRETCH_SCALE
	add_child(_sprite)


func set_look(look: Dictionary, class_id: String, _race_id: String, face: String = "front") -> void:
	_face = face
	_look = look
	_class_id = class_id
	var canvas := ArtPack.doll_canvas(face)
	custom_minimum_size = canvas
	size = canvas
	_sprite.position = Vector2.ZERO
	_sprite.size = canvas
	_base = ArtPack.compose_doll(face, look, class_id)
	_sprite.texture = _base


func show_sheet(sheet: Texture2D, canvas: Vector2) -> void:
	_face = "back"
	custom_minimum_size = canvas
	size = canvas
	_sprite.position = Vector2.ZERO
	_sprite.size = canvas
	_base = sheet
	_sprite.texture = sheet


func set_raised(up: bool) -> void:
	if _base == null:
		return
	if up:
		_sprite.texture = ArtPack.gold_outline(_base)
	else:
		_sprite.texture = _base


func show_gear(member: Dictionary) -> void:
	var old := get_node_or_null("GearMarks")
	if old:
		old.free()
	if _face == "back":
		var spec := seat_spec(member)
		if spec.is_empty():
			return
		var class_id := str(member.get("class_id", _class_id))
		var look: Dictionary = member.get("look", _look)
		_class_id = class_id
		_look = look
		var canvas := ArtPack.doll_canvas("back")
		custom_minimum_size = canvas
		size = canvas
		_sprite.position = Vector2.ZERO
		_sprite.size = canvas
		_base = ArtPack.compose_doll("back", look, class_id, spec)
		_sprite.texture = _base
		return
	var host := Control.new()
	host.name = "GearMarks"
	host.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(host)
	var gear := Formulas.normalize_gear(member.get("gear", {}))
	var main_id := str(gear["main"])
	var two := false
	if main_id != "" and ContentDB.items.has(main_id):
		two = int(ContentDB.item(main_id).get("hands", 1)) >= 2
	_mark(host, main_id, Vector2(maxi(0.0, size.x - 14.0), maxi(0.0, size.y - 16.0)))
	if not two:
		_mark(host, str(gear["off"]), Vector2(0, maxi(0.0, size.y - 16.0)))
	_mark(host, str(gear["armor"]), Vector2(0, 6))


static func seat_spec(member: Dictionary) -> Dictionary:
	## 48x78 overlays for the back-view seat. Empty when nothing painted is worn.
	var gear := Formulas.normalize_gear(member.get("gear", {}))
	var spec := {}
	var armor_id := str(gear["armor"])
	if armor_id != "" and ContentDB.items.has(armor_id):
		var armor: Dictionary = ContentDB.item(armor_id)
		var armor_path := str(armor.get("doll", ""))
		if armor_path != "" and ArtPack.has(armor_path):
			spec["armor"] = armor_path
	var main_id := str(gear["main"])
	var two := false
	if main_id != "" and ContentDB.items.has(main_id):
		var main: Dictionary = ContentDB.item(main_id)
		var main_path := str(main.get("doll", ""))
		if main_path != "" and ArtPack.has(main_path):
			spec["main"] = main_path
			spec["main_weapon"] = str(main.get("slot", "")) == "weapon"
			two = int(main.get("hands", 1)) >= 2
			spec["two_hand"] = two
	if not two:
		var off_id := str(gear["off"])
		if off_id != "" and ContentDB.items.has(off_id):
			var off: Dictionary = ContentDB.item(off_id)
			var off_path := str(off.get("doll", ""))
			if off_path != "" and ArtPack.has(off_path):
				spec["off"] = off_path
				spec["off_flip"] = ArtPack.offhand_flips(off)
	return spec


func _mark(host: Control, item_id: String, at: Vector2) -> void:
	if item_id == "" or not ContentDB.items.has(item_id):
		return
	var item: Dictionary = ContentDB.item(item_id)
	var icon_path := str(item.get("icon", ""))
	if icon_path != "" and ArtPack.has(icon_path):
		var icon := TextureRect.new()
		icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
		icon.texture = ArtPack.texture(icon_path)
		icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		icon.stretch_mode = TextureRect.STRETCH_SCALE
		icon.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		icon.position = at
		icon.size = Vector2(12, 12)
		host.add_child(icon)
		return
	var pip := ColorRect.new()
	pip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	pip.color = Color(Formulas.rarity_hex(str(item.get("rarity", "common"))))
	pip.position = at
	pip.size = Vector2(6, 6)
	host.add_child(pip)
