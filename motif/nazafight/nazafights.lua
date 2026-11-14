-- Nazafights: modulo do motif, carregado pelo motor por [Files] module = nazafights.lua no system.def.
-- Duas coisas: o MODO SUPER (abaixo) e a ESCOLHA DE MAPA em todo modo (no fim do arquivo).

-- MODO SUPER (Breno, 2026-11-13).
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


-- ESCOLHA DE MAPA (Breno, issue #35): depois de escolher os lutadores abre a tela do mapa em todos os modos que
-- tem luta (Arcade inclusive: o mapa escolhido vale para todas as lutas da campanha), e o mapa NUNCA e sorteado.
-- O motor so liga a escolha (main.stageMenu) em Versus, Treino, Sobrevivencia e Assistir; aqui ela liga em todos.
-- O "aleatorio" sai em dois lugares: stage.randomselect = 0 no system.def (a lista comeca no 1o mapa) e a chave
-- stage_randomselect, que o f_stageMenu do start.lua v1.0.0 le com esse nome (com o nome errado ele deixava rolar
-- a lista ate o "Stage: Random").
local SEM_MAPA = {demo = true, options = true, exit = true, replay = true, randomtest = true,
	serverconnect = true, serverhost = true, joinadd = true}

local function semAleatorio()
	motif.select_info.stage_randomselect = 0
	if type(motif.select_info.stage) == 'table' then
		motif.select_info.stage.randomselect = 0
	end
end
semAleatorio()

hook.add("main.t_itemname", "nazaEscolhaMapa", function(t, item)
	local nome = t and t[item] and t[item].itemname or ''
	if SEM_MAPA[nome] then
		return
	end
	main.stageMenu = true
	semAleatorio()
end)
