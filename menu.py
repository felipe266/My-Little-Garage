import os
import ctypes
import numpy as np
import glm
from OpenGL.GL import *
from PIL import Image, ImageDraw
from textura import Textura


# funcao manual para testar se um ponto 2D esta dentro de um retangulo
def pontoNoRetangulo(px, py, rx, ry, rw, rh):
    if px < rx or px > rx + rw:
        return False
    if py < ry or py > ry + rh:
        return False
    return True


# funcao manual para achar o menor entre dois numeros (substitui min)
def menorNumero(a, b):
    if a < b:
        return a
    return b


class Quad2D:
    # renderizador de retangulo 2D em projecao ortografica
    def __init__(self):
        vertices = np.array([
            0.0, 0.0, 0.0,   0.0, 1.0,
            1.0, 0.0, 0.0,   1.0, 1.0,
            1.0, 1.0, 0.0,   1.0, 0.0,

            0.0, 0.0, 0.0,   0.0, 1.0,
            1.0, 1.0, 0.0,   1.0, 0.0,
            0.0, 1.0, 0.0,   0.0, 0.0
        ], dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # posicao (vec3)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        # coordenadas uv (vec2)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def desenhar(self, shaderId, texId, x, y, w, h):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texId)
        glBindVertexArray(self.vao)

        modelMatrix = glm.translate(glm.vec3(x, y, 0.0)) * glm.scale(glm.vec3(w, h, 1.0))
        modelMatrixLoc = glGetUniformLocation(shaderId, 'modelMatrix')
        glUniformMatrix4fv(modelMatrixLoc, 1, GL_FALSE, glm.value_ptr(modelMatrix))

        glDrawArrays(GL_TRIANGLES, 0, 6)
        glBindVertexArray(0)


class MenuLateral:
    # barra lateral com catalogo de itens
    def __init__(self, itens, largura=190, cardLargura=170, cardAltura=85):
        self.itens = itens
        self.quad = Quad2D()

        self.largura = largura
        self.cardLargura = cardLargura
        self.cardAltura = cardAltura
        self.espacamento = 10
        self.margemTopo = 48
        self.margemDireita = 20
        self.margemSuperior = 25
        self.itemHover = None

        # calcula altura total com base na quantidade de itens
        totalItens = len(self.itens)
        self.altura = self.margemTopo + totalItens * (self.cardAltura + self.espacamento) + 12

        # gera as texturas do fundo
        self.texFundo = self.gerarFundo(self.largura, self.altura)

        # cria as texturas dos cards com loop manual (sem list comprehension)
        self.texCards = []
        for item in self.itens:
            tex = self.gerarCard(item, destacado=False)
            self.texCards.append(tex)

        self.texCardsHover = []
        for item in self.itens:
            texHover = self.gerarCard(item, destacado=True)
            self.texCardsHover.append(texHover)

    def obterPosicao(self, resolucao):
        x = resolucao[0] - self.largura - self.margemDireita
        y = self.margemSuperior
        return x, y

    def contemPonto(self, px, py, resolucao):
        x, y = self.obterPosicao(resolucao)
        return pontoNoRetangulo(px, py, x, y, self.largura, self.altura)

    def obterItemNoPonto(self, px, py, resolucao):
        x, y = self.obterPosicao(resolucao)
        if not self.contemPonto(px, py, resolucao):
            return None

        cx = x + (self.largura - self.cardLargura) // 2
        cyAtual = y + self.margemTopo

        for item in self.itens:
            if pontoNoRetangulo(px, py, cx, cyAtual, self.cardLargura, self.cardAltura):
                return item
            cyAtual += self.cardAltura + self.espacamento

        return None

    def atualizarHover(self, px, py, resolucao):
        self.itemHover = self.obterItemNoPonto(px, py, resolucao)

    def render(self, shaderId, resolucao):
        x, y = self.obterPosicao(resolucao)

        # fundo da barra lateral
        self.quad.desenhar(shaderId, self.texFundo.textureId, x, y, self.largura, self.altura)

        # desenha cada cartao
        cx = x + (self.largura - self.cardLargura) // 2
        cyAtual = y + self.margemTopo

        i = 0
        for item in self.itens:
            destacado = (self.itemHover is item)
            if destacado:
                tex = self.texCardsHover[i]
            else:
                tex = self.texCards[i]

            self.quad.desenhar(shaderId, tex.textureId, cx, cyAtual, self.cardLargura, self.cardAltura)
            cyAtual += self.cardAltura + self.espacamento
            i += 1

    def desenharItemArrastando(self, shaderId, item, mx, my):
        # acha o indice do item manualmente (sem usar .index())
        idx = -1
        for i in range(len(self.itens)):
            if self.itens[i] is item:
                idx = i
                break

        if idx != -1:
            tex = self.texCards[idx]
            w = self.cardLargura
            h = self.cardAltura
            posX = mx - w // 2
            posY = my - h // 2
            self.quad.desenhar(shaderId, tex.textureId, posX, posY, w, h)

    def gerarFundo(self, w, h):
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # fundo escuro translúcido com borda
        draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=14, fill=(26, 28, 36, 235), outline=(75, 82, 105, 255), width=2)
        draw.rounded_rectangle([4, 4, w - 5, 36], radius=10, fill=(38, 42, 55, 245))

        # titulo superior
        draw.text((w // 2, 20), "ITENS", fill=(240, 242, 255, 255), anchor="mm")

        return Textura(img)

    def gerarCard(self, item, destacado=False):
        w = self.cardLargura
        h = self.cardAltura
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        if destacado:
            corFundo = (58, 64, 82, 250)
            corBorda = (0, 200, 255, 255)
            larguraBorda = 2
            corTexto = (255, 255, 255, 255)
        else:
            corFundo = (38, 41, 52, 240)
            corBorda = (70, 78, 98, 220)
            larguraBorda = 1
            corTexto = (225, 228, 238, 255)

        draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=10, fill=corFundo, outline=corBorda, width=larguraBorda)

        # miniatura do objeto
        tamanhoIcone = 44
        texPath = ''
        if 'tex' in item:
            texPath = item['tex']

        if os.path.exists(texPath):
            texImg = Image.open(texPath).convert("RGBA")
            tw, th = texImg.size
            lado = menorNumero(tw, th)
            cx = tw // 2
            cy = th // 2
            texImg = texImg.crop((cx - lado // 2, cy - lado // 2, cx + lado // 2, cy + lado // 2))
            texImg = texImg.resize((tamanhoIcone, tamanhoIcone))
            img.paste(texImg, ((w - tamanhoIcone) // 2, 8), texImg)

        # nome do item
        nome = ''
        if 'nome' in item:
            nome = item['nome']

        posicaoYTexto = h - 16
        draw.text((w // 2, posicaoYTexto), nome, fill=corTexto, anchor="mm")

        return Textura(img)
