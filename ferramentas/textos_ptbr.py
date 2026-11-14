"""Textos do motor em português para o system.def do Nazafights (revisão geral, missão 2026-11-14 item 6).

O IKEMEN GO v1.0.0 traz em inglês o menu de opções, a pausa, a pausa do treino, a tela de continuar, a lista de
golpes e o título da seleção ("Versus Mode"). Aqui fica a tradução, na mesma ordem do data/system.base.def do motor
(a ordem dos itens no menu é a ordem em que eles aparecem). `gerar_layout.py` chama `secoes()` e cola o resultado no
system.def.

Fontes: as letras bitmap do motor (f-6x9) só têm ASCII; as nossas (naza_menu) têm acento mas são grandes demais para
menu. A pausa usa a Open Sans do próprio motor (font/Open_Sans.def, TrueType, com acento), do tamanho da f-6x9. As
opções ficam na f-6x9 e sem acento (ver opcoes()). Continuar usa as nossas tabuletas (font1/font2).

Item com valor vazio some do menu (o mesmo truque do [Title Info]): o jogo só tem luta 1 contra 1, sem rede e com uma
língua, então saem os itens de time (Tag, Simul, Turns, vida e barra de time), de rede e de língua.
"""
import unicodedata

# fonte de texto miúdo com acento: (arquivo, banco, alinhamento, r, g, b) -> linha "font =" do motor
FONTE = "Open_Sans.def"
ESCALA = "0.36, 0.36"          # 27 px da Open Sans * 0,36 ~ 9,7: a altura da f-6x9 que estava aí


def _fonte(alinha, cor):
    r, g, b = cor
    return f"{FONTE}, 0, {alinha}, {r}, {g}, {b}, 255, -1"


CINZA, BRANCO, AREIA, AZUL = (191, 191, 191), (255, 255, 255), (240, 200, 120), (120, 220, 240)

