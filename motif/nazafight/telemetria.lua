-- Relatorio local iniciado pelo atalho. Um intervalo corresponde a duas chamadas
-- consecutivas do loop de jogo, inclusive ticks de recuperacao apos uma pausa.
local path = os.getenv("NAZA_TELEMETRIA_CSV")
if not path or path == "" then return end
local file = io.open(path, "a")
if not file then return end

local count = 0
local function write(event, fields)
    if not file then return end
    local row = {getTimestamp("15:04:05.000"), event}
    for _, v in ipairs(fields or {}) do
        row[#row+1] = '"' .. tostring(v):gsub('"', '""'):gsub('[\r\n]', ' ') .. '"'
    end
    while #row < 11 do row[#row+1] = "" end
    local ok = file:write(table.concat(row, ","), "\n")
    if ok then ok = file:flush() end
    count = count + 1
    if not ok or count >= 360 then file:close(); file = nil end
end

write("motif")
local lastScreen, phase, last
local function screen(s)
    if lastScreen ~= s then write(s); lastScreen = s end
end
for event, label in pairs({["main.menu.loop"]="menu", ["start.f_selectScreen"]="selecao",
        ["start.f_selectVersus"]="versus", ["launchFight"]="preparo_luta"}) do
    local s = label
    hook.add(event, "nazaTelemetria", function() screen(s) end)
end

local n, elapsed, worst, over33, over50, worstState = 0, 0, 0, 0, 0, -1
local function flush()
    if n == 0 then return end
    write("amostra", {phase, n, elapsed, worst, over33, over50, worstState,
        string.format("%.1f", getGameFPS())})
    n, elapsed, worst, over33, over50, worstState = 0, 0, 0, 0, 0, -1
end

hook.add("loop", "nazaTelemetria", function()
    if not file or gameMode() == "demo" then return end
    local stamp = getTimestamp("150405.000")
    local now = tonumber(stamp:sub(1,2))*3600000 + tonumber(stamp:sub(3,4))*60000 +
                tonumber(stamp:sub(5))*1000
    local rs = roundState()
    local p = rs < 2 and "introducao" or rs == 2 and "combate" or "fim_round"
    if lastScreen ~= "luta" then
        last = nil
        phase = nil
        n, elapsed, worst, over33, over50, worstState = 0, 0, 0, 0, 0, -1
        screen("luta")
        local before = id()
        local function fighter(i)
            if player(i) then return name() end
            return ""
        end
        local a, b = fighter(1), fighter(2)
        playerId(before)
        local function detail(event, value)
            write(event, {"","","","","","","","",value})
        end
        detail("p1", a)
        detail("p2", b)
        detail("cenario", stageVar("info.name"))
    end
    if last then
        local delta = math.floor(now-last+0.5)
        if delta < -43200000 then delta = delta + 86400000 end
        if delta >= 0 then
            n = n + 1
            elapsed = elapsed + delta
            if delta > worst then worst, worstState = delta, stateNo() end
            if delta > 33 then over33 = over33 + 1 end
            if delta > 50 then over50 = over50 + 1 end
        end
    end
    if phase ~= p or elapsed >= 1000 then flush() end
    if phase ~= p then write("fase", {p}); phase = p end
    last = now
end)
