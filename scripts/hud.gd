extends Control
## HUD no estilo KOF, desenhado em pixels da tela base 304x224.
## As posições vêm de ferramentas/hud_layout.json (barras de vida no topo que esvaziam
## para o centro, tempo no meio, retratos, barra de especial com estoque embaixo).

const LIFE_P1 := Rect2(8, 14, 124, 9)
const LIFE_P2 := Rect2(172, 14, 124, 9)
const TIME_BOX := Rect2(136, 8, 32, 22)
const PORTRAIT_P1 := Rect2(8, 26, 20, 20)
const PORTRAIT_P2 := Rect2(276, 26, 20, 20)
const NAME_P1 := Vector2(31, 28)
const NAME_P2_RIGHT := Vector2(273, 28)
const POWER_P1 := Rect2(22, 210, 80, 6)
const POWER_P2 := Rect2(202, 210, 80, 6)
const STOCK_P1 := Vector2(8, 206)
const STOCK_P2 := Vector2(286, 206)

const LIFE_COLOR := Color("#f8d838")
const DAMAGE_COLOR := Color("#d83818")
const BACK_COLOR := Color("#281828")
const FRAME_COLOR := Color("#f8d838")
const POWER_COLOR := Color("#3898f8")

var game  # o match
var trail := [1000.0, 1000.0]
var trail_delay := [0, 0]
var last_hp := [1000, 1000]
var combo_show := [0, 0]
var combo_timer := [0, 0]


func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	size = Vector2(304, 224)


func reset() -> void:
	trail = [1000.0, 1000.0]
	trail_delay = [0, 0]
	last_hp = [1000, 1000]
	combo_show = [0, 0]
	combo_timer = [0, 0]


func fighter_name(f) -> String:
	if f.character != "":
		return String(f.character).to_upper()
	return "JOGADOR %d" % (f.player_index + 1)


func tick() -> void:
	var fs := [game.p1, game.p2]
	for i in 2:
		var f = fs[i]
		var hp: int = f.hp
		if hp < last_hp[i]:
			trail_delay[i] = 30  # a parte vermelha espera um pouco antes de descer
		last_hp[i] = hp
		if trail_delay[i] > 0:
			trail_delay[i] -= 1
		elif trail[i] > float(hp):
			trail[i] = maxf(float(hp), trail[i] - 8.0)
		if trail[i] < float(hp):
			trail[i] = float(hp)
		# combo de quem bate aparece do lado dele
		var other = fs[1 - i]
		if other.combo_hits >= 2:
			combo_show[i] = other.combo_hits
			combo_timer[i] = 60
		elif combo_timer[i] > 0:
			combo_timer[i] -= 1
	queue_redraw()


