extends Control
## Draws the selected road on the scrolling map. MapScreen owns the route data.


func _ready() -> void:
	# The meadow is drawn here. It must not sit in front of the clip's tap handler.
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _draw() -> void:
	var screen := get_parent().get_parent()
	if screen and screen.has_method("paint_route"):
		screen.paint_route(self)
