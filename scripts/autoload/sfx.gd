extends Node

const Pack := preload("res://scripts/core/packed_file.gd")


func play(name: String) -> void:
	var path := "res://art/sfx/%s.wav" % name
	if not Pack.exists(path):
		push_error("Missing sfx %s" % path)
		return
	var stream: AudioStream = load(path)
	if stream == null:
		push_error("Failed to load sfx %s" % path)
		return
	var player := AudioStreamPlayer.new()
	player.stream = stream
	add_child(player)
	player.finished.connect(player.queue_free)
	player.play()
