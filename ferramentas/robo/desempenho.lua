-- Roteiro em velocidade normal. Uma amostra do contador do motor por tick observado.
do
  local t, terminou = 0, false
  local linhas = {"tick,fase,fps,ck,hazak,vida"}
  local function salvar()
    local f = assert(io.open("fps.csv", "w"))
    f:write(table.concat(linhas, "\n"), "\n")
    f:close()
  end
  hook.add("loop", "benchmark", function()
    if terminou or roundState() ~= 2 then return end
    local original = id()
    t = t + 1
    local perto = t == 75 or t == 145
    local guarda = t >= 148 and t <= 195
    player(2)
    mapSet("t_pos", perto and 1 or 0)
    mapSet("t_posx", 1016)
    mapSet("t_defende", guarda and 1 or 0)
    mapSet("t_holdback", guarda and 1 or 0)
    local rival, hp = stateNo(), life()
    player(1)
    mapSet("t_pos", perto and 1 or 0)
    mapSet("t_posx", 984)
    mapSet("t_x", ((t >= 80 and t <= 83) or (t >= 150 and t <= 153)) and 1 or 0)
    if t == 212 or t == 430 then setPower(3000) end
    mapSet("t_golaco", (t >= 215 and t <= 218) and 1 or 0)
    mapSet("t_despertar", (t >= 435 and t <= 438) and 1 or 0)
    local fase = t < 75 and "luta" or t < 145 and "acerto" or t < 215 and "defesa" or t < 330 and "especial" or t < 435 and "guarda" or "despertar"
    linhas[#linhas+1] = string.format("%d,%s,%.2f,%d,%d,%d", t, fase, getGameFPS(), stateNo(), rival, hp)
    playerId(original)
    if t == 550 then terminou = true; salvar() end
  end)
end
