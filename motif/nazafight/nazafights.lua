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


-- CHEFE FINAL DO ARCADE (checkup geral, 2026-11-25; conceito do Breno de 2026-11-11: o endiabrado e o boss final).
-- Na ultima luta do Arcade, a CPU recebe o map chefe_final. A IA da CPU (ferramentas/ia_cpu.py, no [Statedef -2] de
-- cada lutador) le esse map: enche a barra e desperta logo no comeco, com a cena da transformacao. Como a forma fica ate
-- o fim da luta (forma_permanente.py), o chefe luta despertado o resto da partida.
hook.add("loop#arcade", "nazaChefeFinal", function()
	if not (start and start.t_roster) or #start.t_roster == 0 or matchNo() < #start.t_roster then
		return
	end
	local antes = id()
	for p = 1, 8 do
		if player(p) and aiLevel() > 0 then
			mapSet("chefe_final", 1)
		end
	end
	playerId(antes)
end)


-- >>> falas_vitoria.py (fala da tela de vitoria): gerado, nao edite a mao
-- FALA DA TELA DE VITORIA (Alisson, 2026-11-25). O motor so usa o winquote.text quando o lutador nao tem
-- [Quotes] (e ignora o VictoryQuote), entao a fala e escolhida aqui: forma normal ou Despertar (var(20) > 0).
local FALAS = {
	["pengaro"] = {
		base = {
			"F-f-foi de letra, filho da puta.",
			"T-t-tá achando que é bo-boteco de domingo, é, ca-caralho?",
			"V-v-vai lá contar pra tua mãe que tu a-a-apanhou do gago.",
			"Eu be-bebo... be-be-BATO melhor que tu, porra!",
			"T-tu ficou pa-parado igual cone. Ma-mas cone pelo menos fica de pé.",
			"D-d-demorei pra falar, mas tu de-de-demorou mais pra levantar.",
			"Es-essa vai na tua conta, pa-pa-parceiro. A do bar também.",
			"Olha só, falei inteiro! Agora chama tua irmã que eu vou ensinar ela a gingar, hein!",
		},
		despertado = {
			"A-a-as sombras gostaram de tu. Vão te levar pra casa.",
			"Q-q-quem bebe com o capeta não pa-paga a conta. Tu paga.",
			"O-o-olha pro chão, que a tua sombra já fugiu.",
			"Nem gaguejei. O ca-capeta fala por mim.",
			"Na Ma-maré das Correntes: entrou, não sai mais.",
			"E-e-escuro assim nem a tua mãe te acha.",
			"A roda de capoeira agora é no in-inferno, e tu entrou nela.",
			"B-b-bota mais uma dose. Pra mim, não pra tu.",
		},
	},
	["ck"] = {
		base = {
			"Tá achando que é quem, parça?",
			"Errou o soco, tomou o troco.",
			"Ajeita o boné que a aula acabou.",
			"Vem de novo, eu deixo.",
			"Nem suei a camisa.",
			"Na esquina é assim: piscou, dormiu.",
			"Avisa lá que o CK passou.",
			"Essa luva aqui não é enfeite.",
		},
		despertado = {
			"Liga o paredão que o Ratão ganhou!",
			"Garrafa quebrada, briga encerrada.",
			"No baile da esquina quem manda é o rato.",
			"Dancei na tua cara e tu nem viu o passo.",
			"Ratão não corre de gato. Ratão bate no gato.",
			"Aumenta o grave que eu tô comemorando.",
			"Sobe o som: hoje o rato saiu do bueiro.",
			"Varre os cacos, que a festa acabou pra você.",
		},
	},
	["gutto"] = {
		base = {
			"Foi na ginga do Muay Thai, parceiro!",
			"Quer outra? É só pedir.",
			"Chute baixo não perdoa, né?",
			"Beijinho de despedida!",
			"Tu caiu igual a cavalo de carrossel.",
			"Treino de verdade é na canela.",
			"Essa vai na conta do Gutto.",
			"Levanta que eu dou mais uma.",
		},
		despertado = {
			"Rrrrfff! Coice de cavalo não tem revanche.",
			"Galopei por cima e nem senti o calombo.",
			"Bufei uma vez. Na segunda tu já tava no chão.",
			"Ferradura nova, testada na tua cara.",
			"Relincha agora, vai. Relincha!",
			"Puro-sangue não perde pra pangaré.",
			"A pista é aqui, e tu ficou parado na largada.",
			"Arreio nenhum me segura.",
		},
	},
	["hazak"] = {
		base = {
			"EU SOU GOSTOSO!",
			"Australopiteco mentiroso! Falou que aguentava.",
			"Nem viu a minha cara, só a sola do meu pé.",
			"Pisca não, que eu já chutei três vezes.",
			"Tá vendo esse dedinho? Não, não, não.",
			"Rapidinho, igual eu prometi.",
			"Faixa preta? Só se for a do teu olho roxo.",
			"Vai treinar mais, que hoje deu pra mim.",
		},
		despertado = {
			"Antigamente me chamavam de Diabo Loiro. Agora tu sabe o porquê.",
			"Essa surra entra na conta. Com juros.",
			"A maleta tá cheia. O teu respeito, nem tanto.",
			"Negócio fechado: eu bato, tu paga.",
			"Ajeita o chapéu do chefe e sai da frente.",
			"Meu terno nem amassou, e tu já tá no chão.",
			"O Diabo cobra caro, e tu tá devendo.",
			"Assina aqui que eu devolvo a tua alma... um dia.",
		},
	},
	["raiclaven"] = {
		base = {
			"Próximo!",
			"Vai querer na régua?",
			"Deixa que eu capricho.",
			"Ficou um degradê lindo, hein?",
			"A casa agradece a preferência.",
			"Não mexe a cabeça que eu corto a orelha.",
			"Cabelo e barba: pago na saída.",
			"Volta daqui a quinze dias pra manutenção.",
		},
		despertado = {
			"Experimento concluído: a cobaia não resistiu.",
			"A Cliente adorou o corte. Você, nem tanto.",
			"Hipótese confirmada: você apanha fácil.",
			"Tesoura, navalha e ciência. Próximo!",
			"Anota aí: dose dupla de surra, efeito imediato.",
			"A Cliente tá com fome, e você tá no ponto.",
			"Degradê na tua alma, cortesia da casa.",
			"Volta pro laboratório que eu ainda não terminei.",
		},
	},
	["gbzin"] = {
		base = {
			"Volta pro curral, cabrito.",
			"Bateu três vezes, acabou.",
			"Raspagem limpa, nem suei.",
			"O cajado avisou, você não ouviu.",
			"Pastor não corre, o rebanho que vem.",
			"Faixa marrom, mão pesada.",
			"Fica deitado aí, que dá menos trabalho.",
			"Tchau, cabrito!",
		},
		despertado = {
			"O dízimo de hoje foi pago em pancada.",
			"Grão-Pastor não prega: cobra.",
			"Junta as notas do chão, cabrito. É o teu troco.",
			"Tapa-olho de estrela, e mesmo assim te vi caindo.",
			"O rebanho cresce, e a tua moral diminui.",
			"Ajoelhou? Agora reza.",
			"Bateu três vezes... e eu cobrei as três.",
			"Bênção e porrada, tudo no mesmo pacote.",
		},
	},
}
hook.add("game.victory_init", "nazaFalaVitoria", function()
	local ok, err = pcall(function()
		local lado = getWinnerTeam()
		if lado ~= 1 and lado ~= 2 then return end
		local antes = id()
		local nome, forma = nil, 'base'
		if player(lado) then
			nome = string.lower(name())
			if var(20) > 0 then forma = 'despertado' end
		end
		playerId(antes)
		local lista = nome and FALAS[nome] and FALAS[nome][forma]
		if lista then
			modifyMotif('victory_screen.winquote.text', lista[math.random(#lista)])
		else
			modifyMotif('victory_screen.winquote.text', 'Venceu!')
		end
	end)
	if not ok then print('nazaFalaVitoria: ' .. tostring(err)) end
end)
-- <<< falas_vitoria.py
