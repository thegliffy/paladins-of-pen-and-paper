extends Object
class_name LevelRules
## The required pick when a hero gains a level. Pure: no autoloads.


const SKILL_CAP := 3
const HP_PCT := 0.08
const MP_PCT := 0.08
const CRIT := 3.0
const THREAT := 1
const MANA_RELIEF := 20
const POWER_STEP := 0.08


static func blank() -> Dictionary:
	return {
		"body": 0,
		"senses": 0,
		"mind": 0,
		"hp_pct": 0.0,
		"mp_pct": 0.0,
		"crit": 0.0,
		"threat": 0,
		"skills": {},
	}


static func read(member: Dictionary) -> Dictionary:
	return normalize(member.get("growth", {}))


static func normalize(raw: Dictionary) -> Dictionary:
	var growth := blank()
	growth["body"] = maxi(0, int(raw.get("body", 0)))
	growth["senses"] = maxi(0, int(raw.get("senses", 0)))
	growth["mind"] = maxi(0, int(raw.get("mind", 0)))
	growth["hp_pct"] = maxf(0.0, float(raw.get("hp_pct", 0.0)))
	growth["mp_pct"] = maxf(0.0, float(raw.get("mp_pct", 0.0)))
	growth["crit"] = maxf(0.0, float(raw.get("crit", 0.0)))
	growth["threat"] = maxi(0, int(raw.get("threat", 0)))
	var skills: Dictionary = raw.get("skills", {})
	var kept := {}
	for skill_id in skills.keys():
		kept[str(skill_id)] = clampi(int(skills[skill_id]), 0, SKILL_CAP)
	growth["skills"] = kept
	return growth


static func choice_rank(member: Dictionary, skill_id: String) -> int:
	return int(read(member)["skills"].get(skill_id, 0))


static func tune_skill(skill: Dictionary, extra: int) -> Dictionary:
	var copy := skill.duplicate(true)
	var steps := maxi(0, extra)
	copy["mp_relief"] = steps * MANA_RELIEF
	copy["cd_relief"] = steps
	copy["hp_relief"] = steps
	copy["power_extra"] = steps
	return copy


static func offers(member: Dictionary, skills: Array) -> Array:
	var growth := read(member)
	var level := maxi(1, int(member.get("level", 1)))
	var rankable: Array = []
	for skill in skills:
		if typeof(skill) != TYPE_DICTIONARY:
			continue
		if str(skill.get("type", "active")) == "passive":
			continue
		var skill_id := str(skill.get("id", ""))
		if skill_id == "":
			continue
		if int(growth["skills"].get(skill_id, 0)) < SKILL_CAP:
			rankable.append(skill)
	var stats := ["body", "senses", "mind"]
	var perks := ["hp_pct", "mp_pct", "crit", "threat"]
	var picked: Array = []
	if not rankable.is_empty():
		picked.append(_skill_option(rankable[level % rankable.size()], growth))
	picked.append(_stat_option(stats[level % stats.size()]))
	picked.append(_perk_option(perks[level % perks.size()]))
	if picked.size() < 3:
		picked.append(_stat_option(stats[(level + 1) % stats.size()]))
	var unique: Array = []
	var seen := {}
	for option in picked:
		var option_id := str(option.get("id", ""))
		if seen.has(option_id):
			continue
		seen[option_id] = true
		unique.append(option)
	var extra := 0
	while unique.size() < 3 and extra < stats.size():
		var option := _stat_option(stats[(level + 1 + extra) % stats.size()])
		extra += 1
		if seen.has(str(option["id"])):
			continue
		seen[str(option["id"])] = true
		unique.append(option)
	return unique.slice(0, 3)


static func apply(member: Dictionary, option: Dictionary) -> bool:
	var growth := read(member)
	var kind := str(option.get("kind", ""))
	if kind == "stat":
		var stat := str(option.get("stat", ""))
		if not growth.has(stat):
			return false
		growth[stat] = int(growth[stat]) + 1
	elif kind == "skill":
		var skill_id := str(option.get("skill", ""))
		if skill_id == "":
			return false
		var next := int(growth["skills"].get(skill_id, 0)) + 1
		if next > SKILL_CAP:
			return false
		growth["skills"][skill_id] = next
	elif kind == "perk":
		var perk := str(option.get("perk", ""))
		if perk == "hp_pct":
			growth["hp_pct"] = float(growth["hp_pct"]) + HP_PCT
		elif perk == "mp_pct":
			growth["mp_pct"] = float(growth["mp_pct"]) + MP_PCT
		elif perk == "crit":
			growth["crit"] = float(growth["crit"]) + CRIT
		elif perk == "threat":
			growth["threat"] = int(growth["threat"]) + THREAT
		else:
			return false
	else:
		return false
	member["growth"] = growth
	return true


