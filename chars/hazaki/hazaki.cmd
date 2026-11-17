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

[Command]
name = "dd_a"
command = ~D, >D, a
time = 15

[Command]
name = "dd_b"
command = ~D, >D, b
time = 15

[Command]
name = "dfdf_x"
command = ~D, F, D, F, x
time = 25

[Command]
name = "dfdf_y"
command = ~D, F, D, F, y
time = 25

[Command]
name = "despertar"
command = x+y
time = 3

[Statedef -1]

[State -1, Diabo Loiro (Despertar)]
type = ChangeState
value = 2000
triggerall = command = "despertar"
triggerall = power >= powermax
triggerall = var(20) <= 0
triggerall = statetype != A
trigger1 = ctrl

[State -1, Pode cancelar]
type = VarSet
trigger1 = 1
var(1) = ctrl || ((stateno = 200 || stateno = 210 || stateno = 230 || stateno = 240 || stateno = 400 || stateno = 430 || stateno = 201 || stateno = 301 || stateno = 311 || stateno = 321 || stateno = 331 || stateno = 340 || stateno = 342 || stateno = 344 || stateno = 346) && movecontact && movecontact <= 8) || ((stateno = 410 || stateno = 216 || stateno = 302 || stateno = 312 || stateno = 322 || stateno = 332) && movehit && movehit <= 8)

[State -1, Rapidinho da Quebrada]
type = ChangeState
triggerall = var(20) <= 0
value = 3200
triggerall = command = "bfd_y"
triggerall = power >= 2000
triggerall = statetype != A
trigger1 = var(1)
trigger2 = (stateno = [1000,1701]) && movehit && movehit <= 8

[State -1, Rapidinho da Quebrada]
type = ChangeState
triggerall = var(20) <= 0
value = 3200
triggerall = command = "bfd_x"
triggerall = power >= 2000
triggerall = statetype != A
trigger1 = var(1)
trigger2 = (stateno = [1000,1701]) && movehit && movehit <= 8

[State -1, Faixa no Asfalto]
type = ChangeState
triggerall = var(20) <= 0
value = 3000
triggerall = command = "bfd_b"
triggerall = power >= 1000
triggerall = statetype != A
trigger1 = var(1)
trigger2 = (stateno = [1000,1701]) && movehit && movehit <= 8

[State -1, Faixa no Asfalto]
type = ChangeState
triggerall = var(20) <= 0
value = 3000
triggerall = command = "bfd_a"
triggerall = power >= 1000
triggerall = statetype != A
trigger1 = var(1)
trigger2 = (stateno = [1000,1701]) && movehit && movehit <= 8

[State -1, Ascensão de Faixa]
type = ChangeState
triggerall = var(20) <= 0
value = 1201
triggerall = command = "fd_y"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Ascensão de Faixa]
type = ChangeState
triggerall = var(20) <= 0
value = 1200
triggerall = command = "fd_x"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Pega Bolado]
type = ChangeState
triggerall = var(20) <= 0
value = 1501
triggerall = command = "bd_b"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Pega Bolado]
type = ChangeState
triggerall = var(20) <= 0
value = 1500
triggerall = command = "bd_a"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Rolada de Tatame]
type = ChangeState
triggerall = var(20) <= 0
value = 1701
triggerall = command = "bf_b"
triggerall = statetype != A
triggerall = p2dist x > 0
trigger1 = var(1)

[State -1, Rolada de Tatame]
type = ChangeState
triggerall = var(20) <= 0
value = 1700
triggerall = command = "bf_a"
triggerall = statetype != A
triggerall = p2dist x > 0
trigger1 = var(1)

[State -1, Pedra]
type = ChangeState
triggerall = var(20) <= 0
value = 1001
triggerall = command = "df_y"
triggerall = statetype != A
triggerall = numproj = 0
trigger1 = var(1)

[State -1, Pedra]
type = ChangeState
triggerall = var(20) <= 0
value = 1000
triggerall = command = "df_x"
triggerall = statetype != A
triggerall = numproj = 0
trigger1 = var(1)

[State -1, Bola de ki]
type = ChangeState
triggerall = var(20) <= 0
value = 1601
triggerall = command = "fb_y"
triggerall = statetype != A
triggerall = numproj = 0
trigger1 = var(1)

[State -1, Bola de ki]
type = ChangeState
triggerall = var(20) <= 0
value = 1600
triggerall = command = "fb_x"
triggerall = statetype != A
triggerall = numproj = 0
trigger1 = var(1)