# ------------------------------------------------------------------ [Option Info]
OPCOES = [
    ("menugame", "Jogo"),
    ("menugame.language", ""),
    ("menugame.difficulty", "Dificuldade"),
    ("menugame.roundtime", "Tempo do round"),
    ("menugame.lifemul", "Vida"),
    ("menugame.singlevsteamlife", ""),
    ("menugame.gamespeed", "Velocidade do jogo"),
    ("menugame.roundsnumsingle", "Rounds para vencer"),
    ("menugame.maxdrawgames", "Empates permitidos"),
    ("menugame.credits", "Créditos"),
    ("menugame.aipalette", "Cor da CPU"),
    ("menugame.aisurvivalpalette", ""),
    ("menugame.airamping", "CPU fica mais forte"),
    ("menugame.quickcontinue", "Continuar rápido"),
    ("menugame.autoguard", "Defesa automática"),
    ("menugame.dizzy", "Tontura"),
    ("menugame.guardbreak", "Quebra de guarda"),
    ("menugame.redlife", "Vida vermelha"),
    ("menugame.teamduplicates", ""),
    ("menugame.teamlifeshare", ""),
    ("menugame.teampowershare", ""),
    ("menugame.spacer1", "-"),
    ("menugame.menutag", ""),
    ("menugame.menutag.roundsnumtag", "Rounds para vencer (Tag)"),
    ("menugame.menutag.losekotag", "Parceiro caído perde"),
    ("menugame.menutag.spacer1", "-"),
    ("menugame.menutag.mintag", "Mínimo de lutadores"),
    ("menugame.menutag.maxtag", "Máximo de lutadores"),
    ("menugame.menutag.spacer2", "-"),
    ("menugame.menutag.back", "Voltar"),
    ("menugame.menusimul", ""),
    ("menugame.menusimul.roundsnumsimul", "Rounds para vencer (Simul)"),
    ("menugame.menusimul.losekosimul", "Jogador caído perde"),
    ("menugame.menusimul.spacer1", "-"),
    ("menugame.menusimul.minsimul", "Mínimo de lutadores"),
    ("menugame.menusimul.maxsimul", "Máximo de lutadores"),
    ("menugame.menusimul.spacer2", "-"),
    ("menugame.menusimul.back", "Voltar"),
    ("menugame.menuturns", ""),
    ("menugame.menuturns.turnsrecoverybase", "Vida que volta (base)"),
    ("menugame.menuturns.turnsrecoverybonus", "Vida que volta (bônus)"),
    ("menugame.menuturns.spacer1", "-"),
    ("menugame.menuturns.minturns", "Mínimo de lutadores"),
    ("menugame.menuturns.maxturns", "Máximo de lutadores"),
    ("menugame.menuturns.spacer2", "-"),
    ("menugame.menuturns.back", "Voltar"),
    ("menugame.back", "Voltar"),
    ("menuvideo", "Vídeo"),
    ("menuvideo.renderer", "Renderizador"),
    ("menuvideo.renderer.gles32", "OpenGL ES 3.2"),
    ("menuvideo.renderer.gl33", "OpenGL 3.3"),
    ("menuvideo.renderer.vk13", "Vulkan 1.3"),
    ("menuvideo.renderer.spacer1", "-"),
    ("menuvideo.renderer.back", "Voltar"),
    ("menuvideo.resolution", "Resolução"),
    ("menuvideo.resolution.320x240", "320x240    (4:3 QVGA)"),
    ("menuvideo.resolution.640x480", "640x480    (4:3 VGA)"),
    ("menuvideo.resolution.960x720", "960x720    (4:3 HD)"),
    ("menuvideo.resolution.1280x720", "1280x720   (16:9 HD)"),
    ("menuvideo.resolution.1600x900", "1600x900   (16:9 HD+)"),
    ("menuvideo.resolution.1920x1080", "1920x1080  (16:9 Full HD)"),
    ("menuvideo.resolution.spacer1", "-"),
    ("menuvideo.resolution.customres", "Outra"),
    ("menuvideo.resolution.back", "Voltar"),
    ("menuvideo.fullscreen", "Tela cheia"),
    ("menuvideo.vsync", "VSync"),
    ("menuvideo.aspectratio", "Proporção da tela"),
    ("menuvideo.aspectratio.defaultaspect", "Padrão"),
    ("menuvideo.aspectratio.stageaspect", "Do cenário"),
    ("menuvideo.aspectratio.4x3", "4:3"),
    ("menuvideo.aspectratio.16x9", "16:9"),
    ("menuvideo.aspectratio.customaspect", "Outra"),
    ("menuvideo.aspectratio.spacer1", "-"),
    ("menuvideo.aspectratio.back", "Voltar"),
    ("menuvideo.keepaspect", "Manter a proporção"),
    ("menuvideo.windowscalemode", "Ampliação da janela"),
    ("menuvideo.msaa", "Suavização (MSAA)"),
    ("menuvideo.shaders", "Filtros (shaders)"),
    ("menuvideo.shaders.spacer1", "-"),
    ("menuvideo.shaders.noshader", "Desligar"),
    ("menuvideo.shaders.back", "Voltar"),
    ("menuvideo.model", "Modelos 3D"),
    ("menuvideo.model.enablemodel", "Modelo 3D"),
    ("menuvideo.model.enablemodelshadow", "Sombra"),
    ("menuvideo.model.spacer1", "-"),
    ("menuvideo.model.back", "Voltar"),
    ("menuvideo.spacer1", "-"),
    ("menuvideo.back", "Voltar"),
    ("menuaudio", "Som"),
    ("menuaudio.mastervolume", "Volume geral"),
    ("menuaudio.bgmvolume", "Volume da música"),
    ("menuaudio.sfxvolume", "Volume dos efeitos"),
    ("menuaudio.audioducking", "Música baixa na fala"),
    ("menuaudio.stereoeffects", "Efeitos em estéreo"),
    ("menuaudio.panningrange", "Abertura do estéreo"),
    ("menuaudio.spacer1", "-"),
    ("menuaudio.back", "Voltar"),
    ("menuinput", "Controles"),
    ("menuinput.keyboard", "Teclado"),
    ("menuinput.gamepad", "Controle (joystick)"),
    ("menuinput.spacer1", "-"),
    ("menuinput.inputdefault", "Voltar ao padrão"),
    ("menuinput.back", "Voltar"),
    ("menuengine", "Motor"),
    ("menuengine.players", "Jogadores"),
    ("menuengine.debugkeys", "Teclas de depuração"),
    ("menuengine.debugmode", "Modo de depuração"),
    ("menuengine.vsscreenloading", "Carregar no VS"),
    ("menuengine.turnsloading", ""),
    ("menuengine.spacer1", "-"),
    ("menuengine.back", "Voltar"),
    ("menunetplay", ""),
    ("menunetplay.portchange", "Porta"),
    ("menunetplay.netcode", "Netcode"),
    ("menunetplay.framedelay", "Atraso do rollback"),
    ("menunetplay.spacer1", "-"),
    ("menunetplay.back", "Voltar"),
    ("spacer1", "-"),
    ("default", "Voltar ao padrão"),
    ("spacer2", "-"),
    ("savereturn", "Salvar e sair"),
    ("return", "Sair sem salvar"),
]

