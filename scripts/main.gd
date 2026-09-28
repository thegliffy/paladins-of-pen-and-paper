extends Control

const TouchSuite := preload("res://tests/touch_suite.gd")

var screen: Node
var _busy := false


func _ready() -> void:
	# Letterbox outside the 270×480 viewport uses the canvas clear color.
	RenderingServer.set_default_clear_color(Color(0.12, 0.08, 0.05, 1))
	Layout.setup()
	_apply_theme()
	if OS.get_cmdline_user_args().has("--export-check"):
		await _export_check()
		return
	if OS.get_cmdline_user_args().has("--touch-check"):
		var touch_code: int = await TouchSuite.run(self)
		get_tree().quit(touch_code)
		return
	if OS.get_cmdline_user_args().has("--shots"):
		await _shots()
		get_tree().quit()
		return
	_show_title()


func _apply_theme() -> void:
	var theme := Theme.new()
	var font := load("res://art/fonts/m5x7.ttf") as FontFile
	if font:
		font = font.duplicate() as FontFile
		font.antialiasing = TextServer.FONT_ANTIALIASING_NONE
		theme.default_font = font
	theme.default_font_size = Layout.font_size()
	self.theme = theme


func _show_title() -> void:
	var title := TitleScreen.new()
	await _swap(title)
	title.new_game.connect(_show_creator)
	title.continue_game.connect(_continue)


func _show_creator() -> void:
	var creator := CreatorScreen.new()
	await _swap(creator)
	creator.finished.connect(_begin_campaign)
	creator.cancelled.connect(_show_title)


func _begin_campaign(members: Array) -> void:
	GameState.new_campaign(members)
	await _open_hub(true)


func _continue() -> void:
	if GameState.load_game():
		await _open_hub(false)
	else:
		_show_title()


func _open_hub(banner: bool) -> void:
	var session := SessionScreen.new()
	await _swap(session)
	session.action_pressed.connect(_on_hub_action)
	if banner:
		var place: Dictionary = ContentDB.place(GameState.place_id)
		session.location_banner(place["name"])


func _on_hub_action(action: String) -> void:
	if not screen is SessionScreen:
		return
	var session := screen as SessionScreen
	match action:
		"travel":
			if _busy:
				return
			_open_map()
		"fight":
			if _busy:
				return
			_busy = true
			await _open_builder(session)
			_busy = false
		"rest":
			if _busy:
				return
			_busy = true
			await _rest(session)
			_busy = false
		"quest":
			session.open_quest()
		"party":
			session.open_party()


func _open_map() -> void:
	var map := MapScreen.new()
	await _swap(map)
	map.closed.connect(func(): _open_hub(false))
	map.arrived.connect(_on_arrived)


func _on_arrived(place_id: String, ambush: bool) -> void:
	if ambush:
		var span := Formulas.travel_p(int(ContentDB.place(place_id)["level"]), GameState.party_average())
		var difficulty := float(randi_range(1, 5)) / 10.0
		await _start_battle(difficulty, "ambush")
		if screen is SessionScreen:
			(screen as SessionScreen).set_caption("The road bit back. p was %d." % span)
	else:
		await _open_hub(true)


func _open_builder(session: SessionScreen) -> void:
	var builder := BattleBuilder.new()
	builder.setup(GameState.place_id)
	session.add_child(builder)
	builder.set_anchors_preset(Control.PRESET_FULL_RECT)
	builder.offset_left = 0
	builder.offset_top = 0
	builder.offset_right = 0
	builder.offset_bottom = 0
	var rows: Array = await builder.closed
	if is_instance_valid(builder):
		builder.queue_free()
	if rows.is_empty():
		return
	await _start_battle_rows(rows, "patrol")


func _start_battle(difficulty: float, kind: String) -> void:
	var place: Dictionary = ContentDB.place(GameState.place_id)
	var pool: Array = []
	for monster_id in place.get("monsters", []):
		var monster: Dictionary = ContentDB.monster(str(monster_id))
		pool.append({"id": str(monster_id), "power": int(monster["power"])})
	if pool.is_empty():
		return
	var picks: Array = []
	for _i in 16:
		picks.append(randi())
	var alive := maxi(1, GameState.living_members().size())
	var rows: Array = Formulas.compose_encounter(pool, Formulas.encounter_target_power(GameState.party_power(), difficulty, alive), picks)
	await _start_battle_rows(rows, kind)


