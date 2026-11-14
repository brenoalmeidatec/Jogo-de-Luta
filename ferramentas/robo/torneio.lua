-- TORNEIO CPU x CPU (so na copia de teste, ferramentas/torneio_cpu.py): as duas CPUs lutam e, no fim de cada round,
-- o script anota quem venceu, a vida que sobrou, a duracao, o dano de cada lado e quanto tempo cada um ficou
-- transformado (var(20) > 0). Depois chama resetRound() para a luta nunca acabar e roda @ROUNDS@ rounds.
do
  local SAIDA = "@SAIDA@"
  local ROUNDS = @ROUNDS@
  local LOG = io.open(SAIDA, "w")
  local function log(s) LOG:write(s, "\n"); LOG:flush() end
  local function com(n, fn)
    local old = id()
    player(n)
    local a = fn()
    playerId(old)
    return a
  end
  local n, fase, espera, ligado = 0, "espera", 0, true
  local desp, golpes, maxpow, antes
  local function zera() desp, golpes, maxpow, antes = {0, 0}, {0, 0}, {0, 0}, {0, 0} end
  zera()
  hook.add("loop", "torneio", function()
    if not ligado then return end
    local ok, err = pcall(function()
      local rs = roundState()
      if fase == "espera" then
        if rs == 2 then fase = "luta"; espera = 0; zera() end
        return
      end
      if fase == "luta" then
        espera = espera + 1
        for p = 1, 2 do
          com(p, function()
            if var(20) > 0 then desp[p] = desp[p] + 1 end
            local mh = moveHit()
            if mh == 1 and antes[p] ~= 1 then golpes[p] = golpes[p] + 1 end  -- conta o golpe, nao os ticks
            antes[p] = mh
            if power() > maxpow[p] then maxpow[p] = power() end
            return 0
          end)
        end
        if rs >= 3 or espera > 7000 then
          local v1 = com(1, function() return life() end)
          local v2 = com(2, function() return life() end)
          local m1 = com(1, function() return lifeMax() end)
          local m2 = com(2, function() return lifeMax() end)
          n = n + 1
          log(string.format("ROUND %d v1=%d/%d v2=%d/%d ticks=%d desp1=%d desp2=%d hit1=%d hit2=%d pow1=%d pow2=%d",
            n, v1, m1, v2, m2, espera, desp[1], desp[2], golpes[1], golpes[2], maxpow[1], maxpow[2]))
          if n >= ROUNDS then
            log("FIM")
            ligado = false
            LOG:close()
            return
          end
          fase = "reinicia"; espera = 0
        end
        return
      end
      if fase == "reinicia" then
        espera = espera + 1
        if espera == 5 then
          resetRound()
        elseif espera > 20 and rs == 2 then
          fase = "luta"; espera = 0; zera()
        end
      end
    end)
    if not ok then log("ERRO NO TORNEIO: " .. tostring(err)); ligado = false; LOG:close() end
  end)
  pcall(function() setAccel(4) end)
end
