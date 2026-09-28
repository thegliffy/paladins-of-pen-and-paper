extends Control
class_name PaperDoll
## Front creator doll or back seat doll, baked from the production pack.


var _sprite: TextureRect
var _base: Texture2D


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_sprite = TextureRect.new()
	_sprite.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_sprite.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_sprite.stretch_mode = TextureRect.STRETCH_SCALE
	add_child(_sprite)


func set_look(look: Dictionary, class_id: String, _race_id: String, face: String = "front") -> void:
	var canvas := ArtPack.doll_canvas(face)
	custom_minimum_size = canvas
	size = canvas
	_sprite.position = Vector2.ZERO
	_sprite.size = canvas
	_base = ArtPack.compose_doll(face, look, class_id)
	_sprite.texture = _base


func show_sheet(sheet: Texture2D, canvas: Vector2) -> void:
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
	var host := Control.new()
	host.name = "GearMarks"
	host.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(host)
	var gear := Formulas.normalize_gear(member.get("gear", {}))
	_mark(host, str(gear["main"]), Vector2(maxi(0.0, size.x - 14.0), maxi(0.0, size.y - 16.0)))
	_mark(host, str(gear["armor"]), Vector2(0, 6))


func _mark(host: Control, item_id: String, at: Vector2) -> void:
	if item_id == "" or not ContentDB.items.has(item_id):
		return
	var item: Dictionary = ContentDB.item(item_id)
	var doll_path := str(item.get("doll", ""))
	if doll_path != "" and ArtPack.has(doll_path):
		var plate := TextureRect.new()
		plate.mouse_filter = Control.MOUSE_FILTER_IGNORE
		plate.texture = ArtPack.texture(doll_path)
		plate.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		plate.stretch_mode = TextureRect.STRETCH_SCALE
		plate.position = Vector2.ZERO
		plate.size = size
		host.add_child(plate)
		return
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
