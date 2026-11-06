# Script para gerar o PDF completo e didatico de Iluminacao e Sombra
import os
import sys

def sanitize(text):
    replacements = {
        '“': '"', '”': '"', '‘': "'", '’': "'", '–': '-', '—': '-',
        '•': '*', '→': '->', '←': '<-', '≈': '~', '≤': '<=', '≥': '>=',
        '×': 'x', '·': '.', '°': 'o', 'á': 'a', 'à': 'a', 'ã': 'a',
        'â': 'a', 'é': 'e', 'ê': 'e', 'í': 'i', 'ó': 'o', 'ô': 'o',
        'õ': 'o', 'ú': 'u', 'ç': 'c', 'Á': 'A', 'À': 'A', 'Ã': 'A',
        'Â': 'A', 'É': 'E', 'Ê': 'E', 'Í': 'I', 'Ó': 'O', 'Ô': 'O',
        'Õ': 'O', 'Ú': 'U', 'Ç': 'C'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    result = []
    for ch in text:
        try:
            ch.encode('latin-1')
            result.append(ch)
        except UnicodeEncodeError:
            result.append('?')
    return "".join(result)


class PDFDocument:
    def __init__(self, filename):
        self.filename = filename
        self.pages = []
        self.current_stream = []
        self.width = 595.28  # A4 width in points
        self.height = 841.89 # A4 height in points
        self.margin_x = 42
        self.margin_top = 40
        self.margin_bottom = 45
        self.y = self.height - self.margin_top

    def new_page(self):
        if self.current_stream:
            self.pages.append("".join(self.current_stream))
            self.current_stream = []
        self.y = self.height - self.margin_top
        # Barra superior decorativa azul
        self.rect(0, self.height - 6, self.width, 6, fill=(0.15, 0.45, 0.82))

    def check_space(self, needed):
        if self.y - needed < self.margin_bottom:
            self.new_page()

    def rect(self, x, y, w, h, fill=None, stroke=None, stroke_width=1):
        s = ["q"]
        if stroke:
            s.append(f"{stroke_width} w {stroke[0]:.3f} {stroke[1]:.3f} {stroke[2]:.3f} RG")
        if fill:
            s.append(f"{fill[0]:.3f} {fill[1]:.3f} {fill[2]:.3f} rg")
        s.append(f"{x:.2f} {y:.2f} {w:.2f} {h:.2f} re")
        if fill and stroke:
            s.append("B")
        elif fill:
            s.append("f")
        elif stroke:
            s.append("S")
        s.append("Q\n")
        self.current_stream.append(" ".join(s))

    def text_line(self, x, y, text_str, font="F1", size=10, color=(0.1, 0.1, 0.1)):
        text_str = sanitize(text_str)
        text_str = text_str.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
        s = (
            f"q {color[0]:.3f} {color[1]:.3f} {color[2]:.3f} rg "
            f"BT /{font} {size} Tf {x:.2f} {y:.2f} Td ({text_str}) Tj ET Q\n"
        )
        self.current_stream.append(s)

    def header_banner(self, title, subtitle, tag):
        self.check_space(75)
        w = self.width - 2 * self.margin_x
        h = 65
        # Banner de cabecalho com gradiente simulado
        self.rect(self.margin_x, self.y - h, w, h, fill=(0.12, 0.28, 0.55), stroke=(0.08, 0.20, 0.40), stroke_width=1.5)
        self.rect(self.margin_x, self.y - h, 6, h, fill=(0.95, 0.65, 0.15))
        
        self.text_line(self.margin_x + 18, self.y - 18, tag.upper(), font="F2", size=8.5, color=(0.90, 0.75, 0.30))
        self.text_line(self.margin_x + 18, self.y - 36, title, font="F2", size=15, color=(1.0, 1.0, 1.0))
        self.text_line(self.margin_x + 18, self.y - 52, subtitle, font="F3", size=9.5, color=(0.85, 0.90, 0.98))
        self.y -= (h + 16)

    def heading1(self, title):
        self.check_space(45)
        self.y -= 4
        self.rect(self.margin_x, self.y - 4, self.width - 2 * self.margin_x, 22, fill=(0.92, 0.95, 0.99), stroke=(0.15, 0.45, 0.82), stroke_width=1.2)
        self.rect(self.margin_x, self.y - 4, 4, 22, fill=(0.15, 0.45, 0.82))
        self.text_line(self.margin_x + 12, self.y + 4, title, font="F2", size=12, color=(0.10, 0.30, 0.65))
        self.y -= 26

    def heading2(self, title):
        self.check_space(32)
        self.y -= 4
        self.text_line(self.margin_x, self.y, title, font="F2", size=11, color=(0.15, 0.40, 0.75))
        self.rect(self.margin_x, self.y - 3, self.width - 2 * self.margin_x, 1, fill=(0.80, 0.85, 0.92))
        self.y -= 14

    def paragraph(self, text_str, font="F1", size=9.5, color=(0.18, 0.18, 0.22), line_spacing=13.5):
        max_w = self.width - 2 * self.margin_x
        chars_per_line = int(max_w / 5.1)
        words = text_str.split(' ')
        lines = []
        current_line = []
        current_len = 0

        for w in words:
            if current_len + len(w) + 1 <= chars_per_line:
                current_line.append(w)
                current_len += len(w) + 1
            else:
                lines.append(" ".join(current_line))
                current_line = [w]
                current_len = len(w)
        if current_line:
            lines.append(" ".join(current_line))

        for line in lines:
            self.check_space(line_spacing)
            self.text_line(self.margin_x, self.y, line, font=font, size=size, color=color)
            self.y -= line_spacing

    def bullet(self, bold_prefix, text_str, size=9.5):
        max_w = self.width - 2 * self.margin_x - 18
        chars_per_line = int(max_w / 5.1)
        full_text = bold_prefix + ": " + text_str
        words = full_text.split(' ')
        lines = []
        cur_line = []
        cur_len = 0
        for w in words:
            if cur_len + len(w) + 1 <= chars_per_line:
                cur_line.append(w)
                cur_len += len(w) + 1
            else:
                lines.append(" ".join(cur_line))
                cur_line = [w]
                cur_len = len(w)
        if cur_line:
            lines.append(" ".join(cur_line))

        for i, line in enumerate(lines):
            self.check_space(13)
            if i == 0:
                self.text_line(self.margin_x + 4, self.y, ">", font="F2", size=9.5, color=(0.15, 0.45, 0.82))
                # Extrai bold_prefix se coincidir
                self.text_line(self.margin_x + 16, self.y, line, font="F1", size=size, color=(0.15, 0.15, 0.20))
            else:
                self.text_line(self.margin_x + 16, self.y, line, font="F1", size=size, color=(0.15, 0.15, 0.20))
            self.y -= 13

    def note_box(self, title, text_str):
        self.check_space(55)
        w = self.width - 2 * self.margin_x
        # quebra o texto
        chars = int((w - 24) / 5.1)
        words = text_str.split(' ')
        lines = []
        cur = []
        cur_l = 0
        for wrd in words:
            if cur_l + len(wrd) + 1 <= chars:
                cur.append(wrd)
                cur_l += len(wrd) + 1
            else:
                lines.append(" ".join(cur))
                cur = [wrd]
                cur_l = len(wrd)
        if cur:
            lines.append(" ".join(cur))

        box_h = 24 + len(lines) * 12.5
        self.check_space(box_h + 8)
        self.rect(self.margin_x, self.y - box_h, w, box_h, fill=(0.95, 0.98, 0.95), stroke=(0.60, 0.80, 0.65), stroke_width=1)
        self.rect(self.margin_x, self.y - box_h, 4, box_h, fill=(0.20, 0.65, 0.35))
        self.text_line(self.margin_x + 12, self.y - 14, title, font="F2", size=9.5, color=(0.15, 0.50, 0.25))
        
        y_txt = self.y - 28
        for l in lines:
            self.text_line(self.margin_x + 12, y_txt, l, font="F1", size=9, color=(0.15, 0.25, 0.18))
            y_txt -= 12.5
        self.y -= (box_h + 10)

    def card_box(self, var_name, code_loc, value, meaning, intuition):
        # Quebra simples de texto para caber bem
        card_w = self.width - 2 * self.margin_x
        chars_w = int((card_w - 95) / 5.0)

        # Quebra meaning
        words_m = meaning.split(' ')
        m_lines = []
        cur = []
        l = 0
        for w in words_m:
            if l + len(w) + 1 <= chars_w:
                cur.append(w)
                l += len(w) + 1
            else:
                m_lines.append(" ".join(cur))
                cur = [w]
                l = len(w)
        if cur:
            m_lines.append(" ".join(cur))

        # Quebra intuition
        words_i = intuition.split(' ')
        i_lines = []
        cur = []
        l = 0
        for w in words_i:
            if l + len(w) + 1 <= chars_w:
                cur.append(w)
                l += len(w) + 1
            else:
                i_lines.append(" ".join(cur))
                cur = [w]
                l = len(w)
        if cur:
            i_lines.append(" ".join(cur))

        card_h = 24 + len(m_lines) * 12 + len(i_lines) * 12 + 10
        self.check_space(card_h + 8)

        # Retangulo base
        self.rect(self.margin_x, self.y - card_h, card_w, card_h, fill=(0.97, 0.98, 0.99), stroke=(0.85, 0.88, 0.92), stroke_width=1)
        self.rect(self.margin_x, self.y - card_h, 4, card_h, fill=(0.15, 0.45, 0.82))

        # Topo
        self.text_line(self.margin_x + 12, self.y - 13, var_name, font="F2", size=10, color=(0.10, 0.35, 0.70))
        self.text_line(self.margin_x + 210, self.y - 13, f"Local: {code_loc}", font="F3", size=8.5, color=(0.45, 0.45, 0.50))
        self.text_line(self.margin_x + 370, self.y - 13, f"Valor: {value}", font="F2", size=8.5, color=(0.18, 0.52, 0.28))

        curr_y = self.y - 26
        # Meaning
        self.text_line(self.margin_x + 12, curr_y, "Significado:", font="F2", size=8.8, color=(0.25, 0.25, 0.30))
        for ml in m_lines:
            self.text_line(self.margin_x + 85, curr_y, ml, font="F1", size=8.8, color=(0.15, 0.15, 0.18))
            curr_y -= 12

        # Intuition
        self.text_line(self.margin_x + 12, curr_y, "Como Explicar:", font="F2", size=8.8, color=(0.80, 0.35, 0.10))
        for il in i_lines:
            self.text_line(self.margin_x + 85, curr_y, il, font="F1", size=8.8, color=(0.20, 0.20, 0.25))
            curr_y -= 12

        self.y -= (card_h + 7)

    def save(self):
        if self.current_stream:
            self.pages.append("".join(self.current_stream))
            self.current_stream = []

        total_pages = len(self.pages)
        final_pages = []
        for i, pstream in enumerate(self.pages):
            footer_text = f"Pagina {i+1} de {total_pages}   |   Guia Didatico de Computacao Grafica: Iluminacao e Sombra"
            footer_s = (
                f"q 0.45 0.45 0.50 rg BT /F1 8 Tf {self.margin_x:.2f} 20 Td ({footer_text}) Tj ET Q\n"
            )
            line_s = f"q 0.85 0.87 0.90 RG 0.5 w {self.margin_x:.2f} 32 m {self.width - self.margin_x:.2f} 32 l S Q\n"
            final_pages.append(pstream + line_s + footer_s)

        num_pages = len(final_pages)
        page_obj_ids = [3 + i for i in range(num_pages)]
        content_obj_ids = [3 + num_pages + i for i in range(num_pages)]
        font1_id = 3 + 2 * num_pages
        font2_id = font1_id + 1
        font3_id = font2_id + 1

        catalog = "<< /Type /Catalog /Pages 2 0 R >>"
        kids_str = " ".join([f"{pid} 0 R" for pid in page_obj_ids])
        pages_obj = f"<< /Type /Pages /Kids [{kids_str}] /Count {num_pages} >>"

        page_objs = []
        for i in range(num_pages):
            p = (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {self.width:.2f} {self.height:.2f}] "
                f"/Contents {content_obj_ids[i]} 0 R "
                f"/Resources << /Font << /F1 {font1_id} 0 R /F2 {font2_id} 0 R /F3 {font3_id} 0 R >> >> >>"
            )
            page_objs.append(p)

        stream_objs = []
        for i in range(num_pages):
            data = final_pages[i].encode('latin-1')
            st = f"<< /Length {len(data)} >>\nstream\n{final_pages[i]}endstream"
            stream_objs.append(st)

        font1 = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
        font2 = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"
        font3 = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique /Encoding /WinAnsiEncoding >>"

        all_objs = [catalog, pages_obj] + page_objs + stream_objs + [font1, font2, font3]

        with open(self.filename, 'wb') as f:
            f.write(b"%PDF-1.4\n")
            offsets = []
            for i, obj_content in enumerate(all_objs):
                obj_id = i + 1
                offsets.append(f.tell())
                f.write(f"{obj_id} 0 obj\n".encode('latin-1'))
                f.write(obj_content.encode('latin-1'))
                f.write(b"\nendobj\n")

            xref_start = f.tell()
            f.write(f"xref\n0 {len(all_objs)+1}\n".encode('latin-1'))
            f.write(b"0000000000 65535 f \n")
            for off in offsets:
                f.write(f"{off:010d} 00000 n \n".encode('latin-1'))

            trailer = f"<< /Size {len(all_objs)+1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF\n"
            f.write(trailer.encode('latin-1'))


