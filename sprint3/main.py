import glfw
from OpenGL.GL import *
import math
import glm
import os
import numpy as np
from parede import *
from shader import *
from camera import Camera
from mode3D import Modelo3D
from picking import raioMouse, selecionar, pontoPlano
from menu import MenuLateral

obj = {}
myTexture = None
myShader = None
resolucao = np.array([800, 800])
projMatrix = None
shaderes = {}
veloCam = 0.05
veloGiro = math.radians(1.5)
camera = None
moveis = []
selecionado = None
deslocamento = None
alturaArrasto = 0.0
Mproj = None
anguloHorizontal = math.radians(45.0)
anguloVertical = math.radians(35.264)
angGiroObj = 5.0
tamEscala = 0.01

# controle do menu e arrasto
menu = None
itemArrastando = None        # item selecionado no menu
movelArrastando = None       # preview 3D dele na cena
arrastandoDoMenu = False     # veio do menu?
arrastandoCena = False       # movendo objeto da cena?
posicaoMouse = glm.vec2(0, 0)

# rotacao da camera (botao direito)
rotacionandoCamera = False
ultimoMousePos = glm.vec2(0, 0)

# pan da camera (botao esquerdo no chao)
arrastandoPanCamera = False
ultimoMousePan = glm.vec2(0, 0)

# altura que o objeto levanta enquanto arrasta
ALTURA_ELEVACAO = 0.25


def init():
    global camera, myShader, obj, myTexture, projMatrix, menu
    glClearColor(0.5, 0.5, 0.5, 1)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glAlphaFunc(GL_GREATER, 0.1)
    glEnable(GL_ALPHA_TEST)

    here = os.path.dirname(os.path.abspath(__file__))
    myShader = Shader(os.path.join(here, 'vertexShad.glsl'),
                      os.path.join(here, 'fragmentShad.glsl'))

    shaderes['projMatrix'] = glGetUniformLocation(myShader.shaderId, 'projMatrix')
    shaderes['camMatrix'] = glGetUniformLocation(myShader.shaderId, 'camMatrix')
    shaderes['usarLuz'] = glGetUniformLocation(myShader.shaderId, 'usarLuz')
    shaderes['isSombra'] = glGetUniformLocation(myShader.shaderId, 'isSombra')
    shaderes['lightDir'] = glGetUniformLocation(myShader.shaderId, 'lightDir')
    shaderes['lightColor'] = glGetUniformLocation(myShader.shaderId, 'lightColor')
    shaderes['ambientColor'] = glGetUniformLocation(myShader.shaderId, 'ambientColor')
    shaderes['camPos'] = glGetUniformLocation(myShader.shaderId, 'camPos')

    # chao e paredes
    obj['chao'] = parede(os.path.join(here, "piso.png"), (0, -1.5, -3.5), (10, 10, 1), (90, 0, 0), (10, 0.2, 10))
    obj['fundo'] = parede(os.path.join(here, "parede2.png"), (0, 1.0, -8.5), (10, 5, 1), (0, 0, 0), (10, 5, 0.2))
    obj['lateral'] = parede(os.path.join(here, "parede.png"), (-5, 1.0, -3.5), (10, 5, 1), (0, 90, 0), (0.2, 5, 10))

    # moveis que ja comecam na cena
    moveis.extend([
        Modelo3D(os.path.join(here, 'objetos/bancada.obj'), os.path.join(here, 'parede.png'), (-2, -1.5, -5.5)),
        Modelo3D(os.path.join(here, 'objetos/estante.obj'), os.path.join(here, 'parede2.png'), (2, -1.5, -7)),
        Modelo3D(os.path.join(here, 'objetos/caixa.obj'), os.path.join(here, 'parede.png'), (0, -1.5, -4)),
        Modelo3D(os.path.join(here, 'objetos/caixa.obj'), os.path.join(here, 'parede2.png'), (1, -1.5, -5))
    ])

    camera = Camera(anguloHorizontal, anguloVertical)

    # lista de itens do menu lateral
    itensCatalogo = [
        {
            'nome': 'Bancada',
            'obj': os.path.join(here, 'objetos/bancada.obj'),
            'tex': os.path.join(here, 'parede.png')
        },
        {
            'nome': 'Estante',
            'obj': os.path.join(here, 'objetos/estante.obj'),
            'tex': os.path.join(here, 'parede2.png')
        },
        {
            'nome': 'Caixa Madeira',
            'obj': os.path.join(here, 'objetos/caixa.obj'),
            'tex': os.path.join(here, 'parede.png')
        },
        {
            'nome': 'Caixa Tijolo',
            'obj': os.path.join(here, 'objetos/caixa.obj'),
            'tex': os.path.join(here, 'parede2.png')
        },
        {
            'nome': 'Caixa Grama',
            'obj': os.path.join(here, 'objetos/caixa.obj'),
            'tex': os.path.join(here, 'grass.png')
        }
    ]
    menu = MenuLateral(itensCatalogo)


