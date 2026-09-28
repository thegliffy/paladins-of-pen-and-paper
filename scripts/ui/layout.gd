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


static func party_min() -> int:
	return int(cfg().get("party_min", 1))


static func party_max() -> int:
	return int(cfg().get("party_max", 5))


static func party_seat_points(count: int) -> Array:
	## Centers of up to five seats. x comes from seat_xs. A shorter party
	## uses the same spacing and is centred on the middle seat. Seats listed
	## in seat_lifted (1-based) sit seat_lift pixels higher.
	var combat: Dictionary = cfg()["combat"]
	var xs: Array = combat["seat_xs"]
	var base_y := float(combat["seat_y"])
	var lift := float(combat.get("seat_lift", 0))
	var lifted := {}
	for raw in combat.get("seat_lifted", []):
		lifted[int(raw)] = true
	if xs.is_empty() or count <= 0:
		return []
	var spacing := 0.0
	if xs.size() >= 2:
		spacing = float(xs[1]) - float(xs[0])
	var center := float(xs[int(xs.size() / 2)])
	var n := mini(count, xs.size())
	var start := center - spacing * float(n - 1) * 0.5
	var points: Array = []
	for i in n:
		var y := base_y
		if lifted.has(i + 1):
			y -= lift
		points.append(Vector2(start + spacing * float(i), y))
	return points


static func place(node: Control, area: Rect2) -> void:
	node.set_anchors_preset(Control.PRESET_TOP_LEFT)
	node.position = area.position
	node.size = area.size
	node.custom_minimum_size = area.size
