extends RefCounted
## Carrega e desenha as folhas de efeitos do pixelfx que ficam em assets/efeitos/.
## Cada efeito é um PNG + JSON (estilo Aseprite) com os quadros, o fps e o pivô.

const FOLDER := "res://assets/efeitos/"

static var _cache: Dictionary = {}


static func get_sheet(fx_name: String) -> Dictionary:
	if _cache.has(fx_name):
		return _cache[fx_name]
	var sheet: Dictionary = {}
	var png_path := FOLDER + fx_name + ".png"
	var json_path := FOLDER + fx_name + ".json"
	if ResourceLoader.exists(png_path) and FileAccess.file_exists(json_path):
		var data = JSON.parse_string(FileAccess.get_file_as_string(json_path))
		if typeof(data) == TYPE_DICTIONARY and data.has("frames") and data.has("meta"):
			var frames: Array = []
			for f in data["frames"]:
				var r: Dictionary = f["frame"]
				frames.append(Rect2(float(r["x"]), float(r["y"]), float(r["w"]), float(r["h"])))
			var meta: Dictionary = data["meta"].get("pixelfx", {})
			var pivot: Array = meta.get("pivot", [0, 0])
			sheet = {
				"texture": load(png_path),
				"frames": frames,
				"fps": float(meta.get("fps", 30)),
				"loop": bool(meta.get("loop", false)),
				"pivot": Vector2(float(pivot[0]), float(pivot[1])),
			}
	_cache[fx_name] = sheet
	return sheet


## Duração do efeito em quadros do jogo (60 por segundo). 0 se o efeito não existir.
static func length_frames(fx_name: String) -> int:
	var s := get_sheet(fx_name)
	if s.is_empty():
		return 0
	var frames: Array = s["frames"]
	return int(ceil(float(frames.size()) * 60.0 / float(s["fps"])))


## Desenha o quadro certo do efeito em `at`. Retorna false se o efeito não existe.
static func draw(ci: CanvasItem, fx_name: String, at: Vector2, t: int, flip: bool, scale: float) -> bool:
	var s := get_sheet(fx_name)
	if s.is_empty():
		return false
	var frames: Array = s["frames"]
	var idx := int(float(t) * float(s["fps"]) / 60.0)
	if s["loop"]:
		idx = idx % frames.size()
	elif idx >= frames.size():
		return true
	var src: Rect2 = frames[idx]
	var pivot: Vector2 = s["pivot"]
	ci.draw_set_transform(at, 0.0, Vector2(-scale if flip else scale, scale))
	ci.draw_texture_rect_region(s["texture"], Rect2(-pivot, src.size), src)
	ci.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	return true