def render():
    global Mproj
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    myShader.bind()

    # 1. renderiza a cena 3D
    espectiva = resolucao[0] / max(1, resolucao[1])
    Mproj = glm.perspective(glm.radians(40.0), espectiva, 0.1, 200.0)
    glUniformMatrix4fv(shaderes['projMatrix'], 1, GL_FALSE, glm.value_ptr(Mproj))
    camera.render(shaderes['camMatrix'])

    # parametros da luz
    glUniform1i(shaderes['usarLuz'], 1)
    glUniform1i(shaderes['isSombra'], 0)
    glUniform3f(shaderes['lightDir'], 0.5, 1.0, 0.4)
    glUniform3f(shaderes['lightColor'], 0.85, 0.85, 0.80)
    glUniform3f(shaderes['ambientColor'], 0.45, 0.45, 0.50)
    glUniform3f(shaderes['camPos'], camera.posicao.x, camera.posicao.y, camera.posicao.z)

    # paredes e chao
    obj['chao'].render(myShader.shaderId)
    obj['fundo'].render(myShader.shaderId)
    obj['lateral'].render(myShader.shaderId)

    # desenha as sombras no chao/mesa
    glUniform1i(shaderes['isSombra'], 1)
    glDepthMask(GL_FALSE)  # evita z-fighting com o piso

    for movel in moveis:
        if movel is selecionado and arrastandoCena:
            alturaSombra = encontrarAlturaApoio(selecionado, selecionado.posicao.x, selecionado.posicao.z, moveis)
            selecionado.renderSombra(myShader.shaderId, alturaSombra)
        else:
            movel.renderSombra(myShader.shaderId, movel.posicao.y)

    if movelArrastando is not None:
        alturaSombra = encontrarAlturaApoio(movelArrastando, movelArrastando.posicao.x, movelArrastando.posicao.z, moveis)
        movelArrastando.renderSombra(myShader.shaderId, alturaSombra)

    glDepthMask(GL_TRUE)
    glUniform1i(shaderes['isSombra'], 0)

    # desenha os moveis normais
    for movel in moveis:
        movel.render(myShader.shaderId)

    # preview do movel sendo arrastado do menu
    if movelArrastando is not None:
        movelArrastando.render(myShader.shaderId)

    # 2. desenha o menu 2D por cima
    glDisable(GL_DEPTH_TEST)
    glUniform1i(shaderes['usarLuz'], 0)  # sem luz no menu

    Mortho = glm.ortho(0.0, float(resolucao[0]), float(resolucao[1]), 0.0, -1.0, 1.0)
    Mident = glm.mat4(1.0)
    glUniformMatrix4fv(shaderes['projMatrix'], 1, GL_FALSE, glm.value_ptr(Mortho))
    glUniformMatrix4fv(shaderes['camMatrix'], 1, GL_FALSE, glm.value_ptr(Mident))

    if menu is not None:
        menu.render(myShader.shaderId, resolucao)

        # se tiver arrastando sobre o menu, desenha o icone 2D seguindo o mouse
        if arrastandoDoMenu and itemArrastando is not None and movelArrastando is None:
            menu.desenharItemArrastando(myShader.shaderId, itemArrastando, int(posicaoMouse.x), int(posicaoMouse.y))

    glEnable(GL_DEPTH_TEST)

    myShader.unbind()


def colisaoAABB(a, b, margem=0.01):
    minA = a.Minimo()
    maxA = a.Maximo()
    minB = b.Minimo()
    maxB = b.Maximo()

    # pequena margem pra permitir apoiar em cima sem travar
    return (minA.x < maxB.x - margem and maxA.x > minB.x + margem and
            minA.y < maxB.y - margem and maxA.y > minB.y + margem and
            minA.z < maxB.z - margem and maxA.z > minB.z + margem)


