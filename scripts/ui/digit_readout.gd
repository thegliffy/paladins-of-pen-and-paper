extends Control
class_name DigitReadout
## Sprite digits. The sheet, cell, and advance come from the art manifest.


var text := ""
var sheet := "ui/portrait/digits_3x5_outlined.png"
var cell := Vector2i(5, 7)
var advance := 4
var glyph_order := "0123456789"
var letters_sheet := ""
var letters_order := ""
var h_align := HORIZONTAL_ALIGNMENT_LEFT
var v_align := VERTICAL_ALIGNMENT_TOP


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func set_text(value: String) -> void:
	text = value
	queue_redraw()


func content_size() -> Vector2:
	var count := text.length()
	if count <= 0:
		return Vector2.ZERO
	return Vector2(float((count - 1) * advance + cell.x), float(cell.y))


func _draw() -> void:
	var block := content_size()
	var origin := Vector2.ZERO
	if h_align == HORIZONTAL_ALIGNMENT_CENTER:
		origin.x = floorf((size.x - block.x) * 0.5)
	if v_align == VERTICAL_ALIGNMENT_CENTER:
		origin.y = floorf((size.y - block.y) * 0.5)
	var x := origin.x
	var i := 0
	while i < text.length():
		var ch := text.substr(i, 1)
		var drawn := _draw_glyph(sheet, glyph_order, ch, x, origin.y)
		if not drawn and letters_sheet != "":
			drawn = _draw_glyph(letters_sheet, letters_order, ch, x, origin.y)
		if not drawn and ch == "/":
			_draw_slash(x, origin.y)
			drawn = true
		if drawn:
			x += float(advance)
		elif ch == " ":
			x += float(advance)
		i += 1


func _draw_slash(x: float, y: float) -> void:
	var outline := ArtPack.SEAT_BAR_INK
	var ink := ArtPack.SEAT_BAR_GLYPH
	var start := Vector2(x + 2.0, y + 1.0)
	var finish := Vector2(x, y + float(cell.y - 2))
	for dy in [-1, 0, 1]:
		for dx in [-1, 0, 1]:
			if dx == 0 and dy == 0:
				continue
			var shift := Vector2(float(dx), float(dy))
			draw_line(start + shift, finish + shift, outline, 1.0)
	draw_line(start, finish, ink, 1.0)


func _draw_glyph(rel: String, order: String, ch: String, x: float, y: float) -> bool:
	var index := order.find(ch)
	if index < 0:
		return false
	var tex := ArtPack.texture(rel)
	if tex == null:
		return false
	draw_texture_rect_region(tex, Rect2(x, y, cell.x, cell.y), Rect2(index * cell.x, 0, cell.x, cell.y))
	return true
