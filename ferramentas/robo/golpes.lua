-- GOLPES DO FILME (so na copia de dentro do Windows Sandbox): o P1 se posiciona a @DIST@ px do P2 e solta, um por
-- vez e em volta, os comandos de @GOLPES@ (cada item e uma lista de comandos do .cmd apertados juntos). Usa os
-- AssertCommand/PosSet que ferramentas/filmar_sandbox.py injeta no [Statedef -1] (mesmo esquema do robo.lua).
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
  local i, fase, t, aperta = 1, "espera", 0, 0
  hook.add("loop", "golpes_filme", function()
    local ok, err = pcall(function()
      if roundState() ~= 2 or #GOLPES == 0 then return end
      t = t + 1
      com(1, function()
        mapSet("t_pos", 0)
        for _, g in ipairs(GOLPES) do for _, n in ipairs(g) do mapSet("t_" .. n, 0) end end
        if fase == "espera" then
          if t > 20 then fase, t = "posiciona", 0 end
        elseif fase == "posiciona" then
          if ctrl() and t > 15 then
            local d = p2BodyDistX()
            mapSet("t_posx", posX() + (d - DIST) * (facing() >= 0 and 1 or -1) + 1000)
            mapSet("t_pos", 1)
            fase, t, aperta = "aperta", 0, 2
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
