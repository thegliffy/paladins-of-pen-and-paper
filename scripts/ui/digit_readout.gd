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


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func set_text(value: String) -> void:
	text = value
	queue_redraw()


func _draw() -> void:
	var x := 0.0
	var i := 0
	while i < text.length():
		var ch := text.substr(i, 1)
		var drawn := _draw_glyph(sheet, glyph_order, ch, x)
		if not drawn and letters_sheet != "":
			drawn = _draw_glyph(letters_sheet, letters_order, ch, x)
		if not drawn and ch == "/":
			_draw_slash(x)
			drawn = true
		if drawn:
			x += float(advance)
		elif ch == " ":
			x += float(advance)
		i += 1


func _draw_slash(x: float) -> void:
	var ink := Color("f4efe4")
	draw_line(Vector2(x + 2.0, 1.0), Vector2(x + 0.0, float(cell.y - 2)), ink, 1.0)


func _draw_glyph(rel: String, order: String, ch: String, x: float) -> bool:
	var index := order.find(ch)
	if index < 0:
		return false
	var tex := ArtPack.texture(rel)
	if tex == null:
		return false
	draw_texture_rect_region(tex, Rect2(x, 0, cell.x, cell.y), Rect2(index * cell.x, 0, cell.x, cell.y))
	return true
