extends Control
class_name QuestScreen
## Story log and the Candlewick notice board. Portrait, tap first.

signal closed

var _mode := "log"
var _tab := "story"


func setup(mode: String) -> void:
	_mode = mode if mode == "board" else "log"
	if is_inside_tree():
		_rebuild()


func _ready() -> void:
	_rebuild()


func _rebuild() -> void:
	for child in get_children():
		child.free()
	name = "QuestScreen"
	mouse_filter = Control.MOUSE_FILTER_STOP
	set_anchors_preset(Control.PRESET_FULL_RECT)
	var backdrop := TextureRect.new()
	backdrop.set_anchors_preset(Control.PRESET_FULL_RECT)
	backdrop.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	backdrop.stretch_mode = TextureRect.STRETCH_SCALE
	backdrop.texture = ArtPack.texture(ContentDB.combat_backdrop_path(GameState.place_id))
	backdrop.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(backdrop)
	var sheet := Widgets.panel()
	sheet.position = Vector2(4, 4)
	sheet.size = Vector2(262, 472)
	sheet.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(sheet)
	var title := Widgets.label("QUEST LOG" if _mode == "log" else "NOTICE BOARD", Layout.font_size(), SpriteCatalog.INK)
	title.position = Vector2(12, 10)
	title.size = Vector2(170, 20)
	add_child(title)
	var close := Widgets.make_button("Close", Vector2(64, 28))
	close.name = "CloseQuest"
	close.position = Vector2(196, 8)
	close.pressed.connect(func(): closed.emit())
	add_child(close)
	if _mode == "board":
		_build_board()
	else:
		_build_log()


func _build_log() -> void:
	_tab_button("Story", "story", Vector2(12, 40))
	_tab_button("Board", "active", Vector2(78, 40))
	if _at_candlewick():
		var board := Widgets.make_button("Notice board", Vector2(110, 26))
		board.name = "OpenBoard"
		board.position = Vector2(146, 40)
		board.pressed.connect(func():
			_mode = "board"
			_rebuild()
		)
		add_child(board)
	if _tab == "active":
		_build_active()
	else:
		_build_story()


func _build_story() -> void:
	var step := GameState.story_step()
	var y := 76.0
	if step.is_empty():
		_body("The road is quiet. The board in Candlewick still has work.", y)
		return
	var name := Widgets.label(str(step.get("name", "")), Layout.font_size(), SpriteCatalog.INK)
	name.position = Vector2(12, y)
	name.size = Vector2(246, 20)
	add_child(name)
	y += 22.0
	var objective := Widgets.label(str(step.get("objective", "")), Layout.font_small(), SpriteCatalog.HP)
	objective.position = Vector2(12, y)
	objective.size = Vector2(246, 32)
	Widgets.enable_wrap(objective)
	add_child(objective)
	y += 36.0
	var gm := Widgets.label(str(step.get("gm", "")), Layout.font_tiny(), SpriteCatalog.INK)
	gm.position = Vector2(12, y)
	gm.size = Vector2(246, 64)
	Widgets.enable_wrap(gm)
	add_child(gm)
	y += 68.0
	var reward := Widgets.label(GameState.story_reward_line(step), Layout.font_tiny(), SpriteCatalog.GOLD)
	reward.position = Vector2(12, y)
	reward.size = Vector2(246, 16)
	add_child(reward)
	y += 20.0
	var done := Widgets.label("Steps %d/%d" % [GameState.story_done.size(), ContentDB.story_steps().size()], Layout.font_tiny(), SpriteCatalog.INK)
	done.position = Vector2(12, y)
	done.size = Vector2(246, 16)
	add_child(done)
	y += 22.0
	var header := Widgets.label("On the board", Layout.font_tiny(), SpriteCatalog.INK)
	header.position = Vector2(12, y)
	header.size = Vector2(246, 14)
	add_child(header)
	y += 16.0
	var lines: Array = GameState.active_lines()
	if lines.is_empty():
		_line("No grind quests yet.", y)
		return
	for line in lines:
		_line(str(line), y)
		y += 16.0


func _build_active() -> void:
	var y := 76.0
	var hint := "Turn finished work in at the Candlewick board."
	if not _at_candlewick():
		hint = "The notice board is in Candlewick."
	var note := Widgets.label(hint, Layout.font_tiny(), SpriteCatalog.INK)
	note.position = Vector2(12, y)
	note.size = Vector2(246, 28)
	Widgets.enable_wrap(note)
	add_child(note)
	y += 32.0
	if GameState.board_active.is_empty():
		_body("Nothing accepted. The board posts three at a time.", y)
		return
	for row in GameState.board_active:
		var quest: Dictionary = ContentDB.board_quest(str(row.get("id", "")))
		var card := Widgets.panel()
		card.position = Vector2(12, y)
		card.size = Vector2(246, 72)
		card.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(card)
		var title := Widgets.label(str(quest.get("name", row.get("id", ""))), Layout.font_small(), SpriteCatalog.INK)
		title.position = Vector2(20, y + 4)
		title.size = Vector2(220, 16)
		add_child(title)
		var progress := Widgets.label(QuestRules.progress_line(quest, int(row.get("progress", 0))), Layout.font_size(), SpriteCatalog.HP)
		progress.position = Vector2(20, y + 22)
		progress.size = Vector2(220, 18)
		add_child(progress)
		var drop := Widgets.make_button("Abandon", Vector2(80, 24))
		drop.position = Vector2(20, y + 42)
		var quest_id := str(row.get("id", ""))
		drop.pressed.connect(_abandon.bind(quest_id))
		add_child(drop)
		y += 78.0


