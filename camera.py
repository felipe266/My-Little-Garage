from OpenGL.GL import *
import glm
from colidir import AABB
from shader import *
import math

raio = 25


class Camera:
    def __init__(self, anguloHorizontal, anguloVertical):
        # Ponto central para onde a câmera olha (ponto focal que pode ser arrastado)
        self.alvo = glm.vec3(0.0, 0.0, -3.5)
        self.colide = glm.vec3(0.4, 0.4, 0.4)
        self.mudarPosicao(anguloHorizontal, anguloVertical)

    def colidir(self):
        return AABB(self.posicao, self.colide)

    def mudarPosicao(self, deltH, deltV):
        global raio
        self.posicao = self.alvo + glm.vec3(
            raio * math.cos(deltV) * math.sin(deltH),
            raio * math.sin(deltV),
            raio * math.cos(deltV) * math.cos(deltH)
        )

    def zoom(self, zom):
        global raio
        raio = max(2, min(40, raio - zom))

    def pan(self, dx, dy, deltH, deltV):
        """Move o ponto focal (centralização) da câmera conforme o mouse é arrastado."""
        global raio
        frente = glm.normalize(self.alvo - self.posicao)
        direita = glm.normalize(glm.cross(frente, glm.vec3(0.0, 1.0, 0.0)))
        frentePlano = glm.normalize(glm.vec3(frente.x, 0.0, frente.z))

        # Velocidade proporcional à distância do zoom para sensação 1:1 com o mouse
        velo = raio * 0.001
        self.alvo -= direita * (dx * velo)
        self.alvo += frentePlano * (dy * velo)
        self.mudarPosicao(deltH, deltV)

    def camView(self):
        return glm.lookAt(self.posicao, self.alvo, glm.vec3(0.0, 1.0, 0.0))

    def render(self, shader):
        Mview = self.camView()
        glUniformMatrix4fv(shader, 1, GL_FALSE, glm.value_ptr(Mview))