[State -1, Giro de Garagem]
type = ChangeState
triggerall = var(20) <= 0
value = 1301
triggerall = command = "df_b"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Giro de Garagem]
type = ChangeState
triggerall = var(20) <= 0
value = 1300
triggerall = command = "df_a"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Guarda de Aço]
type = ChangeState
triggerall = var(20) <= 0
value = 1101
triggerall = command = "db_y"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Guarda de Aço]
type = ChangeState
triggerall = var(20) <= 0
value = 1100
triggerall = command = "db_x"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Corte de Base]
type = ChangeState
triggerall = var(20) <= 0
value = 1401
triggerall = command = "db_b"
triggerall = statetype != A
trigger1 = var(1)

[State -1, Corte de Base]
type = ChangeState
triggerall = var(20) <= 0
value = 1400
triggerall = command = "db_a"
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
triggerall = var(20) <= 0
triggerall = command = "afastar"
triggerall = power >= 1000
triggerall = time > 3
trigger1 = stateno = 150 || stateno = 152
value = -1000

[State -1, Afastar de defesa]
type = ChangeState
triggerall = var(20) <= 0
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
triggerall = var(20) <= 0
value = 650
triggerall = command = "afastar"
triggerall = statetype = A
trigger1 = ctrl

[State -1, Afastar]
type = ChangeState
triggerall = var(20) <= 0
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
triggerall = var(20) <= 0
value = 340
triggerall = command = "a"
triggerall = command != "holddown"
triggerall = statetype != A
trigger1 = stateno = 246 && movecontact

[State -1, Kombo 341]
type = ChangeState
triggerall = var(20) <= 0
value = 341
triggerall = command = "b"
triggerall = command != "holddown"
triggerall = statetype != A
trigger1 = stateno = 340 && movecontact

[State -1, Kombo 342]
type = ChangeState
triggerall = var(20) <= 0
value = 342
triggerall = command = "a"
triggerall = command = "holddown"
triggerall = statetype != A
trigger1 = stateno = 200 && movecontact

[State -1, Kombo 343]
type = ChangeState
triggerall = var(20) <= 0
value = 343
triggerall = command = "b"
triggerall = command != "holddown"
triggerall = statetype != A
trigger1 = stateno = 342 && movecontact

[State -1, Kombo 344]
type = ChangeState
triggerall = var(20) <= 0
value = 344
triggerall = command = "y"
triggerall = command != "holddown"
triggerall = command != "holdfwd"
triggerall = statetype != A
trigger1 = stateno = 201 && movecontact

[State -1, Kombo 345]
type = ChangeState
triggerall = var(20) <= 0
value = 345
triggerall = command = "y"
triggerall = command = "holdfwd"
triggerall = statetype != A
trigger1 = stateno = 344 && movecontact

[State -1, Kombo 346]
type = ChangeState
triggerall = var(20) <= 0
value = 346
triggerall = command = "b"
triggerall = command != "holddown"
triggerall = statetype != A
trigger1 = stateno = 230 && movecontact

[State -1, Kombo 347]
type = ChangeState
triggerall = var(20) <= 0
value = 347
triggerall = command = "y"
triggerall = command = "holddown"
triggerall = statetype != A
trigger1 = stateno = 346 && movecontact

[State -1, Corrente x: final]
type = ChangeState
triggerall = var(20) <= 0
value = 303
triggerall = command = "x"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = stateno = 302 && movehit && var(10) >= 4

[State -1, Corrente x: 3o]
type = ChangeState
triggerall = var(20) <= 0
value = 302
triggerall = command = "x"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = stateno = 301 && movecontact && time > 10

[State -1, Corrente x: 2o]
type = ChangeState
triggerall = var(20) <= 0
value = 301
triggerall = command = "x"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = stateno = 200 && movecontact

[State -1, Corrente y: final]
type = ChangeState
triggerall = var(20) <= 0
value = 313
triggerall = command = "y"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = stateno = 312 && movehit && var(10) >= 3

[State -1, Corrente y: 3o]
type = ChangeState
triggerall = var(20) <= 0
value = 312
triggerall = command = "y"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = stateno = 311 && movecontact

[State -1, Corrente y: 2o]
type = ChangeState
triggerall = var(20) <= 0
value = 311
triggerall = command = "y"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = stateno = 210 && movecontact

[State -1, Corrente a: final]
type = ChangeState
triggerall = var(20) <= 0
value = 323
triggerall = command = "a"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = stateno = 322 && movehit && var(10) >= 3

[State -1, Corrente a: 3o]
type = ChangeState
triggerall = var(20) <= 0
value = 322
triggerall = command = "a"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = stateno = 321 && movecontact

[State -1, Corrente a: 2o]
type = ChangeState
triggerall = var(20) <= 0
value = 321
triggerall = command = "a"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = stateno = 230 && movecontact

