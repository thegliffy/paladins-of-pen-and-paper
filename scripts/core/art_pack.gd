extends Object
class_name ArtPack
## Production sprites from art_source/phase0. Paths and frames come from manifest.json.


const ROOT := "res://art_source/phase0/"
const Pack := preload("res://scripts/core/packed_file.gd")

const HAIR_RAMPS: Array = ["black", "brown", "blonde", "ginger", "white", "blue", "pink", "green"]
const OUTFIT_RAMPS: Array = ["white", "red", "blue", "purple", "green", "yellow", "brown", "dark"]
const HAIR_KEYS: Array = ["#46424e", "#6c6a76", "#9c9ca6", "#cfd0d4"]
const OUTFIT_KEYS: Array = ["#6c6a76", "#9c9ca6", "#cfd0d4"]
const SKIN_KEYS: Array = ["#ec5a44", "#8c5836", "#b27a4e", "#d89c72"]

const SEAT_BAR_INK := Color("120c18")
const SEAT_BAR_HP_EMPTY := Color("3e1016")
const SEAT_BAR_MP_EMPTY := Color("161c40")
const SEAT_BAR_GOLD := Color("fcf0a0")
const SEAT_BAR_GLYPH := Color("fcf0a0")

static var _manifest: Dictionary = {}
static var _textures: Dictionary = {}
static var _missing: Dictionary = {}
static var _baked: Dictionary = {}
static var _outlined: Dictionary = {}
static var _strips: Dictionary = {}


static func clear_bake_cache() -> void:
	_baked.clear()


static func manifest() -> Dictionary:
	if _manifest.is_empty():
		var parsed: Variant = Pack.json(ROOT + "manifest.json")
		if parsed is Dictionary:
			_manifest = parsed
		else:
			push_error("ArtPack manifest did not load")
	return _manifest


static func has(rel: String) -> bool:
	return Pack.exists(ROOT + rel)


static func texture(rel: String) -> Texture2D:
	if _textures.has(rel):
		return _textures[rel]
	if _missing.has(rel):
		return null
	var path := ROOT + rel
	if not has(rel):
		_missing[rel] = true
		push_error("ArtPack missing texture: %s" % path)
		return null
	var loaded: Texture2D = load(path)
	if loaded == null:
		_missing[rel] = true
		push_error("ArtPack failed to load texture: %s" % path)
		return null
	_textures[rel] = loaded
	return loaded


static func frame_texture(rel: String, frame: int, frame_size: Vector2) -> AtlasTexture:
	var atlas := AtlasTexture.new()
	atlas.atlas = texture(rel)
	atlas.region = Rect2(float(frame) * frame_size.x, 0, frame_size.x, frame_size.y)
	return atlas


static func vital_strip(kind: String, height: int, flash: int = 0) -> Texture2D:
	## Stretch the refined seat-bar tiles to a taller track. The bands are the
	## tile rows, repeated nearest-neighbour so a wider chair bar stays on palette.
	var key := "%s:%d:%d" % [kind, height, flash]
	if _strips.has(key):
		return _strips[key]
	var bands: Array[Color] = [Color("ec5a44"), Color("c02c2c"), Color("7c1c22")]
	if kind == "mp":
		bands = [Color("86c8f8"), Color("4c9ce8"), Color("3466cc")]
	elif flash == 1:
		bands = [Color("f6f6f2"), Color("fcf0a0"), Color("f09a2c")]
	var rows := maxi(1, height)
	var image := Image.create(1, rows, false, Image.FORMAT_RGBA8)
	var src_h := bands.size()
	for y in rows:
		var sy := mini(src_h - 1, int(float(y) * float(src_h) / float(rows)))
		image.set_pixel(0, y, bands[sy])
	var made := ImageTexture.create_from_image(image)
	_strips[key] = made
	return made


