extends Node2D
## Um lutador. Toda a lógica roda em tick(), que o match chama 60 vezes por segundo.
## Nada aqui usa o tempo real, só quadros. Isso deixa os combos sempre iguais e
## prepara o jogo para ter online com rollback no futuro.
##
## Por enquanto o boneco é desenhado com formas simples. Quando os sprites
## estiverem prontos, só a parte de desenho (_draw) muda.

# Botões e direções, guardados como bits de um número inteiro.
const UP := 1
const DOWN := 2
const LEFT := 4
const RIGHT := 8
const LP := 16  # soco fraco
const HP := 32  # soco forte
const LK := 64  # chute fraco
const HK := 128  # chute forte

const MAX_HP := 1000
const MAX_POWER := 300  # 3 barras de especial, como no KOF
const FLOOR_Y := 620.0
const GRAVITY := 0.95
const JUMP_VEL := -19.0
const JUMP_VX := 5.0
const WALK_FORWARD := 4.5
const WALK_BACK := 3.5
const MOTION_WINDOW := 18  # quadros para completar um comando de especial
## Quantas unidades do mundo valem 1 pixel da tela base 304x224.
## Um lutador normal tem 185 unidades = 112 px, metade da altura da tela, como no KOF.
const WORLD_PER_PX := 185.0 / 112.0

enum State { IDLE, WALK, CROUCH, JUMP, ATTACK, HITSTUN, BLOCKSTUN, LAUNCHED, KNOCKDOWN, KO, WIN }

# Dados de quadro de cada golpe (o "frame data").
#   startup  = quadros antes do golpe acertar
#   active   = quadros em que o golpe pode acertar
#   recovery = quadros para voltar à base (aqui você fica vulnerável)
#   hitbox   = área do golpe. x positivo é para frente, y negativo é para cima, origem nos pés.
#   type     = "mid" (defende em pé ou agachado), "low" (só agachado), "overhead" (só em pé)
#   cancel   = pode cancelar em especial quando conecta
var moves: Dictionary = {
	"lp": {"startup": 4, "active": 3, "recovery": 7, "damage": 40, "hitstun": 14, "blockstun": 10,
		"push": 5.0, "hitstop": 7, "hitbox": Rect2(25, -132, 62, 22), "limb": "arm", "cancel": true},
	"hp": {"startup": 7, "active": 4, "recovery": 16, "damage": 85, "hitstun": 20, "blockstun": 15,
		"push": 7.0, "hitstop": 10, "hitbox": Rect2(25, -138, 88, 26), "limb": "arm", "cancel": true},
	"lk": {"startup": 5, "active": 3, "recovery": 9, "damage": 45, "hitstun": 14, "blockstun": 10,
		"push": 5.0, "hitstop": 7, "hitbox": Rect2(20, -78, 72, 22), "limb": "leg", "cancel": true},
	"hk": {"startup": 9, "active": 4, "recovery": 18, "damage": 95, "hitstun": 21, "blockstun": 15,
		"push": 8.0, "hitstop": 11, "hitbox": Rect2(20, -112, 98, 28), "limb": "leg"},
	"c_lp": {"startup": 4, "active": 3, "recovery": 7, "damage": 35, "hitstun": 13, "blockstun": 9,
		"push": 5.0, "hitstop": 6, "hitbox": Rect2(25, -88, 58, 20), "limb": "arm", "crouch": true, "cancel": true},
	"c_hp": {"startup": 6, "active": 5, "recovery": 18, "damage": 90, "hitstun": 20, "blockstun": 14,
		"push": 6.0, "hitstop": 10, "hitbox": Rect2(12, -190, 55, 80), "limb": "arm", "crouch": true,
		"cancel": true},
	"c_lk": {"startup": 5, "active": 3, "recovery": 10, "damage": 35, "hitstun": 14, "blockstun": 10,
		"push": 5.0, "hitstop": 6, "hitbox": Rect2(20, -24, 80, 20), "limb": "leg", "crouch": true,
		"type": "low", "cancel": true},
	"c_hk": {"startup": 10, "active": 4, "recovery": 22, "damage": 80, "hitstun": 0, "blockstun": 14,
		"push": 6.0, "hitstop": 10, "hitbox": Rect2(20, -22, 105, 20), "limb": "leg", "crouch": true,
		"type": "low", "knockdown": true},
	"j_p": {"startup": 5, "active": 8, "recovery": 5, "damage": 60, "hitstun": 16, "blockstun": 12,
		"push": 4.0, "hitstop": 8, "hitbox": Rect2(15, -125, 62, 30), "limb": "arm", "air": true,
		"type": "overhead"},
	"j_k": {"startup": 6, "active": 10, "recovery": 6, "damage": 75, "hitstun": 18, "blockstun": 13,
		"push": 4.0, "hitstop": 9, "hitbox": Rect2(10, -62, 68, 36), "limb": "leg", "air": true,
		"type": "overhead"},
	# Especial 1: Rajada. Baixo, baixo-frente, frente + soco. Solta um projétil.
	"fireball": {"startup": 13, "active": 0, "recovery": 28, "pose": Rect2(30, -140, 50, 28),
		"limb": "arm", "projectile": true},
	# Especial 2: Chute Ciclone. Baixo, baixo-trás, trás + chute. Avança girando e derruba.
	"cyclone": {"startup": 8, "active": 16, "recovery": 14, "damage": 110, "hitstun": 0, "blockstun": 16,
		"push": 7.0, "hitstop": 10, "hitbox": Rect2(0, -118, 88, 48), "limb": "leg", "vx": 6.5,
		"knockdown": true},
}