[State -1, Corrente b: final]
type = ChangeState
triggerall = var(20) <= 0
value = 333
triggerall = command = "b"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = stateno = 332 && movehit && var(10) >= 3

[State -1, Corrente b: 3o]
type = ChangeState
triggerall = var(20) <= 0
value = 332
triggerall = command = "b"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = stateno = 331 && movecontact

[State -1, Corrente b: 2o]
type = ChangeState
triggerall = var(20) <= 0
value = 331
triggerall = command = "b"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = stateno = 240 && movecontact

[State -1, Cotovelo de Faixa]
type = ChangeState
triggerall = var(20) <= 0
value = 216
triggerall = command = "golpe_216"
triggerall = statetype = S
trigger1 = ctrl
trigger2 = (stateno = 200 || stateno = 230) && movehit && movehit <= 8

[State -1, Machado de Dojo]
type = ChangeState
triggerall = var(20) <= 0
value = 246
triggerall = command = "golpe_246"
triggerall = statetype = S
trigger1 = ctrl

[State -1, Cutucao Sacana]
type = ChangeState
triggerall = var(20) <= 0
value = 201
triggerall = command = "golpe_201"
triggerall = statetype = S
trigger1 = ctrl

[State -1, Coice]
type = ChangeState
triggerall = var(20) <= 0
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
triggerall = var(20) <= 0
value = 400
triggerall = command = "x"
triggerall = command = "holddown"
triggerall = statetype != A
trigger1 = ctrl
trigger2 = (stateno = 200 || stateno = 400 || stateno = 430 || stateno = 230) && movecontact && var(5) < 4

[State -1, Chute na canela]
type = ChangeState
triggerall = var(20) <= 0
value = 430
triggerall = command = "a"
triggerall = command = "holddown"
triggerall = statetype != A
trigger1 = ctrl
trigger2 = stateno = 430 && movecontact && var(5) < 4

[State -1, Joelhada subindo]
type = ChangeState
triggerall = var(20) <= 0
value = 410
triggerall = command = "y"
triggerall = command = "holddown"
triggerall = statetype != A
trigger1 = ctrl

[State -1, Rasteira]
type = ChangeState
triggerall = var(20) <= 0
value = 440
triggerall = command = "b"
triggerall = command = "holddown"
triggerall = statetype != A
trigger1 = ctrl

[State -1, Jab]
type = ChangeState
triggerall = var(20) <= 0
value = 200
triggerall = command = "x"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = ctrl
trigger2 = (stateno = 200 || stateno = 400 || stateno = 430 || stateno = 230) && movecontact && var(5) < 4

[State -1, Chute baixo]
type = ChangeState
triggerall = var(20) <= 0
value = 230
triggerall = command = "a"
triggerall = command != "holddown"
triggerall = statetype = S
trigger1 = ctrl

[State -1, Soco reto]
type = ChangeState
triggerall = var(20) <= 0
value = 210
triggerall = command = "y"
triggerall = statetype = S
trigger1 = ctrl

[State -1, Chute lateral]
type = ChangeState
triggerall = var(20) <= 0
value = 240
triggerall = command = "b"
triggerall = statetype = S
trigger1 = ctrl

[State -1, Golpe no ar]
type = ChangeState
triggerall = var(20) <= 0
value = 600
triggerall = command = "x"
triggerall = statetype = A
trigger1 = ctrl

[State -1, Golpe no ar]
type = ChangeState
triggerall = var(20) <= 0
value = 601
triggerall = command = "y"
triggerall = statetype = A
trigger1 = ctrl
trigger2 = (stateno = 600 || stateno = 610) && movehit && movehit <= 8

[State -1, Golpe no ar]
type = ChangeState
triggerall = var(20) <= 0
value = 610
triggerall = command = "a"
triggerall = statetype = A
trigger1 = ctrl

[State -1, Golpe no ar]
type = ChangeState
triggerall = var(20) <= 0
value = 611
triggerall = command = "b"
triggerall = statetype = A
trigger1 = ctrl
trigger2 = (stateno = 600 || stateno = 610) && movehit && movehit <= 8

[State -1, Demônio: pode cancelar]
type = VarSet
triggerall = var(20) > 0
trigger1 = (stateno = 4200 || stateno = 4201 || stateno = 4202 || stateno = 4203 || stateno = 4210 || stateno = 4211 || stateno = 4212 || stateno = 4213 || stateno = 4301 || stateno = 4302 || stateno = 4303 || stateno = 4311 || stateno = 4312 || stateno = 4313 || stateno = 4321 || stateno = 4322 || stateno = 4323 || stateno = 4331 || stateno = 4332 || stateno = 4333 || stateno = 4400 || stateno = 4401 || stateno = 4402 || stateno = 4403 || stateno = 4600 || stateno = 4601 || stateno = 4602 || stateno = 4603) && movecontact && movecontact <= 8
var(1) = 1

