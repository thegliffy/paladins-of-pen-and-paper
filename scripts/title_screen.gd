extends Control
class_name TitleScreen

signal new_game
signal continue_game


func _ready() -> void:
	var bg := ColorRect.new()
	bg.color = Color("6a9a48")
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	var tex := TextureRect.new()
	tex.texture = SpriteCatalog.background("meadow")
	tex.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tex.set_anchors_preset(Control.PRESET_FULL_RECT)
	tex.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	tex.stretch_mode = TextureRect.STRETCH_SCALE
	add_child(tex)
	var shade := ColorRect.new()
	shade.color = Color(0.1, 0.08, 0.05, 0.35)
	shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	shade.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(shade)

	var block := Layout.rect("title", "block")
	var panel := Widgets.panel()
	Layout.place(panel, block)
	add_child(panel)
	var title := Widgets.label("Paladins of\nPen and Paper", Layout.font_size())
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.position = Vector2(8, 16)
	title.size = Vector2(block.size.x - 16, 70)
	panel.add_child(title)
	var sub := Widgets.label("A table session in Greenmere", Layout.font_tiny())
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sub.position = Vector2(8, 96)
	sub.size = Vector2(block.size.x - 16, 24)
	panel.add_child(sub)

	var actions := VBoxContainer.new()
	Layout.place(actions, Layout.rect("title", "actions"))
	actions.add_theme_constant_override("separation", 8)
	add_child(actions)
	var start := Widgets.make_button("New game", Vector2(200, 52))
	start.pressed.connect(func(): new_game.emit())
	actions.add_child(start)
	if GameState.has_save():
		var cont := Widgets.make_button("Continue", Vector2(200, 52))
		cont.pressed.connect(func(): continue_game.emit())
		actions.add_child(cont)