var player_index := 0
var character := ""  # nome da pasta em sprites/ (ex.: "kaio"). Sem sprite, usa o boneco desenhado.
var display_name := ""  # nome mostrado no HUD, com acentos (ex.: "Pengaró"). Vazio usa character.
var color := Color.WHITE
var opponent  # o outro lutador
var debug_boxes := false

var pos := Vector2.ZERO
var vel := Vector2.ZERO
var push_vel := 0.0
var facing := 1
var state: int = State.IDLE
var state_frame := 0
var hp := MAX_HP
var power := 0
var move_id := ""
var move: Dictionary = {}
var hit_landed := false
var stun_frames := 0
var combo_hits := 0
var spawn_projectile := false
var projectile_out := false
var air_attack_used := false
var input_now := 0
var input_prev := 0
var dir_history: Array[int] = []

# Só para o visual (não afeta a lógica).
var anim_time := 0.0
var crouch_amt := 0.0
var flash := 0
var _df := 1  # direção usada no desenho
var _sheet: Dictionary = {}
var _sheet_loaded := false


func reset(x: float, face: int) -> void:
	pos = Vector2(x, FLOOR_Y)
	vel = Vector2.ZERO
	push_vel = 0.0
	facing = face
	state = State.IDLE
	state_frame = 0
	hp = MAX_HP
	move_id = ""
	move = {}
	hit_landed = false
	stun_frames = 0
	combo_hits = 0
	spawn_projectile = false
	air_attack_used = false
	input_now = 0
	input_prev = 0
	dir_history.clear()
	crouch_amt = 0.0
	flash = 0
	position = pos
	queue_redraw()


# ---------------------------------------------------------------- entrada

func pressed(btn: int) -> bool:
	return (input_now & btn) != 0 and (input_prev & btn) == 0


## Converte a entrada na "notação numpad" usada pela comunidade de jogos de luta,
## já relativa ao lado que o lutador olha: 6 = frente, 4 = trás, 2 = baixo, 8 = cima, 3 = baixo-frente...
func numpad_dir(bits: int) -> int:
	var x := 0
	if (bits & RIGHT) != 0:
		x += 1
	if (bits & LEFT) != 0:
		x -= 1
	x *= facing
	var y := 0
	if (bits & UP) != 0:
		y = 1
	elif (bits & DOWN) != 0:
		y = -1
	return 5 + x + y * 3


func _has_motion(seq: Array) -> bool:
	var idx := seq.size() - 1
	var stop := maxi(0, dir_history.size() - MOTION_WINDOW)
	var i := dir_history.size() - 1
	while i >= stop:
		if dir_history[i] == seq[idx]:
			idx -= 1
			if idx < 0:
				return true
		i -= 1
	return false


