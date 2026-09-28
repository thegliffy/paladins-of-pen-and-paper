extends Node


func play(name: String) -> void:
	var path := "res://art/sfx/%s.wav" % name
	if not FileAccess.file_exists(path):
		return
	var player := AudioStreamPlayer.new()
	player.stream = load(path)
	add_child(player)
	player.finished.connect(player.queue_free)
	player.play()
