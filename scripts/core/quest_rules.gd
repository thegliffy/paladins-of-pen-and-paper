class_name QuestRules
extends RefCounted
## Story chain and Candlewick board. Pure rules so the headless tests can run them.


const ACTIVE_CAP := 3
const BOARD_SLOTS := 3
const DROP_CHANCE := 0.65


static func steps(data: Dictionary) -> Array:
	return data.get("story", [])


static func board(data: Dictionary) -> Array:
	return data.get("board", [])


static func find_row(rows: Array, id: String) -> Dictionary:
	for row in rows:
		if str(row.get("id", "")) == id:
			return row
	return {}


static func empty_state() -> Dictionary:
	return {
		"story_done": [],
		"offers": ["", "", ""],
		"active": [],
		"salt": 1,
	}


static func current_step(story: Array, done: Array) -> Dictionary:
	for step in story:
		if not done.has(str(step.get("id", ""))):
			return step
	return {}


static func revealed_places(story: Array, done: Array) -> Array:
	var places: Array = ["candlewick"]
	for step in story:
		if not done.has(str(step.get("id", ""))):
			continue
		for place_id in step.get("reveal", []):
			var key := str(place_id)
			if not places.has(key):
				places.append(key)
	return places


static func unlocked_regions(revealed: Array) -> Array:
	var regions: Array = []
	if revealed.has("millpond") or revealed.has("briar_cross"):
		regions.append("meadow")
	if revealed.has("lantern_reach"):
		regions.append("coast")
	if revealed.has("howling_cleft"):
		regions.append("cave")
	if revealed.has("gravel_keep"):
		regions.append("keep")
	return regions


static func focus_place(step: Dictionary) -> String:
	var highlight := str(step.get("highlight", ""))
	if highlight != "":
		return highlight
	return str(step.get("place", ""))


static func blocks_travel(_place_id: String, _done: Array) -> bool:
	## The story highlights the next place. Roads that already exist stay open.
	return false


static func step_ready(step: Dictionary, place_id: String, won: bool, killed: Array, inventory: Dictionary) -> bool:
	if step.is_empty():
		return false
	if str(step.get("place", "")) != place_id:
		return false
	match str(step.get("type", "")):
		"visit":
			return true
		"fight":
			return won
		"boss":
			return won and killed.has(str(step.get("monster", "")))
		"deliver":
			return int(inventory.get(str(step.get("item", "")), 0)) > 0
		_:
			return false


static func story_drop_item(step: Dictionary, place_id: String, killed: Array) -> String:
	var drop := str(step.get("drop", ""))
	var monster := str(step.get("monster", ""))
	if drop == "" or monster == "" or not killed.has(monster):
		return ""
	var source := str(step.get("source", step.get("place", "")))
	if source != "" and place_id != source:
		return ""
	return drop


static func advance(story: Array, done: Array, place_id: String, won: bool, killed: Array, inventory: Dictionary) -> Dictionary:
	var next: Array = done.duplicate()
	var completed: Array = []
	for _guard in 8:
		var step := current_step(story, next)
		if not step_ready(step, place_id, won, killed, inventory):
			break
		next.append(str(step.get("id", "")))
		completed.append(step)
	return {"done": next, "completed": completed}


static func reward_takes(completed: Array) -> Array:
	var ids: Array = []
	for step in completed:
		if str(step.get("type", "")) == "deliver":
			var item_id := str(step.get("item", ""))
			if item_id != "":
				ids.append(item_id)
	return ids


static func eligible_ids(rows: Array, regions: Array, blocked: Array) -> Array:
	var ids: Array = []
	for row in rows:
		var id := str(row.get("id", ""))
		if id == "" or blocked.has(id):
			continue
		if not regions.has(str(row.get("region", ""))):
			continue
		ids.append(id)
	ids.sort()
	return ids


static func fill_offers(rows: Array, regions: Array, blocked: Array, salt: int) -> Array:
	var pool := eligible_ids(rows, regions, blocked)
	var offers: Array = []
	for slot in BOARD_SLOTS:
		if pool.is_empty():
			offers.append("")
			continue
		var index := posmod(salt + slot * 13, pool.size())
		var id := str(pool[index])
		offers.append(id)
		pool.erase(id)
	return offers


static func reroll_slot(offers: Array, slot: int, rows: Array, regions: Array, blocked: Array, salt: int) -> Array:
	var next: Array = offers.duplicate()
	while next.size() < BOARD_SLOTS:
		next.append("")
	var pool := eligible_ids(rows, regions, blocked)
	if pool.is_empty():
		next[slot] = ""
		return next
	next[slot] = str(pool[posmod(salt + slot * 13, pool.size())])
	return next


