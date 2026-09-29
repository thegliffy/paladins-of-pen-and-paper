class_name CraftRules
extends RefCounted
## Town shops, forge recipes, and weapon or armor upgrades. Pure, so tests can run them.


const UPGRADE_MAX := 3
const GOLD_STEP := 30


static func base_id(key: String) -> String:
	var at := key.find("@")
	if at < 0:
		return key
	return key.substr(0, at)


static func plus_of(key: String) -> int:
	var at := key.find("@")
	if at < 0:
		return 0
	return maxi(0, int(key.substr(at + 1)))


static func stack_key(item_id: String, plus: int) -> String:
	var rank := clampi(plus, 0, UPGRADE_MAX)
	if rank <= 0:
		return base_id(item_id)
	return "%s@%d" % [base_id(item_id), rank]


static func pack_key(key: String) -> String:
	return stack_key(base_id(key), plus_of(key))


static func display_name(item_name: String, plus: int) -> String:
	if plus <= 0:
		return item_name
	return "%s +%d" % [item_name, plus]


static func scale_int(value: int, plus: int) -> int:
	if plus <= 0:
		return value
	var scaled := int(round(float(value) * (1.0 + 0.25 * float(plus))))
	if value > 0:
		return maxi(value + plus, scaled)
	if value < 0:
		return mini(value - plus, scaled)
	return 0


static func scale_float(value: float, plus: int) -> float:
	if plus <= 0:
		return value
	return snapped(value * (1.0 + 0.25 * float(plus)), 0.01)


static func scaled_stats(stats: Dictionary, plus: int) -> Dictionary:
	var out := {}
	for stat_name in stats.keys():
		var key := str(stat_name)
		if key == "spell_bonus":
			out[key] = scale_float(float(stats[stat_name]), plus)
		else:
			out[key] = scale_int(int(stats[stat_name]), plus)
	return out


static func sell_price(price: int, plus: int) -> int:
	return Formulas.sell_value(price) * (1 + clampi(plus, 0, UPGRADE_MAX))


static func shop_tier(place: Dictionary) -> int:
	return maxi(1, int(place.get("shop_tier", place.get("level", 1))))


static func town_unlocked(place_id: String, revealed: Array) -> bool:
	return place_id == "candlewick" or revealed.has(place_id)


static func is_town(place: Dictionary) -> bool:
	return str(place.get("kind", "")) == "town" or bool(place.get("has_inn", false))


static func shop_ids(items: Array, place: Dictionary, revealed: Array) -> Array:
	if not is_town(place):
		return []
	if not town_unlocked(str(place.get("id", "")), revealed):
		return []
	var tier := shop_tier(place)
	var ids: Array = []
	for row in items:
		if not bool(row.get("shop", false)):
			continue
		if int(row.get("tier", row.get("level", 1))) != tier:
			continue
		var item_id := str(row.get("id", ""))
		if item_id != "":
			ids.append(item_id)
	ids.sort()
	return ids


static func find_recipe(recipes: Array, recipe_id: String) -> Dictionary:
	for row in recipes:
		if str(row.get("id", "")) == recipe_id:
			return row
	return {}


static func can_upgrade(item: Dictionary, plus: int) -> String:
	var slot := str(item.get("slot", ""))
	if slot != "weapon" and slot != "armor":
		return "slot"
	if plus >= UPGRADE_MAX:
		return "max"
	if plus < 0:
		return "plus"
	return ""


static func upgrade_cost(tier: int, plus: int, tiers: Dictionary) -> Dictionary:
	var row: Dictionary = tiers.get(str(maxi(1, tier)), {})
	var primary := str(row.get("primary", ""))
	var secondary := str(row.get("secondary", ""))
	var step := plus + 1
	var materials := {}
	if primary != "":
		materials[primary] = step + 1
	if plus >= 1 and secondary != "":
		materials[secondary] = plus
	return {"gold": GOLD_STEP * maxi(1, tier) * step, "materials": materials}


