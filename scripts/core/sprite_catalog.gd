extends Object
class_name SpriteCatalog
## Sprite paths, doll anchors, and the small palette.
## Every doll layer is a full-canvas image, so the layer anchor is the origin.
## Where a doll, monster, or the GM sits on a screen comes from Layout.


const Pack := preload("res://scripts/core/packed_file.gd")
const LAYER_ANCHOR := Vector2.ZERO
const GM_ANCHOR := Vector2(0.5, 1.0)
const MONSTER_FRAME := Vector2i(48, 48)
const FRONT_SIZE := Vector2(48, 64)
const BACK_SIZE := Vector2(40, 52)

const INK := Color("2a2118")
const CREAM := Color("f3e6c8")
const CREAM_DARK := Color("e2cfa6")
const WOOD := Color("6b4228")
const HP := Color("d64545")
const HP_BACK := Color("3a1818")
const MP := Color("3d7ad6")
const MP_BACK := Color("14243f")
const GOLD := Color("e6b23c")
const SAFE := Color("3ec8c8")
const FREE := Color("f0d050")
const HIGHLIGHT := Color("ffd24a")
const CREAM_INK := Color("2a2118")
const LIGHT := Color("f7f1e4")

static var _appearance: Dictionary = {}


static func appearance() -> Dictionary:
	if _appearance.is_empty():
		var parsed: Variant = Pack.json("res://data/appearance.json")
		if parsed is Dictionary:
			_appearance = parsed
		else:
			push_error("appearance.json did not load")
	return _appearance


static func color_at(list_name: String, index: int) -> Color:
	var list: Array = appearance()[list_name]
	return Color(str(list[clampi(index, 0, list.size() - 1)]))


static func doll_path(facing: String, layer: String) -> String:
	return "res://art/doll/%s/%s.png" % [facing, layer]


static func has_doll(facing: String, layer: String) -> bool:
	return Pack.exists(doll_path(facing, layer))


static func doll(facing: String, layer: String) -> Texture2D:
	return load(doll_path(facing, layer))


static func monster_strip(monster_id: String) -> Texture2D:
	return load("res://art/monsters/%s.png" % monster_id)


static func ui(name: String) -> Texture2D:
	return load("res://art/ui/%s.png" % name)


static func background(kind: String) -> Texture2D:
	var path := "res://art/bg/%s.png" % kind
	if not Pack.exists(path):
		push_error("Missing backdrop %s" % path)
		path = "res://art/bg/meadow.png"
	var loaded: Texture2D = load(path)
	if loaded == null:
		push_error("Failed to load backdrop %s" % path)
	return loaded


static func map_texture() -> Texture2D:
	return load("res://art/map/greenmere.png")


static func monster_frame(strip: Texture2D, frame: int) -> AtlasTexture:
	var atlas := AtlasTexture.new()
	atlas.atlas = strip
	var size := MONSTER_FRAME
	atlas.region = Rect2(frame * size.x, 0, size.x, size.y)
	return atlas
