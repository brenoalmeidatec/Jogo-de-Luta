extends Node2D
## Projétil do especial "Rajada". Usa a bola de fogo do pixelfx se ela existir.

const Fx := preload("res://scripts/fx_library.gd")
const MOVE := {"damage": 70, "hitstun": 18, "blockstun": 14, "push": 6.0, "hitstop": 8, "type": "mid"}
const SPEED := 7.0
const FX_SCALE := 185.0 / 112.0  # 1 pixel do efeito = 1 pixel da tela base (escala 2 ficou grande demais)

var shooter: Node2D
var pos := Vector2.ZERO
var vx := 0.0
var color := Color.WHITE
var alive := true
var frame := 0


func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST


func tick() -> void:
	frame += 1
	pos.x += vx
	position = pos
	if pos.x < -100.0 or pos.x > 1200.0:
		alive = false
	queue_redraw()


func hitbox() -> Rect2:
	return Rect2(pos.x - 30.0, pos.y - 26.0, 52.0, 52.0)


func _draw() -> void:
	if Fx.draw(self, "fireball", Vector2.ZERO, frame, vx < 0.0, FX_SCALE):
		return
	var dir := signf(vx)
	for i in 5:
		draw_circle(Vector2(-dir * float(i) * 12.0, 0.0), 22.0 - float(i) * 3.0, Color(color.lightened(0.3), 0.12 + 0.05 * float(5 - i)))
	draw_circle(Vector2.ZERO, 20.0 + sin(float(frame) * 0.5) * 2.0, Color(color.lightened(0.4), 0.85))
	draw_circle(Vector2.ZERO, 11.0, Color(1, 1, 1, 0.95))
