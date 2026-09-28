extends Control
## Draws the selected road on the scrolling map. MapScreen owns the route data.


func _draw() -> void:
	var screen := get_parent().get_parent()
	if screen and screen.has_method("paint_route"):
		screen.paint_route(self)