static func slot_file(state: String) -> String:
	if state == "passive":
		return "ui/skills/skill_slot_passive.png"
	if state == "locked":
		return "ui/skills/skill_slot_locked.png"
	if state == "selected":
		return "ui/skills/skill_slot_active.png"
	return "ui/skills/skill_slot.png"


static func skill_icon(skill: Dictionary) -> Texture2D:
	var name := str(skill.get("icon", ""))
	if name == "":
		return null
	return texture("ui/skills/%s.png" % name)


static func monster_sprite(monster_id: String) -> String:
	var rows: Variant = Pack.json("res://data/monsters.json")
	if rows is Array:
		for row in rows:
			if row is Dictionary and str(row.get("id", "")) == monster_id:
				var sprite := str(row.get("sprite", ""))
				if sprite != "":
					return sprite
	return "slime"


static func monster_frame(sprite: String, anim: String, frame: int) -> AtlasTexture:
	var info: Dictionary = manifest()["monsters"][sprite]
	var size_raw: Array = info["frame_size"]
	var size := Vector2(float(size_raw[0]), float(size_raw[1]))
	var count := int(info["anims"][anim]["frames"])
	var index := posmod(frame, maxi(1, count))
	return frame_texture("monsters/%s/%s_%s.png" % [sprite, sprite, anim], index, size)


static func monster_size(sprite: String) -> Vector2:
	var size_raw: Array = manifest()["monsters"][sprite]["frame_size"]
	return Vector2(float(size_raw[0]), float(size_raw[1]))


static func monster_feet(sprite: String) -> Vector2:
	var raw: Array = manifest()["monsters"][sprite]["feet_anchor"]
	return Vector2(float(raw[0]), float(raw[1]))


static func monster_hp_anchor(sprite: String) -> Vector2:
	var raw: Array = manifest()["monsters"][sprite]["hp_bar_anchor"]
	return Vector2(float(raw[0]), float(raw[1]))


static func monster_portrait(sprite: String) -> Texture2D:
	return texture("monsters/%s/%s_portrait.png" % [sprite, sprite])


static func default_look(class_id: String) -> Dictionary:
	var row: Dictionary = manifest()["classes"]["seat_defaults"][class_id]
	var look := {
		"skin": int(row["skin"]) - 1,
		"head": int(row["head"]) - 1,
		"hair": int(row["hair"]) - 1,
		"hair_color": HAIR_RAMPS.find(str(row["hair_color"])),
		"outfit_color": 0,
	}
	if row.get("outfit", null) != null:
		look["outfit_color"] = OUTFIT_RAMPS.find(str(row["outfit"]))
	return look


static func seat_is_default(class_id: String, look: Dictionary) -> bool:
	var defaults: Dictionary = manifest()["classes"]["seat_defaults"]
	if not defaults.has(class_id):
		return false
	var row: Dictionary = defaults[class_id]
	var skin := posmod(int(look.get("skin", 0)), 6) + 1
	var head := posmod(int(look.get("head", 0)), 6) + 1
	var hair := posmod(int(look.get("hair", 0)), 8) + 1
	if skin != int(row["skin"]) or head != int(row["head"]) or hair != int(row["hair"]):
		return false
	var hair_name: String = HAIR_RAMPS[posmod(int(look.get("hair_color", 0)), HAIR_RAMPS.size())]
	if hair_name != str(row["hair_color"]):
		return false
	if row.get("outfit", null) == null:
		return true
	var outfit: String = OUTFIT_RAMPS[posmod(int(look.get("outfit_color", 0)), OUTFIT_RAMPS.size())]
	return outfit == str(row["outfit"])


static func seat_idle(class_id: String, main_weapon: bool = false, main_tag: String = "") -> Texture2D:
	return texture(seat_sheet_rel(class_id, "seat_idle", main_weapon, main_tag))


static func seat_active(class_id: String, main_weapon: bool = false, main_tag: String = "") -> Texture2D:
	return texture(seat_sheet_rel(class_id, "seat_active", main_weapon, main_tag))


