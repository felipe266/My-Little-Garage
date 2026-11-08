import glm


def raioMouse(x, y, largura, altura, projecao, camera):
    inversa = glm.inverse(projecao * camera.camView())
    perto = inversa * glm.vec4(2*x/largura-1, 1-2*y/altura, -1, 1)
    longe = inversa * glm.vec4(2*x/largura-1, 1-2*y/altura, 1, 1)
    perto = glm.vec3(perto/perto.w)
    longe = glm.vec3(longe/longe.w)
    return perto, glm.normalize(longe-perto)


def intersecaoCaixa(origem, direcao, minimo, maximo):
    entrada, saida = 0.0, float('inf')
    for i in range(3):
        if abs(direcao[i]) < 0.000001:
            if origem[i] < minimo[i] or origem[i] > maximo[i]:
                return None
        else:
            a = (minimo[i]-origem[i])/direcao[i]
            b = (maximo[i]-origem[i])/direcao[i]
            entrada = max(entrada, min(a,b))
            saida = min(saida, max(a,b))
            if entrada > saida:
                return None
    return entrada


def selecionar(origem, direcao, objetos, paredes):
    escolhido = None
    distancia = float('inf')
    for objeto in objetos:
        inversa = glm.inverse(objeto.operacao())
        inicio = glm.vec3(inversa * glm.vec4(origem, 1))
        vetor = glm.vec3(inversa * glm.vec4(direcao, 0))
        acerto = intersecaoCaixa(inicio, vetor, objeto.minLocal, objeto.maxLocal)
        if acerto is not None and acerto < distancia:
            escolhido, distancia = objeto, acerto
    for parede in paredes:
        acerto = intersecaoCaixa(origem, direcao, parede.colide.Minimo(), parede.colide.Maximo())
        if acerto is not None and acerto < distancia:
            return None
    return escolhido


def pontoPlano(origem, direcao, altura):
    if abs(direcao.y) < 0.000001:
        return None
    distancia = (altura-origem.y)/direcao.y
    if distancia < 0:
        return None
    return origem + direcao*distancia
