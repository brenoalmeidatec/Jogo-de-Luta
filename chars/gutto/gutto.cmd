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
name = "poder47"
command = ~D, F, D, F, x
time = 30

[Command]
name = "poder47"
command = ~D, F, D, F, y
time = 30

[Command]
name = "golaco"
command = ~B, F, D, a
time = 24

[Command]
name = "bola_fraca"
command = ~D, F, a
time = 18

[Command]
name = "compasso_a"
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
name = "compasso_b"
command = ~D, B, b
time = 18

[Command]
name = "armada_x"
command = ~F, D, x
time = 18

[Command]
name = "caneta_x"
command = ~D, B, x
time = 18

[Command]
name = "armada_y"
command = ~F, D, y
time = 18

[Command]
name = "caneta_y"
command = ~D, B, y
time = 18

[Command]
name = "agarrao_whisky"
command = ~B, F, y
time = 18

[Command]
name = "garrafa_x"
command = ~F, B, x
time = 18

[Command]
name = "garrafa_y"
command = ~F, B, y
time = 18

[Command]
name = "role_a"
command = ~F, B, a
time = 18

[Command]
name = "role_b"
command = ~F, B, b
time = 18

[Command]
name = "sombra_x"
command = ~D, D, x
time = 18

[Command]
name = "sombra_y"
command = ~D, D, y
time = 18

[Command]
name = "sombra_a"
command = ~D, D, a
time = 18

[Command]
name = "sombra_b"
command = ~D, D, b
time = 18

[Command]
name = "golpe_216"
command = /F, y
time = 18

[Command]
name = "golpe_246"
command = /F, b
time = 18

[Command]
name = "golpe_201"
command = /B, x
time = 18

[Command]
name = "golpe_231"
command = /B, a
time = 18

[Command]
name = "golpe_1400"
command = ~D, F, x
time = 18

[Command]
name = "golpe_1401"
command = ~D, F, y
time = 18

[Command]
name = "golpe_1500"
command = ~B, D, a
time = 18

[Command]
name = "golpe_1501"
command = ~B, D, b
time = 18

[Command]
name = "golpe_3200"
command = ~B, F, D, x
time = 24

[Command]
name = "golpe_3200"
command = ~B, F, D, y
time = 24

[Command]
name = "parry_baixo"
command = /$D, c
time = 1
buffer.time = 1

[Command]
name = "parry"
command = /F, c
time = 1
buffer.time = 1

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
command = x+y
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
buffer.time = 8

[Command]
name = "y"
command = y
time = 1
buffer.time = 8

[Command]
name = "a"
command = a
time = 1
buffer.time = 8

[Command]
name = "b"
command = b
time = 1
buffer.time = 8

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

[State -1, Poder de longe do despertado (despertados_47.py)]
type = ChangeState
value = 4750
triggerall = command = "poder47"
triggerall = var(20) > 0
triggerall = statetype != A
triggerall = NumProjID(4750) = 0
trigger1 = ctrl

[State -1, Pode cancelar]
type = VarSet
trigger1 = 1
var(1) = ctrl || ((stateno = 200 || stateno = 210 || stateno = 215 || stateno = 216 || stateno = 230 || stateno = 245 || stateno = 400 || stateno = 410 || stateno = 430 || stateno = 260 || stateno = 301 || stateno = 311 || stateno = 321 || stateno = 331 || stateno = 340 || stateno = 342 || stateno = 344 || stateno = 346 || stateno = 3410 || stateno = 3420 || stateno = 3431 || stateno = 3433 || stateno = 3434 || stateno = 348) && movecontact && movecontact <= 8) || ((stateno = 302 || stateno = 312 || stateno = 322 || stateno = 332 || stateno = 3411 || stateno = 3421) && movehit && movehit <= 8)