static func enqueue(queue: Array, member_index: int, levels: int) -> Array:
	var next: Array = queue.duplicate()
	for _i in maxi(0, levels):
		next.append(member_index)
	return next


static func commit(queue: Array, member: Dictionary, skills: Array, option_id: String) -> Dictionary:
	if queue.is_empty():
		return {"ok": false, "reason": "none", "queue": queue}
	var match := {}
	for option in offers(member, skills):
		if str(option.get("id", "")) == option_id:
			match = option
			break
	if match.is_empty():
		return {"ok": false, "reason": "choice", "queue": queue}
	if not apply(member, match):
		return {"ok": false, "reason": "choice", "queue": queue}
	var rest: Array = queue.duplicate()
	rest.pop_front()
	return {"ok": true, "reason": "", "queue": rest, "option": match}


static func sheet_line(member: Dictionary, names: Dictionary) -> String:
	var growth := read(member)
	var parts: PackedStringArray = []
	if int(growth["body"]) > 0:
		parts.append("Body +%d" % int(growth["body"]))
	if int(growth["senses"]) > 0:
		parts.append("Senses +%d" % int(growth["senses"]))
	if int(growth["mind"]) > 0:
		parts.append("Mind +%d" % int(growth["mind"]))
	var skills: Dictionary = growth["skills"]
	var ids: Array = skills.keys()
	ids.sort()
	for skill_id in ids:
		var rank := int(skills[skill_id])
		if rank <= 0:
			continue
		parts.append("%s +%d" % [str(names.get(str(skill_id), skill_id)), rank])
	if float(growth["hp_pct"]) > 0.0:
		parts.append("Health +%d%%" % int(round(float(growth["hp_pct"]) * 100.0)))
	if float(growth["mp_pct"]) > 0.0:
		parts.append("Energy +%d%%" % int(round(float(growth["mp_pct"]) * 100.0)))
	if float(growth["crit"]) > 0.0:
		parts.append("Crit +%d" % int(round(float(growth["crit"]))))
	if int(growth["threat"]) > 0:
		parts.append("Threat +%d" % int(growth["threat"]))
	if parts.is_empty():
		return ""
	return "Grown: %s" % ", ".join(parts)


static func _skill_option(skill: Dictionary, growth: Dictionary) -> Dictionary:
	var skill_id := str(skill.get("id", ""))
	var next := int(growth["skills"].get(skill_id, 0)) + 1
	return {
		"id": "skill_%s" % skill_id,
		"kind": "skill",
		"skill": skill_id,
		"title": "%s +%d" % [str(skill.get("name", "Skill")), next],
		"detail": "The trick hits harder. Mana, health, or the wait between uses drops.",
	}


static func _stat_option(stat: String) -> Dictionary:
	var titles := {"body": "+1 Body", "senses": "+1 Senses", "mind": "+1 Mind"}
	var details := {
		"body": "The arm remembers. Attack and health both climb.",
		"senses": "The eye sharpens. Blows find the seam more often.",
		"mind": "The thought holds. Energy and spells sit deeper.",
	}
	return {
		"id": "stat_%s" % stat,
		"kind": "stat",
		"stat": stat,
		"title": str(titles.get(stat, "+1")),
		"detail": str(details.get(stat, "")),
	}


static func _perk_option(perk: String) -> Dictionary:
	if perk == "hp_pct":
		return {"id": "perk_hp", "kind": "perk", "perk": "hp_pct", "title": "+8% health", "detail": "The chair holds a wider pool."}
	if perk == "mp_pct":
		return {"id": "perk_mp", "kind": "perk", "perk": "mp_pct", "title": "+8% energy", "detail": "The well of energy sits deeper."}
	if perk == "crit":
		return {"id": "perk_crit", "kind": "perk", "perk": "crit", "title": "+3 crit", "detail": "A nick finds the seam more often."}
	return {"id": "perk_threat", "kind": "perk", "perk": "threat", "title": "+1 threat", "detail": "Foes look at this hero first."}
