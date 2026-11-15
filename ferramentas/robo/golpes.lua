-- GOLPES DO FILME (so na copia de dentro do Windows Sandbox): o P1 se posiciona a @DIST@ px do P2 e solta, um por
-- vez e em volta, os comandos de @GOLPES@ (cada item e uma lista de comandos do .cmd apertados juntos). Usa os
-- AssertCommand/PosAdd que ferramentas/filmar_sandbox.py injeta no [Statedef -1] (mesmo esquema do robo.lua).
do
  local GOLPES = {@GOLPES@}
  local DIST = @DIST@
  local function com(n, fn)
    local old = id()
    player(n)
    local a = fn()
    playerId(old)
    return a
  end
  local i, fase, t, aperta, tenta = 1, "espera", 0, 0, 0
  hook.add("loop", "golpes_filme", function()
    local ok, err = pcall(function()
      if roundState() ~= 2 or #GOLPES == 0 then return end
      t = t + 1
      com(1, function()
        mapSet("t_pos", 0)
        mapSet("t_add", 0)
        for _, g in ipairs(GOLPES) do for _, n in ipairs(g) do mapSet("t_" .. n, 0) end end
        if fase == "espera" then
          if t > 20 then fase, t = "posiciona", 0 end
        elseif fase == "posiciona" then
          -- espera o P2 parado (de pé ou no 9911, o agachado do --p2-agachado); reposiciona até chegar perto (um PosSet só pode parar no meio do caminho
          -- quando a câmera ainda está presa no canto, depois de um arremesso)
          if ctrl() and t > 15 and (function() local e = com(2, function() return stateNo() end); return e == 0 or e == 9911 end)() then
            local d = p2BodyDistX()
            if math.abs(d - DIST) > 2 and tenta < 8 then
              tenta = tenta + 1
              -- PosAdd (relativo à frente do P1): o posX() do Lua é medido da câmera e o PosSet do palco, e os
              -- dois só batem antes da câmera andar
              mapSet("t_dx", d - DIST + 1000)
              mapSet("t_add", 1)
              t = 12
            else
              fase, t, aperta, tenta = "aperta", 0, 2, 0
            end
          end
        elseif fase == "aperta" then
          if t > 3 then
            for _, n in ipairs(GOLPES[i]) do mapSet("t_" .. n, 1) end
            aperta = aperta - 1
            if aperta <= 0 then fase, t = "golpe", 0 end
          end
        elseif fase == "golpe" then
          if (t > 12 and ctrl()) or t > 400 then
            i = i % #GOLPES + 1
            fase, t = "posiciona", 0
          end
        end
        return 0
      end)
    end)
    if not ok then GOLPES = {} end
  end)
end
