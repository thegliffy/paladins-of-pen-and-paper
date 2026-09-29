extends Control
class_name QuestScreen
## Story log and the Candlewick notice board. Portrait, tap first.
##
## The parchment sheet is created once and every label is parented to it.
## Rebuilding used to free() the button that was still emitting. Godot refuses
## to free a locked object, the function aborted, and the sheet was already
## gone while the story labels stayed drawn over the town.

signal closed

const TEXT_W := 246.0
const CARD_W := 230.0

var _mode := "log"
var _tab := "story"
var _sheet: Panel
var _header: HBoxContainer
var _tabs: HBoxContainer
var _body: VBoxContainer
var _covering := false


func setup(mode: String) -> void:
	_mode = mode if mode == "board" else "log"
	if is_inside_tree() and _body != null:
		_refresh()


func _ready() -> void:
	_cover()
	_build_chrome()
	_refresh()


func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED and is_inside_tree():
		var view := Vector2(Layout.viewport_size())
		if size.x < view.x * 0.5 or size.y < view.y * 0.5:
			_cover()


func _cover() -> void:
	if _covering:
		return
	_covering = true
	name = "QuestScreen"
	mouse_filter = Control.MOUSE_FILTER_STOP
	var view := Vector2(Layout.viewport_size())
	set_anchors_preset(Control.PRESET_TOP_LEFT)
	position = Vector2.ZERO
	size = view
	custom_minimum_size = view
	_covering = false


func _build_chrome() -> void:
	var veil := ColorRect.new()
	veil.name = "Veil"
	veil.color = Color("e8d6b0")
	veil.mouse_filter = Control.MOUSE_FILTER_STOP
	veil.position = Vector2.ZERO
	veil.size = Vector2(Layout.viewport_size())
	add_child(veil)
	_sheet = Panel.new()
	_sheet.name = "Sheet"
	var parchment := StyleBoxFlat.new()
	parchment.bg_color = Color("e8d6b0")
	parchment.border_color = Color("5a4028")
	parchment.set_border_width_all(4)
	parchment.set_content_margin_all(0)
	_sheet.add_theme_stylebox_override("panel", parchment)
	_sheet.mouse_filter = Control.MOUSE_FILTER_STOP
	_sheet.clip_contents = true
	_sheet.position = Vector2(4, 4)
	_sheet.size = Vector2(262, 472)
	add_child(_sheet)
	var column := VBoxContainer.new()
	column.name = "Column"
	column.position = Vector2(8, 8)
	column.size = Vector2(TEXT_W, 456)
	column.custom_minimum_size = column.size
	column.add_theme_constant_override("separation", 6)
	_sheet.add_child(column)
	_header = HBoxContainer.new()
	_header.name = "Header"
	_header.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_header.add_theme_constant_override("separation", 6)
	column.add_child(_header)
	_tabs = HBoxContainer.new()
	_tabs.name = "Tabs"
	_tabs.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_tabs.add_theme_constant_override("separation", 4)
	column.add_child(_tabs)
	var scroll := ScrollContainer.new()
	scroll.name = "Scroll"
	scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.custom_minimum_size = Vector2(TEXT_W, 360)
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO
	column.add_child(scroll)
	_body = VBoxContainer.new()
	_body.name = "Body"
	_body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_body.add_theme_constant_override("separation", 6)
	scroll.add_child(_body)


func _refresh() -> void:
	if _body == null:
		return
	_clear(_header)
	_clear(_tabs)
	_clear(_body)
	var title := Widgets.wrapped_label(
		"QUEST LOG" if _mode == "log" else "NOTICE BOARD",
		150.0,
		Layout.font_size(),
		SpriteCatalog.INK
	)
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_header.add_child(title)
	var close := Widgets.make_button("Close", Vector2(64, 28))
	close.name = "CloseQuest"
	close.pressed.connect(func(): closed.emit())
	_header.add_child(close)
	if _mode == "board":
		_build_board()
	else:
		_build_log()


func _schedule_refresh() -> void:
	call_deferred("_refresh")


func _build_log() -> void:
	_tabs.add_child(_tab_button("Story", "story"))
	_tabs.add_child(_tab_button("Board", "active"))
	if _at_candlewick():
		var board := Widgets.make_button("Notice board", Vector2(118, 26))
		board.name = "OpenBoard"
		board.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		board.pressed.connect(func():
			_mode = "board"
			_schedule_refresh()
		)
		_tabs.add_child(board)
	if _tab == "active":
		_build_active()
	else:
		_build_story()


func _build_story() -> void:
	var step := GameState.story_step()
	if step.is_empty():
		_body.add_child(_paragraph("The road is quiet. The board in Candlewick still has work.", Layout.font_tiny(), SpriteCatalog.INK))
		return
	_body.add_child(_paragraph(str(step.get("name", "")), Layout.font_size(), SpriteCatalog.INK))
	_body.add_child(_paragraph(str(step.get("objective", "")), Layout.font_small(), SpriteCatalog.HP))
	_body.add_child(_paragraph(str(step.get("gm", "")), Layout.font_tiny(), SpriteCatalog.INK))
	_body.add_child(_paragraph(GameState.story_reward_line(step), Layout.font_tiny(), SpriteCatalog.GOLD))
	_body.add_child(_paragraph("Steps %d/%d" % [GameState.story_done.size(), ContentDB.story_steps().size()], Layout.font_tiny(), SpriteCatalog.INK))
	_body.add_child(_paragraph("On the board", Layout.font_tiny(), SpriteCatalog.INK))
	var lines: Array = GameState.active_lines()
	if lines.is_empty():
		_body.add_child(_paragraph("No grind quests yet.", Layout.font_small(), SpriteCatalog.HP))
		return
	for line in lines:
		_body.add_child(_paragraph(str(line), Layout.font_small(), SpriteCatalog.HP))


