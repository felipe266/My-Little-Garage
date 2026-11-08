import os
import ctypes
import numpy as np
import glm
from OpenGL.GL import *
from PIL import Image, ImageDraw
from textura import Textura

# ==============================================================================
# FUNÇÕES UTILITÁRIAS GEOMÉTRICAS E MATEMÁTICAS
# ==============================================================================

def pontoNoRetangulo(px, py, rx, ry, rw, rh):
    """
    Testa colisão do tipo Ponto-vs-AABB (Axis-Aligned Bounding Box).
    Verifica se o ponto (px, py) está contido na área delimitada por:
    - Origem: (rx, ry)
    - Dimensões: rw (largura), rh (altura)
    Retorna True se estiver dentro, False caso contrário.
    """
    if px < rx or px > rx + rw:
        return False
    if py < ry or py > ry + rh:
        return False
    return True


def menorNumero(a, b):
    """
    Substituto manual para a função nativa min().
    Retorna o menor valor escalar entre 'a' e 'b'.
    """
    if a < b:
        return a
    return b


# ==============================================================================
# RENDERIZADOR BÁSICO 2D (OPENGL)
# ==============================================================================

class Quad2D:
    """
    Responsável por gerenciar os buffers e desenhar retângulos texturizados em 2D.
    Utiliza um quadrado unitário (1x1) que é posicionado e escalado via matrizes uniform.
    """
    def __init__(self):
        # Definição de 6 vértices formando 2 triângulos (quadrado de 0.0 a 1.0).
        # Cada vértice possui 5 floats:
        #   - 3 floats para posição (X, Y, Z)
        #   - 2 floats para coordenadas de textura UV (U, V)
        # Stride total por vértice = 5 * 4 bytes = 20 bytes.
        vertices = np.array([
            # Triângulo 1 (X, Y, Z,   U, V)
            0.0, 0.0, 0.0,   0.0, 1.0,
            1.0, 0.0, 0.0,   1.0, 1.0,
            1.0, 1.0, 0.0,   1.0, 0.0,

            # Triângulo 2 (X, Y, Z,   U, V)
            0.0, 0.0, 0.0,   0.0, 1.0,
            1.0, 1.0, 0.0,   1.0, 0.0,
            0.0, 1.0, 0.0,   0.0, 0.0
        ], dtype=np.float32)

        # Criação e vinculação do Vertex Array Object (VAO)
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # Criação e envio dos dados para o Vertex Buffer Object (VBO) na GPU
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # Atributo 0: Posição (vec3: X, Y, Z)
        # 20 bytes de passo (stride), offset 0
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        # Atributo 1: Coordenadas UV (vec2: U, V)
        # 20 bytes de passo (stride), offset 12 bytes (pula os 3 floats de posição)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        # Desvincula buffers para evitar alterações acidentais de estado
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def desenhar(self, shaderId, texId, x, y, w, h):
        """
        Renderiza o quad com a textura e dimensões fornecidas na posição (x, y).
        """
        # Ativa a unidade de textura 0 e associa a textura desejada
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texId)
        glBindVertexArray(self.vao)

        # Calcula a Matriz de Modelo (Model Matrix):
        # 1. Escala o quad unitário para as dimensões em pixels (w, h)
        # 2. Translada para a posição final na tela (x, y)
        modelMatrix = glm.translate(glm.vec3(x, y, 0.0)) * glm.scale(glm.vec3(w, h, 1.0))
        modelMatrixLoc = glGetUniformLocation(shaderId, 'modelMatrix')
        glUniformMatrix4fv(modelMatrixLoc, 1, GL_FALSE, glm.value_ptr(modelMatrix))

        # Desenha os 6 vértices (2 triângulos)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glBindVertexArray(0)


# ==============================================================================
# MENU LATERAL / CATÁLOGO DE ITENS DA INTERFACE (UI)
# ==============================================================================