# ---------------------------------------------------------------- lógica por quadro

func tick(bits: int) -> void:
	input_prev = input_now
	input_now = bits
	dir_history.append(numpad_dir(bits))
	if dir_history.size() > 32:
		dir_history.pop_front()
	state_frame += 1

	match state:
		State.IDLE, State.WALK, State.CROUCH:
			_tick_neutral()
		State.JUMP:
			_tick_jump()
		State.ATTACK:
			_tick_attack()
		State.HITSTUN, State.BLOCKSTUN:
			stun_frames -= 1
			if stun_frames <= 0:
				_enter(State.IDLE)
		State.KNOCKDOWN:
			if state_frame >= 45:
				_enter(State.IDLE)
		_:
			pass

	_apply_physics()
	_update_visuals()


func _tick_neutral() -> void:
	_face_opponent()
	vel.x = 0.0
	if _try_special():
		return
	var d := numpad_dir(input_now)
	var crouching := d <= 3
	if pressed(LP):
		_start_move("c_lp" if crouching else "lp")
		return
	if pressed(HP):
		_start_move("c_hp" if crouching else "hp")
		return
	if pressed(LK):
		_start_move("c_lk" if crouching else "lk")
		return
	if pressed(HK):
		_start_move("c_hk" if crouching else "hk")
		return
	if d >= 7:
		vel.y = JUMP_VEL
		vel.x = float(d - 8) * JUMP_VX * facing
		air_attack_used = false
		_enter(State.JUMP)
		return
	if crouching:
		_enter(State.CROUCH)
	elif d == 6:
		_enter(State.WALK)
		vel.x = WALK_FORWARD * facing
	elif d == 4:
		_enter(State.WALK)
		vel.x = -WALK_BACK * facing
	else:
		_enter(State.IDLE)


func _tick_jump() -> void:
	if air_attack_used:
		return
	if pressed(LP) or pressed(HP):
		air_attack_used = true
		_start_move("j_p")
	elif pressed(LK) or pressed(HK):
		air_attack_used = true
		_start_move("j_k")


func _tick_attack() -> void:
	var startup: int = move["startup"]
	var active: int = move["active"]
	var total: int = startup + active + int(move["recovery"])
	var f := state_frame
	if move.has("vx"):
		if f > startup and f <= startup + active:
			vel.x = float(move["vx"]) * facing
		else:
			vel.x = 0.0
	if move.get("projectile", false) and f == startup:
		spawn_projectile = true
	if hit_landed and move.get("cancel", false) and _try_special():
		return
	if f >= total:
		move_id = ""
		if move.get("air", false) and not is_grounded():
			_enter_force(State.JUMP)
		else:
			_enter_force(State.IDLE)


func _try_special() -> bool:
	if not is_grounded():
		return false
	if (pressed(LP) or pressed(HP)) and not projectile_out and _has_motion([2, 3, 6]):
		_start_move("fireball")
		return true
	if (pressed(LK) or pressed(HK)) and _has_motion([2, 1, 4]):
		_start_move("cyclone")
		return true
	return false


func _start_move(id: String) -> void:
	move_id = id
	move = moves[id]
	hit_landed = false
	_enter_force(State.ATTACK)
	if not move.get("air", false):
		vel.x = 0.0


func _enter(s: int) -> void:
	if s != state:
		state = s
		state_frame = 0
	if s == State.IDLE or s == State.WALK or s == State.CROUCH:
		combo_hits = 0


func _enter_force(s: int) -> void:
	state = s
	state_frame = 0


func _face_opponent() -> void:
	if opponent == null:
		return
	var dx: float = opponent.pos.x - pos.x
	if absf(dx) > 1.0:
		facing = 1 if dx > 0.0 else -1


func is_grounded() -> bool:
	return pos.y >= FLOOR_Y and vel.y >= 0.0


