extends Object
class_name PackedFile
## File checks that still work after export.
## An exported PCK stores imported art as a resource, not the raw PNG, so
## FileAccess.file_exists() is false for those paths while load() still works.


static func exists(path: String) -> bool:
	if ResourceLoader.exists(path):
		return true
	return FileAccess.file_exists(path)


static func text(path: String) -> String:
	if not FileAccess.file_exists(path):
		push_error("Packed file missing: %s" % path)
		return ""
	return FileAccess.get_file_as_string(path)


static func json(path: String) -> Variant:
	var body := text(path)
	if body == "":
		return null
	var parsed: Variant = JSON.parse_string(body)
	if parsed == null:
		push_error("Packed JSON failed: %s" % path)
	return parsed