func _draw() -> void:
	if game == null:
		return
	var font: Font = ThemeDB.fallback_font
	_life_bar(LIFE_P1, game.p1.hp, trail[0], true)
	_life_bar(LIFE_P2, game.p2.hp, trail[1], false)

	# tempo
	draw_rect(TIME_BOX, Color(0.05, 0.04, 0.08))
	draw_rect(TIME_BOX, FRAME_COLOR, false, 1.0)
	var secs := int(ceil(float(game.timer_frames) / 60.0))
	_text(font, Vector2(TIME_BOX.position.x, TIME_BOX.position.y + 17), "%02d" % secs, 16, TIME_BOX.size.x, HORIZONTAL_ALIGNMENT_CENTER, Color.WHITE)

	# retratos, nomes e rounds ganhos
	_portrait(PORTRAIT_P1, game.p1)
	_portrait(PORTRAIT_P2, game.p2)
	_text(font, NAME_P1 + Vector2(0, 8), fighter_name(game.p1), 8, -1, HORIZONTAL_ALIGNMENT_LEFT, Color.WHITE)
	_text(font, Vector2(NAME_P2_RIGHT.x - 100, NAME_P2_RIGHT.y + 8), fighter_name(game.p2), 8, 100, HORIZONTAL_ALIGNMENT_RIGHT, Color.WHITE)
	for w in int(game.wins[0]):
		draw_rect(Rect2(LIFE_P1.end.x - 6 - w * 8, 26, 5, 5), FRAME_COLOR)
	for w in int(game.wins[1]):
		draw_rect(Rect2(LIFE_P2.position.x + 1 + w * 8, 26, 5, 5), FRAME_COLOR)

	# barra de especial
	_power_bar(POWER_P1, STOCK_P1, game.p1.power, true, font)
	_power_bar(POWER_P2, STOCK_P2, game.p2.power, false, font)

	# combos
	if combo_timer[0] > 0:
		_text(font, Vector2(8, 70), "%d HITS" % combo_show[0], 12, -1, HORIZONTAL_ALIGNMENT_LEFT, LIFE_COLOR)
	if combo_timer[1] > 0:
		_text(font, Vector2(196, 70), "%d HITS" % combo_show[1], 12, 100, HORIZONTAL_ALIGNMENT_RIGHT, LIFE_COLOR)

	# mensagens do centro
	var lines: PackedStringArray = String(game.message).split("\n")
	for i in lines.size():
		var fs := 24 if i == 0 else 10
		_text(font, Vector2(0, 104 + i * 20), lines[i], fs, 304, HORIZONTAL_ALIGNMENT_CENTER, Color.WHITE)


func _text(font: Font, at: Vector2, s: String, fs: int, width: float, align: HorizontalAlignment, col: Color) -> void:
	draw_string_outline(font, at, s, align, width, fs, 3, Color(0, 0, 0))
	draw_string(font, at, s, align, width, fs, col)


func _life_bar(r: Rect2, hp: int, tr: float, left_side: bool) -> void:
	draw_rect(r.grow(1), Color(0, 0, 0))
	draw_rect(r, BACK_COLOR)
	var tw := r.size.x * tr / 1000.0
	var hw := r.size.x * float(hp) / 1000.0
	# esvazia em direção ao centro: a parte cheia fica colada no tempo
	if left_side:
		draw_rect(Rect2(r.end.x - tw, r.position.y, tw, r.size.y), DAMAGE_COLOR)
		draw_rect(Rect2(r.end.x - hw, r.position.y, hw, r.size.y), LIFE_COLOR)
	else:
		draw_rect(Rect2(r.position.x, r.position.y, tw, r.size.y), DAMAGE_COLOR)
		draw_rect(Rect2(r.position.x, r.position.y, hw, r.size.y), LIFE_COLOR)
	draw_line(r.position + Vector2(0, 1), Vector2(r.end.x, r.position.y + 1), Color(1, 1, 1, 0.5), 1.0)


func _portrait(r: Rect2, f) -> void:
	draw_rect(r, Color(0.2, 0.18, 0.28))
	var c: Color = f.color
	draw_rect(r.grow(-3), c.darkened(0.2))
	draw_rect(r, FRAME_COLOR, false, 1.0)


func _power_bar(r: Rect2, stock_at: Vector2, power: int, left_side: bool, font: Font) -> void:
	var stocks := power / 100
	var frac := 1.0 if stocks >= 3 else float(power % 100) / 100.0
	draw_rect(r.grow(1), Color(0, 0, 0))
	draw_rect(r, Color(0.08, 0.07, 0.15))
	var w := r.size.x * frac
	var col := Color.WHITE if stocks >= 3 and (Engine.get_physics_frames() / 6) % 2 == 0 else POWER_COLOR
	if left_side:
		draw_rect(Rect2(r.position.x, r.position.y, w, r.size.y), col)
	else:
		draw_rect(Rect2(r.end.x - w, r.position.y, w, r.size.y), col)
	var box := Rect2(stock_at, Vector2(10, 12))
	draw_rect(box, Color(0, 0, 0))
	draw_rect(box, POWER_COLOR, false, 1.0)
	_text(font, stock_at + Vector2(0, 10), str(stocks), 10, 10, HORIZONTAL_ALIGNMENT_CENTER, Color.WHITE)