func _build_board() -> void:
	var back := Widgets.make_button("Log", Vector2(52, 26))
	back.name = "BackLog"
	back.position = Vector2(12, 40)
	back.pressed.connect(func():
		_mode = "log"
		_tab = "story"
		_rebuild()
	)
	add_child(back)
	var y := 74.0
	for row in GameState.board_active:
		var quest: Dictionary = ContentDB.board_quest(str(row.get("id", "")))
		if not QuestRules.can_turn_in(quest, int(row.get("progress", 0))):
			continue
		var ready := Widgets.label("%s  %s" % [quest.get("name", ""), QuestRules.progress_line(quest, int(row.get("progress", 0)))], Layout.font_tiny(), SpriteCatalog.SAFE)
		ready.position = Vector2(12, y)
		ready.size = Vector2(160, 28)
		Widgets.enable_wrap(ready)
		add_child(ready)
		var turn := Widgets.make_button("Turn in", Vector2(78, 26))
		turn.position = Vector2(178, y)
		var quest_id := str(row.get("id", ""))
		turn.pressed.connect(_turn_in.bind(quest_id))
		add_child(turn)
		y += 32.0
	var posted := Widgets.label("Posted", Layout.font_tiny(), SpriteCatalog.INK)
	posted.position = Vector2(12, y)
	posted.size = Vector2(240, 14)
	add_child(posted)
	y += 16.0
	for slot in GameState.board_offers.size():
		var id := str(GameState.board_offers[slot])
		var quest: Dictionary = ContentDB.board_quest(id)
		var card := Widgets.panel()
		card.position = Vector2(12, y)
		card.size = Vector2(246, 86)
		card.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(card)
		if quest.is_empty():
			var quiet := Widgets.label("The board is quiet.", Layout.font_tiny(), SpriteCatalog.INK)
			quiet.position = Vector2(20, y + 28)
			quiet.size = Vector2(220, 20)
			add_child(quiet)
		else:
			var title := Widgets.label(str(quest.get("name", "")), Layout.font_small(), SpriteCatalog.INK)
			title.position = Vector2(20, y + 4)
			title.size = Vector2(220, 16)
			add_child(title)
			var ask := Widgets.label(_ask_line(quest), Layout.font_tiny(), SpriteCatalog.HP)
			ask.position = Vector2(20, y + 22)
			ask.size = Vector2(220, 16)
			add_child(ask)
			var pay := Widgets.label(GameState.story_reward_line(quest), Layout.font_tiny(), SpriteCatalog.GOLD)
			pay.position = Vector2(20, y + 38)
			pay.size = Vector2(140, 14)
			add_child(pay)
			var take := Widgets.make_button("Accept", Vector2(72, 24))
			take.position = Vector2(168, y + 54)
			take.disabled = GameState.board_active.size() >= QuestRules.ACTIVE_CAP
			take.pressed.connect(_accept.bind(slot))
			add_child(take)
		y += 92.0
	if y < 430.0:
		var cap := Widgets.label("Active %d/%d. Accepting posts a new notice." % [GameState.board_active.size(), QuestRules.ACTIVE_CAP], Layout.font_tiny(), SpriteCatalog.INK)
		cap.position = Vector2(12, 448)
		cap.size = Vector2(246, 16)
		add_child(cap)


func _tab_button(label: String, tab: String, at: Vector2) -> void:
	var button := Widgets.make_button(label, Vector2(60, 26))
	button.position = at
	button.name = "Tab_%s" % tab
	if _tab == tab:
		button.modulate = Color(1, 0.92, 0.6)
	button.pressed.connect(func():
		_tab = tab
		_rebuild()
	)
	add_child(button)


func _body(text: String, y: float) -> void:
	var copy := Widgets.label(text, Layout.font_tiny(), SpriteCatalog.INK)
	copy.position = Vector2(12, y)
	copy.size = Vector2(246, 48)
	Widgets.enable_wrap(copy)
	add_child(copy)


func _line(text: String, y: float) -> void:
	var copy := Widgets.label(text, Layout.font_small(), SpriteCatalog.HP)
	copy.position = Vector2(12, y)
	copy.size = Vector2(246, 16)
	add_child(copy)


func _ask_line(quest: Dictionary) -> String:
	if str(quest.get("kind", "")) == "collect":
		return "Bring %d %s." % [int(quest.get("count", 1)), str(quest.get("item_name", ""))]
	return "Defeat %d %s." % [int(quest.get("count", 1)), str(quest.get("monster_name", ""))]


func _at_candlewick() -> bool:
	return GameState.place_id == "candlewick"


func _accept(slot: int) -> void:
	GameState.accept_board(slot)
	_rebuild()


func _abandon(quest_id: String) -> void:
	GameState.abandon_board(quest_id)
	_rebuild()


func _turn_in(quest_id: String) -> void:
	GameState.turn_in_board(quest_id)
	_rebuild()
