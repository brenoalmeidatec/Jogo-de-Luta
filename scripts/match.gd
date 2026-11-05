extends Node2D
## Controla a luta: lê os comandos, avança os lutadores quadro a quadro,
## checa os golpes, cuida da câmera, dos rounds e do tempo.
##
## Escala estilo KOF: a tela base tem 304x224 pixels e o lutador normal tem 112 px
## (metade da altura). No mundo, 1 pixel da tela vale WORLD_PER_PX unidades.

const FighterScript := preload("res://scripts/fighter.gd")
const ProjectileScript := preload("res://scripts/projectile.gd")
const HudScript := preload("res://scripts/hud.gd")
const EffectsScript := preload("res://scripts/effects.gd")
const Controls := preload("res://scripts/controls.gd")

const K := 185.0 / 112.0  # unidades do mundo por pixel da tela base
const VIEW_W := 304.0 * K
const VIEW_H := 224.0 * K
const STAGE_W := 608.0 * K  # cenário com 2 telas de largura
const STAGE_LEFT := 24.0
const STAGE_RIGHT := STAGE_W - 24.0
const SCREEN_MARGIN := 24.0  # quanto o lutador pode chegar perto da borda da tela
const FLOOR_Y := 620.0
const CAMERA_Y := FLOOR_Y - 200.0 * K + VIEW_H * 0.5  # chão em y = 200 da tela base
const PUSH_WIDTH := 70.0
const ROUND_SECONDS := 60
const ROUNDS_TO_WIN := 2

enum Phase { INTRO, FIGHT, ROUND_END, MATCH_OVER }

var p1: FighterScript
var p2: FighterScript
var world: Node2D
var camera: Camera2D
var effects: EffectsScript
var hud: HudScript
var projectiles: Array = []
var phase: int = Phase.INTRO
var phase_frame := 0
var round_number := 1
var wins := [0, 0]
var timer_frames := ROUND_SECONDS * 60
var hitstop := 0
var shake := 0.0
var message := ""
var round_winner := -1
var cam_x := STAGE_W * 0.5


func _ready() -> void:
	Controls.setup()
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST

	camera = Camera2D.new()
	camera.zoom = Vector2(1.0 / K, 1.0 / K)
	camera.position = Vector2(cam_x, CAMERA_Y)
	add_child(camera)
	camera.make_current()

	world = Node2D.new()
	add_child(world)
	p1 = FighterScript.new()
	p1.player_index = 0
	p1.character = "pengaro"
	p1.color = Color(0.85, 0.22, 0.2)
	p2 = FighterScript.new()
	p2.player_index = 1
	p2.character = "brutus"
	p2.color = Color(0.2, 0.45, 0.9)
	p1.opponent = p2
	p2.opponent = p1
	world.add_child(p1)
	world.add_child(p2)
	effects = EffectsScript.new()
	world.add_child(effects)

	var layer := CanvasLayer.new()
	add_child(layer)
	hud = HudScript.new()
	hud.game = self
	layer.add_child(hud)

	_start_round()


func _start_round() -> void:
	for pr in projectiles:
		pr.queue_free()
	projectiles.clear()
	p1.reset(STAGE_W * 0.5 - 52.0 * K, 1)
	p2.reset(STAGE_W * 0.5 + 52.0 * K, -1)
	timer_frames = ROUND_SECONDS * 60
	hitstop = 0
	shake = 0.0
	phase = Phase.INTRO
	phase_frame = 0
	round_winner = -1
	cam_x = STAGE_W * 0.5
	hud.reset()


func _physics_process(_delta: float) -> void:
	if Input.is_action_just_pressed("debug_boxes"):
		p1.debug_boxes = not p1.debug_boxes
		p2.debug_boxes = p1.debug_boxes
	phase_frame += 1
	_update_phase()

	var b1: int = _read_bits("p1_") if phase == Phase.FIGHT else 0
	var b2: int = _read_bits("p2_") if phase == Phase.FIGHT else 0
	if hitstop > 0:
		hitstop -= 1  # congela a tela no impacto, dá peso ao golpe
	else:
		_step(b1, b2)

	camera.position = Vector2(cam_x, CAMERA_Y)
	camera.offset = Vector2(randf_range(-shake, shake), randf_range(-shake, shake))
	shake = maxf(0.0, shake * 0.85 - 0.1)
	effects.tick()
	hud.tick()


func _update_phase() -> void:
	match phase:
		Phase.INTRO:
			if phase_frame < 70:
				message = "ROUND %d" % round_number
			elif phase_frame < 100:
				message = "LUTE!"
			else:
				phase = Phase.FIGHT
				phase_frame = 0
				message = ""
		Phase.ROUND_END:
			if phase_frame == 90:
				if round_winner >= 0:
					var w: FighterScript = p1 if round_winner == 0 else p2
					w.set_winner()
					message = "%s VENCE" % hud.fighter_name(w)
				else:
					message = "EMPATE"
			elif phase_frame >= 210:
				if wins[0] >= ROUNDS_TO_WIN or wins[1] >= ROUNDS_TO_WIN:
					phase = Phase.MATCH_OVER
					phase_frame = 0
					var champ: FighterScript = p1 if wins[0] >= ROUNDS_TO_WIN else p2
					message = "%s VENCEU!\nSoco fraco: jogar de novo" % hud.fighter_name(champ)
				else:
					round_number += 1
					_start_round()
		Phase.MATCH_OVER:
			if phase_frame > 30 and (Input.is_action_just_pressed("p1_lp") or Input.is_action_just_pressed("p2_lp")):
				wins = [0, 0]
				round_number = 1
				_start_round()


