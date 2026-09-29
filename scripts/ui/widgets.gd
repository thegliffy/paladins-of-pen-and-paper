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
	bind_pointer(button)
	return button


static func is_emulated(event: InputEvent) -> bool:
	return event.device == InputEvent.DEVICE_ID_EMULATION


static func is_press(event: InputEvent) -> bool:
	if is_emulated(event):
		return false
	if event is InputEventScreenTouch:
		return (event as InputEventScreenTouch).pressed
	if event is InputEventMouseButton:
		var mouse := event as InputEventMouseButton
		return mouse.pressed and _primary_button(mouse)
	return false


static func is_release(event: InputEvent) -> bool:
	if is_emulated(event):
		return false
	if event is InputEventScreenTouch:
		return not (event as InputEventScreenTouch).pressed
	if event is InputEventMouseButton:
		var mouse := event as InputEventMouseButton
		return not mouse.pressed and _primary_button(mouse)
	return false


static func is_drag(event: InputEvent) -> bool:
	if is_emulated(event):
		return false
	return event is InputEventScreenDrag or event is InputEventMouseMotion


static func event_position(event: InputEvent) -> Vector2:
	if event is InputEventScreenTouch:
		return (event as InputEventScreenTouch).position
	if event is InputEventScreenDrag:
		return (event as InputEventScreenDrag).position
	if event is InputEventMouse:
		return (event as InputEventMouse).position
	return Vector2.ZERO


static func event_relative(event: InputEvent) -> Vector2:
	if event is InputEventScreenDrag:
		return (event as InputEventScreenDrag).relative
	if event is InputEventMouseMotion:
		return (event as InputEventMouseMotion).relative
	return Vector2.ZERO


static func _primary_button(mouse: InputEventMouseButton) -> bool:
	# Some Android devices report a finger as mouse button 0, which is not Left.
	return mouse.button_index == MOUSE_BUTTON_LEFT or mouse.button_index == MOUSE_BUTTON_NONE


static func bind_pointer(button: Button) -> void:
	## Finger taps fire the button even when touch-to-mouse emulation is off.
	## Emulated echoes are ignored so one finger does not click twice.
	if button.has_meta("pointer_bound"):
		return
	button.set_meta("pointer_bound", true)
	button.set_meta("finger_down", false)
	button.gui_input.connect(_on_button_pointer.bind(button))


static func _on_button_pointer(event: InputEvent, button: Button) -> void:
	if is_emulated(event) or button == null:
		return
	var arm := false
	var release := false
	if event is InputEventScreenTouch:
		if Input.is_emulating_mouse_from_touch():
			return
		var touch := event as InputEventScreenTouch
		arm = touch.pressed
		release = not touch.pressed
	elif event is InputEventMouseButton:
		var mouse := event as InputEventMouseButton
		if mouse.button_index != MOUSE_BUTTON_NONE:
			return
		arm = mouse.pressed
		release = not mouse.pressed
	else:
		return
	if arm:
		button.set_meta("finger_down", true)
		button.get_viewport().set_input_as_handled()
		return
	if release and bool(button.get_meta("finger_down", false)):
		button.set_meta("finger_down", false)
		var local := event_position(event)
		if not button.disabled and Rect2(Vector2.ZERO, button.size).has_point(local):
			button.pressed.emit()
		button.get_viewport().set_input_as_handled()


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


static func ui_font() -> Font:
	return load("res://art/fonts/m5x7.ttf")


static func wrap_size(text: String, width: float, font_size: int) -> Vector2:
	var font: Font = ui_font()
	if text == "":
		return Vector2(0, font.get_height(font_size))
	return font.get_multiline_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, width, font_size)


static func enable_wrap(node: Label) -> void:
	node.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	node.clip_text = true
	node.add_theme_constant_override("line_spacing", 0)


static func place_wrapped(node: Label, at: Vector2, box: Vector2) -> void:
	## Autowrap before size. Setting size first locks the label to the
	## unwrapped line, and it will not shrink once that minimum is cached.
	enable_wrap(node)
	node.position = at
	node.size = box


static func inspect_card_height(description: String, width: float) -> float:
	var block := wrap_size(description, width - 28.0, Layout.font_size())
	return maxf(100.0, 62.0 + block.y + 22.0)


static func pixel_card_height(description: String, width: float) -> float:
	## Pack 3x5 description: 8px lines under the icon block, then the prompt strip.
	var chars := int((width - 32.0 + 1.0) / 4.0)
	var lines := PixelFont.wrap(description, chars)
	return maxf(100.0, 62.0 + float(lines.size()) * 8.0 + 22.0)


static func place_blurb(place: Dictionary, hops: int, cost: int, here: bool) -> String:
	if here:
		return "%s  Lv %d\nYou are here.\n%s" % [place["name"], int(place["level"]), place["description"]]
	return "%s  Lv %d\n%d hop%s, %d gold\n%s" % [
		place["name"], int(place["level"]), hops, "" if hops == 1 else "s", cost, place["description"]
	]


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
