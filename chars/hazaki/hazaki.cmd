; Gerado por ferramentas/gerar_hazaki.py. Edite lá, não aqui.
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
name = "bfd_a"
command = ~B, F, D, a
time = 22

[Command]
name = "bfd_b"
command = ~B, F, D, b
time = 22

[Command]
name = "bfd_x"
command = ~B, F, D, x
time = 22

[Command]
name = "bfd_y"
command = ~B, F, D, y
time = 22

[Command]
name = "fd_y"
command = ~F, D, y
time = 16

[Command]
name = "fd_x"
command = ~F, D, x
time = 16

[Command]
name = "bd_b"
command = ~B, D, b
time = 16

[Command]
name = "bd_a"
command = ~B, D, a
time = 16

[Command]
name = "bf_b"
command = ~B, F, b
time = 16

[Command]
name = "bf_a"
command = ~B, F, a
time = 16

[Command]
name = "df_y"
command = ~D, F, y
time = 16

[Command]
name = "df_x"
command = ~D, F, x
time = 16

[Command]
name = "fb_y"
command = ~F, B, y
time = 16

[Command]
name = "fb_x"
command = ~F, B, x
time = 16

[Command]
name = "df_b"
command = ~D, F, b
time = 16

[Command]
name = "df_a"
command = ~D, F, a
time = 16

[Command]
name = "db_y"
command = ~D, B, y
time = 16

[Command]
name = "db_x"
command = ~D, B, x
time = 16

[Command]
name = "db_b"
command = ~D, B, b
time = 16

[Command]
name = "db_a"
command = ~D, B, a
time = 16

[Command]
name = "bf_y"
command = ~B, F, y
time = 16

[Command]
name = "golpe_216"
command = /F, y
time = 1

[Command]
name = "golpe_246"
command = /F, b
time = 1

[Command]
name = "golpe_201"
command = /B, x
time = 1

[Command]
name = "golpe_231"
command = /B, a
time = 1

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

[State -1, Pode cancelar]
type = VarSet
trigger1 = 1
var(1) = ctrl || ((stateno = 200 || stateno = 230 || stateno = 400 || stateno = 430 || stateno = 201 || stateno = 301 || stateno = 311 || stateno = 321 || stateno = 331 || stateno = 340 || stateno = 342 || stateno = 344 || stateno = 346) && movecontact && movecontact <= 8) || ((stateno = 210 || stateno = 240 || stateno = 410 || stateno = 216 || stateno = 302 || stateno = 312 || stateno = 322 || stateno = 332) && movehit && movehit <= 8)

[State -1, Rapidinho da Quebrada]
type = ChangeState
value = 3200
triggerall = command = "bfd_y"
triggerall = power >= 2000
triggerall = statetype != A
trigger1 = var(1)
trigger2 = (stateno = [1000,1701]) && movehit && movehit <= 8

[State -1, Rapidinho da Quebrada]
type = ChangeState
value = 3200
triggerall = command = "bfd_x"
triggerall = power >= 2000
triggerall = statetype != A
trigger1 = var(1)
trigger2 = (stateno = [1000,1701]) && movehit && movehit <= 8

[State -1, Faixa no Asfalto]
type = ChangeState
value = 3000
triggerall = command = "bfd_b"
triggerall = power >= 1000
triggerall = statetype != A
trigger1 = var(1)
trigger2 = (stateno = [1000,1701]) && movehit && movehit <= 8

[State -1, Faixa no Asfalto]
type = ChangeState
value = 3000
triggerall = command = "bfd_a"
triggerall = power >= 1000
triggerall = statetype != A
trigger1 = var(1)
trigger2 = (stateno = [1000,1701]) && movehit && movehit <= 8

[State -1, Ascensão de Faixa]
type = ChangeState
value = 1201
triggerall = command = "fd_y"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Ascensão de Faixa]
type = ChangeState
value = 1200
triggerall = command = "fd_x"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Pega Bolado]
type = ChangeState
value = 1501
triggerall = command = "bd_b"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Pega Bolado]
type = ChangeState
value = 1500
triggerall = command = "bd_a"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Rolada de Tatame]
type = ChangeState
value = 1701
triggerall = command = "bf_b"
triggerall = statetype != A
triggerall = p2dist x > 0
trigger1 = var(1)

[State -1, Rolada de Tatame]
type = ChangeState
value = 1700
triggerall = command = "bf_a"
triggerall = statetype != A
triggerall = p2dist x > 0
trigger1 = var(1)

[State -1, Punho de Concreto]
type = ChangeState
value = 1001
triggerall = command = "df_y"
triggerall = statetype != A
triggerall = numproj = 0
trigger1 = var(1)

[State -1, Punho de Concreto]
type = ChangeState
value = 1000
triggerall = command = "df_x"
triggerall = statetype != A
triggerall = numproj = 0
trigger1 = var(1)

[State -1, Estatueta Dourada]
type = ChangeState
value = 1601
triggerall = command = "fb_y"
triggerall = statetype != A
triggerall = numproj = 0
trigger1 = var(1)

[State -1, Estatueta Dourada]
type = ChangeState
value = 1600
triggerall = command = "fb_x"
triggerall = statetype != A
triggerall = numproj = 0
trigger1 = var(1)

