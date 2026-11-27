-- Teste da paleta 2 (Endiabrado pela selecao): mede palno, var(20), var(37) no comeco e depois de 700 ticks (> 600 do Despertar).
do
  local LOG = io.open("@SAIDA@", "w")
  local function log(s) LOG:write(s, "\n"); LOG:flush() end
  local n, ligado = 0, true
  hook.add("loop", "paleta", function()
    if not ligado then return end
    local ok, err = pcall(function()
      if roundState() ~= 2 then return end
      n = n + 1
      if n == 30 or n == 700 then
        local old = id(); player(1)
        log(string.format("tick %d: var20=%s var37=%s stateno=%s", n, tostring(var(20)), tostring(var(37)), tostring(stateNo())))
        playerId(old)
      end
      if n == 701 then log("FIM"); ligado = false; LOG:close() end
    end)
    if not ok then log("ERRO NO ROBO: " .. tostring(err)); ligado = false end
  end)
end