func _read_bits(prefix: String) -> int:
	var b := 0
	if Input.is_action_pressed(prefix + "up"):
		b |= FighterScript.UP
	if Input.is_action_pressed(prefix + "down"):
		b |= FighterScript.DOWN
	if Input.is_action_pressed(prefix + "left"):
		b |= FighterScript.LEFT
	if Input.is_action_pressed(prefix + "right"):
		b |= FighterScript.RIGHT
	if Input.is_action_pressed(prefix + "lp"):
		b |= FighterScript.LP
	if Input.is_action_pressed(prefix + "hp"):
		b |= FighterScript.HP
	if Input.is_action_pressed(prefix + "lk"):
		b |= FighterScript.LK
	if Input.is_action_pressed(prefix + "hk"):
		b |= FighterScript.HK
	return b


func _step(b1: int, b2: int) -> void:
	p1.projectile_out = _has_projectile(p1)
	p2.projectile_out = _has_projectile(p2)
	p1.tick(b1)
	p2.tick(b2)
	_spawn_projectile(p1)
	_spawn_projectile(p2)
	for pr in projectiles:
		pr.tick()
	_resolve_push()
	_resolve_hits()
	_cleanup_projectiles()
	for f in [p1, p2]:
		var fighter: FighterScript = f
		if fighter.state == FighterScript.State.KNOCKDOWN and fighter.state_frame == 0:
			effects.spawn(Vector2(fighter.pos.x, FLOOR_Y), "landing", fighter.facing < 0)
	if phase == Phase.FIGHT:
		timer_frames = maxi(0, timer_frames - 1)
		_check_round_over()


func _check_round_over() -> void:
	var ko1: bool = p1.hp <= 0
	var ko2: bool = p2.hp <= 0
	if ko1 or ko2:
		_end_round(ko1, ko2, "K.O.")
		hitstop = 40
		shake = 10.0
	elif timer_frames <= 0:
		_end_round(p1.hp < p2.hp, p2.hp < p1.hp, "TEMPO!")


func _end_round(lost1: bool, lost2: bool, text: String) -> void:
	phase = Phase.ROUND_END
	phase_frame = 0
	message = text
	if lost1 and not lost2:
		round_winner = 1
		wins[1] += 1
	elif lost2 and not lost1:
		round_winner = 0
		wins[0] += 1
	else:
		round_winner = -1


# ---------------------------------------------------------------- empurrão, câmera e paredes

func _resolve_push() -> void:
	for _i in 2:
		var dx: float = p2.pos.x - p1.pos.x
		var dy: float = absf(p2.pos.y - p1.pos.y)
		if absf(dx) < PUSH_WIDTH and dy < 130.0 and p1.has_pushbox() and p2.has_pushbox():
			var s: float = signf(dx)
			if s == 0.0:
				s = float(p1.facing)
			var overlap: float = PUSH_WIDTH - absf(dx)
			p1.pos.x -= s * overlap * 0.5
			p2.pos.x += s * overlap * 0.5
		_update_camera()
		_clamp(p1)
		_clamp(p2)


## A câmera segue o meio dos dois lutadores. Eles não podem sair da tela, como no KOF.
func _update_camera() -> void:
	var mid: float = (p1.pos.x + p2.pos.x) * 0.5
	cam_x = clampf(mid, VIEW_W * 0.5, STAGE_W - VIEW_W * 0.5)


func _left_limit() -> float:
	return maxf(STAGE_LEFT, cam_x - VIEW_W * 0.5 + SCREEN_MARGIN)


func _right_limit() -> float:
	return minf(STAGE_RIGHT, cam_x + VIEW_W * 0.5 - SCREEN_MARGIN)


func _clamp(f: FighterScript) -> void:
	f.pos.x = clampf(f.pos.x, _left_limit(), _right_limit())
	f.position = f.pos


# ---------------------------------------------------------------- golpes