func _start_battle_rows(rows: Array, kind: String) -> void:
	if rows.is_empty():
		return
	GameState.arm_battle()
	var session := SessionScreen.new()
	await _swap(session)
	session.action_pressed.connect(_on_hub_action)
	var flow := BattleFlow.new()
	flow.view = session
	session.add_child(flow)
	await flow.start(rows, kind)
	flow.queue_free()
	session.show_hub()


func _rest(session: SessionScreen) -> void:
	var place: Dictionary = ContentDB.place(GameState.place_id)
	if bool(place.get("has_inn", false)):
		session.set_caption("The inn kettle is on.")
		await _heal_ticks(session, 10)
		return
	var living: Array = []
	for index in GameState.party.size():
		var member: Dictionary = GameState.party[index]
		if int(member["hp"]) <= 0:
			continue
		var stats := GameState.combat_stats(member)
		living.append({"name": ContentDB.persona(str(member["persona"]))["name"], "senses": stats["senses"]})
	session.open_dice(living.size(), "senses")
	var all_fail := true
	for i in living.size():
		var stat := int(living[i]["senses"])
		session.set_die(i, "%d-20" % Formulas.party_die_target(stat), "", -1)
		await get_tree().create_timer(Timing.PARTY_DIE_SPIN).timeout
		var roll := randi_range(1, 20)
		var ok := Formulas.party_die_succeeds(roll, stat, 0)
		session.set_die(i, "OK!" if ok else "MISS", str(roll), 1 if ok else 0)
		if ok:
			all_fail = false
		await get_tree().create_timer(Timing.PARTY_DIE_GAP).timeout
	await get_tree().create_timer(Timing.PARTY_ROLL_END_HOLD).timeout
	session.close_dice()
	if all_fail and not living.is_empty():
		session.set_caption("Something finds the camp.")
		await _start_battle(float(ContentDB.encounters["difficulties"]["wild_rest_ambush"]), "ambush")
		return
	session.set_caption("A short rest on the grass.")
	await _heal_ticks(session, 7)


func _heal_ticks(session: SessionScreen, count: int) -> void:
	for _tick in count:
		for member in GameState.party:
			var stats := GameState.combat_stats(member)
			member["hp"] = mini(int(stats["max_hp"]), int(member["hp"]) + maxi(1, int(float(stats["max_hp"]) * 0.1)))
			member["mp"] = mini(int(stats["max_mp"]), int(member["mp"]) + maxi(1, int(float(stats["max_mp"]) * 0.1)))
		session._sync_party()
		await get_tree().create_timer(0.12).timeout
	GameState.save_game()
	session.show_hub()


func _patrol_difficulty() -> float:
	return float(ContentDB.encounters["difficulties"]["patrol"])


func _swap(next: Control) -> void:
	if screen and is_instance_valid(screen):
		var old := screen
		screen = null
		old.queue_free()
		await get_tree().process_frame
	screen = next
	add_child(next)
	next.set_anchors_preset(Control.PRESET_FULL_RECT)
	next.offset_left = 0
	next.offset_top = 0
	next.offset_right = 0
	next.offset_bottom = 0


