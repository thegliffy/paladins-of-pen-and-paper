extends Object
class_name PixelFont
## The pack's original 3x5 labels (pal.py FONT). Advance is 4px, glyph is 3x5.


const GLYPHS := {
	"A": "010101111101101", "B": "110101110101110", "C": "011100100100011", "D": "110101101101110",
	"E": "111100110100111", "F": "111100110100100", "G": "011100101101011", "H": "101101111101101",
	"I": "111010010010111", "J": "001001001101010", "K": "101101110101101", "L": "100100100100111",
	"M": "101111111101101", "N": "110101101101101", "O": "010101101101010", "P": "110101110100100",
	"Q": "010101101110011", "R": "110101110101101", "S": "011100010001110", "T": "111010010010010",
	"U": "101101101101111", "V": "101101101101010", "W": "101101111111101", "X": "101101010101101",
	"Y": "101101010010010", "Z": "111001010100111",
	"0": "111101101101111", "1": "010110010010111", "2": "110001010100111", "3": "110001010001110",
	"4": "101101111001001", "5": "111100110001110", "6": "011100111101111", "7": "111001010010010",
	"8": "111101111101111", "9": "111101111001110",
	"_": "000000000000111", "-": "000000111000000", "+": "000010111010000", ".": "000000000000010",
	"/": "001001010100100", " ": "000000000000000", "X2": "000101010101000", ":": "000010000010000",
	"(": "010100100100010", ")": "010001001001010", "#": "101111101111101", "!": "010010010000010",
	"%": "101001010100101", ",": "000000000010100", "'": "010010000000000", "=": "000111000111000", "?": "110001010000010",
}


static func width(text: String, scale: int = 1) -> int:
	var body := _letters(text)
	if body.is_empty():
		return 0
	return body.length() * 4 * scale - scale


static func wrap(text: String, max_chars: int) -> PackedStringArray:
	var words := _letters(text).split(" ", false)
	var lines := PackedStringArray()
	var current := ""
	var limit := maxi(1, max_chars)
	for word in words:
		var piece := str(word)
		var extra := piece.length() + (0 if current.is_empty() else 1)
		if not current.is_empty() and current.length() + extra > limit:
			lines.append(current)
			current = piece
		elif current.is_empty():
			current = piece
		else:
			current = current + " " + piece
	if not current.is_empty():
		lines.append(current)
	if lines.is_empty():
		lines.append("")
	return lines


static func texture(text: String, color: Color, scale: int = 1) -> Texture2D:
	var body := _letters(text)
	var sc := maxi(1, scale)
	var w := maxi(1, width(body, sc))
	var h := 5 * sc
	var image := Image.create(w, h, false, Image.FORMAT_RGBA8)
	image.fill(Color(0, 0, 0, 0))
	var pen := 0
	for i in body.length():
		var ch := body.substr(i, 1)
		var glyph := str(GLYPHS.get(ch, GLYPHS[" "]))
		if ch == "x":
			glyph = str(GLYPHS["X2"])
		for bit in glyph.length():
			if glyph.substr(bit, 1) != "1":
				continue
			var gx := bit % 3
			var gy := int(bit / 3)
			for sy in sc:
				for sx in sc:
					image.set_pixel(pen + gx * sc + sx, gy * sc + sy, color)
		pen += 4 * sc
	return ImageTexture.create_from_image(image)


static func label(text: String, color: Color, scale: int = 1) -> TextureRect:
	var node := TextureRect.new()
	node.mouse_filter = Control.MOUSE_FILTER_IGNORE
	node.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	node.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	node.stretch_mode = TextureRect.STRETCH_SCALE
	node.texture = texture(text, color, scale)
	node.size = Vector2(width(text, scale), 5 * maxi(1, scale))
	return node


static func _letters(text: String) -> String:
	var mixed := text != text.to_upper()
	var body := text.to_upper() if mixed else text
	var cleaned := ""
	for i in body.length():
		var ch := body.substr(i, 1)
		if ch == "x":
			cleaned += "x"
		elif GLYPHS.has(ch):
			cleaned += ch
		else:
			cleaned += " "
	return cleaned