func _apply_physics() -> void:
	var airborne := pos.y < FLOOR_Y or vel.y < 0.0
	if airborne:
		vel.y += GRAVITY
	pos += vel
	pos.x += push_vel
	push_vel *= 0.8
	if absf(push_vel) < 0.05:
		push_vel = 0.0
	if pos.y >= FLOOR_Y:
		pos.y = FLOOR_Y
		if airborne and vel.y > 0.0:
			_on_land()
		vel.y = 0.0


func _on_land() -> void:
	match state:
		State.JUMP:
			_enter_force(State.IDLE)
			vel.x = 0.0
		State.ATTACK:
			if move.get("air", false):
				move_id = ""
				_enter_force(State.IDLE)
				vel.x = 0.0
		State.LAUNCHED:
			_enter_force(State.KNOCKDOWN)
			vel.x = 0.0
		_:
			vel.x = 0.0


# ---------------------------------------------------------------- golpes

func _is_crouching_pose() -> bool:
	if state == State.CROUCH:
		return true
	if state == State.ATTACK and move.get("crouch", false):
		return true
	if state == State.BLOCKSTUN and numpad_dir(input_now) <= 3:
		return true
	return false


func _to_world(r: Rect2) -> Rect2:
	if facing == 1:
		return Rect2(pos + r.position, r.size)
	return Rect2(Vector2(pos.x - r.position.x - r.size.x, pos.y + r.position.y), r.size)


## Área onde o lutador pode ser acertado. Vazia quando está invencível (caído).
func hurtbox() -> Rect2:
	if state == State.KNOCKDOWN or state == State.KO or state == State.LAUNCHED or state == State.WIN:
		return Rect2()
	var r: Rect2
	if not is_grounded():
		r = Rect2(-30, -155, 60, 118)
	elif _is_crouching_pose():
		r = Rect2(-36, -112, 72, 112)
	else:
		r = Rect2(-36, -185, 72, 185)
	return _to_world(r)


## Área do golpe nos quadros ativos. Vazia no resto do tempo.
func active_hitbox() -> Rect2:
	if state != State.ATTACK or hit_landed or not move.has("hitbox"):
		return Rect2()
	var startup: int = move["startup"]
	var active: int = move["active"]
	if state_frame > startup and state_frame <= startup + active:
		return _to_world(move["hitbox"])
	return Rect2()


func has_pushbox() -> bool:
	return state != State.KO


func _can_block(kind: String) -> bool:
	if not is_grounded():
		return false
	if state != State.IDLE and state != State.WALK and state != State.CROUCH and state != State.BLOCKSTUN:
		return false
	var d := numpad_dir(input_now)
	if kind == "low":
		return d == 1
	if kind == "overhead":
		return d == 4
	return d == 1 or d == 4


## Recebe um golpe. Retorna true se defendeu.
func receive_hit(m: Dictionary, from_facing: int) -> bool:
	var kind: String = m.get("type", "mid")
	if _can_block(kind):
		_enter_force(State.BLOCKSTUN)
		stun_frames = int(m["blockstun"])
		vel.x = 0.0
		push_vel = from_facing * float(m["push"]) * 0.8
		add_power(4)
		return true
	combo_hits += 1
	var scaling := maxf(0.3, 1.0 - 0.12 * float(combo_hits - 1))
	hp = maxi(0, hp - roundi(float(m["damage"]) * scaling))
	flash = 6
	move_id = ""
	add_power(8)
	if hp <= 0:
		_enter_force(State.KO)
		vel = Vector2(from_facing * 6.0, -11.0)
	elif not is_grounded() or m.get("knockdown", false):
		_enter_force(State.LAUNCHED)
		vel = Vector2(from_facing * 4.5, -9.0)
	else:
		_enter_force(State.HITSTUN)
		stun_frames = int(m["hitstun"])
		vel.x = 0.0
		push_vel = from_facing * float(m["push"])
	return false


func add_power(amount: int) -> void:
	power = mini(MAX_POWER, power + amount)


func set_winner() -> void:
	if is_grounded() and state != State.KO and state != State.KNOCKDOWN and state != State.LAUNCHED:
		_enter_force(State.WIN)
		vel.x = 0.0


# ---------------------------------------------------------------- desenho