VALORES = [
    ("none", "Nenhum"), ("random", "Aleatória"), ("default", "Padrão"), ("f", "(F%i)"), ("esc", "(Esc)"),
    ("page", "(Tab)"), ("nokey", "Sem tecla"), ("presskey", "Aperte uma tecla"), ("yes", "Sim"), ("no", "Não"),
    ("enabled", "Ligado"), ("disabled", "Desligado"), ("normal", "Normal"), ("slow", "Lento %i"),
    ("fast", "Rápido %i"), ("bilinear", "Suave"), ("nearest", "Pixel"), ("rollbacknetcode", "Rollback"),
    ("delaynetcode", "Por atraso"),
]

_FIM = r"\nENTER confirma.\nESC cancela."
ENTRADAS = [
    ("port", "Digite a porta, por exemplo 7500." + _FIM),
    ("reswidth", "Digite a largura da tela." + _FIM),
    ("resheight", "Digite a altura da tela." + _FIM),
    ("aspectwidth", "Digite a largura da proporção." + _FIM),
    ("aspectheight", "Digite a altura da proporção." + _FIM),
]

TECLAS = [
    ("configall", "Configurar tudo"), ("up", "Cima"), ("down", "Baixo"), ("left", "Esquerda"), ("right", "Direita"),
    ("a", "A chute fraco"), ("b", "B chute forte"), ("c", "C parry"), ("x", "X soco fraco"),
    ("y", "Y soco forte"), ("z", "Z"), ("start", "Start"), ("d", "D"), ("w", "W"), ("menu", "Menu"),
    ("rumble", ""), ("back", "Voltar"), ("page", "Pagina"),
]

# ------------------------------------------------------------------ [Pause Menu] e [Training Pause Menu]
PAUSA = [
    ("back", "Continuar"),
    ("menuinput", "Controles"),
    ("menuinput.keyboard", "Teclado"),
    ("menuinput.gamepad", "Controle (joystick)"),
    ("menuinput.spacer", "-"),
    ("menuinput.inputdefault", "Voltar ao padrão"),
    ("menuinput.back", "Voltar"),
    ("commandlist", "Lista de golpes"),
    ("characterchange", "Trocar de lutador"),
    ("exit", "Sair da luta"),
]
TREINO = [
    ("back", "Continuar"),
    ("menutraining", "Treino"),
    ("menutraining.dummycontrol", "Quem controla o boneco"),
    ("menutraining.ailevel", "Nível da CPU"),
    ("menutraining.dummymode", "O que o boneco faz"),
    ("menutraining.guardmode", "Defesa do boneco"),
    ("menutraining.fallrecovery", "Levanta no ar"),
    ("menutraining.distance", "Distância"),
    ("menutraining.buttonjam", "Aperta botão"),
    ("menutraining.back", "Voltar"),
] + PAUSA[1:]

TITULOS_SELECAO = [
    ("arcade", "ARCADE"), ("teamarcade", "ARCADE EM TIME"), ("teamcoop", "COOPERATIVO"), ("versus", "VERSUS"),
    ("teamversus", "VERSUS EM TIME"), ("versuscoop", "VERSUS COOPERATIVO"), ("freebattle", "LUTA RÁPIDA"),
    ("storymode", "HISTÓRIA"), ("netplayversus", "VERSUS ONLINE"), ("netplayteamcoop", "COOPERATIVO ONLINE"),
    ("netplaysurvivalcoop", "SOBREVIVÊNCIA ONLINE"), ("training", "TREINO"), ("timeattack", "CONTRA O TEMPO"),
    ("survival", "SOBREVIVÊNCIA"), ("survivalcoop", "SOBREVIVÊNCIA EM DUPLA"), ("bonus", "BÔNUS"),
    ("watch", "ASSISTIR"), ("replay", "REPLAY"),
]


def _lista(prefixo, pares):
    return "\n".join(f"{prefixo}{k} = {v}" for k, v in pares)


