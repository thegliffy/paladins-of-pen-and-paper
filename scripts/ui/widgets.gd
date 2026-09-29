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


static func header_ink() -> Color:
	return SpriteCatalog.INK


static func header_back() -> Color:
	return SpriteCatalog.CREAM


static func header_plate() -> Panel:
	## Opaque parchment. A light label on the sky disappears into the clouds.
	var plate := Panel.new()
	var box := StyleBoxFlat.new()
	box.bg_color = header_back()
	box.border_color = Color("5a4028")
	box.set_border_width_all(2)
	box.set_content_margin_all(0)
	plate.add_theme_stylebox_override("panel", box)
	plate.mouse_filter = Control.MOUSE_FILTER_IGNORE
	plate.clip_contents = true
	return plate


static func contrast_ratio(fg: Color, bg: Color) -> float:
	var lighter := maxf(_relative_luminance(fg), _relative_luminance(bg))
	var darker := minf(_relative_luminance(fg), _relative_luminance(bg))
	return (lighter + 0.05) / (darker + 0.05)


static func _relative_luminance(color: Color) -> float:
	var weights := [0.2126, 0.7152, 0.0722]
	var channels: Array[float] = [color.r, color.g, color.b]
	var lum := 0.0
	for i in channels.size():
		var ch := channels[i]
		var linear := ch / 12.92 if ch <= 0.04045 else pow((ch + 0.055) / 1.055, 2.4)
		lum += weights[i] * linear
	return lum


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


static func wrapped_label(text: String, width: float, font_size: int, color: Color = SpriteCatalog.INK) -> Label:
	## Autowrap before the text is assigned, then lock the minimum to the
	## wrapped block. The width is the panel column, not the unwrapped line.
	var node := Label.new()
	node.mouse_filter = Control.MOUSE_FILTER_IGNORE
	node.add_theme_font_size_override("font_size", font_size)
	node.add_theme_color_override("font_color", color)
	enable_wrap(node)
	node.text = text
	var block := wrap_size(text, width, font_size)
	node.custom_minimum_size = Vector2(width, maxf(block.y, ui_font().get_height(font_size)))
	node.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	return node


static func action_row_fit(labels: PackedStringArray, width: float, height: float, want_icon: bool) -> Dictionary:
	## Largest font that keeps every word inside the button. Icons stay when
	## they fit beside the word; they drop before a label is clipped mid-word.
	var font := ui_font()
	var side := 8.0
	var gap := 2.0
	var icon_choices: Array = [16, 12] if want_icon else [0]
	for font_size in [16, 14, 12, 10]:
		if float(font.get_height(font_size)) > height - 6.0:
			continue
		for icon_w in icon_choices:
			if _action_row_fits(font, labels, int(font_size), int(icon_w), width, side, gap):
				return {"font_size": int(font_size), "icon_width": int(icon_w), "gap": gap, "side": side}
	if want_icon:
		for font_size in [16, 14, 12, 10]:
			if float(font.get_height(font_size)) > height - 6.0:
				continue
			if _action_row_fits(font, labels, int(font_size), 0, width, side, gap):
				return {"font_size": int(font_size), "icon_width": 0, "gap": gap, "side": side}
	return {"font_size": 10, "icon_width": 0, "gap": 0.0, "side": side}


static func _action_row_fits(font: Font, labels: PackedStringArray, font_size: int, icon_w: int, width: float, side: float, gap: float) -> bool:
	var widest := 0.0
	for label in labels:
		widest = maxf(widest, font.get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x)
	var extra := 0.0 if icon_w == 0 else float(icon_w) + gap
	return widest + extra + side <= width + 0.01


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
