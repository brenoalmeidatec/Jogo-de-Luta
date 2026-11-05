extends Node2D
## Faíscas de golpe, defesa e queda. Usa as folhas do pixelfx (assets/efeitos/).
## Se um arquivo faltar, desenha uma faísca simples no lugar.

const Fx := preload("res://scripts/fx_library.gd")
const FX_SCALE := 185.0 / 112.0  # 1 pixel do efeito = 1 pixel da tela base (escala 2 ficou grande demais)

var items: Array = []


func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST


## kind: "light", "heavy", "block", "clash", "landing"
func spawn(at: Vector2, kind: String, flip: bool) -> void:
	var fx_name: String = {
		"light": "hit-spark", "heavy": "crit-hit", "block": "shield-block",
		"clash": "zap-hit", "landing": "heavy-landing",
	}.get(kind, "hit-spark")
	var life := Fx.length_frames(fx_name)
	if life <= 0:
		fx_name = ""
		life = 16
	items.append({"pos": at, "t": 0, "life": life, "fx": fx_name, "kind": kind, "flip": flip})


func tick() -> void:
	for it in items:
		it["t"] += 1
	items = items.filter(func(it): return it["t"] < it["life"])
	queue_redraw()


func _draw() -> void:
	for it in items:
		var p: Vector2 = it["pos"]
		var t: int = it["t"]
		var fx_name: String = it["fx"]
		if fx_name != "" and Fx.draw(self, fx_name, p, t, it["flip"], FX_SCALE):
			continue
		var k := float(t) / float(it["life"])
		var col := Color(0.5, 0.8, 1.0) if it["kind"] == "block" else Color(1.0, 0.85, 0.3)
		col.a = 1.0 - k
		var r := 24.0 * (0.4 + k)
		draw_arc(p, r, 0.0, TAU, 24, col, 4.0 * (1.0 - k) + 1.0)
		for i in 8:
			var d := Vector2.from_angle(float(i) * TAU / 8.0)
			draw_line(p + d * r * 0.6, p + d * r * 1.6, col, 3.0)