class MenuLateral:
    """
    Interface gráfica lateral em formato de barra vertical com cards clicáveis/arrastáveis.
    Gera o visual dinamicamente via Pillow e envia como textura OpenGL.
    """
    def __init__(self, itens, largura=190, cardLargura=170, cardAltura=85):
        self.itens = itens
        self.quad = Quad2D()

        # Dimensões e espaçamentos do menu
        self.largura = largura
        self.cardLargura = cardLargura
        self.cardAltura = cardAltura
        self.espacamento = 10
        self.margemTopo = 48         # Espaço reservado para o cabeçalho/título
        self.margemDireita = 20      # Distância da borda direita da janela
        self.margemSuperior = 25     # Distância da borda superior da janela
        self.itemHover = None        # Guarda a referência do item que está sob o cursor

        # Calcula a altura total da barra com base no número de cards e espaçamentos
        totalItens = len(self.itens)
        self.altura = self.margemTopo + totalItens * (self.cardAltura + self.espacamento) + 12

        # 1. Gera a textura do fundo da barra lateral
        self.texFundo = self.gerarFundo(self.largura, self.altura)

        # 2. Pré-renderiza as texturas dos cards em estado NORMAL
        self.texCards = []
        for item in self.itens:
            tex = self.gerarCard(item, destacado=False)
            self.texCards.append(tex)

        # 3. Pré-renderiza as texturas dos cards em estado HOVER (com borda/brilho destacado)
        self.texCardsHover = []
        for item in self.itens:
            texHover = self.gerarCard(item, destacado=True)
            self.texCardsHover.append(texHover)

    def obterPosicao(self, resolucao):
        """
        Calcula o canto superior esquerdo (x, y) da barra lateral
        alinhando-a à margem direita da janela.
        """
        x = resolucao[0] - self.largura - self.margemDireita
        y = self.margemSuperior
        return x, y

    def contemPonto(self, px, py, resolucao):
        """Verifica se as coordenadas do mouse (px, py) estão sobre o menu lateral."""
        x, y = self.obterPosicao(resolucao)
        return pontoNoRetangulo(px, py, x, y, self.largura, self.altura)

    def obterItemNoPonto(self, px, py, resolucao):
        """
        Identifica qual item da lista está sob o cursor do mouse (px, py).
        Retorna o dicionário/objeto do item ou None se nada for atingido.
        """
        x, y = self.obterPosicao(resolucao)
        if not self.contemPonto(px, py, resolucao):
            return None

        # Posição X centralizada dos cartões dentro da barra
        cx = x + (self.largura - self.cardLargura) // 2
        cyAtual = y + self.margemTopo

        # Itera verticalmente sobre a área de colisão de cada card
        for item in self.itens:
            if pontoNoRetangulo(px, py, cx, cyAtual, self.cardLargura, self.cardAltura):
                return item
            cyAtual += self.cardAltura + self.espacamento

        return None

    def atualizarHover(self, px, py, resolucao):
        """Atualiza a referência do item atualmente apontado pelo mouse."""
        self.itemHover = self.obterItemNoPonto(px, py, resolucao)

    def render(self, shaderId, resolucao):
        """
        Desenha o menu completo: fundo translúcido e cada um dos cartões.
        Alterna entre a textura normal e a de destaque se houver hover.
        """
        x, y = self.obterPosicao(resolucao)

        # 1. Desenha o fundo da barra lateral
        self.quad.desenhar(shaderId, self.texFundo.textureId, x, y, self.largura, self.altura)

        # 2. Desenha cada um dos cards empilhados
        cx = x + (self.largura - self.cardLargura) // 2
        cyAtual = y + self.margemTopo

        i = 0
        for item in self.itens:
            destacado = (self.itemHover is item)
            # Seleciona o buffer de textura apropriado (hover ou normal)
            if destacado:
                tex = self.texCardsHover[i]
            else:
                tex = self.texCards[i]

            self.quad.desenhar(shaderId, tex.textureId, cx, cyAtual, self.cardLargura, self.cardAltura)
            cyAtual += self.cardAltura + self.espacamento
            i += 1

    def desenharItemArrastando(self, shaderId, item, mx, my):
        """
        Desenha o card centralizado na posição do mouse durante um Drag & Drop.
        """
        # Busca o índice do item na lista para pegar a textura correspondente
        idx = -1
        for i in range(len(self.itens)):
            if self.itens[i] is item:
                idx = i
                break

        if idx != -1:
            tex = self.texCards[idx]
            w = self.cardLargura
            h = self.cardAltura
            # Centraliza o retângulo nas coordenadas do mouse (mx, my)
            posX = mx - w // 2
            posY = my - h // 2
            self.quad.desenhar(shaderId, tex.textureId, posX, posY, w, h)

    def gerarFundo(self, w, h):
        """
        Cria a imagem de fundo do menu usando Pillow:
        - Fundo arredondado translúcido
        - Header superior demarcado
        - Texto de título centralizado
        Retorna uma instância da classe Textura (OpenGL).
        """
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Painel principal arredondado com borda sutil
        draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=14, fill=(26, 28, 36, 235), outline=(75, 82, 105, 255), width=2)
        
        # Caixa de destaque para o cabeçalho
        draw.rounded_rectangle([4, 4, w - 5, 36], radius=10, fill=(38, 42, 55, 245))

        # Título "ITENS" alinhado no meio (anchor="mm")
        draw.text((w // 2, 20), "ITENS", fill=(240, 242, 255, 255), anchor="mm")

        return Textura(img)

    def gerarCard(self, item, destacado=False):
        """
        Gera a textura individual para o card de um item:
        - Ajusta cores e espessura de borda com base no estado (destacado/hover)
        - Abre, corta proporcionalmente em 1:1 e redimensiona a imagem do item (ícone)
        - Escreve o nome do item no rodapé do card
        Retorna uma instância da classe Textura (OpenGL).
        """
        w = self.cardLargura
        h = self.cardAltura
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Configura paleta de cores para o estado Hover / Normal
        if destacado:
            corFundo = (58, 64, 82, 250)
            corBorda = (0, 200, 255, 255)      # Borda ciano/azul neon em hover
            larguraBorda = 2
            corTexto = (255, 255, 255, 255)
        else:
            corFundo = (38, 41, 52, 240)
            corBorda = (70, 78, 98, 220)       # Borda discreta padrão
            larguraBorda = 1
            corTexto = (225, 228, 238, 255)

        # Fundo do cartão com cantos arredondados
        draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=10, fill=corFundo, outline=corBorda, width=larguraBorda)

        # Processamento e desenho do ícone do objeto
        tamanhoIcone = 44
        texPath = ''
        if 'tex' in item:
            texPath = item['tex']

        # Carrega o ícone caso o caminho seja válido no disco
        if os.path.exists(texPath):
            texImg = Image.open(texPath).convert("RGBA")
            tw, th = texImg.size
            
            # Corta (crop) a imagem ao centro no formato 1:1 (quadrado)
            lado = menorNumero(tw, th)
            cx = tw // 2
            cy = th // 2
            texImg = texImg.crop((cx - lado // 2, cy - lado // 2, cx + lado // 2, cy + lado // 2))
            
            # Redimensiona para o tamanho padrão do ícone e cola no card com canal alfa
            texImg = texImg.resize((tamanhoIcone, tamanhoIcone))
            img.paste(texImg, ((w - tamanhoIcone) // 2, 8), texImg)

        # Adiciona o texto descritivo do item centralizado na parte inferior
        nome = ''
        if 'nome' in item:
            nome = item['nome']

        posicaoYTexto = h - 16
        draw.text((w // 2, posicaoYTexto), nome, fill=corTexto, anchor="mm")

        return Textura(img)