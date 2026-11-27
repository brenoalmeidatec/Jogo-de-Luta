-- ROBO DA VANTAGEM (so na copia de teste): mede, golpe a golpe, quem volta a se mexer primeiro depois de acertar e
-- depois de ser defendido. Chamado por ferramentas/vantagem.py, que injeta no .cmd do P1 um ChangeState para
-- map(t_st) e no do P2 (Hazak) a defesa do robo de sempre (map t_defende).
do
  local SAIDA = "@SAIDA@"
  local ESTADOS = {@ESTADOS@}
  local BAIXOS = {}
  for _, e in ipairs({@BAIXOS@}) do BAIXOS[e] = true end
  local LOG = io.open(SAIDA, "w")
  local function log(s) LOG:write(s, "\n"); LOG:flush() end
  local function com(n, fn)
    local old = id(); player(n); local a = fn(); playerId(old); return a
  end
  local function snap(n)
    return com(n, function()
      return {st = stateNo(), ctrl = ctrl(), mt = moveType(), stt = stateType(), x = posX(), life = life(),
              d = p2BodyDistX()}
    end)
  end
  local function maps(p, t)
    com(p, function() for k, v in pairs(t) do mapSet(k, v) end; return 0 end)
  end

  local fila = {}
  for _, e in ipairs(ESTADOS) do
    fila[#fila + 1] = {st = e, defende = 1}
    fila[#fila + 1] = {st = e, defende = 0}
  end

  local i, fase, t, c = 0, "espera", 0, nil
  local ligado = true
  hook.add("loop", "vantagem", function()
    if not ligado then return end
    local ok, err = pcall(function()
      if fase == "espera" then
        if roundState() == 2 then fase = "proximo" end
        return
      end
      local agora = gameTime()
      if fase == "proximo" then
        i = i + 1
        maps(1, {t_st = 0}); maps(2, {t_defende = 0, t_agacha = 0, t_guarda = 0, t_holddown = 0, t_holdback = 0})
        if i > #fila then
          log("FIM " .. #fila)
          ligado = false; LOG:close(); return
        end
        c = fila[i]
        fase, t = "arruma", agora
        return
      end
      local a, b = snap(1), snap(2)
      if fase == "arruma" then
        -- os dois parados, vida e barra cheias, colados no meio da tela
        com(1, function() setLife(1000); setPower(3000); return 0 end)
        com(2, function() setLife(1000); return 0 end)
        if agora - t < 3 then
          maps(1, {t_pos = 1, t_posx = 1000 - 22}); maps(2, {t_pos = 1, t_posx = 1000 + 22})
          return
        end
        maps(1, {t_pos = 0}); maps(2, {t_pos = 0})
        if c.defende == 1 and a.st == 0 and b.st == 0 and agora - t > 20 and not c.pre then
          c.pre = true
          maps(2, {t_guarda = 1, t_agacha = BAIXOS[c.st] and 1 or 0, t_holddown = BAIXOS[c.st] and 1 or 0, t_holdback = 1})
        end
        local p2pronto = (c.defende == 1) and (b.st == 130 or b.st == 131 or b.st == 140) or (c.defende == 0 and b.st == 0 and b.ctrl)
        if a.st == 0 and a.ctrl and p2pronto and agora - t > 24 then
          c.pre = nil
          maps(2, {t_defende = c.defende, t_guarda = c.defende, t_agacha = (c.defende == 1 and BAIXOS[c.st]) and 1 or 0})
          maps(1, {t_st = c.st})
          fase, t = "golpe", agora
          c.t0, c.contato, c.l1, c.l2, c.res = nil, nil, nil, nil, nil
        elseif agora - t > 400 then
          log(string.format("EST %d %s nao_arrumou p1=%d p2=%d", c.st, c.defende == 1 and "def" or "hit", a.st, b.st))
          fase = "proximo"
        end
        return
      end
      if fase == "golpe" then
        if not c.t0 then
          if a.st == c.st then c.t0 = agora; maps(1, {t_st = 0}) end
          if agora - t > 30 then
            log(string.format("EST %d %s nao_entrou p1=%d", c.st, c.defende == 1 and "def" or "hit", a.st))
            fase = "proximo"
          end
          return
        end
        local apanhando = (b.mt == "H") or (b.st >= 150 and b.st <= 155)
        if not c.contato and not apanhando then c.ultimo2 = b.st .. b.stt end
        if not c.contato and apanhando then
          c.contato = agora - c.t0
          c.res = (b.st >= 150 and b.st <= 155) and "def" or "hit"
        end
        if c.contato then
          if not c.l1 and a.ctrl then c.l1 = agora end
          if not c.l2 and b.ctrl and b.mt ~= "H" then c.l2 = agora end
          if b.stt == "L" then c.caiu = true end
        end
        local fim = (c.l1 and c.l2) or (agora - c.t0 > 360) or (not c.contato and a.ctrl and agora - c.t0 > 5)
        if fim then
          if not c.contato then
            log(string.format("EST %d %s errou", c.st, c.defende == 1 and "def" or "hit"))
          elseif c.l1 and c.l2 then
            log(string.format("EST %d %s res=%s contato=%d vantagem=%d caiu=%s antes=%s", c.st,
              c.defende == 1 and "def" or "hit", c.res, c.contato, c.l2 - c.l1, c.caiu and "sim" or "nao", tostring(c.ultimo2)))
          else
            log(string.format("EST %d %s res=%s contato=%d sem_fim l1=%s l2=%s", c.st, c.defende == 1 and "def" or "hit",
              c.res, c.contato, tostring(c.l1), tostring(c.l2)) .. " mt=" .. tostring(b.mt) .. " st2=" .. b.st)
          end
          c.caiu = nil
          fase, t = "proximo", agora
        end
      end
    end)
    if not ok then log("ERRO NO ROBO: " .. tostring(err)); ligado = false; LOG:close() end
  end)
  pcall(function() setAccel(@ACCEL@) end)
end
