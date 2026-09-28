extends Object
class_name ArtPack
## Production sprites from art_source/phase0. Paths and frames come from manifest.json.


const ROOT := "res://art_source/phase0/"

const HAIR_RAMPS: Array = ["black", "brown", "blonde", "ginger", "white", "blue", "pink", "green"]
const OUTFIT_RAMPS: Array = ["white", "red", "blue", "purple", "green", "yellow", "brown", "dark"]
const HAIR_KEYS: Array = ["#46424e", "#6c6a76", "#9c9ca6", "#cfd0d4"]
const OUTFIT_KEYS: Array = ["#6c6a76", "#9c9ca6", "#cfd0d4"]
const SKIN_KEYS: Array = ["#ec5a44", "#8c5836", "#b27a4e", "#d89c72"]

static var _manifest: Dictionary = {}
static var _textures: Dictionary = {}
static var _baked: Dictionary = {}
static var _outlined: Dictionary = {}


static func manifest() -> Dictionary:
	if _manifest.is_empty():
		_manifest = JSON.parse_string(FileAccess.get_file_as_string(ROOT + "manifest.json"))
	return _manifest


static func has(rel: String) -> bool:
	return FileAccess.file_exists(ROOT + rel)


static func texture(rel: String) -> Texture2D:
	if _textures.has(rel):
		return _textures[rel]
	if not has(rel):
		return null
	var loaded: Texture2D = load(ROOT + rel)
	_textures[rel] = loaded
	return loaded


static func frame_texture(rel: String, frame: int, frame_size: Vector2) -> AtlasTexture:
	var atlas := AtlasTexture.new()
	atlas.atlas = texture(rel)
	atlas.region = Rect2(float(frame) * frame_size.x, 0, frame_size.x, frame_size.y)
	return atlas


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
	var rows: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://data/monsters.json"))
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


static func seat_idle(class_id: String) -> Texture2D:
	return texture("party/seat_%s_idle.png" % class_id)


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


static func compose_doll(face: String, look: Dictionary, class_id: String) -> Texture2D:
	var skin := posmod(int(look.get("skin", 0)), 6) + 1
	var head := posmod(int(look.get("head", 0)), 6) + 1
	var hair := posmod(int(look.get("hair", 0)), 8) + 1
	var outfit: String = OUTFIT_RAMPS[posmod(int(look.get("outfit_color", 0)), OUTFIT_RAMPS.size())]
	var hair_name: String = HAIR_RAMPS[posmod(int(look.get("hair_color", 0)), HAIR_RAMPS.size())]
	var key := "%s|%s|%d|%d|%d|%s|%s" % [face, class_id, skin, head, hair, outfit, hair_name]
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
		_blit(image, "paperdoll/back/body_back_skin_%d.png" % skin)
		if class_id != "barbarian":
			_blit_image(image, _tinted("paperdoll/back/outfit_back.png", OUTFIT_KEYS, _ramp("outfit_ramps", outfit)))
		_blit(image, "paperdoll/back/class_back_%s.png" % class_id)
		var hat_back := "paperdoll/back/class_back_%s_hat.png" % class_id
		var hair_img := _tinted("paperdoll/back/hair_back_%d.png" % hair, HAIR_KEYS, _ramp("hair_ramps", hair_name))
		if has(hat_back):
			_clip_under_hat(hair_img, hat_back)
		_blit_image(image, hair_img)
		_blit(image, hat_back)
		_blit(image, "paperdoll/back/chair_back.png")
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


static func _blit_image(dest: Image, source: Image) -> void:
	if source.get_width() <= 1 and source.get_height() <= 1:
		return
	dest.blend_rect(source, Rect2i(0, 0, source.get_width(), source.get_height()), Vector2i.ZERO)
