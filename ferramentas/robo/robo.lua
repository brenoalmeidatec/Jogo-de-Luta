-- ROBO DE TESTE (so na copia de teste): simula botoes pelo AssertCommand e registra o que cada golpe faz.
do
  local SAIDA = "@SAIDA@"
  local LOG = io.open(SAIDA, "w")
  local function log(s) LOG:write(s, "\n"); LOG:flush() end
  local CMDS = {"x","y","a","b","c","holdfwd","holdback","holdup","holddown","agarrao_whisky","garrafa_x","garrafa_y",
    "role_a","role_b","sombra_x","sombra_y","sombra_a","sombra_b","despertar","FF","rolar","afastar","golaco",
    "golpe_216","golpe_246","golpe_201","golpe_231","golpe_1400","golpe_1401","golpe_1500","golpe_1501","golpe_3200","bola_fraca","bola_forte","parry","desperto","agacha","v10"}
  local LUTADOR = "@LUTADOR@"  -- testar_pengaro.py troca pelo --lutador; sem a troca, valem os roteiros de sempre
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
              borda = frontEdgeBodyDist(), proj = numProj(), stt = stateType()}
    end)
  end

  local function clock() return roundTime() end
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
  local function S(name, build) scenarios[#scenarios + 1] = {name = name, build = build} end
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
  local function corrente(nome, botao, primeiro, seq, dist)
    S("corrente " .. nome, function()
      approach(dist or 28)
      acao(function() c.vida0 = lifeP2() end)
      press(1, {botao}, 2)
      need(function() local s = st1(); return s == primeiro[1] or s == primeiro[2] end, 30, "1o golpe entrou em " .. primeiro[1] .. "/" .. primeiro[2])
      for i, est in ipairs(seq) do
        need(function() local s = snap(1); return s.mc > 0 end, 80, "golpe " .. (i == 1 and "1" or seq[i - 1]) .. " encostou")
        press(1, {botao}, 2)
        need(estadoEm(est), 20, "foi para " .. est)
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
    press(1, {"golaco"}, 3)
    need(estadoEm(3100), 14, "entrou em 3100")
    need(function() local s = snap(1); return s.st == 3100 and s.t > 20 and s.v37 == 1 end, 80, "var(37) = 1 (arte endiabrada) no meio do 3100")
    need(function() return st1() == 0 end, 300, "terminou", false)
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
