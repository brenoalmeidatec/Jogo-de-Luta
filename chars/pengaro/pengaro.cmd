; Gerado por ferramentas/gerar_pengaro.py. Edite lá, não aqui.
; x = soco fraco, y = soco forte, a = chute fraco, b = chute forte, c = provocação

[Remap]
x = x
y = y
z = z
a = a
b = b
c = c
s = s

[Defaults]
command.time = 15
command.buffer.time = 3

[Command]
name = "golaco"
command = ~B, F, D, a
time = 24

[Command]
name = "bola_fraca"
command = ~D, F, a
time = 18

[Command]
name = "compasso"
command = ~D, B, a
time = 18

[Command]
name = "golaco"
command = ~B, F, D, b
time = 24

[Command]
name = "bola_forte"
command = ~D, F, b
time = 18

[Command]
name = "compasso"
command = ~D, B, b
time = 18

[Command]
name = "armada"
command = ~F, D, x
time = 18

[Command]
name = "caneta"
command = ~D, B, x
time = 18

[Command]
name = "armada"
command = ~F, D, y
time = 18

[Command]
name = "caneta"
command = ~D, B, y
time = 18

[Command]
name = "FF"
command = F, F
time = 10

[Command]
name = "BB"
command = B, B
time = 10

[Command]
name = "recovery"
command = x+a
time = 1

[Command]
name = "rolar"
command = x+a
time = 3

[Command]
name = "afastar"
command = y+b
time = 3

[Command]
name = "despertar"
command = x+a+y
time = 3

[Command]
name = "superpulo"
command = $D, $U
time = 10
buffer.time = 6

[Command]
name = "x"
command = x
time = 1

[Command]
name = "y"
command = y
time = 1

[Command]
name = "a"
command = a
time = 1

[Command]
name = "b"
command = b
time = 1

[Command]
name = "c"
command = c
time = 1

[Command]
name = "start"
command = s
time = 1

[Command]
name = "holdfwd"
command = /$F
time = 1

[Command]
name = "holdback"
command = /$B
time = 1

[Command]
name = "holdup"
command = /$U
time = 1

[Command]
name = "holddown"
command = /$D
time = 1

[Statedef -1]

[State -1, Pode cancelar]
type = VarSet
trigger1 = 1
var(1) = ctrl || ((stateno = 200 || stateno = 215 || stateno = 230 || stateno = 245 || stateno = 400 || stateno = 410 || stateno = 430 || stateno = 260) && movecontact && movecontact <= 8)

[State -1, Pelada Sombria]
type = ChangeState
value = 3100
triggerall = command = "golaco"
triggerall = power >= 1000
triggerall = ((var(20) > 0) || (life <= 200 && power >= 2000))
triggerall = statetype != A
trigger1 = var(1)
trigger2 = (var(20) > 0) && (stateno = 1000 || stateno = 1001 || stateno = 1100 || stateno = 1200 || stateno = 1300) && movecontact

[State -1, Golaco da Noite]
type = ChangeState
value = 3000
triggerall = command = "golaco"
triggerall = power >= 1000
triggerall = statetype != A
trigger1 = var(1)
trigger2 = (var(20) > 0) && (stateno = 1000 || stateno = 1001 || stateno = 1100 || stateno = 1200 || stateno = 1300) && movecontact

[State -1, Despertar]
type = ChangeState
value = 2000
triggerall = command = "despertar"
triggerall = power >= 1000
triggerall = var(20) = 0
triggerall = statetype = S
trigger1 = ctrl

[State -1, Armada]
type = ChangeState
value = 1200
triggerall = command = "armada"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Caneta]
type = ChangeState
value = 1300
triggerall = command = "caneta"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Compasso]
type = ChangeState
value = 1100
triggerall = command = "compasso"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Bola forte]
type = ChangeState
value = 1001
triggerall = command = "bola_forte"
triggerall = numprojid(1000) = 0
triggerall = statetype != A
trigger1 = var(1)

[State -1, Bola fraca]
type = ChangeState
value = 1000
triggerall = command = "bola_fraca"
triggerall = numprojid(1000) = 0
triggerall = statetype != A
trigger1 = var(1)

[State -1, Rolamento de defesa]
type = VarSet
triggerall = command = "rolar"
triggerall = power >= 1000
triggerall = time > 3
trigger1 = stateno = 150 || stateno = 152
var(8) = 1

[State -1, Gasta rolamento de defesa]
type = PowerAdd
triggerall = var(8) = 1
triggerall = command = "rolar"
trigger1 = stateno = 150 || stateno = 152
value = -1000

[State -1, Rolamento de defesa frente]
type = ChangeState
value = 700
triggerall = var(8) = 1
triggerall = command = "rolar"
triggerall = command != "holdback"
trigger1 = stateno = 150 || stateno = 152