func _export_check() -> void:
	# Runs inside an exported PCK. The project directory must not be on res://.
	var failures: Array[String] = []
	var grass_path := "res://art_source/phase0/map/tile_grass.png"
	var old_gate := FileAccess.file_exists(grass_path)
	var resource_gate := ResourceLoader.exists(grass_path)
	print("EXPORT_GRASS_FILE_EXISTS %s" % old_gate)
	print("EXPORT_GRASS_RESOURCE_EXISTS %s" % resource_gate)
	var isolated := not FileAccess.file_exists("res://tools/check_export.sh")
	print("EXPORT_ISOLATED %s" % isolated)
	if not isolated:
		failures.append("not_isolated")
	if ContentDB.places.is_empty():
		failures.append("places_json")
		push_error("Export check: region places did not load")
	if ArtPack.manifest().is_empty():
		failures.append("manifest")
		push_error("Export check: manifest did not load")
	if not _texture_ok(ArtPack.texture("map/tile_grass.png")):
		failures.append("tile_grass")
	if not _texture_ok(ArtPack.texture("ui/portrait/action_bar_v2.png")):
		failures.append("action_bar")
	if not _texture_ok(ArtPack.texture("ui/skills/paladin_1.png")):
		failures.append("skill_icon")
	if not _texture_ok(ArtPack.texture("combat/bg_forest_portrait.png")):
		failures.append("combat_bg")
	if not _texture_ok(ArtPack.texture("party/seat_paladin_idle.png")):
		failures.append("seat")
	if not _texture_ok(SpriteCatalog.background("meadow")):
		failures.append("title_bg")
	if not _texture_ok(SpriteCatalog.ui("icon_die")):
		failures.append("ui_icon")
	var tap: AudioStream = load("res://art/sfx/tap.wav")
	if tap == null:
		failures.append("sfx")
		push_error("Export check: tap sfx did not load")
	var classes: Dictionary = ArtPack.manifest().get("classes", {})
	var defaults: Dictionary = classes.get("seat_defaults", {})
	if defaults.has("paladin"):
		var doll := ArtPack.compose_doll("front", ArtPack.default_look("paladin"), "paladin")
		if _opaque_pixels(doll) < 20:
			failures.append("doll")
			push_error("Export check: creator doll baked empty")
	else:
		failures.append("doll")
		push_error("Export check: paladin seat defaults missing")
	var map := MapScreen.new()
	map.stage_preview()
	await _swap(map)
	map.queue_redraw()
	var content := map.get_node_or_null("Clip/Content")
	if content is CanvasItem:
		(content as CanvasItem).queue_redraw()
	await _capture("map_exported")
	var nodes := map.place_node_count()
	print("EXPORT_MAP_NODES %d" % nodes)
	if nodes <= 0:
		failures.append("map_nodes")
		push_error("Export check: map spawned 0 place nodes")
	if not map.backdrop_ready():
		failures.append("backdrop")
		push_error("Export check: map backdrop texture missing")
	if failures.is_empty():
		print("EXPORT_CHECK_OK")
		get_tree().quit(0)
	else:
		push_error("EXPORT_CHECK_FAIL %s" % ", ".join(failures))
		get_tree().quit(1)


func _texture_ok(tex: Texture2D) -> bool:
	return tex != null and tex.get_width() > 0 and tex.get_height() > 0


func _opaque_pixels(tex: Texture2D) -> int:
	if tex == null:
		return 0
	var image := tex.get_image()
	if image == null:
		push_error("Export check: texture get_image() returned null")
		return 0
	var count := 0
	for y in image.get_height():
		for x in image.get_width():
			if image.get_pixel(x, y).a > 0.5:
				count += 1
	return count


func _shots() -> void:
	_seed_party()
	var creator := CreatorScreen.new()
	creator.stage_preview()
	await _swap(creator)
	await _capture("creator")
	var map := MapScreen.new()
	map.stage_preview()
	await _swap(map)
	await _capture("map")
	var session := SessionScreen.new()
	await _swap(session)
	session.stage_battle_preview()
	await _capture("combat")
	session.set_threat_debug(_threat_preview())
	await _capture("threat")
	session.set_threat_debug([])
	var ranks: Dictionary = (GameState.party[0]["skill_ranks"] as Dictionary).duplicate(true)
	ranks["rallying_brand"] = 0
	var preview_cd := {"shieldwall": 2}
	session.show_member_bar(0, preview_cd, "skill:oathstrike", ranks, 130)
	session.present_inspect(0, "skill:oathstrike", preview_cd, ranks, 130)
	await _capture("skills")
	var aim: Dictionary = session._inspect_card("skill:oathstrike", ranks, 80, 130, preview_cd, {})
	aim["hint"] = "Pick a target"
	session.set_target_mode(["m0", "m1", "m2"], "")
	session.show_inspect(aim, "skill:oathstrike")
	await _capture("targeting")
	session.clear_target_mode()
	session.hide_inspect()
	session.show_member_bar(0, {}, "", {})
	session.open_party()
	await _capture("party")
	session.hide_choices()
	GameState.place_id = "briar_cross"
	GameState.remember_lineup("briar_cross", {"cinder_mite": 2, "briar_hound": 1, "thicket_imp": 1})
	var builder := BattleBuilder.new()
	builder.setup("briar_cross")
	session.add_child(builder)
	builder.set_anchors_preset(Control.PRESET_FULL_RECT)
	await _capture("builder")
	builder.queue_free()
	session.present_units([
		{"id": "m0", "side": "monster", "kind": "gravel_brute", "hp": 40, "max_hp": 40, "mp": 0, "max_mp": 1, "back_row": false},
		{"id": "m1", "side": "monster", "kind": "briar_hound", "hp": 30, "max_hp": 30, "mp": 0, "max_mp": 1, "back_row": false},
		{"id": "m2", "side": "monster", "kind": "marshlurker", "hp": 28, "max_hp": 28, "mp": 0, "max_mp": 1, "back_row": false},
	])
	await _capture("lineup")
	session.stage_battle_preview()
	var flow := BattleFlow.new()
	flow.view = session
	session.add_child(flow)
	var elapsed := await flow.measure_visible_attack()
	print("BASIC_ATTACK_MS %d" % elapsed)