func _build_active() -> void:
	var hint := "Turn finished work in at the Candlewick board."
	if not _at_candlewick():
		hint = "The notice board is in Candlewick."
	_body.add_child(_paragraph(hint, Layout.font_tiny(), SpriteCatalog.INK))
	if GameState.board_active.is_empty():
		_body.add_child(_paragraph("Nothing accepted. The board posts three at a time.", Layout.font_tiny(), SpriteCatalog.INK))
		return
	for row in GameState.board_active:
		var quest: Dictionary = ContentDB.board_quest(str(row.get("id", "")))
		var quest_id := str(row.get("id", ""))
		var drop := Widgets.make_button("Abandon", Vector2(80, 26))
		drop.pressed.connect(func():
			GameState.abandon_board(quest_id)
			_schedule_refresh()
		)
		_body.add_child(_card([
			_card_line(str(quest.get("name", quest_id)), Layout.font_small(), SpriteCatalog.INK),
			_card_line(QuestRules.progress_line(quest, int(row.get("progress", 0))), Layout.font_size(), SpriteCatalog.HP),
		], drop))


func _build_board() -> void:
	var back := Widgets.make_button("Log", Vector2(64, 26))
	back.name = "BackLog"
	back.pressed.connect(func():
		_mode = "log"
		_tab = "story"
		_schedule_refresh()
	)
	_tabs.add_child(back)
	var ready := 0
	for row in GameState.board_active:
		var quest: Dictionary = ContentDB.board_quest(str(row.get("id", "")))
		if not QuestRules.can_turn_in(quest, int(row.get("progress", 0))):
			continue
		ready += 1
		var quest_id := str(row.get("id", ""))
		var turn := Widgets.make_button("Turn in", Vector2(78, 26))
		turn.pressed.connect(func():
			GameState.turn_in_board(quest_id)
			_schedule_refresh()
		)
		var row_box := HBoxContainer.new()
		row_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row_box.add_theme_constant_override("separation", 6)
		var copy := Widgets.wrapped_label("%s  %s" % [quest.get("name", ""), QuestRules.progress_line(quest, int(row.get("progress", 0)))], 150.0, Layout.font_tiny(), SpriteCatalog.SAFE)
		copy.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row_box.add_child(copy)
		row_box.add_child(turn)
		_body.add_child(row_box)
	if ready == 0:
		_body.add_child(_paragraph("Nothing is ready to turn in.", Layout.font_tiny(), SpriteCatalog.INK))
	_body.add_child(_paragraph("Posted", Layout.font_tiny(), SpriteCatalog.INK))
	for slot in GameState.board_offers.size():
		var id := str(GameState.board_offers[slot])
		var quest: Dictionary = ContentDB.board_quest(id)
		if quest.is_empty():
			_body.add_child(_card([
				_card_line("The board is quiet.", Layout.font_tiny(), SpriteCatalog.INK),
			], null))
			continue
		var take := Widgets.make_button("Accept", Vector2(80, 26))
		take.disabled = GameState.board_active.size() >= QuestRules.ACTIVE_CAP
		var slot_index := int(slot)
		take.pressed.connect(func():
			GameState.accept_board(slot_index)
			_schedule_refresh()
		)
		_body.add_child(_card([
			_card_line(str(quest.get("name", "")), Layout.font_small(), SpriteCatalog.INK),
			_card_line(_ask_line(quest), Layout.font_tiny(), SpriteCatalog.HP),
			_card_line(GameState.story_reward_line(quest), Layout.font_tiny(), SpriteCatalog.GOLD),
		], take))
	_body.add_child(_paragraph("Active %d/%d. Accepting posts a new notice." % [GameState.board_active.size(), QuestRules.ACTIVE_CAP], Layout.font_tiny(), SpriteCatalog.INK))


func _tab_button(label: String, tab: String) -> Button:
	var button := Widgets.make_button(label, Vector2(64, 26))
	button.name = "Tab_%s" % tab
	if _tab == tab:
		button.modulate = Color(1, 0.92, 0.6)
	button.pressed.connect(func():
		_tab = tab
		_schedule_refresh()
	)
	return button


func _paragraph(text: String, font_size: int, color: Color) -> Label:
	return Widgets.wrapped_label(text, TEXT_W, font_size, color)


func _card_line(text: String, font_size: int, color: Color) -> Label:
	return Widgets.wrapped_label(text, CARD_W, font_size, color)


func _card(lines: Array, button: Button) -> PanelContainer:
	var card := PanelContainer.new()
	card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var style := StyleBoxFlat.new()
	style.bg_color = Color("f3e6c8")
	style.border_color = Color("8a6840")
	style.set_border_width_all(2)
	style.set_content_margin_all(4)
	card.add_theme_stylebox_override("panel", style)
	var box := VBoxContainer.new()
	box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	box.add_theme_constant_override("separation", 4)
	card.add_child(box)
	for line in lines:
		box.add_child(line)
	if button != null:
		box.add_child(button)
	return card


func _clear(node: Node) -> void:
	for child in node.get_children():
		node.remove_child(child)
		child.queue_free()


func _ask_line(quest: Dictionary) -> String:
	if str(quest.get("kind", "")) == "collect":
		return "Bring %d %s." % [int(quest.get("count", 1)), str(quest.get("item_name", ""))]
	return "Defeat %d %s." % [int(quest.get("count", 1)), str(quest.get("monster_name", ""))]


func _at_candlewick() -> bool:
	return GameState.place_id == "candlewick"
