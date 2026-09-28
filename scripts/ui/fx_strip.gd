extends TextureRect
class_name FxStrip
## One horizontal strip from manifest fx (frame size, frame count, fps).


var frames := 1
var frame_size := Vector2(16, 16)
var fps := 6.0
var loop := true
var _time := 0.0
var _sheet: Texture2D


func setup(rel: String, size: Vector2, count: int, rate: float, should_loop: bool) -> void:
	_sheet = ArtPack.texture(rel)
	frame_size = size
	frames = maxi(1, count)
	fps = rate
	loop = should_loop
	custom_minimum_size = size
	self.size = size
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	expand_mode = EXPAND_IGNORE_SIZE
	stretch_mode = STRETCH_SCALE
	_show_frame(0)


func _process(delta: float) -> void:
	_time += delta
	var index := int(_time * fps)
	if not loop and index >= frames:
		queue_free()
		return
	_show_frame(posmod(index, frames))


func freeze(index: int) -> void:
	set_process(false)
	_show_frame(posmod(index, frames))


func _show_frame(index: int) -> void:
	if _sheet == null:
		return
	var atlas := AtlasTexture.new()
	atlas.atlas = _sheet
	atlas.region = Rect2(float(index) * frame_size.x, 0, frame_size.x, frame_size.y)
	texture = atlas
