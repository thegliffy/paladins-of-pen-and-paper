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