static func seat_sheet_rel(class_id: String, key: String, main_weapon: bool, main_tag: String = "") -> String:
	var entry := class_noweapon_entry(class_id)
	var state := "idle" if key == "seat_idle" else "active"
	if _ranger_no_quiver(class_id, main_weapon, main_tag):
		var bare := str(entry.get(key + "_nonbow", ""))
		if bare != "" and has(bare):
			return bare
		return "party/seat_ranger_%s_noweapon_noquiver.png" % state
	if main_weapon:
		var rel := str(entry.get(key, ""))
		if rel != "" and has(rel):
			return rel
	return "party/seat_%s_%s.png" % [class_id, state]


static func map_pin_anchor() -> Vector2:
	var raw: Array = manifest()["map_pins"]["anchor"]
	return Vector2(float(raw[0]), float(raw[1]))


static func icon_is_placeholder(tex: Texture2D) -> bool:
	## The old item icons were a parchment square with a #5a4028 frame.
	if tex == null:
		return true
	var image := tex.get_image()
	if image == null or image.get_width() != 16 or image.get_height() != 16:
		return true
	var border := Color("5a4028")
	var hits := 0
	for i in 16:
		for point in [Vector2i(i, 0), Vector2i(i, 15), Vector2i(0, i), Vector2i(15, i)]:
			var px := image.get_pixel(point.x, point.y)
			if px.a > 0.7 and absf(px.r - border.r) < 0.05 and absf(px.g - border.g) < 0.05 and absf(px.b - border.b) < 0.06:
				hits += 1
	return hits >= 52


static func _ranger_no_quiver(class_id: String, main_weapon: bool, main_tag: String) -> bool:
	## No main hand keeps the baked bow and quiver. A bow keeps the quiver.
	## Any other main-hand tag drops both. An empty tag is the older armed
	## lookup and stays on the quiver layer until a real tag is passed.
	if class_id != "ranger" or not main_weapon or main_tag == "":
		return false
	var rule: Dictionary = manifest()["paperdoll"].get("ranger_quiver", {})
	var bows: Array = rule.get("bow_tags", ["bow"])
	return not bows.has(main_tag)


static func class_noweapon_entry(class_id: String) -> Dictionary:
	var block: Dictionary = manifest()["paperdoll"].get("class_noweapon", {})
	var classes: Dictionary = block.get("classes", {})
	if classes.has(class_id):
		return classes[class_id]
	return {}


static func gold_outline(source: Texture2D) -> Texture2D:
	if source == null:
		return null
	if _outlined.has(source):
		return _outlined[source]
	var image := source.get_image()
	if image == null:
		return source
	image = image.duplicate()
	var copy := image.duplicate()
	var gold := Color("f8d040")
	var w := image.get_width()
	var h := image.get_height()
	for y in h:
		for x in w:
			if image.get_pixel(x, y).a > 0.5:
				continue
			var edge := false
			if x > 0 and image.get_pixel(x - 1, y).a > 0.5:
				edge = true
			elif x + 1 < w and image.get_pixel(x + 1, y).a > 0.5:
				edge = true
			elif y > 0 and image.get_pixel(x, y - 1).a > 0.5:
				edge = true
			elif y + 1 < h and image.get_pixel(x, y + 1).a > 0.5:
				edge = true
			if edge:
				copy.set_pixel(x, y, gold)
	var baked := ImageTexture.create_from_image(copy)
	_outlined[source] = baked
	return baked


static func front_portrait(look: Dictionary, class_id: String) -> Image:
	var doll := compose_doll("front", look, class_id)
	var image := doll.get_image()
	if image == null:
		return Image.create(20, 20, false, Image.FORMAT_RGBA8)
	return image.get_region(Rect2i(6, 8, 20, 20))


