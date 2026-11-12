-- ROBO DE TESTE (so na copia de teste): simula botoes pelo AssertCommand e registra o que cada golpe faz.
do
  local SAIDA = "@SAIDA@"
  local LUTADOR = "@LUTADOR@"  -- quem e o P1: o Hazak tem roteiro proprio (no fim); os outros usam o de sempre
  local LOG = io.open(SAIDA, "w")
  local function log(s) LOG:write(s, "\n"); LOG:flush() end
  local CMDS = {"x","y","a","b","c","holdfwd","holdback","holdup","holddown","agarrao_whisky","garrafa_x","garrafa_y",
    "role_a","role_b","sombra_x","sombra_y","sombra_a","sombra_b","despertar","FF","rolar","afastar","golaco",
    "golpe_216","golpe_246","golpe_201","golpe_231","golpe_1400","golpe_1401","golpe_1500","golpe_1501","golpe_3200","bola_fraca","bola_forte","parry","desperto","agacha","v10","fimdesp"}
  for _, nome in ipairs({"bfd_a","bfd_b","bfd_x","bfd_y","df_x","df_y","fb_x","fb_y","fd_x","fd_y","df_a","df_b","db_a",
    "db_b","bf_a","bf_b","bd_a","bd_b","db_x","db_y","bf_y"}) do CMDS[#CMDS + 1] = nome end  -- toques do Hazak
  CMDS[#CMDS + 1] = "defende"  -- so o .cmd do Hazak tem o controlador (testar_pengaro.py); nos outros o mapa nao faz nada
  for _, nome in ipairs({"baile", "caneta_x", "compasso_a"}) do CMDS[#CMDS + 1] = nome end  -- CK

  local function com(n, fn)
    local old = id()
    player(n)
    local a = fn()
    playerId(old)
    return a
  end
  local function snap(n)
    return com(n, function()
      return {st = stateNo(), t = time(), life = life(), pow = power(), ctrl = ctrl(), v10 = var(10), v20 = var(20), v37 = var(37),
              x = posX(), y = posY(), d = p2BodyDistX(), mc = moveContact(), mh = moveHit(), fa = facing(),
              borda = frontEdgeBodyDist(), proj = numProj(), stt = stateType(),
              an = (anim and anim()) or -1, sx = (screenPosX and screenPosX()) or 0}
    end)
  end

  local function clock() return roundTime() end
  -- camadas vivas da aura do endiabrado (aura.py: Pengaro 9600 a 9603, CK 9600 a 9602)
  local function auraN(n)
    return com(n, function() local k = 0; for e = 9600, 9603 do k = k + numExplod(e) end; return k end)
  end
  local held = {{}, {}}
  local pendingPos = {}
  local function setMaps()
    local now = clock()
    for p = 1, 2 do
      com(p, function()
        for _, nome in ipairs(CMDS) do
          local ate = held[p][nome]
          mapSet("t_" .. nome, (ate and ate > now) and 1 or 0)
        end
        local pp = pendingPos[p]
        if pp then mapSet("t_posx", pp + 1000); mapSet("t_pos", 1) else mapSet("t_pos", 0) end
        return 0
      end)
      pendingPos[p] = nil
    end
  end

  -- ---------------------------------------------------------------- DSL de passos
  local scenarios = {}
  local steps, c
  local function add(f) steps[#steps + 1] = f end
  local ativo = (LUTADOR ~= "hazaki")  -- os roteiros daqui ate o bloco do Hazak sao dos outros lutadores
  local function S(name, build) if ativo then scenarios[#scenarios + 1] = {name = name, build = build} end end
  local ABORT = false
  local function wait(n)
    local ate
    add(function() ate = ate or (clock() + n); return clock() >= ate end)
  end
  local function press(p, nomes, n)
    local ate, s0
    add(function()
      if p ~= 1 then for _, nome in ipairs(nomes) do held[p][nome] = clock() + (n or 2) end; return true end
      local s = snap(1).st
      s0 = s0 or s; ate = ate or (clock() + 30)
      if s ~= s0 or clock() >= ate then return true end
      for _, nome in ipairs(nomes) do held[1][nome] = clock() + 2 end
      return false
    end)
  end
  local function acao(fn) add(function() fn(); return true end) end
  -- espera a condicao; registra PASS/FAIL; se abortar ~= false e falhar, encerra o roteiro
  local function need(cond, max, msg, abortar)
    local ate
    add(function()
      ate = ate or (clock() + (max or 60))
      if cond() then log("  PASS " .. msg); return true end
      if clock() >= ate then
        log("  FAIL " .. msg); if abortar ~= false then ABORT = true end
        return true
      end
      return false
    end)
  end
  local function approach(dist)
    local ate
    add(function()
      ate = ate or (clock() + 60)
      local s = snap(1)
      if math.abs(s.d - dist) <= 2 and clock() > ate - 56 then return true end
      if clock() >= ate then log("  FAIL nao conseguiu se posicionar (d=" .. s.d .. ")"); ABORT = true; return true end
      pendingPos[1] = s.x + (s.d - dist) * (s.fa >= 0 and 1 or -1)
      return false
    end)
    wait(3)
  end
  local function st1() return snap(1).st end
  local function lifeP2() return snap(2).life end
  local function contatoEm(est) return function() local s = snap(1); return s.st == est and s.mc > 0 end end
  local function estadoEm(est) return function() return st1() == est end end
  local function livre() return snap(1).ctrl end
  local function note(fn) acao(function() log("  " .. fn()) end) end

  -- ---------------------------------------------------------------- roteiros
  local function corrente(nome, botao, primeiro, seq, dist, janela)
    S("corrente " .. nome, function()
      approach(dist or 28)
      acao(function() c.vida0 = lifeP2() end)
      press(1, {botao}, 2)
      need(function() local s = st1(); return s == primeiro[1] or s == primeiro[2] end, 30, "1o golpe entrou em " .. primeiro[1] .. "/" .. primeiro[2])
      for i, est in ipairs(seq) do
        need(function() local s = snap(1); return s.mc > 0 end, 80, "golpe " .. (i == 1 and "1" or seq[i - 1]) .. " encostou")
        press(1, {botao}, 2)
        need(estadoEm(est), janela or 20, "foi para " .. est)
        acao(function() log("      v10=" .. snap(1).v10) end)
      end
      wait(40)
      note(function() return "dano total no P2: " .. (c.vida0 - lifeP2()) .. "; P2 estado " .. snap(2).st end)
      need(livre, 200, "voltou ao controle", false)
    end)
  end
  corrente("x", "x", {200, 200}, {301, 302, 303})
  corrente("y", "y", {215, 210}, {311, 312, 313})
  corrente("a", "a", {230, 230}, {321, 322, 323})
  corrente("b", "b", {245, 240}, {331, 332, 333})

  S("corrente x contra defesa (nao pode sair o finalizador)", function()
    approach(28)
    press(1, {"x"}, 2)
    need(contatoEm(200), 60, "200 encostou")
    press(1, {"x"}, 2); need(estadoEm(301), 20, "301")
    need(contatoEm(301), 60, "301 encostou")
    press(1, {"x"}, 2); need(estadoEm(302), 20, "302")
    need(contatoEm(302), 60, "302 encostou")
    add(function() held[1].v10 = clock() + 40; return true end)
    press(1, {"x"}, 2); wait(15)
    note(function() return "estado " .. st1() .. ", v10=" .. snap(1).v10 .. ", vida P2 " .. lifeP2() end)
    need(function() return st1() ~= 303 end, 1, "finalizador NAO saiu com golpes defendidos", false)
  end)

  local function kombo(nome, inicio, passos)
    S("kombo " .. nome, function()
      approach(28)
      acao(function() c.vida0 = lifeP2() end)
      press(1, inicio, 2)
      for _, p in ipairs(passos) do
        need(contatoEm(p.de), 80, "golpe " .. p.de .. " encostou")
        press(1, p.botoes, 2)
        need(estadoEm(p.para), 20, "foi para " .. p.para)
      end
      wait(50)
      note(function() return "dano total no P2: " .. (c.vida0 - lifeP2()) .. "; P2 estado " .. snap(2).st end)
    end)
  end
  kombo("1 Abertura", {"golpe_216"}, {{de = 216, botoes = {"x"}, para = 340}, {de = 340, botoes = {"b"}, para = 341}})
  kombo("2 Alto e Baixo", {"x"}, {{de = 200, botoes = {"holddown", "a"}, para = 342}, {de = 342, botoes = {"y"}, para = 343}})
  kombo("3 Empurrao", {"golpe_201"}, {{de = 201, botoes = {"y"}, para = 344}, {de = 344, botoes = {"holdfwd", "b"}, para = 345}})
  if LUTADOR ~= "ck" then
  kombo("4 Lancador", {"a"}, {{de = 230, botoes = {"b"}, para = 346}, {de = 346, botoes = {"holddown", "y"}, para = 347}})
  else  -- CK: Sobe pro Teto (x, y, baixo + y)
  kombo("4 Sobe pro Teto", {"x"}, {{de = 200, botoes = {"y"}, para = 346}, {de = 346, botoes = {"holddown", "y"}, para = 347}})
  end

  S("agarrao Martelo e Garrafada", function()
    approach(8)
    acao(function() c.vida0 = lifeP2() end)
    press(1, {"agarrao_whisky"}, 2)
    need(estadoEm(831), 12, "831 pegou")
    need(function() return lifeP2() < c.vida0 end, 80, "capoeira tirou vida")
    note(function() return "apos capoeira: dano " .. (c.vida0 - lifeP2()) .. ", P2 estado " .. snap(2).st end)
    need(function() return st1() ~= 831 end, 150, "saiu do 831", false)
    wait(25)
    note(function() return "dano total: " .. (c.vida0 - lifeP2()) .. "; P2 estado " .. snap(2).st .. "; P1 estado " .. st1() end)
    need(function() return c.vida0 - lifeP2() >= 140 end, 1, "dano total >= 140", false)
    need(livre, 200, "P1 voltou ao controle", false)
  end)
  S("agarrao Martelo e Garrafada: longe nao pega", function()
    press(1, {"agarrao_whisky"}, 2)
    wait(4)
    note(function() return "estado " .. st1() .. " distancia " .. snap(1).d end)
    need(function() return st1() ~= 830 and st1() ~= 831 end, 1, "nao entrou (precisa estar colado)", false)
  end)
  S("escape do agarrao Martelo e Garrafada", function()
    approach(8)
    press(1, {"agarrao_whisky"}, 2)
    need(estadoEm(831), 12, "831 pegou")
    wait(2)
    press(2, {"y"}, 3)
    wait(60)
    note(function() return "P1 estado " .. st1() .. ", P2 estado " .. snap(2).st .. " (escapou se P1 voltou ao 0)" end)
  end)
  S("agarrao agachado", function()
    approach(5)
    press(2, {"holddown", "agacha"}, 400)
    wait(10)
    note(function() return "P2 estado " .. snap(2).st .. " (11 = agachado)" end)
    acao(function() c.vida0 = lifeP2(); local a, b = snap(1), snap(2); log(string.format("  antes: d=%d P2 st=%d tipo=%s P1 ctrl=%s tipo=%s", a.d, b.st, tostring(b.stt), tostring(a.ctrl), tostring(a.stt))) end)
    add(function()
      if snap(2).st == 12 then held[1].holddown = clock() + 2; held[1].y = clock() + 2; return true end
      return false
    end)
    wait(6)
    need(function() local s = st1(); return s == 840 or s == 841 end, 12, "840/841")
    need(estadoEm(841), 12, "841 pegou")
    need(function() return st1() ~= 841 end, 150, "saiu do 841", false)
    wait(25)
    note(function() return "dano: " .. (c.vida0 - lifeP2()) .. "; P2 estado " .. snap(2).st end)
  end)
  S("agarrao comum em pe", function()
    approach(6)
    press(1, {"holdfwd", "y"}, 3)
    wait(4)
    note(function() return "estado " .. st1() end)
    wait(60)
    note(function() return "dano: " .. (1000 - lifeP2()) .. "; estado " .. st1() end)
  end)

  local function projetil(nome, cmd, dist, esperado)
    S("projetil " .. nome, function()
      approach(dist)
      acao(function() c.vida0 = lifeP2() end)
      press(1, {cmd}, 2)
      need(estadoEm(esperado), 12, "entrou em " .. esperado)
      need(function() return snap(1).proj > 0 end, 70, "projetil na tela", false)
      wait(130)
      note(function() return "dano: " .. (c.vida0 - lifeP2()) .. "; dist " .. snap(1).d end)
    end)
  end
  projetil("LATADA antiga fraca (bola_fraca)", "bola_fraca", 70, 1000)
  projetil("LATADA antiga forte (bola_forte)", "bola_forte", 100, 1001)
  projetil("garrafada fraca (x)", "garrafa_x", 70, 1600)
  projetil("garrafada forte (y)", "garrafa_y", 100, 1601)

  local function role(nome, cmd, est)
    S(nome, function()
      approach(40)
      acao(function() local s = snap(1); c.x1 = s.x; c.x2 = snap(2).x; c.fa = s.fa end)
      press(1, {cmd}, 2)
      need(estadoEm(est), 12, "entrou em " .. est)
      need(function() return st1() == 0 end, 200, "terminou", false)
      note(function()
        local a, b = snap(1), snap(2)
        return string.format("P1 x %.0f -> %.0f; P2 x %.0f; facing %d -> %d; dano %d", c.x1, a.x, b.x, c.fa, a.fa, 1000 - b.life)
      end)
      need(function()
        local a, b = snap(1), snap(2)
        return a.fa ~= c.fa and ((a.x - b.x) * (c.x1 - c.x2) < 0)
      end, 1, "P1 ficou nas costas do P2 e virou para ele", false)
    end)
  end
  role("role por tras (a)", "role_a", 1700)
  role("role por tras e chute (b)", "role_b", 1701)

  S("role por tras no CANTO (a): fica na frente, virado", function()
    add(function() pendingPos[2] = 560; return true end)
    wait(6)
    add(function() pendingPos[1] = snap(2).x - 45; return true end)
    wait(6)
    acao(function() local s = snap(1); c.x1 = s.x; c.fa = s.fa; log(string.format("  P1 x %.0f, P2 x %.0f (canto), borda frente do P1 %.0f", s.x, snap(2).x, s.borda)) end)
    press(1, {"role_a"}, 2)
    need(estadoEm(1700), 12, "entrou em 1700")
    need(function() return st1() == 0 end, 200, "terminou", false)
    note(function() local a, b = snap(1), snap(2); return string.format("depois: P1 x %.0f, P2 x %.0f, facing %d (antes %d)", a.x, b.x, a.fa, c.fa) end)
    need(function() local a, b = snap(1), snap(2); return a.fa == c.fa and a.x < b.x end, 1, "ficou na FRENTE do P2, virado, sem atravessar a parede", false)
  end)

  S("despertar x+y com barra cheia", function()
    approach(60)
    acao(function() com(1, function() setPower(3000); return 0 end); c.d0 = snap(1).d end)
    wait(3)
    press(1, {"despertar"}, 3)
    need(estadoEm(2000), 12, "entrou em 2000")
    if LUTADOR == "ck" then  -- a aura do Ratao nasce quando ele sai da fumaca (tique 69) e o paredao dela espera o de cena
      need(function() local s = snap(1); return s.st == 2000 and s.t >= 60 end, 200, "cena no tique 60 (a superpausa de 30 conta no relogio)")
      need(function() return auraN(1) == 0 end, 1, "sem aura antes de o Ratao sair da fumaca", false)
      need(function() local s = snap(1); return s.st == 2000 and s.t >= 76 end, 60, "cena no tique 76")
      note(function() local p, h = com(1, function() return numExplod(9250) end), com(1, function() return map("au_ck_h0") end)
        return string.format("tique 76: paredao de cena %d, h0 %.2f, camadas %d", p, h, auraN(1)) end)
      need(function() local p, h = com(1, function() return numExplod(9250) end), com(1, function() return map("au_ck_h0") end)
        return auraN(1) == 3 and (p == 0 or h > 0.9) end, 1,
        "aura nascida (3 camadas) e o paredao dela apagado enquanto o paredao da cena toca", false)
      need(function() return com(1, function() return numExplod(9250) end) == 0 end, 60, "paredao de cena saiu")
      note(function() local s = snap(1); return "paredao de cena saiu no tique " .. s.t .. " do estado " .. s.st end)
    end
    need(function() return st1() ~= 2000 end, 500, "transformacao terminou", false)
    note(function() local s = snap(1); return "var20=" .. s.v20 .. " power=" .. s.pow .. " dist " .. c.d0 .. " -> " .. s.d end)
    need(function() local s = snap(1); return s.v20 > 0 and s.pow == 0 end, 1, "despertou e gastou a barra toda", false)
    need(function() return snap(1).d > c.d0 end, 1, "empurrou o oponente para longe", false)
  end)
  S("despertar SEM barra cheia (2 estoques)", function()
    approach(60)
    acao(function() com(1, function() setPower(2000); return 0 end) end)
    wait(3)
    press(1, {"despertar"}, 3)
    wait(12)
    need(function() return st1() ~= 2000 end, 1, "nao despertou com 2 estoques", false)
  end)

  local function desperto(nome, build)
    S("[desperto] " .. nome, function()
      add(function() held[1].desperto = clock() + 3; return true end)
      wait(4)
      build()
    end)
  end
  if LUTADOR == "pengaro" then
    -- a aura liga inteira e ja apagou quando o corpo volta a forma base (o fade de saida acaba junto com o var(20))
    desperto("aura do endiabrado: liga as 4 camadas e apaga junto com a forma endiabrada", function()
      wait(70)
      need(function() return auraN(1) == 4 end, 10, "as 4 camadas da aura (9600 a 9603) vivas no Despertar")
      add(function() held[1].fimdesp = clock() + 2; return true end)
      need(function() local v = snap(1).v20; return v > 0 and v <= 40 end, 10, "Despertar no fim (var20 <= 40)")
      need(function() return snap(1).v37 == 0 end, 60, "o corpo voltou a forma base (var37 = 0)")
      acao(function() c.aura_volta = auraN(1); c.t_volta = clock() end)
      need(function() return auraN(1) == 0 end, 2, "a aura apaga no maximo 2 tiques depois do corpo voltar", false)
      note(function() return "camadas quando o corpo voltou: " .. c.aura_volta .. "; apagou " .. (clock() - c.t_volta) .. " tiques depois" end)
    end)
  end
  if LUTADOR == "ck" then
    -- aura do Ratao (ferramentas/aura_ck.py: paredao 9600, chao 9601, fagulhas 9602): liga inteira e ja apagou
    -- quando o corpo volta a forma base (o fade de saida acaba junto com o var(20))
    desperto("aura do Ratao: liga as 3 camadas e apaga junto com a forma do Ratao", function()
      wait(70)
      need(function() return auraN(1) == 3 end, 10, "as 3 camadas da aura (9600 a 9602) vivas no Despertar")
      need(function() return com(1, function() return map("au_ck_h0") end) < 0.05 end, 1, "o paredao da aura aparece (sem paredao de cena)", false)
      add(function() held[1].fimdesp = clock() + 2; return true end)
      need(function() local v = snap(1).v20; return v > 0 and v <= 40 end, 10, "Despertar no fim (var20 <= 40)")
      need(function() return snap(1).v37 == 0 end, 60, "o corpo voltou a forma base (var37 = 0)")
      acao(function() c.aura_volta = auraN(1); c.t_volta = clock() end)
      need(function() return auraN(1) == 0 end, 2, "a aura apaga no maximo 2 tiques depois do corpo voltar", false)
      note(function() return "camadas quando o corpo voltou: " .. c.aura_volta .. "; apagou " .. (clock() - c.t_volta) .. " tiques depois" end)
    end)
    -- o Grave do Paredao poe o paredao de cena (Explod 9250): o da aura sai da frente enquanto ele toca e volta depois
    desperto("aura do Ratao: o paredao dela da lugar ao paredao do Grave (3403) e volta", function()
      approach(50)
      wait(40)
      press(1, {"sombra_b"}, 3)
      need(estadoEm(3403), 14, "entrou em 3403")
      need(function() return com(1, function() return numExplod(9250) end) > 0 end, 20, "paredao de cena na tela")
      wait(12)
      need(function() return com(1, function() return map("au_ck_h0") end) > 0.9 end, 1, "paredao da aura apagado enquanto o de cena toca", false)
      need(function() return com(1, function() return numExplod(9250) end) == 0 end, 80, "paredao de cena saiu")
      wait(20)
      need(function() return com(1, function() return map("au_ck_h0") end) < 0.01 and auraN(1) == 3 end, 1, "paredao da aura de volta, 3 camadas", false)
    end)
  end
  local function exclusivo(nome, cmd, est, dist)
    desperto(nome, function()
      approach(dist)
      acao(function() c.vida0 = lifeP2(); c.x1 = snap(1).x end)
      press(1, {cmd}, 2)
      need(estadoEm(est), 12, "entrou em " .. est)
      need(function() return st1() == 0 end, 250, "terminou", false)
      wait(110)
      note(function() return string.format("dano %d; P1 x %.0f -> %.0f; estado final %d; v20=%d", c.vida0 - lifeP2(), c.x1, snap(1).x, st1(), snap(1).v20) end)
      need(livre, 100, "voltou ao controle", false)
    end)
  end
  exclusivo("Mao de Sombra", "sombra_x", 3400, 60)
  exclusivo("Chute da Corrente", "sombra_y", 3401, 90)
  exclusivo("Sombra Atravessada", "sombra_a", 3402, 40)
  exclusivo("Queda Escura", "sombra_b", 3403, 50)

  local function normalDesp(nome, botoes, est, dist)
    desperto("normal " .. nome, function()
      approach(dist)
      acao(function() c.vida0 = lifeP2() end)
      press(1, botoes, 3)
      need(estadoEm(est), 14, "entrou em " .. est)
      wait(70)
      note(function() return "dano " .. (c.vida0 - lifeP2()) .. "; P2 estado " .. snap(2).st end)
    end)
  end
  normalDesp("baixo+y", {"holddown", "y"}, 3430, 22)
  normalDesp("baixo+b", {"holddown", "b"}, 3435, 40)
  normalDesp("frente+y", {"holdfwd", "y"}, 3431, 38)
  normalDesp("frente+b", {"holdfwd", "b"}, 3432, 50)
  normalDesp("tras+x", {"holdback", "x"}, 3433, 38)
  normalDesp("tras+a", {"holdback", "a"}, 3434, 38)

  local function correnteDesp(nome, botao, seq)
    desperto("corrente " .. nome, function()
      approach(30)
      acao(function() c.vida0 = lifeP2() end)
      press(1, {botao}, 2)
      need(estadoEm(seq[1]), 14, "1o golpe " .. seq[1])
      for i = 2, #seq do
        need(contatoEm(seq[i - 1]), 80, seq[i - 1] .. " encostou")
        press(1, {botao}, 2)
        need(estadoEm(seq[i]), 20, "foi para " .. seq[i])
      end
      wait(55)
      note(function() return "dano total " .. (c.vida0 - lifeP2()) .. "; P2 estado " .. snap(2).st .. "; v10=" .. snap(1).v10 end)
    end)
  end
  correnteDesp("y", "y", {3410, 3411, 3412, 3413})
  correnteDesp("b", "b", {3420, 3421, 3422, 3423})
  if LUTADOR ~= "ck" then
  desperto("kombo Possessao (b, a, x)", function()
    approach(28)
    acao(function() c.vida0 = lifeP2() end)
    press(1, {"b"}, 2)
    need(contatoEm(3420), 60, "3420 encostou")
    press(1, {"a"}, 2); need(estadoEm(348), 20, "348")
    need(contatoEm(348), 80, "348 encostou")
    press(1, {"x"}, 2); need(estadoEm(349), 20, "349")
    wait(70)
    note(function() return "dano " .. (c.vida0 - lifeP2()) end)
  end)
  else  -- CK: Fim de Baile (x, frente + y, b)
  desperto("kombo Fim de Baile (x, frente+y, b)", function()
    approach(28)
    acao(function() c.vida0 = lifeP2() end)
    press(1, {"x"}, 2)
    need(contatoEm(200), 60, "200 encostou")
    press(1, {"holdfwd", "y"}, 2); need(estadoEm(3431), 20, "3431")
    need(contatoEm(3431), 80, "3431 encostou")
    press(1, {"b"}, 2); need(estadoEm(349), 20, "349")
    wait(70)
    note(function() return "dano " .. (c.vida0 - lifeP2()) end)
  end)
  end

  S("super 1: Chuva de Bebidas (1 estoque)", function()
    approach(80)
    acao(function() com(1, function() setPower(1000); return 0 end); c.vida0 = lifeP2() end)
    wait(3)
    press(1, {"golaco"}, 3)
    need(estadoEm(3000), 14, "entrou em 3000")
    need(function() return st1() == 0 end, 300, "terminou", false)
    wait(70)
    note(function() return "dano " .. (c.vida0 - lifeP2()) .. "; barra " .. snap(1).pow end)
    need(function() return c.vida0 - lifeP2() > 100 end, 1, "a chuva acertou (dano > 100)", false)
    need(function() return snap(1).pow == 0 end, 1, "gastou o estoque", false)
  end)

  desperto("super: Saideira Sombria (3100) fica endiabrado do comeco ao fim", function()
    approach(60)
    acao(function() com(1, function() setPower(1000); return 0 end); c.vida0 = lifeP2() end)
    wait(3)
    press(1, {LUTADOR == "ck" and "baile" or "golaco"}, 3)  -- no CK o golaco do Ratao e a Rajada (3000)
    need(estadoEm(3100), 14, "entrou em 3100")
    need(function() local s = snap(1); return s.st == 3100 and s.t > 20 and s.v37 == 1 end, 80, "var(37) = 1 (arte endiabrada) no meio do 3100")
    need(function() return st1() == 0 end, 300, "terminou", false)
    if LUTADOR == "pengaro" then  -- o 3100 zera o var(20): a aura apaga antes de ele acabar, pelo AnimTime
      need(function() return auraN(1) == 0 end, 2, "a aura ja apagou quando o 3100 acabou (forma base)", false)
    end
    note(function() local s = snap(1); return "dano " .. (c.vida0 - lifeP2()) .. "; var20=" .. s.v20 .. " var37=" .. s.v37 end)
    need(function() return c.vida0 - lifeP2() > 150 end, 1, "o super acertou (dano > 150)", false)
  end)

  local function golpeSimples(nome, cmd, est, dist)
    S(nome, function()
      approach(dist)
      acao(function() c.vida0 = lifeP2() end)
      press(1, cmd, 3)
      need(estadoEm(est), 14, "entrou em " .. est)
      need(function() return st1() == 0 end, 200, "terminou", false)
      wait(40)
      note(function() return "dano " .. (c.vida0 - lifeP2()) .. "; P2 estado " .. snap(2).st end)
      need(function() return c.vida0 - lifeP2() > 0 end, 1, "acertou", false)
    end)
  end
  golpeSimples("Passo de Letra (246)", {"golpe_246"}, 246, 40)
  golpeSimples("Mao de Chimpa fraca (1400)", {"golpe_1400"}, 1400, 40)
  golpeSimples("Sola de Varzea fraca (1500)", {"golpe_1500"}, 1500, 40)

  S("super 2: Bando da Varzea (3200, 2 estoques)", function()
    approach(60)
    acao(function() com(1, function() setPower(2000); return 0 end); c.vida0 = lifeP2() end)
    wait(3)
    press(1, {"golpe_3200"}, 3)
    need(estadoEm(3200), 14, "entrou em 3200")
    need(function() return st1() == 0 end, 300, "terminou", false)
    wait(40)
    note(function() return "dano " .. (c.vida0 - lifeP2()) .. "; barra " .. snap(1).pow end)
    need(function() return c.vida0 - lifeP2() > 150 end, 1, "o super acertou (dano > 150)", false)
  end)

  S("cancelar o 2o golpe da corrente em especial (garrafada)", function()
    approach(28)
    press(1, {"x"}, 2); need(contatoEm(200), 60, "200 encostou")
    press(1, {"x"}, 2); need(estadoEm(301), 20, "301")
    need(contatoEm(301), 60, "301 encostou")
    press(1, {"garrafa_x"}, 2)
    need(estadoEm(1600), 15, "cancelou 301 em 1600")
  end)

  if LUTADOR == "ck" then  -- golpes que so o CK tem
    desperto("super: Baile da Esquina pelo comando proprio (tras, frente, baixo + x+y)", function()
      approach(60)
      acao(function() com(1, function() setPower(1000); return 0 end); c.vida0 = lifeP2() end)
      wait(3)
      press(1, {"baile"}, 3)
      need(estadoEm(3100), 14, "entrou em 3100")
      need(function() return st1() == 0 end, 300, "terminou", false)
      note(function() return "dano " .. (c.vida0 - lifeP2()) end)
      need(function() return c.vida0 - lifeP2() > 150 end, 1, "o super acertou (dano > 150)", false)
    end)
    desperto("Baile da Esquina nao encerra o Ratao (var(20) continua ligado)", function()
      approach(60)
      acao(function() com(1, function() setPower(1000); return 0 end) end)
      wait(3)
      press(1, {"baile"}, 3)
      need(estadoEm(3100), 14, "entrou em 3100")
      need(function() local s = snap(1); return s.st == 3100 and s.t > 20 and s.v20 > 0 end, 80, "var(20) > 0 no meio do 3100")
      need(function() return st1() == 0 end, 300, "terminou", false)
      need(function() return snap(1).v20 > 0 end, 1, "continua no Ratao depois do Baile", false)
      need(function() return auraN(1) == 3 end, 1, "a aura do Ratao segue inteira depois do Baile (3 camadas)", false)
    end)
    desperto("Rajada da Esquina no Ratao (golaco entra em 3000, nao no Baile)", function()
      approach(80)
      acao(function() com(1, function() setPower(1000); return 0 end); c.vida0 = lifeP2() end)
      wait(3)
      press(1, {"golaco"}, 3)
      need(estadoEm(3000), 14, "entrou em 3000")
      need(function() return st1() == 0 end, 300, "terminou", false)
      wait(70)
      note(function() return "dano " .. (c.vida0 - lifeP2()) end)
      need(function() return c.vida0 - lifeP2() > 100 end, 1, "a rajada acertou (dano > 100)", false)
    end)
    S("Encosta na Parede: no 344, frente + b com o role_b junto sai o 345 (nao o Gingado)", function()
      approach(28)
      press(1, {"golpe_201"}, 2)
      need(contatoEm(201), 60, "201 encostou")
      press(1, {"y"}, 2); need(estadoEm(344), 20, "344")
      need(contatoEm(344), 80, "344 encostou")
      press(1, {"holdfwd", "b", "role_b"}, 2)
      need(estadoEm(345), 20, "foi para 345", false)
    end)
    S("Tragada no ar nao trava o Bone Voador", function()
      approach(120)
      press(1, {"bola_fraca"}, 2)
      need(estadoEm(1000), 12, "entrou em 1000")
      need(function() return st1() == 0 and snap(1).proj > 0 end, 120, "voltou ao 0 com a nuvem no ar")
      press(1, {"garrafa_x"}, 2)
      need(estadoEm(1600), 15, "entrou em 1600 com a nuvem no ar", false)
    end)
    S("Agarrao em pe: tres socos (dano em 3 vezes, 100 no total)", function()
      approach(6)
      acao(function() c.vida0 = lifeP2(); c.golpes = 0; c.ult = lifeP2() end)
      press(1, {"holdfwd", "y"}, 3)
      need(estadoEm(810), 30, "entrou em 810")
      add(function()
        local v = lifeP2()
        if v < c.ult then c.golpes = c.golpes + 1; c.ult = v end
        return st1() ~= 810
      end)
      note(function() return "socos " .. c.golpes .. "; dano " .. (c.vida0 - lifeP2()) end)
      need(function() return c.golpes == 3 end, 1, "o dano saiu em 3 socos", false)
    end)
    S("Contragolpe (caneta_x) sem apanhar: guarda baixa e volta", function()
      approach(60)
      press(1, {"caneta_x"}, 2)
      need(estadoEm(1300), 12, "entrou em 1300")
      need(function() return st1() == 0 end, 200, "voltou ao 0", false)
    end)
    S("Contragolpe: apanhou na janela, responde com o cruzado (1310)", function()
      approach(28)
      acao(function() c.vida0 = lifeP2(); c.vida1 = snap(1).life end)
      press(1, {"caneta_x"}, 2)
      need(estadoEm(1300), 12, "entrou em 1300")
      wait(4)
      press(2, {"x"}, 3)
      need(estadoEm(1310), 40, "aparou o soco e foi para 1310", false)
      wait(70)
      note(function() return "dano no P2 " .. (c.vida0 - lifeP2()) .. "; dano no P1 " .. (c.vida1 - snap(1).life) end)
      need(function() return c.vida0 - lifeP2() > 0 end, 1, "o cruzado acertou", false)
    end)
    S("Pendulo (compasso_a): balanca e volta", function()
      approach(60)
      press(1, {"compasso_a"}, 2)
      need(estadoEm(1100), 12, "entrou em 1100")
      need(function() return st1() == 0 end, 200, "voltou ao 0", false)
    end)
    S("Pendulo: x no meio sai com o direto (1110)", function()
      approach(28)
      acao(function() c.vida0 = lifeP2() end)
      press(1, {"compasso_a"}, 2)
      need(estadoEm(1100), 12, "entrou em 1100")
      wait(10)
      press(1, {"x"}, 2)
      need(estadoEm(1110), 20, "saiu com o direto (1110)", false)
      wait(60)
      note(function() return "dano " .. (c.vida0 - lifeP2()) end)
      need(function() return c.vida0 - lifeP2() > 0 end, 1, "o direto acertou", false)
    end)
  end

  -- ================================================================ HAZAK (so quando o P1 e o hazaki)
  -- Os roteiros acima ficam desligados para ele (S() nao registra) e os de baixo so entram para ele: a lista dos
  -- outros lutadores nao muda. Golpes e numeros em ferramentas/hazaki_golpes.py.
  ativo = (LUTADOR == "hazaki")
  -- janela 40: o jab duplo (301) so continua depois do 2o jab
  corrente("x (jab, jab duplo, cutucao, tapa)", "x", {200, 200}, {301, 302, 303}, 28, 40)
  corrente("y (soco reto, cruzado, cotovelada, punho curto)", "y", {210, 210}, {311, 312, 313})
  corrente("a (chute baixo, cintura, alto, tesoura)", "a", {230, 230}, {321, 322, 323})
  corrente("b (lateral, giratorio, gancho, machado)", "b", {240, 240}, {331, 332, 333})
  S("corrente x contra defesa (nao pode sair o finalizador)", function()
    approach(28)
    press(1, {"x"}, 2)
    need(contatoEm(200), 60, "200 encostou")
    press(1, {"x"}, 2); need(estadoEm(301), 20, "301")
    need(contatoEm(301), 60, "301 encostou")
    press(1, {"x"}, 2); need(estadoEm(302), 40, "302")
    need(contatoEm(302), 60, "302 encostou")
    add(function() held[1].v10 = clock() + 40; return true end)
    press(1, {"x"}, 2); wait(15)
    note(function() return "estado " .. st1() .. ", v10=" .. snap(1).v10 .. ", vida P2 " .. lifeP2() end)
    need(function() return st1() ~= 303 end, 1, "finalizador NAO saiu com acertos abaixo do limite", false)
  end)
  kombo("1 Bom Dia, Vizinho", {"golpe_246"}, {{de = 246, botoes = {"a"}, para = 340}, {de = 340, botoes = {"b"}, para = 341}})
  kombo("2 Rasteira de Calcada", {"x"}, {{de = 200, botoes = {"holddown", "a"}, para = 342}, {de = 342, botoes = {"b"}, para = 343}})
  kombo("3 Sai Daqui", {"golpe_201"}, {{de = 201, botoes = {"y"}, para = 344}, {de = 344, botoes = {"holdfwd", "y"}, para = 345}})
  kombo("4 Sobe, Mentiroso", {"a"}, {{de = 230, botoes = {"b"}, para = 346}, {de = 346, botoes = {"holddown", "y"}, para = 347}})

  S("agarrao Cutucao Sacana (bf_y)", function()
    approach(8)
    acao(function() c.vida0 = lifeP2() end)
    press(1, {"bf_y"}, 2)
    need(estadoEm(831), 12, "831 pegou")
    need(function() return lifeP2() < c.vida0 end, 80, "1o cutucao tirou vida")
    note(function() return "apos o 1o cutucao: dano " .. (c.vida0 - lifeP2()) .. ", P2 estado " .. snap(2).st end)
    need(function() return st1() ~= 831 end, 150, "saiu do 831", false)
    wait(25)
    note(function() return "dano total: " .. (c.vida0 - lifeP2()) .. "; P2 estado " .. snap(2).st .. "; P1 estado " .. st1() end)
    need(function() return c.vida0 - lifeP2() >= 140 end, 1, "dano total >= 140", false)
    need(livre, 200, "P1 voltou ao controle", false)
  end)
  S("agarrao Cutucao Sacana: longe nao pega", function()
    press(1, {"bf_y"}, 2)
    wait(4)
    note(function() return "estado " .. st1() .. " distancia " .. snap(1).d end)
    need(function() return st1() ~= 830 and st1() ~= 831 end, 1, "nao entrou (precisa estar colado)", false)
  end)
  S("escape do agarrao Cutucao Sacana", function()
    approach(8)
    acao(function() c.vida0 = lifeP2() end)
    press(1, {"bf_y"}, 2)
    need(estadoEm(831), 12, "831 pegou")
    wait(2)
    press(2, {"y"}, 3)
    wait(60)
    -- so nota (como no roteiro do Pengaro): preso no 832 o P2 roda o estado do P1 e o [Statedef -1] dele, onde o robo
    -- injeta o botao, nao roda. O escape com y/b so da para conferir com controle de verdade.
    note(function() return "P1 estado " .. st1() .. ", P2 estado " .. snap(2).st .. ", dano " .. (c.vida0 - lifeP2()) .. " (escapou se o dano e 0)" end)
  end)
  S("agarrao agachado Puxa a Perna", function()
    approach(5)
    press(2, {"holddown", "agacha"}, 400)
    wait(10)
    note(function() return "P2 estado " .. snap(2).st .. " (11 = agachado)" end)
    acao(function() c.vida0 = lifeP2(); local a, b = snap(1), snap(2); log(string.format("  antes: d=%d P2 st=%d tipo=%s P1 ctrl=%s tipo=%s", a.d, b.st, tostring(b.stt), tostring(a.ctrl), tostring(a.stt))) end)
    add(function()
      if snap(2).st == 12 then held[1].holddown = clock() + 2; held[1].y = clock() + 2; return true end
      return false
    end)
    wait(6)
    need(function() local s = st1(); return s == 840 or s == 841 end, 12, "840/841")
    need(estadoEm(841), 12, "841 pegou")
    need(function() return st1() ~= 841 end, 150, "saiu do 841", false)
    wait(25)
    note(function() return "dano: " .. (c.vida0 - lifeP2()) .. "; P2 estado " .. snap(2).st end)
    need(function() return c.vida0 - lifeP2() >= 100 end, 1, "dano >= 100", false)
  end)
  S("agarrao em pe Abraco de Quebrada", function()
    approach(6)
    acao(function() c.vida0 = lifeP2() end)
    press(1, {"holdfwd", "y"}, 3)
    need(estadoEm(810), 14, "810 pegou")
    wait(60)
    note(function() return "dano: " .. (c.vida0 - lifeP2()) .. "; estado " .. st1() .. "; P2 estado " .. snap(2).st end)
    need(function() return c.vida0 - lifeP2() >= 120 end, 1, "dano >= 120", false)
  end)

  local function projetilH(nome, cmd, dist, esperado)
    S("projetil " .. nome, function()
      approach(dist)
      acao(function() c.vida0 = lifeP2() end)
      press(1, {cmd}, 2)
      need(estadoEm(esperado), 12, "entrou em " .. esperado)
      need(function() return snap(1).proj > 0 end, 70, "projetil na tela", false)
      wait(130)
      note(function() return "dano: " .. (c.vida0 - lifeP2()) .. "; dist " .. snap(1).d end)
      need(function() return c.vida0 - lifeP2() > 0 end, 1, "o projetil acertou", false)
    end)
  end
  projetilH("Punho de Concreto fraco (df_x)", "df_x", 70, 1000)
  projetilH("Punho de Concreto forte (df_y)", "df_y", 100, 1001)
  projetilH("Estatueta Dourada fraca (fb_x)", "fb_x", 70, 1600)
  projetilH("Estatueta Dourada forte (fb_y)", "fb_y", 170, 1601)
  S("2o projetil recusado com um na tela", function()
    approach(170)
    press(1, {"df_x"}, 2)
    need(estadoEm(1000), 12, "entrou em 1000")
    need(function() return snap(1).proj > 0 end, 70, "projetil na tela")
    need(function() local s = snap(1); return s.st == 0 and s.ctrl end, 60, "P1 livre com o projetil na tela")
    add(function() held[1].df_x = clock() + 2; return true end)
    wait(5)
    note(function() local s = snap(1); return "estado " .. s.st .. ", projeteis " .. s.proj end)
    need(function() local s = snap(1); return s.st ~= 1000 and s.proj > 0 end, 1, "o 2o Punho de Concreto NAO saiu", false)
  end)

  role("Rolada de Tatame (a)", "bf_a", 1700)
  role("Rolada de Tatame e chute (b)", "bf_b", 1701)
  S("Rolada de Tatame no CANTO (a): fica na frente, virado", function()
    add(function() pendingPos[2] = 560; return true end)
    wait(6)
    add(function() pendingPos[1] = snap(2).x - 45; return true end)
    wait(6)
    acao(function() local s = snap(1); c.x1 = s.x; c.fa = s.fa; log(string.format("  P1 x %.0f, P2 x %.0f (canto), borda frente do P1 %.0f", s.x, snap(2).x, s.borda)) end)
    press(1, {"bf_a"}, 2)
    need(estadoEm(1700), 12, "entrou em 1700")
    need(function() return st1() == 0 end, 200, "terminou", false)
    note(function() local a, b = snap(1), snap(2); return string.format("depois: P1 x %.0f, P2 x %.0f, facing %d (antes %d)", a.x, b.x, a.fa, c.fa) end)
    need(function() local a, b = snap(1), snap(2); return a.fa == c.fa and a.x < b.x end, 1, "ficou na FRENTE do P2, virado, sem atravessar a parede", false)
  end)

  golpeSimples("Ascensao de Faixa fraca (fd_x)", {"fd_x"}, 1200, 10)
  golpeSimples("Ascensao de Faixa forte (fd_y)", {"fd_y"}, 1201, 10)
  golpeSimples("Giro de Garagem fraco (df_a)", {"df_a"}, 1300, 60)
  golpeSimples("Giro de Garagem forte (df_b)", {"df_b"}, 1301, 90)
  golpeSimples("Corte de Base fraco (db_a)", {"db_a"}, 1400, 40)
  golpeSimples("Corte de Base forte (db_b)", {"db_b"}, 1401, 50)
  golpeSimples("Pega Bolado fraco (bd_a)", {"bd_a"}, 1500, 70)
  golpeSimples("Pega Bolado forte (bd_b)", {"bd_b"}, 1501, 130)
  golpeSimples("Machado de Dojo por cima (246)", {"golpe_246"}, 246, 40)
  golpeSimples("Cotovelo de Faixa (216)", {"golpe_216"}, 216, 20)
  golpeSimples("rasteira (baixo + b)", {"holddown", "b"}, 440, 28)
  golpeSimples("joelhada subindo (baixo + y)", {"holddown", "y"}, 410, 8)

  S("Guarda de Aco (db_x): o P2 bate e leva a resposta", function()
    approach(28)
    acao(function() c.vida0 = lifeP2(); c.vida1 = snap(1).life end)
    press(1, {"db_x"}, 2)
    need(estadoEm(1100), 12, "entrou em 1100")
    press(2, {"x"}, 3)
    need(estadoEm(1102), 40, "reverteu o jab do P2 (1102)", false)
    wait(70)
    note(function() return "dano no P2: " .. (c.vida0 - lifeP2()) .. "; dano no P1: " .. (c.vida1 - snap(1).life) end)
    need(function() return c.vida0 - lifeP2() > 0 and snap(1).life == c.vida1 end, 1, "a resposta acertou e o P1 nao tomou dano", false)
  end)
  S("Guarda de Aco no vazio: nada acontece e volta", function()
    approach(60)
    press(1, {"db_x"}, 2)
    need(estadoEm(1100), 12, "entrou em 1100")
    need(function() return st1() == 0 end, 80, "voltou ao 0 sem responder", false)
  end)

  S("super 1: Faixa no Asfalto (bfd_a, 1 estoque)", function()
    approach(28)
    acao(function() com(1, function() setPower(1000); return 0 end); c.vida0 = lifeP2() end)
    wait(3)
    press(1, {"bfd_a"}, 3)
    need(estadoEm(3000), 14, "entrou em 3000")
    need(estadoEm(3001), 120, "rajada (3001)", false)
    need(estadoEm(3002), 120, "subiu chutando (3002)", false)
    need(estadoEm(3003), 120, "machado no pouso (3003)", false)
    need(function() return st1() == 0 end, 300, "terminou", false)
    wait(70)
    note(function() return "dano " .. (c.vida0 - lifeP2()) .. "; barra " .. snap(1).pow end)
    need(function() return c.vida0 - lifeP2() > 100 end, 1, "o super acertou (dano > 100)", false)
    need(function() return snap(1).pow < 1000 end, 1, "gastou o estoque", false)
  end)
  S("super 1 sem barra: nao sai", function()
    approach(28)
    acao(function() com(1, function() setPower(0); return 0 end) end)
    wait(3)
    add(function() held[1].bfd_a = clock() + 2; return true end)
    wait(8)
    need(function() return st1() ~= 3000 end, 1, "nao entrou em 3000 sem estoque", false)
  end)
  S("super 2: Rapidinho da Quebrada (bfd_x, 2 estoques)", function()
    approach(60)
    acao(function() com(1, function() setPower(2000); return 0 end); c.vida0 = lifeP2() end)
    wait(3)
    press(1, {"bfd_x"}, 3)
    need(estadoEm(3200), 14, "entrou em 3200")
    need(estadoEm(3201), 120, "1a passagem (3201)", false)
    need(estadoEm(3202), 200, "fechou com a voadora (3202)", false)
    need(function() return st1() == 0 end, 300, "terminou", false)
    wait(60)
    note(function() return "dano " .. (c.vida0 - lifeP2()) .. "; barra " .. snap(1).pow end)
    need(function() return c.vida0 - lifeP2() > 150 end, 1, "o super acertou (dano > 150)", false)
  end)

  S("cancelar o 2o golpe da corrente em especial (Punho de Concreto)", function()
    approach(28)
    press(1, {"x"}, 2); need(contatoEm(200), 60, "200 encostou")
    press(1, {"x"}, 2); need(estadoEm(301), 20, "301")
    need(contatoEm(301), 60, "301 encostou")
    press(1, {"df_x"}, 2)
    need(estadoEm(1000), 15, "cancelou 301 em 1000")
  end)

  -- ---- defesa de verdade (o P2 e o Hazak com T_defende): entra na guarda do motor e segura para tras
  local function p2defende(agachado)
    press(2, agachado and {"holddown", "agacha", "holdback", "defende"} or {"holdback", "defende"}, 900)
    wait(12)
    note(function() return "P2 estado " .. snap(2).st .. " tipo " .. tostring(snap(2).stt) end)
    acao(function() c.vida0 = lifeP2(); c.defendeu = false end)
  end
  -- vigia n ticks: anota se o P2 passou por um estado de golpe defendido (150 a 155)
  local function espia(n)
    local ate
    add(function()
      ate = ate or (clock() + n)
      local s = snap(2).st
      if s >= 150 and s <= 155 then c.defendeu = true end
      return clock() >= ate
    end)
  end
  local function seDefendeu() return "P2 defendeu: " .. tostring(c.defendeu) .. "; dano " .. (c.vida0 - lifeP2()) .. "; P2 estado " .. snap(2).st end
  S("corrente x contra DEFESA DE VERDADE (P2 em guarda): o finalizador nao sai", function()
    approach(28)
    p2defende(false)
    press(1, {"x"}, 2)
    need(contatoEm(200), 60, "200 encostou")
    espia(3)
    press(1, {"x"}, 2); need(estadoEm(301), 20, "301")
    need(contatoEm(301), 60, "301 encostou")
    espia(3)
    press(1, {"x"}, 2); need(estadoEm(302), 40, "302")
    need(contatoEm(302), 60, "302 encostou")
    espia(3)
    press(1, {"x"}, 2); wait(15)
    note(function() return "estado " .. st1() .. ", v10=" .. snap(1).v10 .. "; " .. seDefendeu() end)
    need(function() return c.defendeu and c.vida0 == lifeP2() end, 1, "os golpes foram DEFENDIDOS (sem dano)", false)
    need(function() return st1() ~= 303 end, 1, "finalizador NAO saiu com os golpes defendidos", false)
  end)
  S("Machado por cima (246) contra defesa AGACHADA: fura", function()
    approach(40)
    p2defende(true)
    press(1, {"golpe_246"}, 2)
    need(estadoEm(246), 12, "entrou em 246")
    espia(50)
    note(seDefendeu)
    need(function() return c.vida0 - lifeP2() > 20 and not c.defendeu end, 1, "o por cima acertou quem defendia agachado", false)
  end)
  S("Machado por cima (246) contra defesa EM PE: defende", function()
    approach(40)
    p2defende(false)
    press(1, {"golpe_246"}, 2)
    need(estadoEm(246), 12, "entrou em 246")
    espia(50)
    note(seDefendeu)
    need(function() return c.vida0 == lifeP2() and c.defendeu end, 1, "em pe o por cima foi defendido", false)
  end)
  S("Punho de Concreto (df_x) contra defesa EM PE: acerta (so defende agachado)", function()
    approach(70)
    p2defende(false)
    press(1, {"df_x"}, 2)
    need(estadoEm(1000), 12, "entrou em 1000")
    espia(140)
    note(seDefendeu)
    need(function() return c.vida0 - lifeP2() > 20 and not c.defendeu end, 1, "a lasca acertou quem defendia em pe", false)
  end)
  S("Punho de Concreto (df_x) contra defesa AGACHADA: defende", function()
    approach(70)
    p2defende(true)
    press(1, {"df_x"}, 2)
    need(estadoEm(1000), 12, "entrou em 1000")
    espia(140)
    note(seDefendeu)
    need(function() return c.vida0 - lifeP2() <= 10 and c.defendeu end, 1, "agachado a lasca foi defendida (so o dano de raspao)", false)
  end)
  S("Pega Bolado forte (bd_b) DEFENDIDO: cai no 1503 (erra feio)", function()
    approach(130)
    p2defende(false)
    press(1, {"bd_b"}, 2)
    need(estadoEm(1501), 12, "entrou em 1501")
    need(estadoEm(1503), 120, "defendido, pousou no 1503", false)
    note(seDefendeu)
  end)
  local function guardaContraBaixo(nome, cmd, est, reverte)
    S(nome, function()
      approach(28)
      press(2, {"holddown", "agacha"}, 600)
      wait(12)
      acao(function() c.vida0 = lifeP2(); c.vida1 = snap(1).life; c.resp = false end)
      press(1, {cmd}, 2)
      need(estadoEm(est), 12, "entrou em " .. est)
      press(2, {"a"}, 3)
      local ate
      add(function()
        ate = ate or (clock() + 60)
        if st1() == est + 2 then c.resp = true end
        return clock() >= ate
      end)
      note(function() return "respondeu: " .. tostring(c.resp) .. "; dano no P2 " .. (c.vida0 - lifeP2()) .. "; dano no P1 " .. (c.vida1 - snap(1).life) end)
      if reverte then
        need(function() return c.resp and snap(1).life == c.vida1 end, 1, "reverteu o chute na canela do P2 agachado", false)
      else
        need(function() return (not c.resp) and snap(1).life < c.vida1 end, 1, "o x NAO pega golpe baixo: o P1 levou o chute na canela", false)
      end
    end)
  end
  guardaContraBaixo("Guarda de Aco y (db_y) contra golpe baixo: reverte", "db_y", 1101, true)
  guardaContraBaixo("Guarda de Aco x (db_x) contra golpe baixo: nao reverte", "db_x", 1100, false)

  S("Despertar desligado: x + y com barra cheia nao transforma", function()
    approach(60)
    acao(function() com(1, function() setPower(3000); return 0 end) end)
    wait(3)
    add(function() held[1].x = clock() + 3; held[1].y = clock() + 3; return true end)
    wait(14)
    note(function() local s = snap(1); return "estado " .. s.st .. ", var20=" .. s.v20 .. ", barra " .. s.pow end)
    need(function() local s = snap(1); return s.st ~= 2000 and s.v20 == 0 end, 1, "nao entrou no 2000 (Despertar pendente)", false)
  end)

  -- fica por ultimo: o nocaute acaba com o round
  S("DERROTA: o P1 com 1 de vida leva um jab; levanta e foge da tela", function()
    approach(28)
    acao(function() com(1, function() setLife(1); return 0 end) end)
    wait(3)
    acao(function() local s = snap(1); c.x0 = s.x; c.fa = s.fa; c.saiu = false; c.viu171 = false end)
    press(2, {"x"}, 3)
    need(function() return snap(1).life <= 0 end, 60, "P1 nocauteado")
    for i = 1, 30 do
      local ate
      add(function()
        ate = ate or (clock() + 10)
        local s = snap(1)
        if s.an == 171 and not c.viu171 then c.viu171 = true; c.x171 = s.x end
        if s.sx < -20 or s.sx > 340 then c.saiu = true end
        return clock() >= ate
      end)
      note(function()
        local s = snap(1)
        return string.format("+%3d P1 estado %d anim %d x %.0f telaX %.0f facing %d; round %d", i * 10, s.st, s.an, s.x, s.sx, s.fa, roundState())
      end)
    end
    need(function() return c.viu171 end, 1, "a animacao da fuga (171) tocou", false)
    need(function() local s = snap(1); return c.x171 and (s.x - c.x171) * c.fa < -100 end, 1, "depois de levantar ele andou mais de 100 px para TRAS (para longe do oponente)", false)
    need(function() return c.saiu end, 1, "saiu da tela (telaX fora de 0..320)", false)
  end)

  -- ---------------------------------------------------------------- motor do robo
  local fase, idx, espera = "espera", 0, 0
  local ligado = true
  local passo, last, t0 = 1, {}, 0
  hook.add("loop", "robo", function()
    if not ligado then return end
    local ok, err = pcall(function()
      if fase == "espera" then
        if roundState() == 2 then fase = "novo" end
        return
      end
      if fase == "novo" then
        idx = idx + 1
        if idx > #scenarios then
          log("\nFIM: " .. (idx - 1) .. " roteiros")
          ligado = false
          LOG:close()
          return
        end
        held = {{}, {}}
        resetRound()
        fase = "reiniciando"; espera = 0
        return
      end
      if fase == "reiniciando" then
        espera = espera + 1
        if espera > 12 and roundState() == 2 then
          local cur = scenarios[idx]
          log("\n=== " .. idx .. " " .. cur.name)
          steps, c, ABORT = {}, {}, false
          cur.build()
          passo, last, t0, espera = 1, {}, clock(), 0
          fase = "roda"
        end
        return
      end
      if fase == "roda" then
        espera = espera + 1
        setMaps()
        local a, b = snap(1), snap(2)
        if last.s1 ~= a.st then log(string.format("  [%3d] P1 estado %s (vida %d)", clock() - t0, a.st, a.life)); last.s1 = a.st end
        if last.s2 ~= b.st then log(string.format("  [%3d] P2 estado %s (vida %d)", clock() - t0, b.st, b.life)); last.s2 = b.st end
        if ABORT or passo > #steps or espera > 2500 then
          if espera > 2500 then log("  TEMPO ESGOTADO NO ROTEIRO (passo " .. passo .. ")") end
          fase = "novo"
          return
        end
        if steps[passo]() then passo = passo + 1 end
      end
    end)
    if not ok then log("ERRO NO ROBO: " .. tostring(err)); ligado = false; LOG:close() end
  end)
  pcall(function() setAccel(4) end)
  log("robo carregado: " .. #scenarios .. " roteiros")
end
