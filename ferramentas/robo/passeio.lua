-- PASSEIO DO FILME DE CENARIO (so na copia de dentro do Windows Sandbox): os dois lutadores, sem IA, deslizam juntos
-- ate a ponta esquerda do cenario, o P1 sobe e desce (a camera sobe), vao ate a ponta direita, o P2 sobe e desce, e
-- voltam ao centro. Serve para ver a paralaxe e as bordas. Usa o PosAdd que ferramentas/filmar_sandbox.py --passeio
-- injeta no [Statedef -1] dos dois (map c_dx em px por tick no mundo, map c_dy em px por tick na vertical).
do
  local V = 4
  local t = 0
  local function com(n, fn)
    local old = id()
    if player(n) then fn() end
    playerId(old)
  end
  local function subida(t0)  -- 20 ticks subindo 4 px, 10 parado, 20 descendo
    if t >= t0 and t < t0 + 20 then return -4 end
    if t >= t0 + 30 and t < t0 + 50 then return 4 end
    return 0
  end
  hook.add("loop", "passeio_cenario", function()
    pcall(function()
      if roundState() ~= 2 then return end
      t = t + 1
      local dx = 0
      if t >= 30 and t < 110 then dx = -V
      elseif t >= 165 and t < 325 then dx = V
      elseif t >= 380 and t < 460 then dx = -V end
      local dy1, dy2 = subida(112), subida(327)
      com(1, function() mapSet("c_dx", dx); mapSet("c_dy", dy1) end)
      com(2, function() mapSet("c_dx", dx); mapSet("c_dy", dy2) end)
    end)
  end)
end