[State -1, Rajadona de Ki das Trevas]
type = ChangeState
value = 1650
triggerall = command = "fb_x" || command = "fb_y"
triggerall = var(20) > 0
triggerall = power >= 1000
triggerall = statetype != A
triggerall = numproj = 0
trigger1 = ctrl || var(1)

[State -1, Cobrança do Diabo]
type = ChangeState
value = ifelse(command = "df_b", 1661, 1660)
triggerall = command = "df_a" || command = "df_b"
triggerall = var(20) > 0
triggerall = statetype != A
trigger1 = ctrl || var(1)

[State -1, Demônio: Juízo Infernal (super)]
type = ChangeState
value = 4650
triggerall = var(20) > 0
triggerall = command = "dfdf_x" || command = "dfdf_y"
triggerall = power >= 1000
triggerall = statetype != A
trigger1 = ctrl || var(1)

[State -1, Demônio: Rasgo Ascendente]
type = ChangeState
value = ifelse(command = "fd_y", 4521, 4520)
triggerall = var(20) > 0
triggerall = command = "fd_x" || command = "fd_y"
triggerall = statetype != A
trigger1 = ctrl || var(1)

[State -1, Demônio: Bola das Trevas]
type = ChangeState
value = ifelse(command = "df_y", 4501, 4500)
triggerall = var(20) > 0
triggerall = command = "df_x" || command = "df_y"
triggerall = numprojid(4500) = 0 && numprojid(4501) = 0
triggerall = statetype != A
trigger1 = ctrl || var(1)

[State -1, Demônio: Voo Infernal]
type = ChangeState
value = ifelse(command = "dd_b", 4511, 4510)
triggerall = var(20) > 0
triggerall = command = "dd_a" || command = "dd_b"
triggerall = statetype != A
trigger1 = ctrl || var(1)

[State -1, Demônio: Pisoteio: pisão voador]
type = ChangeState
value = 4333
triggerall = var(20) > 0
triggerall = command = "b"
triggerall = command != "holddown"
trigger1 = (stateno = 4332) && movehit && var(10) >= 3

[State -1, Demônio: Dança do Rabo: chicotada]
type = ChangeState
value = 4323
triggerall = var(20) > 0
triggerall = command = "a"
triggerall = command != "holddown"
trigger1 = (stateno = 4322) && movehit && var(10) >= 3

[State -1, Demônio: Dilacerar: rasgo de fogo]
type = ChangeState
value = 4313
triggerall = var(20) > 0
triggerall = command = "y"
triggerall = command != "holddown"
trigger1 = (stateno = 4312) && movehit && var(10) >= 3

[State -1, Demônio: Fúria das Garras: rasgo]
type = ChangeState
value = 4303
triggerall = var(20) > 0
triggerall = command = "x"
triggerall = command != "holddown"
trigger1 = (stateno = 4302) && movehit && var(10) >= 3

[State -1, Demônio: Pisoteio 3]
type = ChangeState
value = 4332
triggerall = var(20) > 0
triggerall = command = "b"
triggerall = command != "holddown"
trigger1 = (stateno = 4331) && movecontact

[State -1, Demônio: Pisoteio 2]
type = ChangeState
value = 4331
triggerall = var(20) > 0
triggerall = command = "b"
triggerall = command != "holddown"
trigger1 = (stateno = 4203) && movecontact

[State -1, Demônio: Dança do Rabo 3]
type = ChangeState
value = 4322
triggerall = var(20) > 0
triggerall = command = "a"
triggerall = command != "holddown"
trigger1 = (stateno = 4321) && movecontact

[State -1, Demônio: Dança do Rabo 2]
type = ChangeState
value = 4321
triggerall = var(20) > 0
triggerall = command = "a"
triggerall = command != "holddown"
trigger1 = (stateno = 4202 || stateno = 4402) && movecontact

[State -1, Demônio: Dilacerar 3]
type = ChangeState
value = 4312
triggerall = var(20) > 0
triggerall = command = "y"
triggerall = command != "holddown"
trigger1 = (stateno = 4311) && movecontact

[State -1, Demônio: Dilacerar 2]
type = ChangeState
value = 4311
triggerall = var(20) > 0
triggerall = command = "y"
triggerall = command != "holddown"
trigger1 = (stateno = 4201) && movecontact