func _resolve_hits() -> void:
	if phase != Phase.FIGHT:
		return
	# Calcula tudo antes de aplicar, para os dois golpes poderem se trocar no mesmo quadro.
	var h1: Rect2 = p1.active_hitbox()
	var h2: Rect2 = p2.active_hitbox()
	var hurt1: Rect2 = p1.hurtbox()
	var hurt2: Rect2 = p2.hurtbox()
	var m1: Dictionary = p1.move
	var m2: Dictionary = p2.move
	var f1_hits: bool = h1.has_area() and hurt2.has_area() and h1.intersects(hurt2)
	var f2_hits: bool = h2.has_area() and hurt1.has_area() and h2.intersects(hurt1)
	if f1_hits:
		_apply_hit(p1, p2, m1, p1.facing, h1.intersection(hurt2).get_center())
	if f2_hits:
		_apply_hit(p2, p1, m2, p2.facing, h2.intersection(hurt1).get_center())

	for pr in projectiles:
		if not pr.alive:
			continue
		var target: FighterScript = p2 if pr.shooter == p1 else p1
		var hurt: Rect2 = target.hurtbox()
		var box: Rect2 = pr.hitbox()
		if hurt.has_area() and box.intersects(hurt):
			pr.alive = false
			var shooter: FighterScript = pr.shooter
			shooter.add_power(6)
			_apply_hit(null, target, ProjectileScript.MOVE, int(signf(pr.vx)), box.get_center())

	# Dois projéteis se anulam.
	for a in projectiles:
		for b in projectiles:
			if a != b and a.alive and b.alive and a.shooter != b.shooter and a.hitbox().intersects(b.hitbox()):
				a.alive = false
				b.alive = false
				effects.spawn((a.pos + b.pos) * 0.5, "clash", false)


func _apply_hit(attacker, defender: FighterScript, m: Dictionary, from_facing: int, at: Vector2) -> void:
	if attacker != null:
		attacker.hit_landed = true
	var blocked: bool = defender.receive_hit(m, from_facing)
	if attacker != null:
		attacker.add_power(5 if blocked else 10)
		# Se quem apanhou está na parede, quem bateu é empurrado para trás.
		var at_wall: bool = defender.pos.x <= _left_limit() + 6.0 or defender.pos.x >= _right_limit() - 6.0
		if at_wall and attacker.is_grounded():
			attacker.push_vel = -float(from_facing) * float(m["push"])
	var heavy: bool = int(m.get("damage", 0)) >= 80
	if blocked:
		hitstop = 5
		shake = 1.5
		effects.spawn(at, "block", from_facing < 0)
	else:
		hitstop = int(m.get("hitstop", 8))
		shake = 5.0 if heavy else 2.5
		effects.spawn(at, "heavy" if heavy else "light", from_facing < 0)


# ---------------------------------------------------------------- projéteis

func _has_projectile(f: FighterScript) -> bool:
	for pr in projectiles:
		if pr.shooter == f and pr.alive:
			return true
	return false


func _spawn_projectile(f: FighterScript) -> void:
	if not f.spawn_projectile:
		return
	f.spawn_projectile = false
	if _has_projectile(f):
		return
	var pr: ProjectileScript = ProjectileScript.new()
	pr.shooter = f
	pr.pos = f.pos + Vector2(70.0 * f.facing, -125.0)
	pr.position = pr.pos
	pr.vx = ProjectileScript.SPEED * f.facing
	pr.color = f.color
	world.add_child(pr)
	projectiles.append(pr)


func _cleanup_projectiles() -> void:
	var keep: Array = []
	for pr in projectiles:
		var off_screen: bool = absf(pr.pos.x - cam_x) > VIEW_W * 0.5 + 60.0
		if pr.alive and not off_screen:
			keep.append(pr)
		else:
			pr.queue_free()
	projectiles = keep


# ---------------------------------------------------------------- cenário

func _draw() -> void:
	var top := FLOOR_Y - 220.0 * K
	var bottom := FLOOR_Y + 40.0 * K
	# céu de entardecer
	var bands := 14
	for i in bands:
		var t := float(i) / float(bands - 1)
		var y := lerpf(top, FLOOR_Y, t)
		draw_rect(Rect2(0.0, y, STAGE_W, (FLOOR_Y - top) / float(bands) + 2.0),
			Color(0.13, 0.1, 0.26).lerp(Color(0.9, 0.48, 0.34), t))
	# montanhas ao fundo
	var pts := PackedVector2Array([Vector2(0, FLOOR_Y)])
	var n := 12
	for i in n + 1:
		var x := STAGE_W * float(i) / float(n)
		var h := 70.0 + 45.0 * sin(float(i) * 1.7) + 25.0 * sin(float(i) * 3.1)
		pts.append(Vector2(x, FLOOR_Y - 40.0 - h))
	pts.append(Vector2(STAGE_W, FLOOR_Y))
	draw_colored_polygon(pts, Color(0.22, 0.15, 0.3))
	# prédios
	for i in 18:
		var bx := float(i) * STAGE_W / 18.0 + 6.0
		var bh := 40.0 + float((i * 37) % 60)
		draw_rect(Rect2(bx, FLOOR_Y - bh, STAGE_W / 18.0 - 12.0, bh), Color(0.16, 0.11, 0.2))
	# chão
	draw_rect(Rect2(0.0, FLOOR_Y, STAGE_W, bottom - FLOOR_Y), Color(0.26, 0.2, 0.2))
	draw_line(Vector2(0, FLOOR_Y), Vector2(STAGE_W, FLOOR_Y), Color(0.55, 0.42, 0.34), 3.0)
	for i in range(-12, 13):
		var cx := STAGE_W * 0.5
		draw_line(Vector2(cx + float(i) * 40.0, FLOOR_Y), Vector2(cx + float(i) * 110.0, bottom), Color(0.32, 0.25, 0.24), 2.0)