static func nine_slice(rel: String, left: int, top: int, right: int, bottom: int) -> StyleBoxTexture:
	var box := StyleBoxTexture.new()
	box.texture = texture(rel)
	box.texture_margin_left = left
	box.texture_margin_right = right
	box.texture_margin_top = top
	box.texture_margin_bottom = bottom
	box.axis_stretch_horizontal = StyleBoxTexture.AXIS_STRETCH_MODE_TILE
	box.axis_stretch_vertical = StyleBoxTexture.AXIS_STRETCH_MODE_TILE
	return box


static func front_anchor() -> Vector2:
	var raw: Array = manifest()["paperdoll"]["front"]["anchor"]
	return Vector2(float(raw[0]), float(raw[1]))


static func back_anchor() -> Vector2:
	var raw: Array = manifest()["paperdoll"]["seat_recipe"]["anchor"]
	return Vector2(float(raw[0]), float(raw[1]))


static func doll_canvas(face: String) -> Vector2:
	var block: Dictionary = manifest()["paperdoll"]["front"] if face == "front" else manifest()["paperdoll"]["seat_recipe"]
	var raw: Array = block["canvas"]
	return Vector2(float(raw[0]), float(raw[1]))


static func seat_gear_order() -> PackedStringArray:
	return PackedStringArray(["body", "outfit", "class", "armor", "hair", "hat", "off", "main", "chair"])


static func recipe_gear_order() -> PackedStringArray:
	var steps: Array = manifest()["paperdoll"]["seat_recipe"]["steps_with_gear"]
	var order := PackedStringArray()
	for step in steps:
		var text := str(step)
		if text.begins_with("ACTIVE"):
			continue
		var token := ""
		if text.find("chair_back") >= 0:
			token = "chair"
		elif text.find("OFF HAND") >= 0:
			token = "off"
		elif text.find("MAIN HAND") >= 0:
			token = "main"
		elif text.find("ARMOR") >= 0:
			token = "armor"
		elif text.find("hair_back") >= 0:
			token = "hair"
		elif text.find("_hat") >= 0:
			token = "hat"
		elif text.find("outfit") >= 0:
			token = "outfit"
		elif text.find("body_back") >= 0:
			token = "body"
		elif text.find("class_back") >= 0:
			token = "class"
		if token != "":
			order.append(token)
	return order


static func class_noweapon_rel(class_id: String) -> String:
	return str(class_noweapon_entry(class_id).get("layer", ""))


static func pick_class_back(class_id: String, main_weapon: bool, noweapon_present: bool, main_tag: String = "") -> String:
	if _ranger_no_quiver(class_id, main_weapon, main_tag):
		var nonbow := str(class_noweapon_entry(class_id).get("layer_nonbow", ""))
		if nonbow != "":
			return nonbow
		return "paperdoll/back/class_back_ranger_noweapon_noquiver.png"
	if main_weapon and noweapon_present:
		var listed := class_noweapon_rel(class_id)
		if listed != "":
			return listed
		return "paperdoll/back/class_back_%s_noweapon.png" % class_id
	return "paperdoll/back/class_back_%s.png" % class_id


static func class_back_rel(class_id: String, main_weapon: bool, main_tag: String = "") -> String:
	## Cleric and rogue are absent from paperdoll.class_noweapon, so they keep the normal layer.
	var bare := class_noweapon_rel(class_id)
	if bare == "":
		return "paperdoll/back/class_back_%s.png" % class_id
	return pick_class_back(class_id, main_weapon, has(bare), main_tag)


static func offhand_flips(item: Dictionary) -> bool:
	## One-handed weapons are painted for the right hand. Shields and orbs already face the left arm.
	var tag := str(item.get("tag", ""))
	if tag == "shield" or tag == "orb":
		return false
	if str(item.get("slot", "")) != "weapon":
		return false
	return int(item.get("hands", 1)) < 2