def gerar_pdf_completo():
    pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Guia_Iluminacao_e_Sombra.pdf")
    doc = PDFDocument(pdf_path)
    doc.new_page()

    # ==================== PAGINA 1 ====================
    doc.header_banner(
        title="Iluminacao & Sombra em Computacao Grafica",
        subtitle="Dicionario Didatico de Variaveis, Matematica Intuitiva e Roteiro de Explicacao",
        tag="Sprint 2 - Projeto 3D OpenGL & Python"
    )

    doc.heading1("1. Visao Geral: O Desafio da Luz e da Sombra em 3D")
    doc.paragraph(
        "Em Computacao Grafica, uma tela de computador e estritamente bidimensional (2D). Quando renderizamos "
        "modelos 3D apenas com cores ou texturas puras, os objetos parecem figuras de papel ou desenhos planos. "
        "Nao da para distinguir onde comeca ou termina uma aresta ou se uma face esta inclinada."
    )
    doc.y -= 4
    doc.paragraph(
        "A Iluminacao e a Sombra sao as duas principais pistas visuais que o cerebro humano usa para deduzir profundidade, "
        "volume e contato fisico com o chao. Neste projeto, implementamos uma solucao elegante e compacta ideal para o nivel junior: "
        "um modelo de Iluminacao Difusa Direcional (Lambert) somado a uma Luz Ambiente, e Sombras Planar Projetadas baseadas na propria malha 3D."
    )
    doc.y -= 6

    doc.note_box(
        "Regra de Ouro da Computacao Grafica Junior",
        "O CPU (Python) cuida da logica, das posicoes e envia ordens. A GPU (Placa de Video e Shaders GLSL) "
        "executa os calculos de iluminacao em paralelo para cada pixel desenhado na tela!"
    )

    doc.heading1("2. Dicionario de Variaveis: O Que Cada Uma Faz?")
    doc.paragraph("Abaixo estao detalhadas todas as variaveis criadas no projeto, seus valores e como explica-las com naturalidade:")
    doc.y -= 4

    doc.card_box(
        var_name="usarLuz (Uniform booleano)",
        code_loc="mode3D.py / fragmentShad.glsl",
        value="1 (3D) ou 0 (2D)",
        meaning="Interruptor que avisa a GPU se o que esta sendo desenhado agora deve receber calculo de luz ou ser desenhado com cor pura.",
        intuition="Pense no interruptor de um quarto. No mundo 3D queremos luz ligada (1). Ja para desenhar o menu 2D e icones da barra lateral, desligamos a luz (0) para que os botoes fiquem sempre nitidos e legiveis."
    )

    doc.card_box(
        var_name="lightDir (vec3)",
        code_loc="mode3D.py (0.5, 1.0, 0.4)",
        value="X=0.5, Y=1.0, Z=0.4",
        meaning="Vetor tridimensional que define a direcao de onde vem a luz direta (como os raios do Sol).",
        intuition="Imagine que colocamos o Sol no ceu: Y=1.0 significa bem do alto, X=0.5 um pouco a direita, e Z=0.4 um pouco a frente. Isso cria um contraste bonito em 3 lados de qualquer caixa."
    )

    doc.card_box(
        var_name="lightColor (vec3)",
        code_loc="mode3D.py (0.85, 0.85, 0.80)",
        value="R=0.85, G=0.85, B=0.80",
        meaning="Cor e intensidade da luz direta do Sol que atinge os objetos.",
        intuition="Valores vao de 0.0 (preto) a 1.0 (branco maximo). Escolhemos 0.85 com azul um pouco menor (0.80), gerando uma luz levemente amarelada e quente como a luz solar suave do meio da manha."
    )

    doc.card_box(
        var_name="ambientColor (vec3)",
        code_loc="mode3D.py (0.45, 0.45, 0.50)",
        value="R=0.45, G=0.45, B=0.50",
        meaning="Luz ambiente indireta, que simula a luz que rebate nas paredes, no chao e no ceu da sala.",
        intuition="Sem luz ambiente, as partes dos objetos viradas de costas para o Sol ficariam pretas como breu! A luz ambiente garante que o lado de tras continue visivel com 45% de claridade suave."
    )

    # ==================== PAGINA 2 ====================
    doc.new_page()
    doc.heading2("Dicionario de Variaveis (Continuacao)")

    doc.card_box(
        var_name="worldPos (vec3)",
        code_loc="vertexShad.glsl -> fragment",
        value="Calculado via M * position",
        meaning="A coordenada exata (X, Y, Z) do ponto no espaco do mundo real do cenario.",
        intuition="E a posicao real no mundo daquele pedaco da peca. O fragment shader precisa saber onde cada pixel esta no espaco para calcular a inclinacao da face e a direcao da luz."
    )

    doc.card_box(
        var_name="N (Normal da Superficie)",
        code_loc="fragmentShad.glsl",
        value="Calculado com cross(dFdx, dFdy)",
        meaning="Vetor perpendicular a superficie, como uma flecha apontando para fora da parede ou face do cubo.",
        intuition="Imagine um prego perpendicular espetado na madeira. Se o prego aponta para o teto, a face e horizontal. Se aponta para a direita, e uma parede lateral. E a 'bussola' de cada face!"
    )

    doc.card_box(
        var_name="L (Vetor da Luz Normalizado)",
        code_loc="fragmentShad.glsl",
        value="normalize(lightDir)",
        meaning="O vetor apontando em direcao ao Sol com comprimento matematico obrigatoriamente igual a 1.",
        intuition="Reduzimos a forca da seta para exatamente 1 unidade de comprimento, para que ela guarde apenas a DIRECAO da luz, sem distorcer as contas de brilho."
    )

    doc.card_box(
        var_name="diff (Fator Difuso / Brilho)",
        code_loc="fragmentShad.glsl",
        value="max(dot(N, L), 0.0)",
        meaning="Numero entre 0.0 e 1.0 que diz quanta luz do Sol a superficie recebe pelo seu angulo de inclinacao.",
        intuition="E a famosa Lei do Cosseno de Lambert: se a face aponta de frente para a luz, diff=1.0 (brilho maximo). Se estiver de lado, diff cai. Se estiver de costas, fica zero (sombra)."
    )

    doc.card_box(
        var_name="isSombra (Uniform booleano)",
        code_loc="mode3D.py / fragmentShad.glsl",
        value="1 (renderizando sombra) ou 0",
        meaning="Informa ao fragment shader que nao e para pintar o modelo com texturas, mas sim como uma silhueta escura translucida.",
        intuition="Quando ativado, o shader ignora madeira e texturas e cospe a cor vec4(0.06, 0.06, 0.10, 0.45): um azul-marinho bem escuro com 45% de opacidade (55% transparente)."
    )

    doc.card_box(
        var_name="ALTURA_ELEVACAO (float)",
        code_loc="main.py",
        value="0.25 (unidades do mundo)",
        meaning="Distancia vertical fixa que o objeto 'levita' no ar quando o usuario clica e comeca a arrasta-lo com o mouse.",
        intuition="Quando pegamos uma caixa no chao do mundo real, nos a erguemos. Elevar 0.25 unidades faz o objeto descolar do chao e revela a sombra embaixo dele, dando sensacao tatil de arrasto 3D."
    )

    doc.card_box(
        var_name="alturaApoio (float)",
        code_loc="main.py / mode3D.py",
        value="0.0 (chao) ou 1.15 (mesa/bancada)",
        meaning="Altura da superficie mais proxima logo abaixo do objeto onde a sombra deve ser carimbada e onde ele vai pousar.",
        intuition="Se a caixa estiver no chao, a sombra fica no chao (Y=0.0). Se estiver em cima da bancada, a sombra sobe para o tampo da mesa (Y=1.15). A sombra nunca afunda no vazio."
    )

    doc.card_box(
        var_name="S.y = 0.0001 (Matriz de Escala)",
        code_loc="mode3D.py (renderSombra)",
        value="glm.scale(1.0, 0.0001, 1.0)",
        meaning="Fator de escala no eixo Y que achata a malha 3D completa do objeto contra o chao.",
        intuition="A analogia do 'rolo compressor': pegamos o modelo 3D original e esmagamos sua altura ate virar uma folha quase plana. Assim, a sombra tem exatamente o formato do objeto!"
    )

    # ==================== PAGINA 3 ====================
    doc.new_page()
    doc.heading1("3. A Matematica Explicada Sem Segredos e Sem Jargoes")
    doc.paragraph(
        "Muitas pessoas travam quando ouvem palavras como 'vetores', 'produto escalar' ou 'derivadas parciais'. "
        "Mas a intuicao por tras e incrivelmente simples quando usamos analogias do mundo real:"
    )
    doc.y -= 4

    doc.heading2("A. O que e um Vetor e por que usamos a Normalizacao (normalize)?")
    doc.paragraph(
        "Em Computacao Grafica, um vetor tridimensional vec3(x, y, z) nada mais e do que uma FLECHA que sai da origem "
        "e aponta para algum lugar no espaco. Ela possui uma DIRECAO e um COMPRIMENTO (tamanho da flecha)."
    )
    doc.y -= 2
    doc.paragraph(
        "Quando queremos saber apenas para onde o Sol esta apontando, o tamanho da flecha atrapalha as multiplicacoes. "
        "A funcao normalize() divide a flecha pelo seu proprio tamanho. O resultado e um vetor com tamanho exatamente 1.0 "
        "(chamado de Vetor Unitario). Ele guarda pura direcao sem distorcer nenhuma conta!"
    )
    doc.y -= 6

    doc.heading2("B. A Normal da Superficie: A 'Bussola' de cada Face")
    doc.paragraph(
        "Para saber se uma parede esta recebendo sol, a GPU precisa saber para onde aquela parede esta 'olhando'. "
        "A esse olhar damos o nome de Vetor Normal (N). Pense em um prego apontando 90 graus para fora da madeira. "
        "Se o prego aponta para cima, e o teto. Se aponta para os lados, sao as paredes."
    )
    doc.y -= 4

    doc.note_box(
        "O Truque de Mestre: dFdx e dFdy (Sem precisar criar buffers de normais)",
        "Em codigos mais antigos e pesados, o programador precisava cadastrar a normal de cada vertice na mao. "
        "No nosso projeto moderno, usamos dFdx(worldPos) e dFdy(worldPos). A GPU compara a posicao no espaco de pixels "
        "vizinhos na tela e descobre a inclinacao da face instantaneamente com um Produto Vetorial (cross)! "
        "Isso deixa o codigo limpo, ultra rapido e perfeito para nivel junior."
    )
    doc.y -= 6

    doc.heading2("C. Produto Escalar (dot) e a 'Analogia da Lanterna na Parede'")
    doc.paragraph(
        "Como a GPU calcula o brilho diff = max(dot(N, L), 0.0)? Essa e a famosa Lei de Lambert e pode ser explicada assim:"
    )
    doc.y -= 2
    doc.bullet(
        "Luz de Frente (Angulo 0 graus)",
        "Aponte uma lanterna reta contra a parede. O facho fica concentrado em um circulo pequeno e ultra brilhante. "
        "O produto escalar entre N e L vale 1.0 (brilho maximo)."
    )
    doc.bullet(
        "Luz Inclinada (Angulo 45 a 60 graus)",
        "Incline a lanterna. O circulo de luz se espalha em uma elipse maior e a parede fica menos brilhante. "
        "O produto escalar diminui para algo entre 0.7 e 0.3."
    )
    doc.bullet(
        "Luz Rasante ou de Costas (90 a 180 graus)",
        "Se a luz vier de lado ou por tras da parede, nenhuma luz atinge a face frontal. O produto escalar daria zero "
        "ou um numero negativo. O comando max(..., 0.0) impede que o brilho fique negativo e crava em 0.0 (lado de sombra)."
    )
    doc.y -= 4

    doc.heading2("D. A Equacao Final de Iluminacao do Pixel")
    doc.paragraph(
        "A cor de cada ponto no nosso shader e calculada por uma formula simples de adicao e multiplicacao:"
    )
    doc.y -= 2
    doc.bullet(
        "Luz Total",
        "corFinal = (ambientColor + lightColor * diff) * texColor"
    )
    doc.bullet(
        "Em bom portugues",
        "Pegamos a claridade minima que nunca zera (ambientColor), somamos com a luz do Sol proporcional ao angulo (lightColor * diff), "
        "e multiplicamos o resultado pela cor da textura da madeira ou da caixa. Resultado: faces iluminadas ganham vida e faces opostas ganham sombra suave!"
    )

    # ==================== PAGINA 4 ====================
    doc.new_page()
    doc.heading1("4. O Mecanismo de Sombra Planar Projetada e Elevacao")
    doc.paragraph(
        "Criar sombras em Computacao Grafica pode ser um dos topicos mais complexos (como Shadow Mapping com buffers de profundidade). "
        "Para o nosso projeto, escolhemos a tecnica de Sombra Planar Projetada, que e elegante, extremamente eficiente e visualmente impecavel."
    )
    doc.y -= 4

    doc.heading2("A. Como funciona o 'Carimbo' da Sombra?")
    doc.bullet(
        "1. Mesma Geometria",
        "Ao inves de tentar desenhar um circulo generico, pegamos o proprio modelo 3D do objeto (com todos os seus triangulos e curvas)."
    )
    doc.bullet(
        "2. O Rolo Compressor (Escala Y = 0.0001)",
        "Aplicamos uma matriz de escala que reduz a altura do modelo a quase zero. O objeto 3D vira uma estampa plana encostada no solo."
    )
    doc.bullet(
        "3. Silhueta Escura (isSombra = 1)",
        "Mandamos o shader desenhar essa estampa com cor azul-escura suave e 45% de opacidade, com blend transparente ativado (glBlendFunc)."
    )
    doc.bullet(
        "4. Anti Z-Fighting (+0.005)",
        "Posicionamos a sombra 5 milimetros acima do chao real (yChao + 0.005). Isso impede que a sombra e o piso disputem o mesmo pixel na tela (efeito de piscar)."
    )
    doc.y -= 6

    doc.heading2("B. O Efeito de Elevacao Visual (ALTURA_ELEVACAO = 0.25)")
    doc.paragraph(
        "Quando o usuario clica e arrasta um objeto pelo cenario, somamos 0.25 unidades na sua posicao Y. "
        "O objeto sobe no ar, enquanto a sombra continua projetada perfeitamente no chao ou no tampo da mesa (alturaApoio). "
        "Isso cria um efeito visual fantastico: a pessoa que joga tem a certeza absoluta de que pegou o item no colo e sabe "
        "exatamente em qual ponto do chao ele vai aterrissar quando soltar o botao do mouse!"
    )
    doc.y -= 8

    doc.heading1("5. Roteiro Pratico para Apresentar aos Colegas (2 Minutos)")
    doc.paragraph(
        "Use este passo a passo caso va demonstrar o projeto em sala de aula ou em reuniao de equipe:"
    )
    doc.y -= 4

    doc.bullet(
        "Passo 1 (Introducao)",
        "'Reparem como o cenario 3D ganha volume quando as faces recebem luz de acordo com a sua inclinacao em relacao ao Sol virtual.'"
    )
    doc.bullet(
        "Passo 2 (Luz Ambiente vs Sol)",
        "'Usamos duas luzes: uma luz ambiente suave (para as costas dos moveis nao ficarem pretas) e uma luz solar direcional calculada em tempo real na GPU pela Lei de Lambert.'"
    )
    doc.bullet(
        "Passo 3 (Demonstracao do Arrasto)",
        "'Ao clicar e arrastar qualquer objeto da mesa, vejam que ele levita um pouco (ALTURA_ELEVACAO = 0.25). Imediatamente vemos a sombra projetada no chao com o formato exato da peca!'"
    )
    doc.bullet(
        "Passo 4 (Inteligencia da Sombra)",
        "'Se eu arrastar uma caixa para cima da bancada, a sombra projeta no tampo da mesa. Se arrastar para fora, a sombra desce para o piso, gracas a deteccao de altura de apoio.'"
    )
    doc.bullet(
        "Passo 5 (Conclusao Tecnica)",
        "'A sombra usa a tecnica planar projetada com matriz de escala Y minima, e a iluminacao calcula normais por derivadas de tela (dFdx/dFdy), mantendo o codigo leve, limpo e profissional.'"
    )
    doc.y -= 8

    doc.note_box(
        "Resumo Final em Uma Frase",
        "A iluminacao diz para o olho onde a peca esta virada; a sombra diz para o olho onde a peca esta pisando!"
    )

    doc.save()
    print(f"PDF gerado com sucesso em: {pdf_path}")
    print(f"Total de paginas geradas: {len(doc.pages)}")


if __name__ == "__main__":
    gerar_pdf_completo()