[State -1, Bando da Várzea]
type = ChangeState
value = 3200
triggerall = command = "golpe_3200"
triggerall = statetype != A
triggerall = power >= 2000
trigger1 = var(1)
trigger2 = (stateno = [1000,1501]) && movehit && movehit <= 8

[State -1, Mão de Chimpá]
type = ChangeState
value = 1400
triggerall = command = "golpe_1400"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Mão de Chimpá]
type = ChangeState
value = 1401
triggerall = command = "golpe_1401"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Sola de Várzea]
type = ChangeState
value = 1500
triggerall = command = "golpe_1500"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Sola de Várzea]
type = ChangeState
value = 1501
triggerall = command = "golpe_1501"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Saideira Sombria]
type = ChangeState
value = 3100
triggerall = command = "golaco"
triggerall = power >= 1000
triggerall = ((var(20) > 0) || (life <= 200 && power >= 2000))
triggerall = statetype != A
trigger1 = var(1)
trigger2 = (stateno = [1000,1501]) && movehit && movehit <= 8

[State -1, Chuva de Bebidas]
type = ChangeState
value = 3000
triggerall = command = "golaco"
triggerall = power >= 1000
triggerall = statetype != A
trigger1 = var(1)
trigger2 = (stateno = [1000,1501]) && movehit && movehit <= 8

[State -1, Despertar]
type = ChangeState
value = 2000
triggerall = command = "despertar"
triggerall = power >= powermax
triggerall = var(20) = 0
triggerall = statetype = S
trigger1 = ctrl

[State -1, armada]
type = ChangeState
value = 1200
triggerall = command = "armada_x"
triggerall = statetype != A
trigger1 = var(1)

[State -1, armada]
type = ChangeState
value = 1201
triggerall = command = "armada_y"
triggerall = statetype != A
trigger1 = var(1)

[State -1, caneta]
type = ChangeState
value = 1300
triggerall = command = "caneta_x"
triggerall = statetype != A
trigger1 = var(1)

[State -1, caneta]
type = ChangeState
value = 1301
triggerall = command = "caneta_y"
triggerall = statetype != A
trigger1 = var(1)

[State -1, compasso]
type = ChangeState
value = 1100
triggerall = command = "compasso_a"
triggerall = statetype != A
trigger1 = var(1)

[State -1, compasso]
type = ChangeState
value = 1101
triggerall = command = "compasso_b"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Bola forte]
type = ChangeState
value = 1001
triggerall = command = "bola_forte"
triggerall = numprojid(1000) + numprojid(1001) + numprojid(1002) + numprojid(1003) = 0
triggerall = statetype != A
trigger1 = var(1)

[State -1, Bola fraca]
type = ChangeState
value = 1000
triggerall = command = "bola_fraca"
triggerall = numprojid(1000) + numprojid(1001) + numprojid(1002) + numprojid(1003) = 0
triggerall = statetype != A
trigger1 = var(1)

[State -1, Garrafada forte]
type = ChangeState
value = 1601
triggerall = command = "garrafa_y"
triggerall = numprojid(1000) + numprojid(1001) + numprojid(1002) + numprojid(1003) = 0
triggerall = var(20) = 0
triggerall = statetype != A
trigger1 = var(1)

[State -1, Garrafada fraca]
type = ChangeState
value = 1600
triggerall = command = "garrafa_x"
triggerall = numprojid(1000) + numprojid(1001) + numprojid(1002) + numprojid(1003) = 0
triggerall = var(20) = 0
triggerall = statetype != A
trigger1 = var(1)

[State -1, Role por tras e chute]
type = ChangeState
value = 1701
triggerall = command = "role_b"
triggerall = p2dist x > 0
triggerall = statetype != A
trigger1 = var(1)

[State -1, Role por tras]
type = ChangeState
value = 1700
triggerall = command = "role_a"
triggerall = p2dist x > 0
triggerall = statetype != A
trigger1 = var(1)