def selecao():
    """Linhas para o [Select Info]: título de cada modo e o 'Random'/'Color' da seleção."""
    return "\n".join([
        "; titulo de cada modo em portugues (o motor escrevia VERSUS MODE, WATCH MODE...)",
        _lista("title.", [(k + ".text", v) for k, v in TITULOS_SELECAO]),
        "p1.name.random.text = ALEATÓRIO",
        "p2.name.random.text = ALEATÓRIO",
    ])


def _fontes_menu(item_cor=CINZA):
    """Fontes do menu. O localcoord vai junto de cada fonte: sem ele o motor passa a ler posição e escala em
    1280x720 (o localcoord do nosso motif) e o menu inteiro encolhia num canto."""
    linhas = _FONTES_MENU.format(cinza=_fonte(1, item_cor), branco=_fonte(1, BRANCO), azul=_fonte(1, AZUL),
                                 tit=_fonte(0, BRANCO), vcinza=_fonte(-1, item_cor), vbranco=_fonte(-1, BRANCO),
                                 esc=ESCALA)
    return "\n".join(linhas.splitlines() + [l.split(".font")[0] + ".localcoord = 320, 240"
                                             for l in linhas.splitlines() if ".font =" in l])


_FONTES_MENU = """title.font = {tit}
title.scale = 0.42, 0.42
menu.item.font = {cinza}
menu.item.scale = {esc}
menu.item.active.font = {branco}
menu.item.active.scale = {esc}
menu.item.selected.font = {azul}
menu.item.selected.scale = {esc}
menu.item.selected.active.font = {azul}
menu.item.selected.active.scale = {esc}
menu.item.value.font = {vcinza}
menu.item.value.scale = {esc}
menu.item.value.active.font = {vbranco}
menu.item.value.active.scale = {esc}"""


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def opcoes():
    """Só os textos. Aqui a fonte NÃO muda: a tela de configurar teclas herda fonte, escala e localcoord do menu.item
    e qualquer troca (Open Sans, escala, localcoord, até a própria f-6x9 explícita) fazia as letras dela sumirem
    (testado em 10 variações na nuvem, 2026-11-14). A f-6x9 do motor só tem ASCII, então as opções vão sem acento."""
    return sem_acento("\n".join([
        "title.text = OPCOES",
        "title.localcoord = 320, 240",
        _lista("menu.itemname.", OPCOES),
        _lista("menu.valuename.", VALORES),
        _lista("textinput.", [(k + ".text", v) for k, v in ENTRADAS]),
        "keymenu.p1.playerno.text = JOGADOR %i",
        "keymenu.p2.playerno.text = JOGADOR %i",
        "\n".join(f"keymenu.{e}.localcoord = 320, 240" for e in ("p1.playerno", "p2.playerno")),
        _lista("keymenu.itemname.", TECLAS),
    ]))


def pausa(treino=False):
    return "\n".join([
        "title.text = " + ("TREINO" if treino else "PAUSA"),
        _fontes_menu(),
        "movelist.text.text = Lista de golpes não encontrada.",
        "movelist.text.localcoord = 320, 240",
        _lista("menu.itemname.", TREINO if treino else PAUSA),
    ])


def continuar():
    """Tela de continuar com as nossas tabuletas (font1 normal, font2 a ativa), em 1280x720."""
    linhas = ["pos = 640,200"]
    for nome, texto, x, fonte in (("continue", "CONTINUAR?", 0, 1), ("yes", "SIM", -90, 1), ("yes.active", "SIM", -90, 2),
                                  ("no", "NÃO", 90, 1), ("no.active", "NÃO", 90, 2)):
        y = 0 if nome == "continue" else 64
        linhas += [f"{nome}.font = {fonte},0,0", f"{nome}.offset = {x},{y}", f"{nome}.scale = 1,1",
                   f"{nome}.text = {texto}", f"{nome}.localcoord = 1280,720"]
    return "\n".join(linhas)


def vitoria():
    return "winquote.text = Venceu!\nwinquote.localcoord = 320, 240"


def secoes():
    """As seções traduzidas, prontas para o system.def (o .bat ainda injeta done.key nelas)."""
    return f"""[Victory Screen]
{vitoria()}

[Option Info]
{opcoes()}

[OptionBgDef]
bgclearcolor = 20,12,16

[Pause Menu]
{pausa()}

[Training Pause Menu]
{pausa(treino=True)}

[Replay Info]

[Continue Screen]
{continuar()}
"""