static func accept(offers: Array, slot: int, active: Array, rows: Array, regions: Array, salt: int) -> Dictionary:
	if slot < 0 or slot >= offers.size():
		return {"ok": false, "reason": "slot", "offers": offers, "active": active, "salt": salt}
	if active.size() >= ACTIVE_CAP:
		return {"ok": false, "reason": "cap", "offers": offers, "active": active, "salt": salt}
	var id := str(offers[slot])
	if id == "" or find_row(rows, id).is_empty():
		return {"ok": false, "reason": "empty", "offers": offers, "active": active, "salt": salt}
	for row in active:
		if str(row.get("id", "")) == id:
			return {"ok": false, "reason": "active", "offers": offers, "active": active, "salt": salt}
	var next_active: Array = active.duplicate(true)
	next_active.append({"id": id, "progress": 0})
	var blocked: Array = _active_ids(next_active)
	for i in offers.size():
		if i == slot:
			continue
		var other := str(offers[i])
		if other != "":
			blocked.append(other)
	var next_salt := salt + 1
	var next_offers := reroll_slot(offers, slot, rows, regions, blocked, next_salt)
	return {"ok": true, "reason": "", "offers": next_offers, "active": next_active, "salt": next_salt}


static func abandon(active: Array, id: String) -> Array:
	var next: Array = []
	for row in active:
		if str(row.get("id", "")) == id:
			continue
		next.append(row)
	return next


static func note_kill(active: Array, rows: Array, monster_id: String) -> PackedStringArray:
	var lines := PackedStringArray()
	for row in active:
		var quest := find_row(rows, str(row.get("id", "")))
		if str(quest.get("kind", "")) != "kill":
			continue
		if str(quest.get("monster", "")) != monster_id:
			continue
		var count := int(quest.get("count", 1))
		var progress := int(row.get("progress", 0))
		if progress >= count:
			continue
		progress += 1
		row["progress"] = progress
		lines.append(progress_line(quest, progress))
	return lines


static func collect_drop(active: Array, rows: Array, monster_id: String, roll: float, chance: float = DROP_CHANCE) -> String:
	if roll >= chance:
		return ""
	for row in active:
		var quest := find_row(rows, str(row.get("id", "")))
		if str(quest.get("kind", "")) != "collect":
			continue
		if str(quest.get("monster", "")) != monster_id:
			continue
		if int(row.get("progress", 0)) >= int(quest.get("count", 1)):
			continue
		return str(quest.get("item", ""))
	return ""


static func bump_collect(active: Array, item_id: String, rows: Array) -> String:
	for row in active:
		var quest := find_row(rows, str(row.get("id", "")))
		if str(quest.get("kind", "")) != "collect":
			continue
		if str(quest.get("item", "")) != item_id:
			continue
		var count := int(quest.get("count", 1))
		var progress := int(row.get("progress", 0))
		if progress >= count:
			continue
		progress += 1
		row["progress"] = progress
		return progress_line(quest, progress)
	return ""


static func progress_line(quest: Dictionary, progress: int) -> String:
	var count := int(quest.get("count", 1))
	var label := str(quest.get("monster_name", quest.get("name", "Quest")))
	if str(quest.get("kind", "")) == "collect":
		label = str(quest.get("item_name", label))
	return "%s %d/%d" % [label, mini(progress, count), count]


static func can_turn_in(quest: Dictionary, progress: int) -> bool:
	return not quest.is_empty() and progress >= int(quest.get("count", 1))


static func turn_in(active: Array, rows: Array, id: String) -> Dictionary:
	var quest := find_row(rows, id)
	for row in active:
		if str(row.get("id", "")) != id:
			continue
		if not can_turn_in(quest, int(row.get("progress", 0))):
			return {"ok": false, "reason": "progress", "quest": quest, "active": active}
		return {"ok": true, "reason": "", "quest": quest, "active": abandon(active, id)}
	return {"ok": false, "reason": "missing", "quest": quest, "active": active}


static func turn_in_takes(quest: Dictionary) -> int:
	if str(quest.get("kind", "")) != "collect":
		return 0
	return int(quest.get("count", 1))


static func tracker_line(step: Dictionary) -> String:
	if step.is_empty():
		return "Story: the road is quiet."
	return "Story: %s" % str(step.get("objective", ""))


static func pack_state(state: Dictionary) -> Dictionary:
	return {
		"story_done": state.get("story_done", []).duplicate(),
		"offers": state.get("offers", ["", "", ""]).duplicate(),
		"active": state.get("active", []).duplicate(true),
		"salt": int(state.get("salt", 1)),
	}


static func unpack_state(raw: Dictionary) -> Dictionary:
	var state := empty_state()
	var done: Array = []
	for quest_id in raw.get("story_done", []):
		done.append(str(quest_id))
	state["story_done"] = done
	var offers: Array = []
	for quest_id in raw.get("offers", []):
		offers.append(str(quest_id))
	while offers.size() < BOARD_SLOTS:
		offers.append("")
	if offers.size() > BOARD_SLOTS:
		offers = offers.slice(0, BOARD_SLOTS)
	state["offers"] = offers
	var active: Array = []
	for row in raw.get("active", []):
		if row is Dictionary:
			active.append({"id": str(row.get("id", "")), "progress": maxi(0, int(row.get("progress", 0)))})
	state["active"] = active
	state["salt"] = maxi(1, int(raw.get("salt", 1)))
	return state


static func _active_ids(active: Array) -> Array:
	var ids: Array = []
	for row in active:
		var id := str(row.get("id", ""))
		if id != "":
			ids.append(id)
	return ids