func _threat_preview() -> Array:
	var rules: Dictionary = ContentDB.threat_rules()
	var body_per := float(rules.get("body_per", 0.0))
	var armor_per := float(rules.get("armor_per", 0.0))
	var threats: Array = []
	var total := 0
	for member in GameState.party:
		var stats := GameState.combat_stats(member)
		var cls: Dictionary = ContentDB.class_def(str(member["class_id"]))
		var effects: Array = []
		for skill_id in cls["skills"]:
			var skill: Dictionary = ContentDB.skill(str(skill_id))
			if not Formulas.is_passive(skill):
				continue
			var listed: Array = skill.get("effects", [])
			for effect in listed:
				effects.append(effect)
		var threat := Formulas.member_threat(
			int(cls.get("base_threat", 1)),
			int(stats["body"]),
			int(stats["dr"]),
			0,
			Formulas.threat_multiplier(effects),
			1.0,
			body_per,
			armor_per
		)
		threats.append(threat)
		total += threat
	var rows: Array = []
	for i in threats.size():
		var pct := 0
		if total > 0:
			pct = int(round(100.0 * float(int(threats[i])) / float(total)))
		rows.append({"id": "p%d" % i, "text": "%d%%" % pct})
	return rows


func _paladin_skill_preview() -> Array:
	var entries: Array = []
	var cooldowns := {"shieldwall": 2}
	var mp := 130
	var cls: Dictionary = ContentDB.class_def("paladin")
	for skill_id in cls["skills"]:
		var skill: Dictionary = ContentDB.skill(str(skill_id))
		if Formulas.is_passive(skill):
			continue
		var usable := Formulas.skill_usable(skill, 1, 80, mp, cooldowns, {})
		entries.append({
			"id": "skill:%s" % str(skill_id),
			"text": Formulas.skill_cost_label(skill, 1, cooldowns, {}),
			"disabled": not usable,
		})
	return entries


func _capture(shot_name: String) -> void:
	for _i in 3:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	var paths := [
		"/opt/cursor/artifacts/%s.png" % shot_name,
		"res://docs/screenshots/%s.png" % shot_name,
	]
	DirAccess.make_dir_recursive_absolute("/opt/cursor/artifacts")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://docs/screenshots"))
	for path in paths:
		var absolute := str(path)
		if absolute.begins_with("res://"):
			absolute = ProjectSettings.globalize_path(absolute)
		var err := image.save_png(absolute)
		print("SHOT %s %s %s" % [shot_name, absolute, err])


func _seed_party() -> void:
	var members: Array = [
		GameState.make_member("mason", "delver", "paladin", {"skin": 4, "head": 2, "hair": 1, "hair_color": 0, "outfit_color": 0}),
		GameState.make_member("nim", "glenfolk", "wizard", {"skin": 1, "head": 5, "hair": 3, "hair_color": 6, "outfit_color": 1}),
		GameState.make_member("pip", "hearthborn", "ranger", {"skin": 2, "head": 0, "hair": 6, "hair_color": 2, "outfit_color": 2}),
		GameState.make_member("sable", "hearthborn", "cleric", {"skin": 3, "head": 4, "hair": 2, "hair_color": 4, "outfit_color": 1}),
		GameState.make_member("holt", "glenfolk", "bard", {"skin": 0, "head": 6, "hair": 5, "hair_color": 5, "outfit_color": 2}),
	]
	GameState.new_campaign(members)