func _update_visuals() -> void:
	anim_time += 1.0
	var target := 1.0 if _is_crouching_pose() else 0.0
	crouch_amt = lerpf(crouch_amt, target, 0.35)
	if flash > 0:
		flash -= 1
	position = pos
	queue_redraw()


## 0 = braço ou perna recolhido, 1 = totalmente esticado. Suavizado para a animação ficar fluida.
func _extension() -> float:
	if state != State.ATTACK or move.is_empty():
		return 0.0
	var s := float(move["startup"])
	var a := float(move["active"])
	var r := float(move["recovery"])
	var f := float(state_frame)
	if f <= s:
		return sin(clampf(f / maxf(s, 1.0), 0.0, 1.0) * PI * 0.5)
	if f <= s + a:
		return 1.0
	var t := clampf(1.0 - (f - s - a) / maxf(r, 1.0), 0.0, 1.0)
	return t * t * (3.0 - 2.0 * t)


func _limb_target() -> Vector2:
	var hb: Rect2 = move.get("hitbox", move.get("pose", Rect2(30, -130, 40, 20)))
	return Vector2(hb.position.x + hb.size.x - 8.0, hb.position.y + hb.size.y * 0.5)


func _p(v: Vector2) -> Vector2:
	return Vector2(v.x * _df, v.y)


func _limb(a: Vector2, b: Vector2, w: float, c: Color) -> void:
	draw_line(_p(a), _p(b), c, w, true)
	draw_circle(_p(a), w * 0.5, c)
	draw_circle(_p(b), w * 0.5, c)


func _draw() -> void:
	_df = facing
	if move_id == "cyclone" and state == State.ATTACK and state_frame > int(move["startup"]):
		_df = facing if (state_frame / 3) % 2 == 0 else -facing  # gira

	# sombra
	draw_set_transform(Vector2(0, FLOOR_Y - pos.y), 0.0, Vector2(1.0, 0.22))
	draw_circle(Vector2.ZERO, 48.0, Color(0, 0, 0, 0.35))
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)

	if _draw_sprite():
		_draw_debug_boxes()
		return

	var body := color
	if flash > 0:
		body = color.lightened(0.6)
	var dark := body.darkened(0.4)
	var skin := Color(0.93, 0.76, 0.6)
	if flash > 0:
		skin = skin.lightened(0.5)

	if (state == State.KNOCKDOWN or state == State.KO) and is_grounded():
		_draw_lying(body, dark, skin)
	else:
		_draw_body(body, dark, skin)
	_draw_debug_boxes()


func _draw_debug_boxes() -> void:
	if debug_boxes:
		var hb := hurtbox()
		if hb.has_area():
			draw_rect(Rect2(hb.position - pos, hb.size), Color(0.2, 0.6, 1.0, 0.3))
			draw_rect(Rect2(hb.position - pos, hb.size), Color(0.2, 0.6, 1.0), false, 2.0)
		var ab := active_hitbox()
		if ab.has_area():
			draw_rect(Rect2(ab.position - pos, ab.size), Color(1.0, 0.1, 0.1, 0.4))
			draw_rect(Rect2(ab.position - pos, ab.size), Color(1.0, 0.1, 0.1), false, 2.0)


func _draw_lying(body: Color, dark: Color, skin: Color) -> void:
	_limb(Vector2(-5, -14), Vector2(48, -8), 15.0, dark)
	_limb(Vector2(-5, -18), Vector2(52, -20), 15.0, dark)
	_limb(Vector2(-10, -16), Vector2(-78, -14), 34.0, body)
	draw_circle(_p(Vector2(-100, -16)), 18.0, skin)
	_limb(Vector2(-60, -22), Vector2(-40, -40), 11.0, skin)


