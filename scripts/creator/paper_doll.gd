extends Control
class_name PaperDoll
## Front creator doll or back seat doll, baked from the production pack.


var _sprite: TextureRect


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
	_sprite.texture = ArtPack.compose_doll(face, look, class_id)