[State -1, Demônio: Fúria das Garras 3]
type = ChangeState
value = 4302
triggerall = var(20) > 0
triggerall = command = "x"
triggerall = command != "holddown"
trigger1 = (stateno = 4301) && movecontact

[State -1, Demônio: Fúria das Garras 2]
type = ChangeState
value = 4301
triggerall = var(20) > 0
triggerall = command = "x"
triggerall = command != "holddown"
trigger1 = (stateno = 4200) && movecontact

[State -1, Demônio: Martelo Infernal]
type = ChangeState
value = 4210
triggerall = var(20) > 0
triggerall = command = "x"
triggerall = command = "holdfwd"
triggerall = command != "holddown"
trigger1 = ctrl
trigger1 = statetype = S

[State -1, Demônio: Estocada de Garra]
type = ChangeState
value = 4211
triggerall = var(20) > 0
triggerall = command = "y"
triggerall = command = "holdfwd"
triggerall = command != "holddown"
trigger1 = ctrl
trigger1 = statetype = S
trigger2 = (stateno = 4301) && movecontact

[State -1, Demônio: Chicote de Rabo]
type = ChangeState
value = 4212
triggerall = var(20) > 0
triggerall = command = "b"
triggerall = command = "holdfwd"
triggerall = command != "holddown"
trigger1 = ctrl
trigger1 = statetype = S

[State -1, Demônio: Mordida]
type = ChangeState
value = 4213
triggerall = var(20) > 0
triggerall = command = "y"
triggerall = command = "holdback"
triggerall = command != "holddown"
trigger1 = ctrl
trigger1 = statetype = S

[State -1, Demônio: Arranhão Baixo]
type = ChangeState
value = 4400
triggerall = var(20) > 0
triggerall = command = "x"
triggerall = command = "holddown"
trigger1 = ctrl
trigger1 = statetype != A
trigger2 = (stateno = 4200 || stateno = 4202 || stateno = 4400 || stateno = 4402) && movecontact && var(5) < 4

[State -1, Demônio: Garra Subindo]
type = ChangeState
value = 4401
triggerall = var(20) > 0
triggerall = command = "y"
triggerall = command = "holddown"
trigger1 = ctrl
trigger1 = statetype != A

[State -1, Demônio: Rabo Rasteiro]
type = ChangeState
value = 4402
triggerall = var(20) > 0
triggerall = command = "a"
triggerall = command = "holddown"
trigger1 = ctrl
trigger1 = statetype != A

[State -1, Demônio: Varrida de Garras]
type = ChangeState
value = 4403
triggerall = var(20) > 0
triggerall = command = "b"
triggerall = command = "holddown"
trigger1 = ctrl
trigger1 = statetype != A

[State -1, Demônio: Arranhão]
type = ChangeState
value = 4200
triggerall = var(20) > 0
triggerall = command = "x"
triggerall = command != "holddown"
trigger1 = ctrl
trigger1 = statetype = S
trigger2 = (stateno = 4200 || stateno = 4202 || stateno = 4400 || stateno = 4402) && movecontact && var(5) < 4

[State -1, Demônio: Garra Cruzada]
type = ChangeState
value = 4201
triggerall = var(20) > 0
triggerall = command = "y"
triggerall = command != "holddown"
trigger1 = ctrl
trigger1 = statetype = S

[State -1, Demônio: Joelhada Selvagem]
type = ChangeState
value = 4202
triggerall = var(20) > 0
triggerall = command = "a"
triggerall = command != "holddown"
trigger1 = ctrl
trigger1 = statetype = S

[State -1, Demônio: Coice com Garra]
type = ChangeState
value = 4203
triggerall = var(20) > 0
triggerall = command = "b"
triggerall = command != "holddown"
trigger1 = ctrl
trigger1 = statetype = S

[State -1, Demônio: Garra no Ar]
type = ChangeState
value = 4600
triggerall = var(20) > 0
triggerall = command = "x"
trigger1 = ctrl
trigger1 = statetype = A

[State -1, Demônio: Mergulho de Garras]
type = ChangeState
value = 4601
triggerall = var(20) > 0
triggerall = command = "y"
trigger1 = ctrl
trigger1 = statetype = A

[State -1, Demônio: Joelhada Aérea]
type = ChangeState
value = 4602
triggerall = var(20) > 0
triggerall = command = "a"
trigger1 = ctrl
trigger1 = statetype = A

[State -1, Demônio: Pisão de Garras]
type = ChangeState
value = 4603
triggerall = var(20) > 0
triggerall = command = "b"
trigger1 = ctrl
trigger1 = statetype = A