[State -1, Mao de Sombra]
type = ChangeState
value = 3400
triggerall = command = "sombra_x"
triggerall = numprojid(1000) + numprojid(1001) + numprojid(1002) + numprojid(1003) = 0
triggerall = var(20) > 0
triggerall = statetype != A
trigger1 = var(1)

[State -1, Chute da Corrente]
type = ChangeState
value = 3401
triggerall = command = "sombra_y"
triggerall = var(20) > 0
triggerall = statetype != A
trigger1 = var(1)

[State -1, Sombra Atravessada]
type = ChangeState
value = 3402
triggerall = command = "sombra_a"
triggerall = p2dist x > 0
triggerall = var(20) > 0
triggerall = statetype != A
trigger1 = var(1)

[State -1, Queda Escura]
type = ChangeState
value = 3403
triggerall = command = "sombra_b"
triggerall = var(20) > 0
triggerall = statetype != A
trigger1 = var(1)

[State -1, Parry embaixo]
type = ChangeState
value = 764
triggerall = command = "parry_baixo"
triggerall = statetype != A
trigger1 = ctrl

[State -1, Parry]
type = ChangeState
value = 760
triggerall = command = "parry"
triggerall = statetype = S
trigger1 = ctrl

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

[State -1, Agarrao whisky]
type = ChangeState
value = 830
triggerall = command = "agarrao_whisky"
triggerall = statetype = S
triggerall = stateno != 100
triggerall = p2bodydist x < 12
triggerall = p2statetype != A
triggerall = p2movetype != H
trigger1 = ctrl

[State -1, Agarrao agachado]
type = ChangeState
value = 840
triggerall = command = "y"
triggerall = command = "holddown"
triggerall = statetype != A
triggerall = ctrl
triggerall = stateno != 100
triggerall = p2bodydist x < 8
triggerall = p2statetype = C
triggerall = p2movetype != H
trigger1 = 1

[State -1, Agarrao do despertado (despertados_47.py)]
type = ChangeState
value = 4700
triggerall = var(20) > 0
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
triggerall = command = "y"
triggerall = statetype = S
triggerall = ctrl
triggerall = stateno != 100
triggerall = p2bodydist x < 8
triggerall = p2statetype != A
triggerall = p2movetype != H
triggerall = (command = "holdfwd" || command = "holdback")
trigger1 = 1

[State -1, Agarrao do despertado (despertados_47.py)]
type = ChangeState
value = 4700
triggerall = var(20) > 0
triggerall = command = "b"
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

[State -1, Desp: Mao de Chao Possuida]
type = ChangeState
value = 3430
triggerall = command = "y"
triggerall = command = "holddown"
triggerall = statetype != A
triggerall = var(20) > 0
trigger1 = ctrl

[State -1, Desp: Foice Escura]
type = ChangeState
value = 3435
triggerall = command = "b"
triggerall = command = "holddown"
triggerall = statetype != A
triggerall = var(20) > 0
trigger1 = ctrl

[State -1, Desp: Tranco Possuido]
type = ChangeState
value = 3431
triggerall = command = "y"
triggerall = command = "holdfwd"
triggerall = statetype = S
triggerall = var(20) > 0
trigger1 = ctrl
trigger2 = (stateno = 200 || stateno = 230) && movehit && movehit <= 8

[State -1, Desp: Passo de Sombra]
type = ChangeState
value = 3432
triggerall = command = "b"
triggerall = command = "holdfwd"
triggerall = statetype = S
triggerall = var(20) > 0
trigger1 = ctrl

[State -1, Desp: Palma Torta]
type = ChangeState
value = 3433
triggerall = command = "x"
triggerall = command = "holdback"
triggerall = statetype = S
triggerall = var(20) > 0
trigger1 = ctrl

[State -1, Desp: Puxada Sombria]
type = ChangeState
value = 3434
triggerall = command = "a"
triggerall = command = "holdback"
triggerall = statetype = S
triggerall = var(20) > 0
trigger1 = ctrl

