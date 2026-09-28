extends Object
class_name Layout
## Screen rectangles, type sizes, and the reserved landscape slot.
## Screens ask Layout for geometry. They do not hardcode portrait coordinates.


static var _root: Dictionary = {}
static var active_name := "portrait"


static func setup() -> void:
	if not _root.is_empty():
		return
	var raw = JSON.parse_string(FileAccess.get_file_as_string("res://data/layout.json"))
	_root = raw
	active_name = str(raw.get("active", "portrait"))
	var block: Dictionary = raw.get(active_name, {})
	if active_name != "portrait" and not bool(block.get("ready", false)):
		push_warning("Layout '%s' is not authored yet. Using portrait." % active_name)
		active_name = "portrait"


static func cfg() -> Dictionary:
	setup()
	return _root[active_name]


static func rect(group: String, key: String) -> Rect2:
	var raw: Array = cfg()[group][key]
	return Rect2(float(raw[0]), float(raw[1]), float(raw[2]), float(raw[3]))


static func vec(group: String, key: String) -> Vector2:
	var raw: Array = cfg()[group][key]
	return Vector2(float(raw[0]), float(raw[1]))


static func num(key: String) -> float:
	return float(cfg()[key])


static func font_size() -> int:
	return int(cfg()["font"])


static func font_small() -> int:
	return int(cfg()["font_small"])


static func font_tiny() -> int:
	return int(cfg()["font_tiny"])


static func viewport_size() -> Vector2i:
	var raw: Array = cfg()["viewport"]
	return Vector2i(int(raw[0]), int(raw[1]))


static func seat_points() -> Array:
	var points: Array = []
	for pair in cfg()["combat"]["seats"]:
		points.append(Vector2(float(pair[0]), float(pair[1])))
	return points


static func place(node: Control, area: Rect2) -> void:
	node.set_anchors_preset(Control.PRESET_TOP_LEFT)
	node.position = area.position
	node.size = area.size
	node.custom_minimum_size = area.size