static func seat_blit_plan(class_id: String, gear: Dictionary) -> Array:
	var steps: Array = []
	var two := bool(gear.get("two_hand", false))
	var main_weapon := bool(gear.get("main_weapon", false))
	var main_tag := str(gear.get("main_tag", ""))
	steps.append({"id": "body", "kind": "body"})
	if class_id != "barbarian":
		steps.append({"id": "outfit", "kind": "outfit"})
	steps.append({"id": "class", "kind": "blit", "path": class_back_rel(class_id, main_weapon, main_tag)})
	var armor := str(gear.get("armor", ""))
	if armor != "":
		steps.append({"id": "armor", "kind": "gear", "path": armor, "flip": false})
	steps.append({"id": "hair", "kind": "hair"})
	steps.append({"id": "hat", "kind": "hat"})
	if not two:
		var off := str(gear.get("off", ""))
		if off != "":
			steps.append({"id": "off", "kind": "gear", "path": off, "flip": bool(gear.get("off_flip", false))})
	var main := str(gear.get("main", ""))
	if main != "":
		steps.append({"id": "main", "kind": "gear", "path": main, "flip": false})
	steps.append({"id": "chair", "kind": "blit", "path": "paperdoll/back/chair_back.png"})
	return steps


static func gear_image(rel: String, flip_h: bool) -> Image:
	if rel == "" or not has(rel):
		return Image.create(1, 1, false, Image.FORMAT_RGBA8)
	var source := texture(rel)
	if source == null or source.get_image() == null:
		return Image.create(1, 1, false, Image.FORMAT_RGBA8)
	var image := source.get_image()
	if flip_h:
		image = image.duplicate()
		image.flip_x()
	return image


static func compose_doll(face: String, look: Dictionary, class_id: String, gear: Dictionary = {}) -> Texture2D:
	var skin := posmod(int(look.get("skin", 0)), 6) + 1
	var head := posmod(int(look.get("head", 0)), 6) + 1
	var hair := posmod(int(look.get("hair", 0)), 8) + 1
	var outfit: String = OUTFIT_RAMPS[posmod(int(look.get("outfit_color", 0)), OUTFIT_RAMPS.size())]
	var hair_name: String = HAIR_RAMPS[posmod(int(look.get("hair_color", 0)), HAIR_RAMPS.size())]
	var gear_key := ""
	if face != "front" and not gear.is_empty():
		gear_key = "|%s|%s|%s|%s|%s|%s|%s" % [
			str(gear.get("armor", "")),
			str(gear.get("off", "")),
			str(bool(gear.get("off_flip", false))),
			str(gear.get("main", "")),
			str(bool(gear.get("main_weapon", false))),
			str(bool(gear.get("two_hand", false))),
			str(gear.get("main_tag", "")),
		]
	var key := "%s|%s|%d|%d|%d|%s|%s%s" % [face, class_id, skin, head, hair, outfit, hair_name, gear_key]
	if _baked.has(key):
		return _baked[key]
	var canvas := doll_canvas(face)
	var image := Image.create(int(canvas.x), int(canvas.y), false, Image.FORMAT_RGBA8)
	image.fill(Color(0, 0, 0, 0))
	if face == "front":
		_blit(image, "paperdoll/body_skin_%d.png" % skin)
		if class_id != "barbarian":
			_blit_image(image, _tinted("paperdoll/outfit_base.png", OUTFIT_KEYS, _ramp("outfit_ramps", outfit)))
		_blit(image, "paperdoll/class_%s.png" % class_id)
		_blit_image(image, _tinted("paperdoll/head_%d.png" % head, SKIN_KEYS, _skin_colors(skin)))
		var hat := "paperdoll/class_%s_hat.png" % class_id
		var hair_img := _tinted("paperdoll/hair_%d.png" % hair, HAIR_KEYS, _ramp("hair_ramps", hair_name))
		if has(hat):
			_clip_under_hat(hair_img, hat)
		_blit_image(image, hair_img)
		_blit(image, hat)
	else:
		var hat_back := "paperdoll/back/class_back_%s_hat.png" % class_id
		for step in seat_blit_plan(class_id, gear):
			match str(step["kind"]):
				"body":
					_blit(image, "paperdoll/back/body_back_skin_%d.png" % skin)
				"outfit":
					_blit_image(image, _tinted("paperdoll/back/outfit_back.png", OUTFIT_KEYS, _ramp("outfit_ramps", outfit)))
				"blit":
					_blit(image, str(step["path"]))
				"gear":
					_blit_gear(image, str(step["path"]), bool(step.get("flip", false)))
				"hair":
					var hair_img := _tinted("paperdoll/back/hair_back_%d.png" % hair, HAIR_KEYS, _ramp("hair_ramps", hair_name))
					if has(hat_back):
						_clip_under_hat(hair_img, hat_back)
					_blit_image(image, hair_img)
				"hat":
					_blit(image, hat_back)
	var baked := ImageTexture.create_from_image(image)
	_baked[key] = baked
	return baked


