extends Node
## Party, gold, place, inventory, and the save that survives the process being killed.

const SAVE_PATH := "user://paladins_save.json"
const START_GOLD := 500

var gold := START_GOLD
var place_id := "candlewick"
var party: Array = []
var inventory := {"tonic": 3, "vial": 2}
var quests_done: Array = []
var hops := 0
var campaign_started := false
var in_battle := false
var battle_lock: Dictionary = {}


func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST or what == NOTIFICATION_APPLICATION_PAUSED or what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		if campaign_started:
			save_game()


func has_save() -> bool:
	return FileAccess.file_exists(SAVE_PATH)


func new_campaign(members: Array) -> void:
	gold = START_GOLD
	place_id = str(ContentDB.region.get("start", "candlewick"))
	party = members
	inventory = {"tonic": 3, "vial": 2}
	quests_done = []
	hops = 0
	in_battle = false
	battle_lock = {}
	campaign_started = true
	save_game()


func make_member(persona_id: String, race_id: String, class_id: String, look: Dictionary) -> Dictionary:
	var member := {
		"persona": persona_id,
		"race": race_id,
		"class_id": class_id,
		"look": look.duplicate(true),
		"level": 1,
		"xp": 0,
		"hp": 1,
		"mp": 1,
		"skill_ranks": {},
		"skill_points_spent": 0,
	}
	for skill_id in ContentDB.class_def(class_id)["skills"]:
		member["skill_ranks"][str(skill_id)] = 1
	var stats := combat_stats(member)
	member["hp"] = stats["max_hp"]
	member["mp"] = stats["max_mp"]
	return member


func combat_stats(member: Dictionary) -> Dictionary:
	var persona: Dictionary = ContentDB.persona(str(member["persona"]))
	var race: Dictionary = ContentDB.race(str(member["race"]))
	var cls: Dictionary = ContentDB.class_def(str(member["class_id"]))
	var stats := Formulas.compose_stats(
		int(cls["body"]), int(cls["senses"]), int(cls["mind"]),
		int(persona["body"]), int(persona["senses"]), int(persona["mind"]),
		int(race["body"]), int(race["senses"]), int(race["mind"])
	)
	var level := int(member["level"])
	var max_hp := Formulas.max_hp(level, stats["body"], stats["mind"])
	var max_mp := Formulas.max_energy(level, stats["body"], stats["mind"]) + int(race.get("energy", 0))
	return {
		"body": stats["body"],
		"senses": stats["senses"],
		"mind": stats["mind"],
		"max_hp": max_hp,
		"max_mp": max_mp,
		"attack": Formulas.player_attack(level, stats["body"]),
		"dr": int(race.get("dr", 0)) + int(persona.get("dr", 0)),
		"initiative": int(persona.get("initiative", 0)),
		"spell_bonus": float(persona.get("spell_bonus", 0.0)),
		"travel_bonus": int(persona.get("travel_bonus", 0)),
		"skill_points": int(race.get("skill_points", 0)),
	}


func display_name(member: Dictionary) -> String:
	return "%s the %s %s" % [
		ContentDB.persona(str(member["persona"]))["name"],
		ContentDB.race(str(member["race"]))["name"],
		ContentDB.class_def(str(member["class_id"]))["name"],
	]


func unspent_points(member: Dictionary) -> int:
	var stats := combat_stats(member)
	return Formulas.total_skill_points(int(member["level"]), int(stats["skill_points"])) - int(member["skill_points_spent"])


func spend_point(member: Dictionary, skill_id: String) -> bool:
	if unspent_points(member) <= 0:
		return false
	var rank := int(member["skill_ranks"].get(skill_id, 1))
	if rank >= 15:
		return false
	member["skill_ranks"][skill_id] = rank + 1
	member["skill_points_spent"] = int(member["skill_points_spent"]) + 1
	save_game()
	return true