[State -1, Desp: Kombo 3]
type = ChangeState
value = 349
triggerall = command = "x"
triggerall = statetype = S
triggerall = var(20) > 0
trigger1 = stateno = 348 && movecontact

[State -1, Desp: Kombo 2]
type = ChangeState
value = 348
triggerall = command = "a"
triggerall = command != "holddown"
triggerall = statetype = S
triggerall = var(20) > 0
trigger1 = stateno = 3420 && movecontact

[State -1, Desp: corrente y final]
type = ChangeState
value = 3413
triggerall = command = "y"
triggerall = command != "holddown"
triggerall = statetype = S
triggerall = var(20) > 0
trigger1 = stateno = 3412 && movehit && var(10) >= 3

[State -1, Desp: corrente y 3]
type = ChangeState
value = 3412
triggerall = command = "y"
triggerall = command != "holddown"
triggerall = statetype = S
triggerall = var(20) > 0
trigger1 = stateno = 3411 && movecontact

[State -1, Desp: corrente y 2]
type = ChangeState
value = 3411
triggerall = command = "y"
triggerall = command != "holddown"
triggerall = statetype = S
triggerall = var(20) > 0
trigger1 = stateno = 3410 && movecontact

[State -1, Desp: corrente y 1]
type = ChangeState
value = 3410
triggerall = command = "y"
triggerall = command != "holddown"
triggerall = command != "holdfwd"
triggerall = command != "holdback"
triggerall = statetype = S
triggerall = var(20) > 0
trigger1 = ctrl

[State -1, Desp: corrente b final]
type = ChangeState
value = 3423
triggerall = command = "b"
triggerall = command != "holddown"
triggerall = statetype = S
triggerall = var(20) > 0
trigger1 = stateno = 3422 && movehit && var(10) >= 3

[State -1, Desp: corrente b 3]
type = ChangeState
value = 3422
triggerall = command = "b"
triggerall = command != "holddown"
triggerall = statetype = S
triggerall = var(20) > 0
trigger1 = stateno = 3421 && movecontact

[State -1, Desp: corrente b 2]
type = ChangeState
value = 3421
triggerall = command = "b"
triggerall = command != "holddown"
triggerall = statetype = S
triggerall = var(20) > 0
trigger1 = stateno = 3420 && movecontact

[State -1, Desp: corrente b 1]
type = ChangeState
value = 3420
triggerall = command = "b"
triggerall = command != "holddown"
triggerall = command != "holdfwd"
triggerall = command != "holdback"
triggerall = statetype = S
triggerall = var(20) > 0
trigger1 = ctrl

[State -1, Kombo 1: x]
type = ChangeState
value = 340
triggerall = command = "x"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = stateno = 216 && movecontact

[State -1, Kombo 1: b]
type = ChangeState
value = 341
triggerall = command = "b"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = stateno = 340 && movecontact

[State -1, Kombo 2: baixo a]
type = ChangeState
value = 342
triggerall = command = "a"
triggerall = command = "holddown"
triggerall = statetype != A
trigger1 = stateno = 200 && movecontact

[State -1, Kombo 2: y]
type = ChangeState
value = 343
triggerall = command = "y"
triggerall = command != "holddown"
triggerall = statetype != A
trigger1 = stateno = 342 && movecontact

[State -1, Kombo 3: y]
type = ChangeState
value = 344
triggerall = command = "y"
triggerall = command != "holddown"
triggerall = statetype = S
triggerall = command != "holdfwd"
trigger1 = stateno = 201 && movecontact

[State -1, Kombo 3: frente b]
type = ChangeState
value = 345
triggerall = command = "b"
triggerall = command = "holdfwd"
triggerall = statetype = S
trigger1 = stateno = 344 && movecontact

[State -1, Kombo 4: b]
type = ChangeState
value = 346
triggerall = command = "b"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = stateno = 230 && movecontact

