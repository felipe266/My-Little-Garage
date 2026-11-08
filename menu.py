import os
import ctypes
import numpy as np
import glm
from OpenGL.GL import *
from PIL import Image, ImageDraw
from textura import Textura


class Quad2D:
    """Renderizador de retângulos 2D usando projeção ortográfica."""
    def __init__(self):
        # Vértices 2D de (0,0) a (1,1): pos (x, y, z), uv (u, v)
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

        # local 0: posição (vec3)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        # local 1: coordenadas de textura uv (vec2)
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
    """Menu lateral flutuante com catálogo de itens arrastáveis."""
    def __init__(self, itens, largura=190, cardLargura=170, cardAltura=85):
        self.itens = itens
        self.quad = Quad2D()

        # ==============================================================
        # CONFIGURAÇÕES DE TAMANHO DO MENU (Altere estes valores para mudar o tamanho)
        # ==============================================================
        self.largura = largura            # Largura total da barra lateral (ex: 190 a 230)
        self.cardLargura = cardLargura    # Largura de cada cartão/botão de item (ex: 170 a 200)
        self.cardAltura = cardAltura      # Altura de cada cartão/botão de item (ex: 85 a 100)
        self.espacamento = 10             # Espaçamento vertical entre os cartões
        self.margemTopo = 48              # Altura do cabeçalho com o título "ITENS"
        self.margemDireita = 20           # Distância da borda direita da janela
        self.margemSuperior = 25          # Distância da borda superior da janela
        self.itemHover = None

        # Altura total calculada automaticamente com base no número de itens
        self.altura = self.margemTopo + len(self.itens) * (self.cardAltura + self.espacamento) + 12

        # Gera as texturas do fundo e dos cartões
        self.texFundo = self.gerarFundo(self.largura, self.altura)
        self.texCards = [self.gerarCard(item, destacado=False) for item in self.itens]
        self.texCardsHover = [self.gerarCard(item, destacado=True) for item in self.itens]

    def obterPosicao(self, resolucao):
        x = resolucao[0] - self.largura - self.margemDireita
        y = self.margemSuperior
        return x, y

    def contemPonto(self, px, py, resolucao):
        x, y = self.obterPosicao(resolucao)
        return x <= px <= x + self.largura and y <= py <= y + self.altura

    def obterItemNoPonto(self, px, py, resolucao):
        x, y = self.obterPosicao(resolucao)
        if not self.contemPonto(px, py, resolucao):
            return None

        cx = x + (self.largura - self.cardLargura) // 2
        cyAtual = y + self.margemTopo

        for item in self.itens:
            if cx <= px <= cx + self.cardLargura and cyAtual <= py <= cyAtual + self.cardAltura:
                return item
            cyAtual += self.cardAltura + self.espacamento

        return None

    def atualizarHover(self, px, py, resolucao):
        self.itemHover = self.obterItemNoPonto(px, py, resolucao)

    def render(self, shaderId, resolucao):
        x, y = self.obterPosicao(resolucao)

        # 1. Desenha o fundo da barra lateral
        self.quad.desenhar(shaderId, self.texFundo.textureId, x, y, self.largura, self.altura)

        # 2. Desenha cada item como um cartão
        cx = x + (self.largura - self.cardLargura) // 2
        cyAtual = y + self.margemTopo

        for i, item in enumerate(self.itens):
            destacado = (self.itemHover is item)
            tex = self.texCardsHover[i] if destacado else self.texCards[i]
            self.quad.desenhar(shaderId, tex.textureId, cx, cyAtual, self.cardLargura, self.cardAltura)
            cyAtual += self.cardAltura + self.espacamento

    def desenharItemArrastando(self, shaderId, item, mx, my):
        try:
            idx = self.itens.index(item)
            tex = self.texCards[idx]
            w, h = self.cardLargura, self.cardAltura
            self.quad.desenhar(shaderId, tex.textureId, mx - w // 2, my - h // 2, w, h)
        except Exception:
            pass

    def gerarFundo(self, w, h):
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Painel de fundo escuro translúcido com borda suave
        if hasattr(draw, 'rounded_rectangle'):
            draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=14, fill=(26, 28, 36, 235), outline=(75, 82, 105, 255), width=2)
            draw.rounded_rectangle([4, 4, w - 5, 36], radius=10, fill=(38, 42, 55, 245))
        else:
            draw.rectangle([0, 0, w - 1, h - 1], fill=(26, 28, 36, 235), outline=(75, 82, 105, 255), width=2)
            draw.rectangle([4, 4, w - 5, 36], fill=(38, 42, 55, 245))

        # Título superior "ITENS"
        try:
            draw.text((w // 2, 20), "ITENS", fill=(240, 242, 255, 255), anchor="mm")
        except Exception:
            draw.text((w // 2 - 18, 12), "ITENS", fill=(240, 242, 255, 255))

        return Textura(img)

    def gerarCard(self, item, destacado=False):
        w, h = self.cardLargura, self.cardAltura
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        corFundo = (58, 64, 82, 250) if destacado else (38, 41, 52, 240)
        corBorda = (0, 200, 255, 255) if destacado else (70, 78, 98, 220)

        if hasattr(draw, 'rounded_rectangle'):
            draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=10, fill=corFundo, outline=corBorda, width=2 if destacado else 1)
        else:
            draw.rectangle([0, 0, w - 1, h - 1], fill=corFundo, outline=corBorda, width=2 if destacado else 1)

        # Tamanho da miniatura proporcional à altura do cartão
        tamanhoIcone = 44
        texPath = item.get('tex', '')
        if os.path.exists(texPath):
            try:
                texImg = Image.open(texPath).convert("RGBA")
                tw, th = texImg.size
                lado = min(tw, th)
                cx, cy = tw // 2, th // 2
                texImg = texImg.crop((cx - lado // 2, cy - lado // 2, cx + lado // 2, cy + lado // 2))
                texImg = texImg.resize((tamanhoIcone, tamanhoIcone))
                img.paste(texImg, ((w - tamanhoIcone) // 2, 8), texImg)
            except Exception:
                pass

        # Nome do item
        nome = item.get('nome', '')
        corTexto = (255, 255, 255, 255) if destacado else (225, 228, 238, 255)
        posicaoYTexto = h - 16
        try:
            draw.text((w // 2, posicaoYTexto), nome, fill=corTexto, anchor="mm")
        except Exception:
            draw.text((12, posicaoYTexto - 6), nome, fill=corTexto)

        return Textura(img)