func _draw_body(body: Color, dark: Color, skin: Color) -> void:
	var c := crouch_amt
	var air := not is_grounded()
	var ext := _extension()
	var limb: String = move.get("limb", "") if state == State.ATTACK else ""
	var target := _limb_target()

	var bob := 0.0
	if state == State.IDLE:
		bob = sin(anim_time * 0.09) * 3.0
	var lean := 0.0
	match state:
		State.HITSTUN:
			lean = -16.0 * (float(stun_frames) / 20.0 + 0.3)
		State.BLOCKSTUN:
			lean = -6.0
		State.LAUNCHED, State.KO:
			lean = -24.0
		State.ATTACK:
			lean = 10.0 * ext
		State.WALK:
			lean = 4.0 if vel.x * facing > 0.0 else -3.0

	var hip := Vector2(lean * 0.4, lerpf(-86.0, -50.0, c) + bob * 0.4)
	var neck := Vector2(lean, hip.y - lerpf(66.0, 58.0, c) + bob)
	if air:
		hip = Vector2(lean * 0.4, -96.0)
		neck = Vector2(lean, -160.0)

	# pernas
	var foot_b := Vector2(-22, 0)
	var foot_f := Vector2(24, 0)
	if state == State.WALK:
		var s := sin(anim_time * 0.28)
		foot_b += Vector2(s * 14.0, -maxf(0.0, s) * 8.0)
		foot_f += Vector2(-s * 14.0, -maxf(0.0, -s) * 8.0)
	foot_b.x -= 12.0 * c
	foot_f.x += 12.0 * c
	if air:
		foot_b = Vector2(-20, -52)
		foot_f = Vector2(22, -58)
	var knee_b := (hip + foot_b) * 0.5 + Vector2(6.0 + 12.0 * c, -4.0)
	var knee_f := (hip + foot_f) * 0.5 + Vector2(10.0 + 16.0 * c, -4.0)
	if air:
		knee_b = hip + Vector2(10, 30)
		knee_f = hip + Vector2(30, 22)
	_limb(hip, knee_b, 17.0, dark)
	_limb(knee_b, foot_b, 14.0, dark)

	# braço de trás
	var sh := neck + Vector2(0, 10)
	var hand_b := sh + Vector2(14, 32)
	if state == State.BLOCKSTUN:
		hand_b = sh + Vector2(26, 2)
	elif move_id == "fireball":
		hand_b = sh.lerp(target + Vector2(-6, 10), ext)
	_limb(sh + Vector2(-10, 4), sh + Vector2(-6, 30), 12.0, skin.darkened(0.15))
	_limb(sh + Vector2(-6, 30), hand_b, 11.0, skin.darkened(0.15))
	draw_circle(_p(hand_b), 9.0, Color(0.85, 0.85, 0.85))

	# tronco
	draw_colored_polygon(PackedVector2Array([
		_p(hip + Vector2(-17, 6)), _p(hip + Vector2(17, 6)),
		_p(sh + Vector2(22, 0)), _p(sh + Vector2(-20, -2)),
	]), body)
	draw_line(_p(hip + Vector2(-18, 0)), _p(hip + Vector2(18, 0)), dark, 7.0)

	# perna da frente (ou chute)
	if limb == "leg":
		var kick_end := foot_f.lerp(target, ext)
		var kick_knee := hip.lerp(kick_end, 0.5) + Vector2(0, -14.0 * (1.0 - ext))
		_limb(hip, kick_knee, 17.0, body.darkened(0.25))
		_limb(kick_knee, kick_end, 14.0, body.darkened(0.25))
		draw_circle(_p(kick_end), 9.0, skin)
	else:
		_limb(hip, knee_f, 17.0, body.darkened(0.25))
		_limb(knee_f, foot_f, 14.0, body.darkened(0.25))

	# cabeça e faixa
	var head := neck + Vector2(4, -20)
	draw_circle(_p(head), 18.0, skin)
	draw_line(_p(head + Vector2(-16, -6)), _p(head + Vector2(17, -6)), color.lightened(0.3), 6.0)
	var wave := sin(anim_time * 0.3) * 5.0
	draw_line(_p(head + Vector2(-16, -6)), _p(head + Vector2(-36, 2.0 + wave)), color.lightened(0.3), 4.0)

	# braço da frente (ou soco)
	var hand_f := sh + Vector2(34, 16)
	var elbow_f := sh + Vector2(24, 34)
	if limb == "arm":
		hand_f = hand_f.lerp(target, ext)
		elbow_f = sh.lerp(hand_f, 0.5) + Vector2(0, 14.0 * (1.0 - ext))
	elif state == State.BLOCKSTUN:
		hand_f = sh + Vector2(32, -8)
		elbow_f = sh + Vector2(30, 18)
	elif state == State.WIN:
		hand_f = sh + Vector2(8, -62)
		elbow_f = sh + Vector2(18, -30)
	_limb(sh + Vector2(12, 4), elbow_f, 12.0, skin)
	_limb(elbow_f, hand_f, 11.0, skin)
	draw_circle(_p(hand_f), 10.0, Color.WHITE)
	if move_id == "fireball" and state == State.ATTACK and state_frame <= int(move["startup"]) + 4:
		draw_circle(_p(target), 6.0 + 14.0 * ext, Color(color.lightened(0.5), 0.5))


