extends Object
class_name Widgets


static func style_texture(path: String) -> StyleBoxTexture:
	var box := StyleBoxTexture.new()
	box.texture = load(path)
	box.texture_margin_left = 4
	box.texture_margin_right = 4
	box.texture_margin_top = 4
	box.texture_margin_bottom = 4
	box.axis_stretch_horizontal = StyleBoxTexture.AXIS_STRETCH_MODE_STRETCH
	box.axis_stretch_vertical = StyleBoxTexture.AXIS_STRETCH_MODE_STRETCH
	box.content_margin_left = 4
	box.content_margin_right = 4
	box.content_margin_top = 2
	box.content_margin_bottom = 2
	return box


static func skin_button(button: Button) -> void:
	button.focus_mode = Control.FOCUS_NONE
	button.add_theme_stylebox_override("normal", style_texture("res://art/ui/btn_tan.png"))
	button.add_theme_stylebox_override("hover", style_texture("res://art/ui/btn_tan.png"))
	button.add_theme_stylebox_override("pressed", style_texture("res://art/ui/btn_tan_down.png"))
	button.add_theme_stylebox_override("disabled", style_texture("res://art/ui/btn_tan_down.png"))
	button.add_theme_color_override("font_color", SpriteCatalog.INK)
	button.add_theme_color_override("font_disabled_color", Color(0.35, 0.28, 0.2))
	button.add_theme_font_size_override("font_size", Layout.font_small())


static func make_button(text: String, minimum: Vector2) -> Button:
	var button := Button.new()
	button.text = text
	button.custom_minimum_size = minimum
	button.clip_text = true
	skin_button(button)
	return button


static func panel(path: String = "res://art/ui/panel_tan.png") -> Panel:
	var node := Panel.new()
	node.add_theme_stylebox_override("panel", style_texture(path))
	return node


static func label(text: String, size: int, color: Color = SpriteCatalog.INK) -> Label:
	var node := Label.new()
	node.text = text
	node.add_theme_font_size_override("font_size", size)
	node.add_theme_color_override("font_color", color)
	node.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return node


static func bar(width: float, height: float, fill_color: Color, back_color: Color) -> Dictionary:
	var root := ColorRect.new()
	root.color = back_color
	root.custom_minimum_size = Vector2(width, height)
	root.size = Vector2(width, height)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var fill := ColorRect.new()
	fill.name = "Fill"
	fill.color = fill_color
	fill.position = Vector2(1, 1)
	fill.size = Vector2(maxf(0.0, width - 2.0), maxf(1.0, height - 2.0))
	fill.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(fill)
	return {"root": root, "fill": fill, "width": width - 2.0}


static func set_bar(bar_info: Dictionary, ratio: float) -> void:
	var fill: ColorRect = bar_info["fill"]
	var width: float = bar_info["width"]
	fill.size.x = maxf(0.0, width * clampf(ratio, 0.0, 1.0))


static func tween_bar(bar_info: Dictionary, ratio: float, duration: float) -> Tween:
	var fill: ColorRect = bar_info["fill"]
	var width: float = bar_info["width"]
	var tween := fill.create_tween()
	tween.tween_property(fill, "size:x", maxf(0.0, width * clampf(ratio, 0.0, 1.0)), duration)
	return tween
