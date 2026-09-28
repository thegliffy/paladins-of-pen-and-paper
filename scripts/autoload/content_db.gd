extends Node
## Loads the JSON content tables once. Numbers come back as floats; callers cast.


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


func _ready() -> void:
	_index("res://data/personas.json", personas)
	_index("res://data/races.json", races)
	_index("res://data/classes.json", classes)
	_index("res://data/skills.json", skills)
	_index("res://data/monsters.json", monsters)
	_index("res://data/items.json", items)
	quests = _read("res://data/quests.json")
	region = _read("res://data/region.json")
	edges = region.get("edges", [])
	for place in region.get("places", []):
		places[str(place["id"])] = place
	encounters = _read("res://data/encounters.json")
	threat = _read("res://data/threat.json")


func _read(path: String):
	return JSON.parse_string(FileAccess.get_file_as_string(path))


func _index(path: String, into: Dictionary) -> void:
	for row in _read(path):
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


func quest(id: String) -> Dictionary:
	for row in quests:
		if str(row["id"]) == id:
			return row
	return {}