static func _ramp(table: String, name: String) -> Array:
	var rows: Dictionary = manifest()["paperdoll"][table]
	return rows[name]


static func _skin_colors(tone: int) -> Array:
	var tones: Array = manifest()["paperdoll"]["skin_tones"]
	var row: Dictionary = tones[clampi(tone, 1, tones.size()) - 1]
	return [row["blush"], row["detail"], row["shadow"], row["base"]]


static func _tinted(rel: String, keys: Array, colors: Array) -> Image:
	var source := texture(rel)
	if source == null:
		return Image.create(1, 1, false, Image.FORMAT_RGBA8)
	var image := source.get_image()
	if image == null:
		return Image.create(1, 1, false, Image.FORMAT_RGBA8)
	image = image.duplicate()
	var key_colors: Array[Color] = []
	for key in keys:
		key_colors.append(Color(str(key)))
	var dest: Array[Color] = []
	for color in colors:
		dest.append(Color(str(color)))
	for y in image.get_height():
		for x in image.get_width():
			var px := image.get_pixel(x, y)
			if px.a < 0.5:
				continue
			for i in key_colors.size():
				var key: Color = key_colors[i]
				var delta := Vector3(px.r, px.g, px.b).distance_to(Vector3(key.r, key.g, key.b))
				if delta < 0.04:
					var next: Color = dest[i]
					next.a = px.a
					image.set_pixel(x, y, next)
					break
	return image


static func _clip_under_hat(hair: Image, hat_rel: String) -> void:
	var hat := texture(hat_rel)
	if hat == null:
		return
	var hat_img := hat.get_image()
	if hat_img == null:
		return
	var clip_y := hat_img.get_height()
	for y in hat_img.get_height():
		for x in hat_img.get_width():
			if hat_img.get_pixel(x, y).a > 0.5:
				clip_y = mini(clip_y, y)
				break
	for y in mini(clip_y, hair.get_height()):
		for x in hair.get_width():
			var px := hair.get_pixel(x, y)
			px.a = 0.0
			hair.set_pixel(x, y, px)


static func _blit(dest: Image, rel: String) -> void:
	if not has(rel):
		return
	var source := texture(rel)
	if source == null or source.get_image() == null:
		return
	_blit_image(dest, source.get_image())


static func _blit_gear(dest: Image, rel: String, flip_h: bool) -> void:
	var image := gear_image(rel, flip_h)
	if image.get_width() <= 1 and image.get_height() <= 1:
		return
	_blit_image(dest, image)


static func _blit_image(dest: Image, source: Image) -> void:
	if source.get_width() <= 1 and source.get_height() <= 1:
		return
	dest.blend_rect(source, Rect2i(0, 0, source.get_width(), source.get_height()), Vector2i.ZERO)