[State -1, Rolamento de defesa tras]
type = ChangeState
value = 705
triggerall = var(8) = 1
triggerall = command = "rolar"
trigger1 = stateno = 150 || stateno = 152

[State -1, Gasta afastar de defesa]
type = PowerAdd
triggerall = command = "afastar"
triggerall = power >= 1000
triggerall = time > 3
trigger1 = stateno = 150 || stateno = 152
value = -1000

[State -1, Afastar de defesa]
type = ChangeState
value = 720
triggerall = command = "afastar"
triggerall = time > 3
trigger1 = stateno = 150 || stateno = 152

[State -1, Rolar para tras]
type = ChangeState
value = 705
triggerall = command = "rolar"
triggerall = command = "holdback"
triggerall = statetype = S
trigger1 = ctrl

[State -1, Rolar]
type = ChangeState
value = 700
triggerall = command = "rolar"
triggerall = statetype = S
trigger1 = ctrl

[State -1, Afastar no ar]
type = ChangeState
value = 650
triggerall = command = "afastar"
triggerall = statetype = A
trigger1 = ctrl

[State -1, Afastar]
type = ChangeState
value = 260
triggerall = command = "afastar"
triggerall = statetype = S
trigger1 = var(1)

[State -1, Agarrao]
type = ChangeState
value = 800
triggerall = command = "y"
triggerall = statetype = S
triggerall = ctrl
triggerall = stateno != 100
triggerall = p2bodydist x < 8
triggerall = p2statetype != A
triggerall = p2movetype != H
triggerall = (command = "holdfwd" || command = "holdback")
trigger1 = 1

[State -1, Agarrao]
type = ChangeState
value = 800
triggerall = command = "b"
triggerall = statetype = S
triggerall = ctrl
triggerall = stateno != 100
triggerall = p2bodydist x < 8
triggerall = p2statetype != A
triggerall = p2movetype != H
triggerall = (command = "holdfwd" || command = "holdback")
trigger1 = 1

[State -1, Corre]
type = ChangeState
value = 100
triggerall = command = "FF"
triggerall = statetype = S
trigger1 = ctrl

[State -1, Recua]
type = ChangeState
value = 105
triggerall = command = "BB"
triggerall = statetype = S
trigger1 = ctrl

[State -1, Provocacao]
type = ChangeState
value = 195
triggerall = command = "c"
triggerall = statetype != A
trigger1 = ctrl

[State -1, Agachado soco fraco]
type = ChangeState
value = 400
triggerall = command = "x"
triggerall = command = "holddown"
trigger1 = ctrl
trigger2 = (stateno = 200 || stateno = 400 || stateno = 430 || stateno = 230) && movecontact && var(5) < 4

[State -1, Agachado chute fraco]
type = ChangeState
value = 430
triggerall = command = "a"
triggerall = command = "holddown"
trigger1 = ctrl
trigger2 = stateno = 430 && movecontact && var(5) < 4

[State -1, Agachado soco forte]
type = ChangeState
value = 410
triggerall = command = "y"
triggerall = command = "holddown"
triggerall = statetype != A
trigger1 = ctrl

[State -1, Agachado chute forte]
type = ChangeState
value = 440
triggerall = command = "b"
triggerall = command = "holddown"
triggerall = statetype != A
trigger1 = ctrl

[State -1, Soco fraco]
type = ChangeState
value = 200
triggerall = command = "x"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = ctrl
trigger2 = (stateno = 200 || stateno = 400 || stateno = 430 || stateno = 230) && movecontact && var(5) < 4

[State -1, Chute fraco]
type = ChangeState
value = 230
triggerall = command = "a"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = ctrl

[State -1, Soco forte perto]
type = ChangeState
value = 215
triggerall = command = "y"
triggerall = statetype = S
triggerall = p2bodydist x < 30
trigger1 = ctrl

[State -1, Soco forte longe]
type = ChangeState
value = 210
triggerall = command = "y"
triggerall = statetype = S
trigger1 = ctrl

[State -1, Chute forte perto]
type = ChangeState
value = 245
triggerall = command = "b"
triggerall = statetype = S
triggerall = p2bodydist x < 30
trigger1 = ctrl

[State -1, Chute forte longe]
type = ChangeState
value = 240
triggerall = command = "b"
triggerall = statetype = S
trigger1 = ctrl

[State -1, Soco no ar]
type = ChangeState
value = 600
triggerall = (command = "x" || command = "y")
triggerall = statetype = A
trigger1 = ctrl

[State -1, Chute no ar]
type = ChangeState
value = 610
triggerall = (command = "a" || command = "b")
triggerall = statetype = A
trigger1 = ctrl

