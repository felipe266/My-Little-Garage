import numpy as np
import ctypes
import glm
from OpenGL.GL import *
import math
import os
from textura import Textura
from colidir import AABB

menorEscala = 1
maiorEscala = 3.5

class Modelo3D():
    def __init__(self, hereObj, hereText, posicao=(0, 0, 0), escala=1, rotacao=(0, 1, 0)):
        self.posicao = glm.vec3(posicao)
        self.escala = escala
        self.rotacao = glm.vec3(rotacao)
        self.angRotate = 0.0

        posicoes = []
        texturas = []
        vertices = []

        with open(hereObj, encoding='utf-8') as arquivo:
            for linha in arquivo:
                partes = linha.split()

                if not partes:
                    continue

                if partes[0] == 'v':
                    posicoes.append(tuple(map(float, partes[1:4])))

                elif partes[0] == 'vt':
                    texturas.append(tuple(map(float, partes[1:3])))

                elif partes[0] == 'f':
                    face = []

                    for item in partes[1:]:
                        indices = item.split('/')
                        indice = int(indices[0])
                        ponto = posicoes[indice - 1 if indice > 0 else indice]
                        uv = (0.0, 0.0)

                        if len(indices) > 1 and indices[1]:
                            indice = int(indices[1])
                            uv = texturas[indice - 1 if indice > 0 else indice]

                        face.append((*ponto, *uv))

                    for i in range(1, len(face) - 1):
                        vertices.extend((face[0], face[i], face[i + 1]))

        if not vertices:
            raise ValueError('Modelo sem faces: ' + str(hereObj))

        self.vertices = np.array(vertices, dtype=np.float32)
        self.minLocal = glm.vec3(self.vertices[:, :3].min(axis=0))
        self.maxLocal = glm.vec3(self.vertices[:, :3].max(axis=0))

        # Define sub-colisores detalhados para modelos ocos (como bancada com vão embaixo)
        nomeObj = os.path.basename(hereObj).lower()
        if 'bancada' in nomeObj:
            self.caixasLocais = [
                # Tampo superior da bancada
                (glm.vec3(0.0, 1.10, 0.0), glm.vec3(2.2, 0.18, 1.0)),
                # 4 Pés da bancada
                (glm.vec3(-0.90, 0.52, -0.35), glm.vec3(0.14, 1.04, 0.14)),
                (glm.vec3(-0.90, 0.52, 0.35), glm.vec3(0.14, 1.04, 0.14)),
                (glm.vec3(0.90, 0.52, -0.35), glm.vec3(0.14, 1.04, 0.14)),
                (glm.vec3(0.90, 0.52, 0.35), glm.vec3(0.14, 1.04, 0.14)),
            ]
        elif 'estante' in nomeObj:
            self.caixasLocais = [
                # Laterais da estante
                (glm.vec3(-0.70, 1.0, 0.0), glm.vec3(0.12, 2.0, 0.70)),
                (glm.vec3(0.70, 1.0, 0.0), glm.vec3(0.12, 2.0, 0.70)),
                # Prateleiras
                (glm.vec3(0.0, 0.06, 0.0), glm.vec3(1.4, 0.12, 0.70)),
                (glm.vec3(0.0, 0.70, 0.0), glm.vec3(1.4, 0.12, 0.70)),
                (glm.vec3(0.0, 1.35, 0.0), glm.vec3(1.4, 0.12, 0.70)),
                (glm.vec3(0.0, 1.94, 0.0), glm.vec3(1.4, 0.12, 0.70)),
            ]
        else:
            # Objeto sólido por padrão (ex: caixa)
            centroPadrao = (self.minLocal + self.maxLocal) / 2
            tamanhoPadrao = self.maxLocal - self.minLocal
            self.caixasLocais = [(centroPadrao, tamanhoPadrao)]

        self.atualizarColide()

        self.texId = Textura(hereText).textureId
        self.qtdIndices = len(vertices)

        self.vaoId = glGenVertexArrays(1)
        glBindVertexArray(self.vaoId)

        self.vboId = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vboId)
        glBufferData(
            GL_ARRAY_BUFFER,
            self.vertices.nbytes,
            self.vertices,
            GL_STATIC_DRAW
        )

        glVertexAttribPointer(
            0, 3, GL_FLOAT, GL_FALSE, 5*4, ctypes.c_void_p(0)
        )
        glEnableVertexAttribArray(0)

        glVertexAttribPointer(
            1, 2, GL_FLOAT, GL_FALSE, 5*4, ctypes.c_void_p(3*4)
        )
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def atualizarColide(self):
        matriz = self.operacao()
        self.colisores = []

        # Caixa envolvente geral (broadphase e limites gerais)
        pontos = []
        for x in (self.minLocal.x, self.maxLocal.x):
            for y in (self.minLocal.y, self.maxLocal.y):
                for z in (self.minLocal.z, self.maxLocal.z):
                    canto = glm.vec4(x, y, z, 1)
                    cantoTransformado = matriz * canto
                    pontos.append(glm.vec3(cantoTransformado))

        minimo = glm.vec3(pontos[0])
        maximo = glm.vec3(pontos[0])

        for ponto in pontos:
            minimo.x = min(minimo.x, ponto.x)
            minimo.y = min(minimo.y, ponto.y)
            minimo.z = min(minimo.z, ponto.z)

            maximo.x = max(maximo.x, ponto.x)
            maximo.y = max(maximo.y, ponto.y)
            maximo.z = max(maximo.z, ponto.z)

        centro = (minimo + maximo) / 2
        tamanho = maximo - minimo

        self.colide = AABB(centro, tamanho)

        # Atualiza a lista de sub-colisores (peças sólidas individuais)
        for centroL, tamL in self.caixasLocais:
            minL = centroL - tamL / 2
            maxL = centroL + tamL / 2
            subPontos = []
            for x in (minL.x, maxL.x):
                for y in (minL.y, maxL.y):
                    for z in (minL.z, maxL.z):
                        subPontos.append(glm.vec3(matriz * glm.vec4(x, y, z, 1)))

            subMin = glm.vec3(subPontos[0])
            subMax = glm.vec3(subPontos[0])
            for sp in subPontos:
                subMin.x = min(subMin.x, sp.x)
                subMin.y = min(subMin.y, sp.y)
                subMin.z = min(subMin.z, sp.z)
                subMax.x = max(subMax.x, sp.x)
                subMax.y = max(subMax.y, sp.y)
                subMax.z = max(subMax.z, sp.z)

            self.colisores.append(AABB((subMin + subMax) / 2, subMax - subMin))

    def girar(self, graus):
        self.angRotate = (self.angRotate + graus) %360

    def escalar(self, escala):
        self.escala = max(menorEscala,min(maiorEscala,escala+self.escala))

    def operacao(self):
        T = glm.translate(self.posicao)
        R = glm.rotate(glm.radians(self.angRotate), glm.vec3(0,1,0))
        S = glm.scale(glm.vec3(self.escala))
    
        M = T*R*S
        return M

    def render(self, shaderId):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texId)
        glBindVertexArray(self.vaoId)

        modelMatrix = self.operacao()
        glUniformMatrix4fv(
            glGetUniformLocation(shaderId, 'modelMatrix'),
            1,
            GL_FALSE,
            glm.value_ptr(modelMatrix)
        )

        glDrawArrays(GL_TRIANGLES, 0, self.qtdIndices)
        glBindVertexArray(0)

    def renderSombra(self, shaderId, alturaChao):
        """Desenha a sombra projetada achatando a mesma malha do objeto na superfície de apoio."""
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texId)
        glBindVertexArray(self.vaoId)

        T = glm.translate(glm.vec3(self.posicao.x, alturaChao + 0.003, self.posicao.z))
        R = glm.rotate(glm.radians(self.angRotate), glm.vec3(0, 1, 0))
        # Escala Y próxima de zero para achatar a geometria no plano
        S = glm.scale(glm.vec3(self.escala, 0.0001, self.escala))
        modelMatrix = T * R * S

        glUniformMatrix4fv(
            glGetUniformLocation(shaderId, 'modelMatrix'),
            1,
            GL_FALSE,
            glm.value_ptr(modelMatrix)
        )

        glDrawArrays(GL_TRIANGLES, 0, self.qtdIndices)
        glBindVertexArray(0)