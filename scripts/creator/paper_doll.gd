extends Control
class_name PaperDoll
## Layered front or back doll. Layer images share SpriteCatalog.LAYER_ANCHOR.


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func set_look(look: Dictionary, class_id: String, race_id: String, face: String = "front") -> void:
	for child in get_children():
		remove_child(child)
		child.free()
	var canvas: Vector2 = SpriteCatalog.FRONT_SIZE if face == "front" else SpriteCatalog.BACK_SIZE
	custom_minimum_size = canvas
	size = canvas
	var skin := SpriteCatalog.color_at("skins", int(look.get("skin", 0)))
	var hair := SpriteCatalog.color_at("hairs", int(look.get("hair_color", 0)))
	var cloth := SpriteCatalog.color_at("outfits", int(look.get("outfit_color", 0)))
	var feature := str(ContentDB.race(race_id).get("feature", "none"))
	_layer(face, "body", skin)
	_layer(face, "outfit_%s" % class_id, cloth)
	if face == "front":
		_layer(face, "head_%d" % int(look.get("head", 0)), skin)
		if feature == "ears":
			_layer(face, "ears", skin)
		_layer(face, "face_%d" % int(look.get("head", 0)), Color.WHITE)
		if feature == "beard":
			_layer(face, "beard", hair)
		_layer(face, "hair_%d" % int(look.get("hair", 0)), hair)
	else:
		if feature == "ears":
			_layer(face, "ears", skin)
		_layer(face, "hair_%d" % int(look.get("hair", 0)), hair)
		if feature == "beard":
			_layer(face, "beard", hair)
	_layer(face, "hat_%s" % class_id, cloth)
	_layer(face, "weapon_%s" % class_id, Color.WHITE)


func _layer(face: String, layer: String, tint: Color) -> void:
	if not SpriteCatalog.has_doll(face, layer):
		return
	var rect := TextureRect.new()
	rect.texture = SpriteCatalog.doll(face, layer)
	rect.modulate = tint
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	rect.position = SpriteCatalog.LAYER_ANCHOR
	rect.size = size
	rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	rect.stretch_mode = TextureRect.STRETCH_SCALE
	add_child(rect)