def colisao(a, b):
    # se o objeto tiver partes separadas (ex: bancada com vao embaixo)
    colisoresA = getattr(a, 'colisores', None) or [getattr(a, 'colide', a)]
    colisoresB = getattr(b, 'colisores', None) or [getattr(b, 'colide', b)]

    # teste rapido da caixa geral
    aabbA = getattr(a, 'colide', None) or a
    aabbB = getattr(b, 'colide', None) or b
    if hasattr(aabbA, 'Minimo') and hasattr(aabbB, 'Minimo'):
        if not colisaoAABB(aabbA, aabbB, margem=0.0):
            return False

    # se passou no teste geral, testa parte por parte
    for ca in colisoresA:
        for cb in colisoresB:
            if colisaoAABB(ca, cb):
                return True
    return False


def encontrarAlturaApoio(objeto, posX, posZ, obstaculos):
    # acha onde o objeto vai pousar (chao ou em cima de outro movel)
    alturaChao = -1.5
    alturaApoio = alturaChao

    tamX = (objeto.maxLocal.x - objeto.minLocal.x) * objeto.escala * 0.35
    tamZ = (objeto.maxLocal.z - objeto.minLocal.z) * objeto.escala * 0.35

    minX = posX - tamX
    maxX = posX + tamX
    minZ = posZ - tamZ
    maxZ = posZ + tamZ

    for m in obstaculos:
        if m is objeto or not hasattr(m, 'colide'):
            continue
        minObs = m.colide.Minimo()
        maxObs = m.colide.Maximo()

        # ta em cima da area desse obstaculo?
        if minX < maxObs.x and maxX > minObs.x and minZ < maxObs.z and maxZ > minObs.z:
            topo = maxObs.y
            if topo > alturaApoio:
                alturaApoio = topo

    return alturaApoio


def moverCamera(movimento):
    novaPosicao = (camera.posicao + movimento)
    novoCollider = AABB(novaPosicao, camera.colide)

    paredes = [
        obj["fundo"],
        obj["lateral"],
        obj['chao'],
        *moveis
    ]

    for paredeObj in paredes:
        if colisao(novoCollider, paredeObj):
            return

    # não bateu em nada
    camera.posicao = novaPosicao


def update(window):
    global anguloHorizontal, anguloVertical
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        anguloHorizontal += veloGiro
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        anguloHorizontal += -veloGiro
    camera.mudarPosicao(anguloHorizontal, anguloVertical)
    if selecionado is not None:
        if glfw.get_key(window, glfw.KEY_Q) == glfw.PRESS:
            selecionado.girar(angGiroObj)
        elif glfw.get_key(window, glfw.KEY_E) == glfw.PRESS:
            selecionado.girar(-angGiroObj)
        if glfw.get_key(window, glfw.KEY_G) == glfw.PRESS:
            selecionado.escalar(tamEscala)
        if glfw.get_key(window, glfw.KEY_F) == glfw.PRESS:
            selecionado.escalar(-tamEscala)


def scrollMouse(window, xoffset, yoffset):
    camera.zoom(yoffset)


def teclado(window, key, scancode, action, mods):
    global selecionado
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
        elif key in (glfw.KEY_DELETE, glfw.KEY_BACKSPACE):
            if selecionado is not None and selecionado in moveis:
                moveis.remove(selecionado)
                selecionado = None


def raioJanela(window, x, y):
    largura, altura = glfw.get_window_size(window)
    return raioMouse(x, y, largura, altura, Mproj, camera)


