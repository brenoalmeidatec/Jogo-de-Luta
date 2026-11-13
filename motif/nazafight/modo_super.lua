-- Nazafights: MODO SUPER (Breno, 2026-11-13).
-- Modulo do motif, carregado pelo motor por [Files] module = modo_super.lua no system.def.
-- E o versus de sempre (1 contra 1, jogador contra jogador), mas a barra de power dos dois lutadores fica cheia a
-- luta inteira: depois de cada super ela volta ao maximo no quadro seguinte. A vida continua normal.
-- O motor roda o modo como 'versus' (placar, telas e pausa iguais); quem diz que e o super e a variavel abaixo.

local ligado = false

main.t_itemname.supermode = function(t, item)
	-- mesmo preparo do VERSUS 1 contra 1 do main.lua
	main.cpuSide[2] = false
	main.motif.vsscreen = true
	main.motif.victoryscreen = true
	main.orderSelect[1] = true
	main.orderSelect[2] = true
	main.selectMenu[2] = true
	main.stageMenu = true
	main.teamMenu[1].single = true
	main.teamMenu[2].single = true
	textImgSetText(motif.select_info.title.TextSpriteData, 'MODO SUPER')
	setGameMode('versus')
	setHomeTeam(1)
	hook.run("main.t_itemname", t, item)
	ligado = true -- depois do hook, que desliga o super ao entrar em qualquer modo
	return start.f_selectMode
end

-- Qualquer outro modo escolhido no menu desliga o super.
hook.add("main.t_itemname", "nazaModoSuper", function(t, item)
	ligado = false
end)

-- Todo quadro de luta em modo versus: se o super esta ligado, enche o power dos lutadores.
hook.add("loop#versus", "nazaModoSuper", function()
	if not ligado then
		return
	end
	local antes = id()
	for p = 1, 8 do
		if player(p) then
			setPower(powerMax())
		end
	end
	playerId(antes)
end)