[State -1, Giro de Garagem]
type = ChangeState
value = 1301
triggerall = command = "df_b"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Giro de Garagem]
type = ChangeState
value = 1300
triggerall = command = "df_a"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Guarda de Aço]
type = ChangeState
value = 1101
triggerall = command = "db_y"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Guarda de Aço]
type = ChangeState
value = 1100
triggerall = command = "db_x"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Corte de Base]
type = ChangeState
value = 1401
triggerall = command = "db_b"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Corte de Base]
type = ChangeState
value = 1400
triggerall = command = "db_a"
triggerall = statetype != A
trigger1 = var(1)

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
triggerall = power >= 1000
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

[State -1, Cutucao Sacana (agarrao)]
type = ChangeState
value = 830
triggerall = command = "bf_y"
triggerall = statetype = S
triggerall = p2bodydist x < 12
triggerall = stateno != 100
triggerall = p2statetype != A
triggerall = p2movetype != H
trigger1 = ctrl

[State -1, Puxa a Perna]
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

[State -1, Abraco de Quebrada]
type = ChangeState
value = 800
triggerall = command = "y"
triggerall = (command = "holdfwd" || command = "holdback")
triggerall = statetype = S
triggerall = ctrl
triggerall = stateno != 100
triggerall = p2bodydist x < 8
triggerall = p2statetype = S
triggerall = p2movetype != H
trigger1 = 1

[State -1, Kombo 340]
type = ChangeState
value = 340
triggerall = command = "a"
triggerall = command != "holddown"
triggerall = statetype != A
trigger1 = stateno = 246 && movecontact

[State -1, Kombo 341]
type = ChangeState
value = 341
triggerall = command = "b"
triggerall = command != "holddown"
triggerall = statetype != A
trigger1 = stateno = 340 && movecontact

[State -1, Kombo 342]
type = ChangeState
value = 342
triggerall = command = "a"
triggerall = command = "holddown"
triggerall = statetype != A
trigger1 = stateno = 200 && movecontact

[State -1, Kombo 343]
type = ChangeState
value = 343
triggerall = command = "b"
triggerall = command != "holddown"
triggerall = statetype != A
trigger1 = stateno = 342 && movecontact

[State -1, Kombo 344]
type = ChangeState
value = 344
triggerall = command = "y"
triggerall = command != "holddown"
triggerall = command != "holdfwd"
triggerall = statetype != A
trigger1 = stateno = 201 && movecontact

[State -1, Kombo 345]
type = ChangeState
value = 345
triggerall = command = "y"
triggerall = command = "holdfwd"
triggerall = statetype != A
trigger1 = stateno = 344 && movecontact

[State -1, Kombo 346]
type = ChangeState
value = 346
triggerall = command = "b"
triggerall = command != "holddown"
triggerall = statetype != A
trigger1 = stateno = 230 && movecontact

[State -1, Kombo 347]
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
trigger1 = stateno = 302 && movehit && var(10) >= 4

[State -1, Corrente x: 3o]
type = ChangeState
value = 302
triggerall = command = "x"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = stateno = 301 && movecontact && time > 10

[State -1, Corrente x: 2o]
type = ChangeState
value = 301
triggerall = command = "x"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = stateno = 200 && movecontact

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
trigger1 = stateno = 210 && movecontact

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
trigger1 = stateno = 230 && movecontact

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
trigger1 = stateno = 240 && movecontact

[State -1, Cotovelo de Faixa]
type = ChangeState
value = 216
triggerall = command = "golpe_216"
triggerall = statetype = S
trigger1 = ctrl
trigger2 = (stateno = 200 || stateno = 230) && movehit && movehit <= 8

[State -1, Machado de Dojo]
type = ChangeState
value = 246
triggerall = command = "golpe_246"
triggerall = statetype = S
trigger1 = ctrl

[State -1, Cutucao Sacana]
type = ChangeState
value = 201
triggerall = command = "golpe_201"
triggerall = statetype = S
trigger1 = ctrl

[State -1, Coice]
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

[State -1, Jab baixo]
type = ChangeState
value = 400
triggerall = command = "x"
triggerall = command = "holddown"
triggerall = statetype != A
trigger1 = ctrl
trigger2 = (stateno = 200 || stateno = 400 || stateno = 430 || stateno = 230) && movecontact && var(5) < 4

[State -1, Chute na canela]
type = ChangeState
value = 430
triggerall = command = "a"
triggerall = command = "holddown"
triggerall = statetype != A
trigger1 = ctrl
trigger2 = stateno = 430 && movecontact && var(5) < 4

[State -1, Joelhada subindo]
type = ChangeState
value = 410
triggerall = command = "y"
triggerall = command = "holddown"
triggerall = statetype != A
trigger1 = ctrl

[State -1, Rasteira]
type = ChangeState
value = 440
triggerall = command = "b"
triggerall = command = "holddown"
triggerall = statetype != A
trigger1 = ctrl

[State -1, Jab]
type = ChangeState
value = 200
triggerall = command = "x"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = ctrl
trigger2 = (stateno = 200 || stateno = 400 || stateno = 430 || stateno = 230) && movecontact && var(5) < 4

[State -1, Chute baixo]
type = ChangeState
value = 230
triggerall = command = "a"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = ctrl

[State -1, Soco reto]
type = ChangeState
value = 210
triggerall = command = "y"
triggerall = statetype = S
trigger1 = ctrl

[State -1, Chute lateral]
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