def mouse(window, button, action, mods):
    global selecionado, deslocamento, alturaArrasto
    global itemArrastando, movelArrastando, arrastandoDoMenu, arrastandoCena
    global rotacionandoCamera, ultimoMousePos
    global arrastandoPanCamera, ultimoMousePan

    mx, my = glfw.get_cursor_pos(window)

    # botao direito: gira a camera
    if button == glfw.MOUSE_BUTTON_RIGHT:
        if action == glfw.PRESS:
            rotacionandoCamera = True
            ultimoMousePos.x = mx
            ultimoMousePos.y = my
        elif action == glfw.RELEASE:
            rotacionandoCamera = False
        return

    if button != glfw.MOUSE_BUTTON_LEFT:
        return

    # soltou o botao esquerdo
    if action == glfw.RELEASE:
        if arrastandoPanCamera:
            arrastandoPanCamera = False
            return

        if arrastandoDoMenu:
            # soltou o item na cena (fora da barra do menu)
            if movelArrastando is not None and not menu.contemPonto(mx, my, resolucao):
                # pousa no chao ou no apoio
                modoChao = glfw.get_key(window, glfw.KEY_LEFT_CONTROL) == glfw.PRESS or glfw.get_key(window, glfw.KEY_RIGHT_CONTROL) == glfw.PRESS
                alturaBase = -1.5 if modoChao else encontrarAlturaApoio(movelArrastando, movelArrastando.posicao.x, movelArrastando.posicao.z, moveis)
                movelArrastando.posicao.y = alturaBase
                movelArrastando.atualizarColide()

                moveis.append(movelArrastando)
                selecionado = movelArrastando
            movelArrastando = None
            itemArrastando = None
            arrastandoDoMenu = False
            return

        if arrastandoCena and selecionado is not None:
            # pousa o movel no apoio
            modoChao = glfw.get_key(window, glfw.KEY_LEFT_CONTROL) == glfw.PRESS or glfw.get_key(window, glfw.KEY_RIGHT_CONTROL) == glfw.PRESS
            alturaBase = -1.5 if modoChao else encontrarAlturaApoio(selecionado, selecionado.posicao.x, selecionado.posicao.z, moveis)
            selecionado.posicao.y = alturaBase
            selecionado.atualizarColide()

        arrastandoCena = False
        deslocamento = None
        return

    # clicou com botao esquerdo
    if action != glfw.PRESS:
        return

    # 1. clicou no menu?
    if menu is not None:
        itemClicado = menu.obterItemNoPonto(mx, my, resolucao)
        if itemClicado is not None:
            arrastandoDoMenu = True
            itemArrastando = itemClicado
            movelArrastando = None
            return

        # clicou no fundo do menu
        if menu.contemPonto(mx, my, resolucao):
            return

    # 2. clicou na cena: tenta pegar um movel
    raio = raioJanela(window, mx, my)
    if raio is None:
        return
    novoSelecionado = selecionar(*raio, moveis, list(obj.values()))
    if novoSelecionado is not None:
        selecionado = novoSelecionado
        arrastandoCena = True
        alturaArrasto = selecionado.colide.centro.y
        ponto = pontoPlano(*raio, alturaArrasto)
        if ponto is None:
            arrastandoCena = False
        else:
            deslocamento = selecionado.posicao - ponto
            # ergue um pouco o objeto ao arrastar
            modoChao = glfw.get_key(window, glfw.KEY_LEFT_CONTROL) == glfw.PRESS or glfw.get_key(window, glfw.KEY_RIGHT_CONTROL) == glfw.PRESS
            alturaBase = -1.5 if modoChao else encontrarAlturaApoio(selecionado, selecionado.posicao.x, selecionado.posicao.z, moveis)
            selecionado.posicao.y = alturaBase + ALTURA_ELEVACAO
            selecionado.atualizarColide()
    else:
        # clicou no chao/nada: arrasta a camera (pan)
        selecionado = None
        arrastandoCena = False
        arrastandoPanCamera = True
        ultimoMousePan.x = mx
        ultimoMousePan.y = my