static func stat_preview(before: Dictionary, after: Dictionary) -> String:
	var order := ["attack", "dr", "body", "senses", "mind", "max_hp", "max_mp", "crit", "threat", "spell_bonus"]
	var labels := {
		"attack": "Atk", "dr": "DR", "body": "Body", "senses": "Senses", "mind": "Mind",
		"max_hp": "HP", "max_mp": "EN", "crit": "Crit", "threat": "Threat", "spell_bonus": "Spell",
	}
	var parts: PackedStringArray = []
	for key in order:
		if not before.has(key) and not after.has(key):
			continue
		if str(key) == "spell_bonus":
			var from_f := float(before.get(key, 0.0))
			var to_f := float(after.get(key, 0.0))
			if is_equal_approx(from_f, to_f):
				continue
			parts.append("Spell %.2f to %.2f" % [from_f, to_f])
			continue
		var from_i := int(before.get(key, 0))
		var to_i := int(after.get(key, 0))
		if from_i == to_i:
			continue
		parts.append("%s %d to %d" % [str(labels[key]), from_i, to_i])
	if parts.is_empty():
		return "No change"
	return "  ".join(parts)


static func pack_bag(bag: Dictionary) -> Dictionary:
	var out := {}
	for raw_key in bag.keys():
		var count := int(bag[raw_key])
		if count <= 0:
			continue
		var key := pack_key(str(raw_key))
		if key == "":
			continue
		out[key] = int(out.get(key, 0)) + count
	return out


static func apply_craft(recipe: Dictionary, bag: Dictionary, gold: int, stack_cap: int) -> Dictionary:
	if recipe.is_empty() or str(recipe.get("result", "")) == "":
		return _fail(bag, gold, "recipe")
	var result_id := str(recipe["result"])
	var cost := {"gold": int(recipe.get("gold", 0)), "materials": recipe.get("materials", {})}
	var have := int(bag.get(result_id, 0))
	if have >= stack_cap:
		return _fail(bag, gold, "full")
	var paid := _pay(bag, gold, cost)
	if not bool(paid["ok"]):
		return paid
	var next: Dictionary = paid["inventory"]
	next[result_id] = int(next.get(result_id, 0)) + 1
	return {"ok": true, "reason": "", "inventory": next, "gold": int(paid["gold"]), "key": result_id}


static func apply_upgrade(key: String, item: Dictionary, bag: Dictionary, gold: int, tiers: Dictionary, stack_cap: int) -> Dictionary:
	var plus := plus_of(key)
	var block := can_upgrade(item, plus)
	if block != "":
		return _fail(bag, gold, block)
	if int(bag.get(key, 0)) <= 0:
		return _fail(bag, gold, "bag")
	var tier := int(item.get("tier", item.get("level", 1)))
	var next_key := stack_key(base_id(key), plus + 1)
	if int(bag.get(next_key, 0)) >= stack_cap:
		return _fail(bag, gold, "full")
	var paid := _pay(bag, gold, upgrade_cost(tier, plus, tiers))
	if not bool(paid["ok"]):
		return paid
	var next: Dictionary = paid["inventory"]
	if int(next.get(key, 0)) <= 0:
		return _fail(bag, gold, "bag")
	next[key] = int(next[key]) - 1
	if int(next[key]) <= 0:
		next.erase(key)
	next[next_key] = int(next.get(next_key, 0)) + 1
	return {"ok": true, "reason": "", "inventory": next, "gold": int(paid["gold"]), "key": next_key}


static func apply_worn_upgrade(key: String, item: Dictionary, bag: Dictionary, gold: int, tiers: Dictionary) -> Dictionary:
	var plus := plus_of(key)
	var block := can_upgrade(item, plus)
	if block != "":
		return _fail(bag, gold, block)
	var tier := int(item.get("tier", item.get("level", 1)))
	var paid := _pay(bag, gold, upgrade_cost(tier, plus, tiers))
	if not bool(paid["ok"]):
		return paid
	return {
		"ok": true,
		"reason": "",
		"inventory": paid["inventory"],
		"gold": int(paid["gold"]),
		"key": stack_key(base_id(key), plus + 1),
	}


static func _pay(bag: Dictionary, gold: int, cost: Dictionary) -> Dictionary:
	var price := int(cost.get("gold", 0))
	if gold < price:
		return _fail(bag, gold, "gold")
	var materials: Dictionary = cost.get("materials", {})
	for mat_id in materials.keys():
		if int(bag.get(str(mat_id), 0)) < int(materials[mat_id]):
			return _fail(bag, gold, "material")
	var next := bag.duplicate()
	for mat_id in materials.keys():
		var key := str(mat_id)
		var left := int(next.get(key, 0)) - int(materials[mat_id])
		if left <= 0:
			next.erase(key)
		else:
			next[key] = left
	return {"ok": true, "reason": "", "inventory": next, "gold": gold - price}


static func _fail(bag: Dictionary, gold: int, reason: String) -> Dictionary:
	return {"ok": false, "reason": reason, "inventory": bag, "gold": gold, "key": ""}