[State -1, Kombo 4: baixo y]
type = ChangeState
value = 347
triggerall = command = "y"
triggerall = command = "holddown"
triggerall = statetype != A
trigger1 = stateno = 346 && movecontact

[State -1, Corrente x: final]
type = ChangeState
value = 303
triggerall = command = "x"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = stateno = 302 && movehit && var(10) >= 3

[State -1, Corrente x: 3o]
type = ChangeState
value = 302
triggerall = command = "x"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = stateno = 301 && movecontact

[State -1, Corrente x: 2o]
type = ChangeState
value = 301
triggerall = command = "x"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = (stateno = 200) && movecontact

[State -1, Corrente y: final]
type = ChangeState
value = 313
triggerall = command = "y"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = stateno = 312 && movehit && var(10) >= 3

[State -1, Corrente y: 3o]
type = ChangeState
value = 312
triggerall = command = "y"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = stateno = 311 && movecontact

[State -1, Corrente y: 2o]
type = ChangeState
value = 311
triggerall = command = "y"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = (stateno = 210 || stateno = 215) && movecontact

[State -1, Corrente a: final]
type = ChangeState
value = 323
triggerall = command = "a"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = stateno = 322 && movehit && var(10) >= 3

[State -1, Corrente a: 3o]
type = ChangeState
value = 322
triggerall = command = "a"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = stateno = 321 && movecontact

[State -1, Corrente a: 2o]
type = ChangeState
value = 321
triggerall = command = "a"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = (stateno = 230) && movecontact

[State -1, Corrente b: final]
type = ChangeState
value = 333
triggerall = command = "b"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = stateno = 332 && movehit && var(10) >= 3

[State -1, Corrente b: 3o]
type = ChangeState
value = 332
triggerall = command = "b"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = stateno = 331 && movecontact

[State -1, Corrente b: 2o]
type = ChangeState
value = 331
triggerall = command = "b"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = (stateno = 240 || stateno = 245) && movecontact

[State -1, Tranco de Ombro]
type = ChangeState
value = 216
triggerall = command = "golpe_216"
triggerall = statetype = S
trigger1 = ctrl
trigger2 = (stateno = 200 || stateno = 230) && movehit && movehit <= 8

[State -1, Passo de Letra]
type = ChangeState
value = 246
triggerall = command = "golpe_246"
triggerall = statetype = S
trigger1 = ctrl

[State -1, Mão de Ginga]
type = ChangeState
value = 201
triggerall = command = "golpe_201"
triggerall = statetype = S
trigger1 = ctrl

[State -1, Puxada de Sola]
type = ChangeState
value = 231
triggerall = command = "golpe_231"
triggerall = statetype = S
trigger1 = ctrl

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
triggerall = statetype != A
trigger1 = ctrl
trigger2 = (stateno = 200 || stateno = 400 || stateno = 430 || stateno = 230) && movecontact && var(5) < 4

[State -1, Agachado chute fraco]
type = ChangeState
value = 430
triggerall = command = "a"
triggerall = command = "holddown"
triggerall = statetype != A
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

[State -1, Golpe no ar]
type = ChangeState
value = 600
triggerall = command = "x"
triggerall = statetype = A
trigger1 = ctrl

[State -1, Golpe no ar]
type = ChangeState
value = 601
triggerall = command = "y"
triggerall = statetype = A
trigger1 = ctrl
trigger2 = (stateno = 600 || stateno = 610) && movehit && movehit <= 8

[State -1, Golpe no ar]
type = ChangeState
value = 610
triggerall = command = "a"
triggerall = statetype = A
trigger1 = ctrl

[State -1, Golpe no ar]
type = ChangeState
value = 611
triggerall = command = "b"
triggerall = statetype = A
trigger1 = ctrl
trigger2 = (stateno = 600 || stateno = 610) && movehit && movehit <= 8