def moverMouse(window, x, y):
    global posicaoMouse, movelArrastando, anguloHorizontal, anguloVertical
    global rotacionandoCamera, ultimoMousePos
    global arrastandoPanCamera, ultimoMousePan
    posicaoMouse.x = x
    posicaoMouse.y = y

    # girando a camera com botao direito
    if rotacionandoCamera:
        dx = x - ultimoMousePos.x
        dy = y - ultimoMousePos.y
        ultimoMousePos.x = x
        ultimoMousePos.y = y

        sensibilidade = 0.005
        anguloHorizontal -= dx * sensibilidade
        anguloVertical = max(math.radians(5.0), min(math.radians(85.0), anguloVertical + dy * sensibilidade))
        camera.mudarPosicao(anguloHorizontal, anguloVertical)
        return

    # movendo o centro da camera (pan) com botao esquerdo
    if arrastandoPanCamera:
        dx = x - ultimoMousePan.x
        dy = y - ultimoMousePan.y
        ultimoMousePan.x = x
        ultimoMousePan.y = y
        camera.pan(dx, dy, anguloHorizontal, anguloVertical)
        return

    # hover nos botoes do menu
    if menu is not None and not arrastandoDoMenu:
        menu.atualizarHover(x, y, resolucao)

    # arrastando item novo do menu pra cena
    if arrastandoDoMenu and itemArrastando is not None:
        # ainda ta dentro da barra do menu
        if menu.contemPonto(x, y, resolucao):
            movelArrastando = None
            return

        raio = raioJanela(window, x, y)
        if raio is None:
            return
        ponto = pontoPlano(*raio, -1.5)
        if ponto is None:
            return

        # cria o objeto 3D quando entra na cena
        if movelArrastando is None:
            movelArrastando = Modelo3D(itemArrastando['obj'], itemArrastando['tex'], (ponto.x, -1.5, ponto.z))

        # segurar ctrl forca o chao (pra enfiar embaixo de mesas)
        modoChao = glfw.get_key(window, glfw.KEY_LEFT_CONTROL) == glfw.PRESS or glfw.get_key(window, glfw.KEY_RIGHT_CONTROL) == glfw.PRESS
        if modoChao:
            alturaBase = -1.5
        else:
            alturaBase = encontrarAlturaApoio(movelArrastando, ponto.x, ponto.z, moveis)

        # deixa um pouco levantado enquanto arrasta
        alturaY = alturaBase + ALTURA_ELEVACAO

        anterior = glm.vec3(movelArrastando.posicao)
        movelArrastando.posicao.x = ponto.x
        movelArrastando.posicao.y = alturaY
        movelArrastando.posicao.z = ponto.z
        movelArrastando.atualizarColide()

        minimo = movelArrastando.colide.Minimo()
        maximo = movelArrastando.colide.Maximo()
        bloqueado = minimo.x < -4.9 or maximo.x > 5.0 or minimo.z < -8.4 or maximo.z > 1.5
        obstaculos = [obj['fundo'], obj['lateral'], *moveis]
        if bloqueado or any(colisao(movelArrastando, m) for m in obstaculos):
            movelArrastando.posicao = anterior
            movelArrastando.atualizarColide()
        return

    # arrastando movel que ja ta no cenario
    if arrastandoCena and selecionado is not None and deslocamento is not None:
        raio = raioJanela(window, x, y)
        if raio is None:
            return
        ponto = pontoPlano(*raio, alturaArrasto)
        if ponto is None:
            return

        novaX = ponto.x + deslocamento.x
        novaZ = ponto.z + deslocamento.z

        # segurar ctrl forca o chao
        modoChao = glfw.get_key(window, glfw.KEY_LEFT_CONTROL) == glfw.PRESS or glfw.get_key(window, glfw.KEY_RIGHT_CONTROL) == glfw.PRESS
        if modoChao:
            alturaBase = -1.5
        else:
            alturaBase = encontrarAlturaApoio(selecionado, novaX, novaZ, moveis)

        # deixa um pouco levantado enquanto arrasta
        alturaY = alturaBase + ALTURA_ELEVACAO

        anterior = glm.vec3(selecionado.posicao)
        selecionado.posicao.x = novaX
        selecionado.posicao.y = alturaY
        selecionado.posicao.z = novaZ
        selecionado.atualizarColide()

        minimo = selecionado.colide.Minimo()
        maximo = selecionado.colide.Maximo()
        bloqueado = minimo.x < -4.9 or maximo.x > 5.0 or minimo.z < -8.4 or maximo.z > 1.5
        obstaculos = [obj['fundo'], obj['lateral'], *[m for m in moveis if m is not selecionado]]
        if bloqueado or colisao(selecionado, camera.colidir()) or any(colisao(selecionado, m) for m in obstaculos):
            selecionado.posicao = anterior
            selecionado.atualizarColide()


def windowResize(window, width, height):
    global resolucao
    resolucao[0] = width
    resolucao[1] = height
    glViewport(0, 0, width, height)


def main():
    glfw.init()
    window = glfw.create_window(resolucao[0], resolucao[1], 'Transformação - Cenário e Menu de Itens', None, None)
    glfw.make_context_current(window)
    glfw.set_key_callback(window, teclado)
    glfw.set_mouse_button_callback(window, mouse)
    glfw.set_scroll_callback(window, scrollMouse)
    glfw.set_cursor_pos_callback(window, moverMouse)
    glfw.set_framebuffer_size_callback(window, windowResize)
    init()
    while not glfw.window_should_close(window):
        glfw.poll_events()
        update(window)
        render()
        glfw.swap_buffers(window)
    glfw.terminate()


if __name__ == '__main__':
    main()
