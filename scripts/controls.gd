extends RefCounted
## Cria os comandos de teclado e controle quando o jogo abre.
## Assim não depende de configurar nada no editor.
##
## Jogador 1: W A S D para mover, U / I socos (fraco / forte), J / K chutes (fraco / forte).
## Jogador 2: setas para mover, Numpad 4 / 5 socos, Numpad 1 / 2 chutes.
## Controles: o primeiro controle é o jogador 1, o segundo é o jogador 2.
##   Direcional ou analógico esquerdo, X / Y socos, A / B chutes.


static func setup() -> void:
	_player("p1_", 0, KEY_W, KEY_S, KEY_A, KEY_D, KEY_U, KEY_I, KEY_J, KEY_K)
	_player("p2_", 1, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_KP_4, KEY_KP_5, KEY_KP_1, KEY_KP_2)
	_add("debug_boxes", [KEY_F1], -1, [], -1, 0.0)


static func _player(p: String, pad: int, up: int, down: int, left: int, right: int,
		lp: int, hp: int, lk: int, hk: int) -> void:
	_add(p + "up", [up], pad, [JOY_BUTTON_DPAD_UP], JOY_AXIS_LEFT_Y, -1.0)
	_add(p + "down", [down], pad, [JOY_BUTTON_DPAD_DOWN], JOY_AXIS_LEFT_Y, 1.0)
	_add(p + "left", [left], pad, [JOY_BUTTON_DPAD_LEFT], JOY_AXIS_LEFT_X, -1.0)
	_add(p + "right", [right], pad, [JOY_BUTTON_DPAD_RIGHT], JOY_AXIS_LEFT_X, 1.0)
	_add(p + "lp", [lp], pad, [JOY_BUTTON_X], -1, 0.0)
	_add(p + "hp", [hp], pad, [JOY_BUTTON_Y], -1, 0.0)
	_add(p + "lk", [lk], pad, [JOY_BUTTON_A], -1, 0.0)
	_add(p + "hk", [hk], pad, [JOY_BUTTON_B], -1, 0.0)


static func _add(action: String, keys: Array, pad: int, buttons: Array, axis: int, axis_dir: float) -> void:
	if InputMap.has_action(action):
		return
	InputMap.add_action(action, 0.5)
	for k in keys:
		var e := InputEventKey.new()
		e.device = -1  # qualquer teclado
		e.physical_keycode = k
		InputMap.action_add_event(action, e)
	for b in buttons:
		var j := InputEventJoypadButton.new()
		j.device = pad
		j.button_index = b
		InputMap.action_add_event(action, j)
	if axis >= 0:
		var m := InputEventJoypadMotion.new()
		m.device = pad
		m.axis = axis
		m.axis_value = axis_dir
		InputMap.action_add_event(action, m)
