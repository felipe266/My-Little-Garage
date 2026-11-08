from PIL import Image
from OpenGL.GL import *


class Textura:
    def __init__(self, caminho):
        if isinstance(caminho, str):
            self.imagem = Image.open(caminho)
        else:
            self.imagem = caminho
        self.imagem = self.imagem.convert("RGBA")
        self.imagem = self.imagem.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

        self.larg, self.alt = self.imagem.size
        self.dados = self.imagem.tobytes()

        self.textureId = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.textureId)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.larg, self.alt, 0, GL_RGBA, GL_UNSIGNED_BYTE, self.dados)
        glBindTexture(GL_TEXTURE_2D, 0)
