class_name RouteFinder
## Fewest-hop routing. Every road edge has weight 1.


static func fewest_hops(start: String, goal: String, edges: Array) -> Array:
	if start == goal:
		return [start]
	var adj := {}
	for edge in edges:
		var a := str(edge["a"])
		var b := str(edge["b"])
		if not adj.has(a):
			adj[a] = []
		if not adj.has(b):
			adj[b] = []
		adj[a].append(b)
		adj[b].append(a)
	var dist := {start: 0}
	var prev := {}
	var queue: Array = [start]
	while not queue.is_empty():
		var node: String = queue.pop_front()
		if node == goal:
			break
		for nxt in adj.get(node, []):
			if dist.has(nxt):
				continue
			dist[nxt] = int(dist[node]) + 1
			prev[nxt] = node
			queue.append(nxt)
	if not dist.has(goal):
		return []
	var path: Array = [goal]
	var cursor: String = goal
	while cursor != start:
		cursor = str(prev[cursor])
		path.push_front(cursor)
	return path


static func edge_between(a: String, b: String, edges: Array) -> Dictionary:
	for edge in edges:
		var ea := str(edge["a"])
		var eb := str(edge["b"])
		if (ea == a and eb == b) or (ea == b and eb == a):
			return edge
	return {}


static func edge_points(a: String, b: String, edges: Array, places: Dictionary) -> PackedVector2Array:
	var edge := edge_between(a, b, edges)
	var pts := PackedVector2Array()
	if edge.is_empty():
		if places.has(a) and places.has(b):
			pts.append(Vector2(float(places[a]["x"]), float(places[a]["y"])))
			pts.append(Vector2(float(places[b]["x"]), float(places[b]["y"])))
		return pts
	var raw: Array = edge.get("points", [])
	if str(edge["a"]) == b and str(edge["b"]) == a:
		raw = raw.duplicate()
		raw.reverse()
	for p in raw:
		pts.append(Vector2(float(p[0]), float(p[1])))
	return pts


static func polyline_length(pts: PackedVector2Array) -> float:
	var total := 0.0
	for i in range(1, pts.size()):
		total += pts[i - 1].distance_to(pts[i])
	return total


static func point_along(pts: PackedVector2Array, distance: float) -> Vector2:
	if pts.is_empty():
		return Vector2.ZERO
	if pts.size() == 1:
		return pts[0]
	var remaining := maxf(0.0, distance)
	for i in range(1, pts.size()):
		var seg := pts[i - 1].distance_to(pts[i])
		if remaining <= seg or i == pts.size() - 1:
			var t := 0.0 if seg <= 0.0 else clampf(remaining / seg, 0.0, 1.0)
			return pts[i - 1].lerp(pts[i], t)
		remaining -= seg
	return pts[pts.size() - 1]


static func spring_offset(view: Vector2, content: Vector2, focus: Vector2) -> Vector2:
	## Offset that centers `focus` inside the view, clamped so the content
	## covers the viewport. A region that already fits clamps to 0.
	var target := focus - view * 0.5
	var max_x := maxf(0.0, content.x - view.x)
	var max_y := maxf(0.0, content.y - view.y)
	return Vector2(clampf(target.x, 0.0, max_x), clampf(target.y, 0.0, max_y))
