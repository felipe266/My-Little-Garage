from OpenGL.GL import *
import numpy as np
import ctypes
from textura import *
import glm
from colidir import AABB

class parede():
    def __init__(self, caminho, posicao, escala, rotacao, colide):
        self.posicao = glm.vec3(posicao)
        self.escala = glm.vec3(escala)
        self.rotacao = glm.vec3(rotacao)
        self.colide = AABB(self.posicao, colide)

        myTexture = Textura(caminho)
        self.texId = myTexture.textureId

        vertices = [
           [-0.5,-0.5, 0.0, 0.0],
           [0.5, -0.5, 1.0, 0.0],
           [0.5, 0.5, 1.0, 1.0],
           [-0.5, 0.5, 0.0, 1.0]
        ]
        faces=[
            [0,1,2],
            [2,3,0]
        ]

        vertices = np.array(vertices, dtype=np.float32)
        faces = np.array(faces, dtype=np.uint32)
        self.qtdIndices = faces.size

        self.vaoId = glGenVertexArrays(1)
        glBindVertexArray(self.vaoId)

        vboId = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vboId)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glVertexAttribPointer(0,2, GL_FLOAT, GL_FALSE, 4*4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4*4, ctypes.c_void_p(2*4))
        glEnableVertexAttribArray(1)

        faces = np.array(faces, np.dtype(np.uint32))

        eboId = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, eboId)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, faces.nbytes, faces, GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def operacao(self):
        T = glm.translate(self.posicao)
        Rx = glm.rotate(glm.radians(self.rotacao.x), glm.vec3(1,0,0))
        Ry = glm.rotate(glm.radians(self.rotacao.y), glm.vec3(0,1,0))
        Rz = glm.rotate(glm.radians(self.rotacao.z), glm.vec3(0,0,1))
        S = glm.scale(self.escala)

        M = T*Rx*Ry*Rz*S

        return M

    def render(self, shaderId):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texId)
        
        glBindVertexArray(self.vaoId)
        
        modelMatrix = self.operacao()
        modelMatrix_loc = glGetUniformLocation(shaderId, 'modelMatrix')
        glUniformMatrix4fv(modelMatrix_loc, 1, GL_FALSE, glm.value_ptr(modelMatrix))

        glDrawElements(GL_TRIANGLES, self.qtdIndices, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