# ---------------------------------------------------------------- sprites

## Lê sprites/<personagem>/pixel/<personagem>.png + .json, gerados por ferramentas/pixelizar.py.
func _load_sheet() -> void:
	_sheet_loaded = true
	if character == "":
		return
	var base := "res://sprites/%s/pixel/%s" % [character, character]
	if not ResourceLoader.exists(base + ".png") or not FileAccess.file_exists(base + ".json"):
		return
	var data = JSON.parse_string(FileAccess.get_file_as_string(base + ".json"))
	if typeof(data) != TYPE_DICTIONARY or not data.has("frames"):
		return
	var frames: Dictionary = {}
	for k in data["frames"]:
		var r: Dictionary = data["frames"][k]["frame"]
		frames[k] = Rect2(float(r["x"]), float(r["y"]), float(r["w"]), float(r["h"]))
	var pv: Dictionary = data["meta"].get("pivot", {"x": 0, "y": 0})
	_sheet = {"texture": load(base + ".png"), "frames": frames, "pivot": Vector2(float(pv["x"]), float(pv["y"]))}


func _pose_name() -> String:
	match state:
		State.WALK:
			return "andando"
		State.CROUCH:
			return "agachado"
		State.JUMP:
			return "pulo"
		State.BLOCKSTUN:
			return "defesa"
		State.HITSTUN, State.LAUNCHED, State.KO, State.KNOCKDOWN:
			return "apanhando"
		State.ATTACK:
			if move_id == "fireball":
				return "especial"
			# "rasteira" é o "especial" sem a bola: serve para os golpes rentes ao chão.
			if move_id == "cyclone" or move_id == "c_lk" or move_id == "c_hk":
				return "rasteira"
			if move_id == "c_lp":
				return "agachado"  # ainda sem pose própria; a de soco é em pé e mostraria ele alto demais
			if _extension() < 0.35:
				return "agachado" if move.get("crouch", false) else ("pulo" if move.get("air", false) else "parado")
			return "soco" if move.get("limb", "") == "arm" else "chute"
	return "parado"


func _draw_sprite() -> bool:
	if not _sheet_loaded:
		_load_sheet()
	if _sheet.is_empty():
		return false
	var frames: Dictionary = _sheet["frames"]
	var pose := _pose_name()
	if pose == "rasteira" and not frames.has(pose):
		pose = "especial"
	if not frames.has(pose):
		pose = "parado"
		if not frames.has(pose):
			return false
	var src: Rect2 = frames[pose]
	var pivot: Vector2 = _sheet["pivot"]
	var rot := 0.0
	var off := Vector2.ZERO
	if (state == State.KNOCKDOWN or state == State.KO) and is_grounded():
		rot = -PI * 0.5  # deitado de costas (a escala negativa de _df já espelha depois de girar)
		off = Vector2(50.0 * _df, -47.0) * WORLD_PER_PX  # apoia o corpo no chão, centrado em pos
	elif state == State.HITSTUN:
		off.x = sin(float(state_frame) * 2.0) * 2.0
	var mod := Color(1.0, 0.55, 0.55) if flash > 0 else Color.WHITE
	draw_set_transform(off, rot, Vector2(WORLD_PER_PX * _df, WORLD_PER_PX))
	draw_texture_rect_region(_sheet["texture"], Rect2(-pivot, src.size), src, mod)
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	return true
