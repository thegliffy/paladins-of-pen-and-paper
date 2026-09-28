extends Node
## Loads the JSON content tables once. Numbers come back as floats; callers cast.

const Pack := preload("res://scripts/core/packed_file.gd")


var personas := {}
var races := {}
var classes := {}
var skills := {}
var monsters := {}
var items := {}
var quests: Array = []
var region := {}
var places := {}
var edges: Array = []
var encounters := {}
var threat := {}
var actions := {}


func _ready() -> void:
	_index("res://data/personas.json", personas)
	_index("res://data/races.json", races)
	_index("res://data/classes.json", classes)
	_index("res://data/skills.json", skills)
	_index("res://data/monsters.json", monsters)
	_index("res://data/items.json", items)
	var quest_raw: Variant = _read("res://data/quests.json")
	if quest_raw is Array:
		quests = quest_raw
	else:
		push_error("ContentDB quests.json did not load")
		quests = []
	var region_raw: Variant = _read("res://data/region.json")
	if region_raw is Dictionary:
		region = region_raw
	else:
		push_error("ContentDB region.json did not load")
		region = {}
	edges = region.get("edges", [])
	for place in region.get("places", []):
		places[str(place["id"])] = place
	var encounter_raw: Variant = _read("res://data/encounters.json")
	if encounter_raw is Dictionary:
		encounters = encounter_raw
	else:
		push_error("ContentDB encounters.json did not load")
	var threat_raw: Variant = _read("res://data/threat.json")
	if threat_raw is Dictionary:
		threat = threat_raw
	else:
		push_error("ContentDB threat.json did not load")
	_index("res://data/actions.json", actions)


func _read(path: String) -> Variant:
	var parsed: Variant = Pack.json(path)
	if parsed == null:
		push_error("ContentDB could not read %s" % path)
	return parsed


func _index(path: String, into: Dictionary) -> void:
	var rows: Variant = _read(path)
	if not rows is Array:
		push_error("ContentDB expected a list in %s" % path)
		return
	for row in rows:
		if row is Dictionary:
			into[str(row["id"])] = row


func persona(id: String) -> Dictionary:
	return personas[id]


func race(id: String) -> Dictionary:
	return races[id]


func class_def(id: String) -> Dictionary:
	return classes[id]


func skill(id: String) -> Dictionary:
	return skills[id]


func monster(id: String) -> Dictionary:
	return monsters[id]


func item(id: String) -> Dictionary:
	return items[id]


func place(id: String) -> Dictionary:
	return places[id]


func threat_rules() -> Dictionary:
	return threat


func threat_debug() -> bool:
	return bool(threat.get("debug", false))


func action_def(id: String) -> Dictionary:
	return actions.get(id, {})


func quest(id: String) -> Dictionary:
	for row in quests:
		if str(row["id"]) == id:
			return row
	return {}