func apply_xp(member: Dictionary, amount: int) -> bool:
	var before := combat_stats(member)
	member["xp"] = int(member["xp"]) + amount
	var leveled := false
	while int(member["xp"]) >= Formulas.xp_to_next(int(member["level"])):
		member["xp"] = int(member["xp"]) - Formulas.xp_to_next(int(member["level"]))
		member["level"] = int(member["level"]) + 1
		leveled = true
	var after := combat_stats(member)
	member["hp"] = mini(after["max_hp"], int(member["hp"]) + maxi(0, after["max_hp"] - before["max_hp"]))
	member["mp"] = mini(after["max_mp"], int(member["mp"]) + maxi(0, after["max_mp"] - before["max_mp"]))
	return leveled


func party_levels() -> Array:
	var levels: Array = []
	for member in party:
		levels.append(int(member["level"]))
	return levels


func party_average() -> float:
	return Formulas.party_average(party_levels())


func living_members() -> Array:
	var living: Array = []
	for member in party:
		if int(member["hp"]) > 0:
			living.append(member)
	return living


func party_power() -> int:
	var total := 0
	var source: Array = living_members()
	if source.is_empty():
		source = party
	for member in source:
		total += int(combat_stats(member)["attack"])
	return maxi(1, total)


func travel_bonus() -> int:
	var bonus := 0
	for member in party:
		bonus += int(combat_stats(member)["travel_bonus"])
	return bonus


func give_item(item_id: String, count: int = 1) -> void:
	inventory[item_id] = int(inventory.get(item_id, 0)) + count


func take_item(item_id: String) -> bool:
	var have := int(inventory.get(item_id, 0))
	if have <= 0:
		return false
	inventory[item_id] = have - 1
	if int(inventory[item_id]) <= 0:
		inventory.erase(item_id)
	return true


func arm_battle() -> void:
	battle_lock = _capture()
	in_battle = true
	_write(battle_lock)


func disarm_battle() -> void:
	in_battle = false
	battle_lock = {}
	save_game()


func save_game() -> void:
	if not campaign_started:
		return
	if in_battle and not battle_lock.is_empty():
		_write(battle_lock)
	else:
		_write(_capture())


func load_game() -> bool:
	if not has_save():
		return false
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(SAVE_PATH))
	if typeof(parsed) != TYPE_DICTIONARY:
		return false
	var data: Dictionary = parsed
	gold = int(data.get("gold", START_GOLD))
	place_id = str(data.get("place_id", "candlewick"))
	hops = int(data.get("hops", 0))
	quests_done = []
	for quest_id in data.get("quests_done", []):
		quests_done.append(str(quest_id))
	inventory = {}
	var raw_items: Dictionary = data.get("inventory", {})
	for item_id in raw_items.keys():
		inventory[str(item_id)] = int(raw_items[item_id])
	party = []
	for raw in data.get("party", []):
		party.append(_normalize_member(raw))
	campaign_started = not party.is_empty()
	in_battle = false
	battle_lock = {}
	return campaign_started


func _normalize_member(raw: Dictionary) -> Dictionary:
	var look: Dictionary = raw.get("look", {})
	var member := {
		"persona": str(raw.get("persona", "mason")),
		"race": str(raw.get("race", "hearthborn")),
		"class_id": str(raw.get("class_id", "paladin")),
		"look": {
			"skin": int(look.get("skin", 0)),
			"head": int(look.get("head", 0)),
			"hair": int(look.get("hair", 0)),
			"hair_color": int(look.get("hair_color", 0)),
			"outfit_color": int(look.get("outfit_color", 0)),
		},
		"level": int(raw.get("level", 1)),
		"xp": int(raw.get("xp", 0)),
		"hp": int(raw.get("hp", 1)),
		"mp": int(raw.get("mp", 1)),
		"skill_ranks": {},
		"skill_points_spent": int(raw.get("skill_points_spent", 0)),
	}
	var ranks: Dictionary = raw.get("skill_ranks", {})
	for skill_id in ranks.keys():
		member["skill_ranks"][str(skill_id)] = int(ranks[skill_id])
	return member


func _capture() -> Dictionary:
	return {
		"version": 1,
		"gold": gold,
		"place_id": place_id,
		"party": party.duplicate(true),
		"inventory": inventory.duplicate(true),
		"quests_done": quests_done.duplicate(),
		"hops": hops,
	}


func _write(data: Dictionary) -> void:
	var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(data))
