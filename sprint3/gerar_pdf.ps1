# Gerador em PowerShell puro para Guia_Iluminacao_e_Sombra.pdf
[System.Threading.Thread]::CurrentThread.CurrentCulture = [System.Globalization.CultureInfo]::InvariantCulture
[System.Threading.Thread]::CurrentThread.CurrentUICulture = [System.Globalization.CultureInfo]::InvariantCulture
[System.Globalization.CultureInfo]::DefaultThreadCurrentCulture = [System.Globalization.CultureInfo]::InvariantCulture
[System.Globalization.CultureInfo]::DefaultThreadCurrentUICulture = [System.Globalization.CultureInfo]::InvariantCulture

function F([double]$val, [int]$dec = 2) {
    return $val.ToString("F" + $dec, [System.Globalization.CultureInfo]::InvariantCulture)
}

function Sanitize-Text([string]$text) {
    if (-not $text) { return "" }
    $sb = [System.Text.StringBuilder]::new()
    for ($i = 0; $i -lt $text.Length; $i++) {
        $c = $text[$i]
        $code = [int][char]$c
        if ($code -ge 32 -and $code -le 126) {
            $sb.Append($c) | Out-Null
        } elseif ($code -ge 192 -and $code -le 255) {
            switch ($code) {
                192 { $sb.Append('A') | Out-Null }
                193 { $sb.Append('A') | Out-Null }
                194 { $sb.Append('A') | Out-Null }
                195 { $sb.Append('A') | Out-Null }
                199 { $sb.Append('C') | Out-Null }
                200 { $sb.Append('E') | Out-Null }
                201 { $sb.Append('E') | Out-Null }
                202 { $sb.Append('E') | Out-Null }
                205 { $sb.Append('I') | Out-Null }
                211 { $sb.Append('O') | Out-Null }
                212 { $sb.Append('O') | Out-Null }
                213 { $sb.Append('O') | Out-Null }
                218 { $sb.Append('U') | Out-Null }
                224 { $sb.Append('a') | Out-Null }
                225 { $sb.Append('a') | Out-Null }
                226 { $sb.Append('a') | Out-Null }
                227 { $sb.Append('a') | Out-Null }
                231 { $sb.Append('c') | Out-Null }
                232 { $sb.Append('e') | Out-Null }
                233 { $sb.Append('e') | Out-Null }
                234 { $sb.Append('e') | Out-Null }
                237 { $sb.Append('i') | Out-Null }
                243 { $sb.Append('o') | Out-Null }
                244 { $sb.Append('o') | Out-Null }
                245 { $sb.Append('o') | Out-Null }
                250 { $sb.Append('u') | Out-Null }
                default { $sb.Append(' ') | Out-Null }
            }
        } else {
            $sb.Append(' ') | Out-Null
        }
    }
    return $sb.ToString()
}

class PDFBuilder {
    [double]$width = 595.28
    [double]$height = 841.89
    [double]$marginX = 42.0
    [double]$marginTop = 40.0
    [double]$marginBottom = 45.0
    [double]$y = 801.89
    [System.Collections.Generic.List[string]]$pages = [System.Collections.Generic.List[string]]::new()
    [System.Text.StringBuilder]$currentStream = [System.Text.StringBuilder]::new()

    NewPage() {
        if ($this.currentStream.Length -gt 0) {
            $this.pages.Add($this.currentStream.ToString())
            $this.currentStream.Clear()
        }
        $this.y = $this.height - $this.marginTop
        $this.Rect(0, $this.height - 6, $this.width, 6, 0.15, 0.45, 0.82, $false, 0, 0, 0, 1)
    }

    CheckSpace([double]$needed) {
        if ($this.y - $needed -lt $this.marginBottom) {
            $this.NewPage()
        }
    }

    Rect([double]$x, [double]$y, [double]$w, [double]$h, [double]$fr, [double]$fg, [double]$fb, [bool]$hasStroke, [double]$sr, [double]$sg, [double]$sb, [double]$sw) {
        $s = [System.Text.StringBuilder]::new("q ")
        if ($hasStroke) {
            $s.Append(("{0} w {1} {2} {3} RG " -f (F $sw 2), (F $sr 3), (F $sg 3), (F $sb 3))) | Out-Null
        }
        if ($fr -ge 0) {
            $s.Append(("{0} {1} {2} rg " -f (F $fr 3), (F $fg 3), (F $fb 3))) | Out-Null
        }
        $s.Append(("{0} {1} {2} {3} re " -f (F $x 2), (F $y 2), (F $w 2), (F $h 2))) | Out-Null
        if ($fr -ge 0 -and $hasStroke) {
            $s.Append("B") | Out-Null
        } elseif ($fr -ge 0) {
            $s.Append("f") | Out-Null
        } elseif ($hasStroke) {
            $s.Append("S") | Out-Null
        }
        $s.Append(" Q`n") | Out-Null
        $this.currentStream.Append($s.ToString()) | Out-Null
    }

    TextLine([double]$x, [double]$y, [string]$text, [string]$font, [double]$size, [double]$r, [double]$g, [double]$b) {
        $clean = Sanitize-Text $text
        $clean = $clean.Replace("\", "\\").Replace("(", "\(").Replace(")", "\)")
        $s = ("q {0} {1} {2} rg BT /{3} {4} Tf {5} {6} Td ({7}) Tj ET Q`n" -f (F $r 3), (F $g 3), (F $b 3), $font, (F $size 1), (F $x 2), (F $y 2), $clean)
        $this.currentStream.Append($s) | Out-Null
    }

    HeaderBanner([string]$title, [string]$subtitle, [string]$tag) {
        $this.CheckSpace(75)
        $w = $this.width - 2 * $this.marginX
        $h = 65.0
        $this.Rect($this.marginX, $this.y - $h, $w, $h, 0.12, 0.28, 0.55, $true, 0.08, 0.20, 0.40, 1.5)
        $this.Rect($this.marginX, $this.y - $h, 6, $h, 0.95, 0.65, 0.15, $false, 0, 0, 0, 1)

        $this.TextLine($this.marginX + 18, $this.y - 18, $tag.ToUpper(), "F2", 8.5, 0.92, 0.78, 0.35)
        $this.TextLine($this.marginX + 18, $this.y - 36, $title, "F2", 15.0, 1.0, 1.0, 1.0)
        $this.TextLine($this.marginX + 18, $this.y - 52, $subtitle, "F3", 9.5, 0.85, 0.90, 0.98)
        $this.y -= ($h + 16)
    }

    Heading1([string]$title) {
        $this.CheckSpace(45)
        $this.y -= 4
        $w = $this.width - 2 * $this.marginX
        $this.Rect($this.marginX, $this.y - 4, $w, 22, 0.92, 0.95, 0.99, $true, 0.15, 0.45, 0.82, 1.2)
        $this.Rect($this.marginX, $this.y - 4, 4, 22, 0.15, 0.45, 0.82, $false, 0, 0, 0, 1)
        $this.TextLine($this.marginX + 12, $this.y + 4, $title, "F2", 12.0, 0.10, 0.30, 0.65)
        $this.y -= 26
    }

    Heading2([string]$title) {
        $this.CheckSpace(32)
        $this.y -= 4
        $w = $this.width - 2 * $this.marginX
        $this.TextLine($this.marginX, $this.y, $title, "F2", 11.0, 0.15, 0.40, 0.75)
        $this.Rect($this.marginX, $this.y - 3, $w, 1, 0.80, 0.85, 0.92, $false, 0, 0, 0, 1)
        $this.y -= 14
    }

    Paragraph([string]$text) {
        $maxW = $this.width - 2 * $this.marginX
        $charsPerLine = [int]($maxW / 5.1)
        $words = $text.Split(' ')
        $lines = [System.Collections.Generic.List[string]]::new()
        $curLine = [System.Collections.Generic.List[string]]::new()
        $curLen = 0

        foreach ($w in $words) {
            if ($curLen + $w.Length + 1 -le $charsPerLine) {
                $curLine.Add($w)
                $curLen += $w.Length + 1
            } else {
                $lines.Add([string]::Join(" ", $curLine))
                $curLine.Clear()
                $curLine.Add($w)
                $curLen = $w.Length
            }
        }
        if ($curLine.Count -gt 0) {
            $lines.Add([string]::Join(" ", $curLine))
        }

        foreach ($line in $lines) {
            $this.CheckSpace(13.5)
            $this.TextLine($this.marginX, $this.y, $line, "F1", 9.5, 0.18, 0.18, 0.22)
            $this.y -= 13.5
        }
    }

    Bullet([string]$prefix, [string]$text) {
        $maxW = $this.width - 2 * $this.marginX - 18
        $charsPerLine = [int]($maxW / 5.1)
        $fullText = $prefix + ": " + $text
        $words = $fullText.Split(' ')
        $lines = [System.Collections.Generic.List[string]]::new()
        $cur = [System.Collections.Generic.List[string]]::new()
        $curL = 0

        foreach ($w in $words) {
            if ($curL + $w.Length + 1 -le $charsPerLine) {
                $cur.Add($w)
                $curL += $w.Length + 1
            } else {
                $lines.Add([string]::Join(" ", $cur))
                $cur.Clear()
                $cur.Add($w)
                $curL = $w.Length
            }
        }
        if ($cur.Count -gt 0) {
            $lines.Add([string]::Join(" ", $cur))
        }

        for ($i = 0; $i -lt $lines.Count; $i++) {
            $this.CheckSpace(13.0)
            if ($i -eq 0) {
                $this.TextLine($this.marginX + 4, $this.y, ">", "F2", 9.5, 0.15, 0.45, 0.82)
            }
            $this.TextLine($this.marginX + 16, $this.y, $lines[$i], "F1", 9.5, 0.15, 0.15, 0.20)
            $this.y -= 13.0
        }
    }

    NoteBox([string]$title, [string]$text) {
        $w = $this.width - 2 * $this.marginX
        $chars = [int](($w - 24) / 5.1)
        $words = $text.Split(' ')
        $lines = [System.Collections.Generic.List[string]]::new()
        $cur = [System.Collections.Generic.List[string]]::new()
        $curL = 0
        foreach ($wrd in $words) {
            if ($curL + $wrd.Length + 1 -le $chars) {
                $cur.Add($wrd)
                $curL += $wrd.Length + 1
            } else {
                $lines.Add([string]::Join(" ", $cur))
                $cur.Clear()
                $cur.Add($wrd)
                $curL = $wrd.Length
            }
        }
        if ($cur.Count -gt 0) {
            $lines.Add([string]::Join(" ", $cur))
        }

        $boxH = 24.0 + $lines.Count * 12.5
        $this.CheckSpace($boxH + 8)
        $this.Rect($this.marginX, $this.y - $boxH, $w, $boxH, 0.95, 0.98, 0.95, $true, 0.60, 0.80, 0.65, 1.0)
        $this.Rect($this.marginX, $this.y - $boxH, 4, $boxH, 0.20, 0.65, 0.35, $false, 0, 0, 0, 1)
        $this.TextLine($this.marginX + 12, $this.y - 14, $title, "F2", 9.5, 0.15, 0.50, 0.25)

        $yTxt = $this.y - 28
        foreach ($l in $lines) {
            $this.TextLine($this.marginX + 12, $yTxt, $l, "F1", 9.0, 0.15, 0.25, 0.18)
            $yTxt -= 12.5
        }
        $this.y -= ($boxH + 10)
    }

    CardBox([string]$varName, [string]$codeLoc, [string]$value, [string]$meaning, [string]$intuition) {
        $cardW = $this.width - 2 * $this.marginX
        $charsW = [int](($cardW - 95) / 5.0)

        $wordsM = $meaning.Split(' ')
        $mLines = [System.Collections.Generic.List[string]]::new()
        $cur = [System.Collections.Generic.List[string]]::new()
        $curL = 0
        foreach ($w in $wordsM) {
            if ($curL + $w.Length + 1 -le $charsW) {
                $cur.Add($w)
                $curL += $w.Length + 1
            } else {
                $mLines.Add([string]::Join(" ", $cur))
                $cur.Clear()
                $cur.Add($w)
                $curL = $w.Length
            }
        }
        if ($cur.Count -gt 0) { $mLines.Add([string]::Join(" ", $cur)) }

        $wordsI = $intuition.Split(' ')
        $iLines = [System.Collections.Generic.List[string]]::new()
        $cur = [System.Collections.Generic.List[string]]::new()
        $curL = 0
        foreach ($w in $wordsI) {
            if ($curL + $w.Length + 1 -le $charsW) {
                $cur.Add($w)
                $curL += $w.Length + 1
            } else {
                $iLines.Add([string]::Join(" ", $cur))
                $cur.Clear()
                $cur.Add($w)
                $curL = $w.Length
            }
        }
        if ($cur.Count -gt 0) { $iLines.Add([string]::Join(" ", $cur)) }

        $cardH = 24.0 + $mLines.Count * 12.0 + $iLines.Count * 12.0 + 10.0
        $this.CheckSpace($cardH + 8)

        $this.Rect($this.marginX, $this.y - $cardH, $cardW, $cardH, 0.97, 0.98, 0.99, $true, 0.85, 0.88, 0.92, 1.0)
        $this.Rect($this.marginX, $this.y - $cardH, 4, $cardH, 0.15, 0.45, 0.82, $false, 0, 0, 0, 1)

        $this.TextLine($this.marginX + 12, $this.y - 13, $varName, "F2", 10.0, 0.10, 0.35, 0.70)
        $this.TextLine($this.marginX + 210, $this.y - 13, ("Local: " + $codeLoc), "F3", 8.5, 0.45, 0.45, 0.50)
        $this.TextLine($this.marginX + 370, $this.y - 13, ("Valor: " + $value), "F2", 8.5, 0.18, 0.52, 0.28)

        $currY = $this.y - 26
        $this.TextLine($this.marginX + 12, $currY, "Significado:", "F2", 8.8, 0.25, 0.25, 0.30)
        foreach ($ml in $mLines) {
            $this.TextLine($this.marginX + 85, $currY, $ml, "F1", 8.8, 0.15, 0.15, 0.18)
            $currY -= 12.0
        }

        $this.TextLine($this.marginX + 12, $currY, "Como Explicar:", "F2", 8.8, 0.80, 0.35, 0.10)
        foreach ($il in $iLines) {
            $this.TextLine($this.marginX + 85, $currY, $il, "F1", 8.8, 0.20, 0.20, 0.25)
            $currY -= 12.0
        }

        $this.y -= ($cardH + 7)
    }

    Save([string]$filePath) {
        if ($this.currentStream.Length -gt 0) {
            $this.pages.Add($this.currentStream.ToString())
            $this.currentStream.Clear()
        }

        $totalPages = $this.pages.Count
        $finalPages = [System.Collections.Generic.List[string]]::new()
        for ($i = 0; $i -lt $totalPages; $i++) {
            $footerText = ("Pagina {0} de {1}   |   Guia Didatico de Computacao Grafica: Iluminacao e Sombra" -f ($i + 1), $totalPages)
            $footerS = ("q 0.450 0.450 0.500 rg BT /F1 8.0 Tf {0} 20.00 Td ({1}) Tj ET Q`n" -f (F $this.marginX 2), $footerText)
            $lineS = ("q 0.850 0.870 0.900 RG 0.50 w {0} 32.00 m {1} 32.00 l S Q`n" -f (F $this.marginX 2), (F ($this.width - $this.marginX) 2))
            $finalPages.Add($this.pages[$i] + $lineS + $footerS)
        }

        $numPages = $finalPages.Count
        $catalog = "<< /Type /Catalog /Pages 2 0 R >>"
        $kidsList = [System.Collections.Generic.List[string]]::new()
        for ($i = 0; $i -lt $numPages; $i++) {
            $kidsList.Add(("{0} 0 R" -f (3 + $i)))
        }
        $pagesObj = ("<< /Type /Pages /Kids [{0}] /Count {1} >>" -f [string]::Join(" ", $kidsList), $numPages)

        $pageObjs = [System.Collections.Generic.List[string]]::new()
        $font1Id = 3 + 2 * $numPages
        $font2Id = $font1Id + 1
        $font3Id = $font2Id + 1

        for ($i = 0; $i -lt $numPages; $i++) {
            $cId = 3 + $numPages + $i
            $p = ("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {0} {1}] /Contents {2} 0 R /Resources << /Font << /F1 {3} 0 R /F2 {4} 0 R /F3 {5} 0 R >> >> >>" -f (F $this.width 2), (F $this.height 2), $cId, $font1Id, $font2Id, $font3Id)
            $pageObjs.Add($p)
        }

        $streamObjs = [System.Collections.Generic.List[string]]::new()
        $enc = [System.Text.Encoding]::GetEncoding("ISO-8859-1")
        for ($i = 0; $i -lt $numPages; $i++) {
            $rawBytes = $enc.GetBytes($finalPages[$i])
            $st = ("<< /Length {0} >>`nstream`n{1}endstream" -f $rawBytes.Length, $finalPages[$i])
            $streamObjs.Add($st)
        }

        $font1 = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
        $font2 = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"
        $font3 = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique /Encoding /WinAnsiEncoding >>"

        $allObjs = [System.Collections.Generic.List[string]]::new()
        $allObjs.Add($catalog)
        $allObjs.Add($pagesObj)
        foreach ($p in $pageObjs) { $allObjs.Add($p) }
        foreach ($s in $streamObjs) { $allObjs.Add($s) }
        $allObjs.Add($font1)
        $allObjs.Add($font2)
        $allObjs.Add($font3)

        $fs = [System.IO.File]::Create($filePath)
        $header = $enc.GetBytes("%PDF-1.4`n")
        $fs.Write($header, 0, $header.Length)

        $offsets = [System.Collections.Generic.List[long]]::new()
        for ($i = 0; $i -lt $allObjs.Count; $i++) {
            $objId = $i + 1
            $offsets.Add($fs.Position)
            $pre = $enc.GetBytes(("{0} 0 obj`n" -f $objId))
            $fs.Write($pre, 0, $pre.Length)
            $data = $enc.GetBytes($allObjs[$i])
            $fs.Write($data, 0, $data.Length)
            $post = $enc.GetBytes("`nendobj`n")
            $fs.Write($post, 0, $post.Length)
        }

        $xrefStart = $fs.Position
        $xrefHeader = $enc.GetBytes(("xref`n0 {0}`n0000000000 65535 f `n" -f ($allObjs.Count + 1)))
        $fs.Write($xrefHeader, 0, $xrefHeader.Length)

        foreach ($off in $offsets) {
            $entry = $enc.GetBytes(("{0:D10} 00000 n `n" -f $off))
            $fs.Write($entry, 0, $entry.Length)
        }

        $trailer = $enc.GetBytes(("trailer`n<< /Size {0} /Root 1 0 R >>`nstartxref`n{1}`n%%EOF`n" -f ($allObjs.Count + 1), $xrefStart))
        $fs.Write($trailer, 0, $trailer.Length)
        $fs.Close()
    }
}

$pdfPath = "c:\Users\caeta\OneDrive\Desktop\codiguin\sprint2\sprint2\Guia_Iluminacao_e_Sombra.pdf"
$doc = [PDFBuilder]::new()
$doc.NewPage()

# ==================== PAGINA 1 ====================
$doc.HeaderBanner(
    "Iluminacao e Sombra em Computacao Grafica",
    "Dicionario Didatico de Variaveis, Matematica Intuitiva e Roteiro de Explicacao",
    "Sprint 2 - Projeto 3D OpenGL e Python"
)

$doc.Heading1("1. Visao Geral: O Desafio da Luz e da Sombra em 3D")
$doc.Paragraph("Em Computacao Grafica, uma tela de computador e estritamente bidimensional (2D). Quando renderizamos modelos 3D apenas com cores ou texturas puras, os objetos parecem figuras de papel ou desenhos planos. Nao da para distinguir onde comeca ou termina uma aresta ou se uma face esta inclinada.")
$doc.y -= 4
$doc.Paragraph("A Iluminacao e a Sombra sao as duas principais pistas visuais que o cerebro humano usa para deduzir profundidade, volume e contato fisico com o chao. Neste projeto, implementamos uma solucao elegante e compacta ideal para o nivel junior: um modelo de Iluminacao Difusa Direcional (Lambert) somado a uma Luz Ambiente, com funcoes proprias de algebra linear e Sombras Planar Projetadas baseadas na propria malha 3D.")
$doc.y -= 6

$doc.NoteBox(
    "Regra de Ouro da Computacao Grafica Junior",
    "O CPU (Python) cuida da logica, das posicoes e envia ordens. A GPU (Placa de Video e Shaders GLSL) executa os calculos de iluminacao em paralelo para cada pixel desenhado na tela!"
)

$doc.Heading1("2. Dicionario de Variaveis e Funcoes: O Que Cada Uma Faz?")
$doc.Paragraph("Abaixo estao detalhadas todas as variaveis e funcoes manuais criadas no projeto, seus valores e como explica-las com naturalidade:")
$doc.y -= 4

$doc.CardBox(
    "usarLuz (Uniform booleano)",
    "mode3D.py / fragmentShad.glsl",
    "1 (3D) ou 0 (2D)",
    "Interruptor que avisa a GPU se o que esta sendo desenhado agora deve receber calculo de luz ou ser desenhado com cor pura.",
    "Pense no interruptor de um quarto. No mundo 3D queremos luz ligada (1). Ja para desenhar o menu 2D e icones da barra lateral, desligamos a luz (0) para que os botoes fiquem sempre nitidos e legiveis."
)

$doc.CardBox(
    "lightDir (vec3)",
    "mode3D.py (0.5, 1.0, 0.4)",
    "X=0.5, Y=1.0, Z=0.4",
    "Vetor tridimensional que define a direcao de onde vem a luz direta (como os raios do Sol).",
    "Imagine que colocamos o Sol no ceu: Y=1.0 significa bem do alto, X=0.5 um pouco a direita, e Z=0.4 um pouco a frente. Isso cria um contraste bonito em 3 lados de qualquer caixa."
)

$doc.CardBox(
    "lightColor (vec3)",
    "mode3D.py (0.85, 0.85, 0.80)",
    "R=0.85, G=0.85, B=0.80",
    "Cor e intensidade da luz direta do Sol que atinge os objetos.",
    "Valores vao de 0.0 (preto) a 1.0 (branco maximo). Escolhemos 0.85 com azul um pouco menor (0.80), gerando uma luz levemente amarelada e quente como a luz solar suave do meio da manha."
)

$doc.CardBox(
    "ambientColor (vec3)",
    "mode3D.py (0.45, 0.45, 0.50)",
    "R=0.45, G=0.45, B=0.50",
    "Luz ambiente indireta, que simula a luz que rebate nas paredes, no chao e no ceu da sala.",
    "Sem luz ambiente, as partes dos objetos viradas de costas para o Sol ficariam pretas como breu! A luz ambiente garante que o lado de tras continue visivel com 45% de claridade suave."
)

# ==================== PAGINA 2 ====================
$doc.NewPage()
$doc.Heading2("Dicionario de Variaveis e Funcoes (Continuacao)")

$doc.CardBox(
    "calcularNormal(vec3 A, vec3 B)",
    "fragmentShad.glsl",
    "A x B (Produto Vetorial)",
    "Funcao manual que substitui o cross do GLSL. Multiplica componentes cruzados e retorna um vetor perpendicular a A e B.",
    "Calcula a perpendicular exata entre duas tangentes da face: vec3(A.y*B.z - A.z*B.y, A.z*B.x - A.x*B.z, A.x*B.y - A.y*B.x). Mostra dominio real da algebra linear sem depender de funcoes prontas!"
)

$doc.CardBox(
    "calcularIluminacao(vec3 A, vec3 B)",
    "fragmentShad.glsl",
    "A . B (Produto Escalar)",
    "Funcao manual que substitui o dot do GLSL. Multiplica cada coordenada correspondente e soma tudo: A.x*B.x + A.y*B.y + A.z*B.z.",
    "Retorna um unico numero que mede o quanto dois vetores apontam na mesma direcao. Usado tanto para testar visibilidade com a camera quanto para calcular o brilho da luz!"
)

$doc.CardBox(
    "normalizarVetor(vec3 A)",
    "fragmentShad.glsl",
    "A / comprimento",
    "Funcao manual que substitui o normalize do GLSL. Calcula o tamanho por Pitagoras 3D sqrt(x^2 + y^2 + z^2) e divide o vetor por ele.",
    "Garante que o vetor tenha tamanho exatamente 1.0 (vetor unitario). Conta com protecao contra divisao por zero (comprimento < 0.000001) para nao travar a GPU!"
)

$doc.CardBox(
    "N (Normal da Superficie)",
    "fragmentShad.glsl",
    "normalizarVetor(calcularNormal(...))",
    "Vetor perpendicular a superficie, como uma flecha apontando para fora da parede ou face do cubo.",
    "Imagine um prego perpendicular espetado na madeira. Se o prego aponta para o teto, a face e horizontal. Se aponta para a direita, e uma parede lateral. E a bussola de cada face!"
)

$doc.CardBox(
    "L (Vetor da Luz Normalizado)",
    "fragmentShad.glsl",
    "normalizarVetor(lightDir)",
    "O vetor apontando em direcao ao Sol com comprimento matematico obrigatoriamente igual a 1.",
    "Reduzimos a forca da seta para exatamente 1 unidade de comprimento, para que ela guarde apenas a DIRECAO da luz, sem distorcer as contas de brilho."
)

$doc.CardBox(
    "diff (Fator Difuso / Brilho)",
    "fragmentShad.glsl",
    "max(calcularIluminacao(N, L), 0.0)",
    "Numero entre 0.0 e 1.0 que diz quanta luz do Sol a superficie recebe pelo seu angulo de inclinacao.",
    "E a famosa Lei do Cosseno de Lambert: se a face aponta de frente para a luz, diff=1.0 (brilho maximo). Se estiver de lado, diff cai. Se estiver de costas, fica zero (sombra)."
)

$doc.CardBox(
    "isSombra (Uniform booleano)",
    "mode3D.py / fragmentShad.glsl",
    "1 (renderizando sombra) ou 0",
    "Informa ao fragment shader que nao e para pintar o modelo com texturas, mas sim como uma silhueta escura translucida.",
    "Quando ativado, o shader ignora madeira e texturas e cospe a cor vec4(0.06, 0.06, 0.10, 0.45): um azul-marinho bem escuro com 45% de opacidade (55% transparente)."
)

$doc.CardBox(
    "ALTURA_ELEVACAO (float)",
    "main.py",
    "0.25 (unidades do mundo)",
    "Distancia vertical fixa que o objeto levita no ar quando o usuario clica e comeca a arrasta-lo com o mouse.",
    "Quando pegamos uma caixa no chao do mundo real, nos a erguemos. Elevar 0.25 unidades faz o objeto descolar do chao e revela a sombra embaixo dele, dando sensacao tatil de arrasto 3D."
)

$doc.CardBox(
    "alturaApoio (float)",
    "main.py / mode3D.py",
    "0.0 (chao) ou 1.15 (mesa/bancada)",
    "Altura da superficie mais proxima logo abaixo do objeto onde a sombra deve ser carimbada e onde ele vai pousar.",
    "Se a caixa estiver no chao, a sombra fica no chao (Y=0.0). Se estiver em cima da bancada, a sombra sobe para o tampo da mesa (Y=1.15). A sombra nunca afunda no vazio."
)

$doc.CardBox(
    "S.y = 0.0001 (Matriz de Escala)",
    "mode3D.py (renderSombra)",
    "glm.scale(1.0, 0.0001, 1.0)",
    "Fator de escala no eixo Y que achata a malha 3D completa do objeto contra o chao.",
    "A analogia do rolo compressor: pegamos o modelo 3D original e esmagamos sua altura ate virar uma folha quase plana. Assim, a sombra tem exatamente o formato do objeto!"
)

# ==================== PAGINA 3 ====================
$doc.NewPage()
$doc.Heading1("3. A Matematica Explicada Sem Segredos e Sem Jargoes")
$doc.Paragraph("Muitas pessoas travam quando ouvem palavras como vetores, produto escalar ou derivadas parciais. Mas a intuicao por tras e incrivelmente simples quando usamos analogias do mundo real:")
$doc.y -= 4

$doc.Heading2("A. O que e um Vetor e a Funcao normalizarVetor(A)")
$doc.Paragraph("Em Computacao Grafica, um vetor tridimensional vec3(x, y, z) nada mais e do que uma FLECHA que sai da origem e aponta para algum lugar no espaco. Ela possui uma DIRECAO e um COMPRIMENTO (tamanho da flecha).")
$doc.y -= 2
$doc.Paragraph("Quando queremos saber apenas para onde o Sol esta apontando, o tamanho da flecha atrapalha as multiplicacoes. A nossa funcao normalizarVetor divide a flecha pelo seu proprio tamanho sqrt(x^2 + y^2 + z^2). O resultado e garantidamente um vetor de tamanho 1.0 (Unitario), com trava contra divisao por zero!")
$doc.y -= 6

$doc.Heading2("B. A Normal da Superficie e a Funcao calcularNormal(A, B)")
$doc.Paragraph("Para saber se uma parede esta recebendo sol, a GPU precisa saber para onde aquela parede esta olhando (Vetor Normal N). Pense em um prego apontando 90 graus para fora da madeira.")
$doc.y -= 2
$doc.Paragraph("Ao inves de usar o built-in cross, criamos a funcao calcularNormal(A, B) que aplica a formula classica do Produto Vetorial: multiplicamos cruzadamente os eixos Y e Z, Z e X, X e Y. O resultado e garantidamente uma seta perpendicular a face!")
$doc.y -= 4

$doc.NoteBox(
    "O Truque de Mestre: dFdx e dFdy (Sem precisar criar buffers de normais)",
    "Em codigos mais antigos e pesados, o programador precisava cadastrar a normal de cada vertice na mao. No nosso projeto moderno, usamos dFdx(worldPos) e dFdy(worldPos). A GPU compara a posicao no espaco de pixels vizinhos na tela e passa para a nossa funcao calcularNormal, descobrindo o relevo instantaneamente!"
)
$doc.y -= 6

$doc.Heading2("C. Produto Escalar com a Funcao calcularIluminacao(A, B)")
$doc.Paragraph("Como a GPU calcula o brilho diff = max(calcularIluminacao(N, L), 0.0)? Essa e a famosa Lei de Lambert e pode ser explicada assim:")
$doc.y -= 2
$doc.Bullet("Luz de Frente (Angulo 0 graus)", "Aponte uma lanterna reta contra a parede. O facho fica concentrado em um circulo pequeno e ultra brilhante. O produto escalar entre N e L vale 1.0 (brilho maximo).")
$doc.Bullet("Luz Inclinada (Angulo 45 a 60 graus)", "Incline a lanterna. O circulo de luz se espalha em uma elipse maior e a parede fica menos brilhante. O produto escalar diminui para algo entre 0.7 e 0.3.")
$doc.Bullet("Luz Rasante ou de Costas (90 a 180 graus)", "Se a luz vier de lado ou por tras da parede, nenhuma luz atinge a face frontal. A nossa funcao calcularIluminacao daria zero ou um numero negativo. O comando max(..., 0.0) impede que o brilho fique negativo e crava em 0.0 (lado de sombra).")
$doc.y -= 4

$doc.Heading2("D. A Equacao Final de Iluminacao do Pixel")
$doc.Paragraph("A cor de cada ponto no nosso shader e calculada por uma formula simples de adicao e multiplicacao:")
$doc.y -= 2
$doc.Bullet("Luz Total", "corFinal = (ambientColor + lightColor * diff) * texColor")
$doc.Bullet("Em bom portugues", "Pegamos a claridade minima que nunca zera (ambientColor), somamos com a luz do Sol proporcional ao angulo (lightColor * diff), e multiplicamos o resultado pela cor da textura da madeira ou da caixa. Resultado: faces iluminadas ganham vida e faces opostas ganham sombra suave!")

# ==================== PAGINA 4 ====================
$doc.NewPage()
$doc.Heading1("4. O Mecanismo de Sombra Planar Projetada e Elevacao")
$doc.Paragraph("Criar sombras em Computacao Grafica pode ser um dos topicos mais complexos (como Shadow Mapping com buffers de profundidade). Para o nosso projeto, escolhemos a tecnica de Sombra Planar Projetada, que e elegante, extremamente eficiente e visualmente impecavel.")
$doc.y -= 4

$doc.Heading2("A. Como funciona o Carimbo da Sombra?")
$doc.Bullet("1. Mesma Geometria", "Ao inves de tentar desenhar um circulo generico, pegamos o proprio modelo 3D do objeto (com todos os seus triangulos e curvas).")
$doc.Bullet("2. O Rolo Compressor (Escala Y = 0.0001)", "Aplicamos uma matriz de escala que reduz a altura do modelo a quase zero. O objeto 3D vira uma estampa plana encostada no solo.")
$doc.Bullet("3. Silhueta Escura (isSombra = 1)", "Mandamos o shader desenhar essa estampa com cor azul-escura suave e 45% de opacidade, com blend transparente ativado (glBlendFunc).")
$doc.Bullet("4. Anti Z-Fighting (+0.005)", "Posicionamos a sombra 5 milimetros acima do chao real (yChao + 0.005). Isso impede que a sombra e o piso disputem o mesmo pixel na tela (efeito de piscar).")
$doc.y -= 6

$doc.Heading2("B. O Efeito de Elevacao Visual (ALTURA_ELEVACAO = 0.25)")
$doc.Paragraph("Quando o usuario clica e arrasta um objeto pelo cenario, somamos 0.25 unidades na sua posicao Y. O objeto sobe no ar, enquanto a sombra continua projetada perfeitamente no chao ou no tampo da mesa (alturaApoio). Isso cria um efeito visual fantastico: a pessoa que joga tem a certeza absoluta de que pegou o item no colo e sabe exatamente em qual ponto do chao ele vai aterrissar quando soltar o botao do mouse!")
$doc.y -= 8

$doc.Heading1("5. Roteiro Pratico para Apresentar aos Colegas (2 Minutos)")
$doc.Paragraph("Use este passo a passo caso va demonstrar o projeto em sala de aula ou em reuniao de equipe:")
$doc.y -= 4

$doc.Bullet("Passo 1 (Introducao)", "Reparem como o cenario 3D ganha volume quando as faces recebem luz de acordo com a sua inclinacao em relacao ao Sol virtual.")
$doc.Bullet("Passo 2 (Luz Ambiente vs Sol)", "Usamos duas luzes: uma luz ambiente suave (para as costas dos moveis nao ficarem pretas) e uma luz solar direcional calculada em tempo real na GPU pela Lei de Lambert.")
$doc.Bullet("Passo 3 (Funcoes Proprias)", "Ao inves de usar funcoes prontas da GPU, escrevemos nossas proprias funcoes calcularNormal (produto vetorial), calcularIluminacao (produto escalar) e normalizarVetor (modulo unitario) para demonstrar a matematica pura.")
$doc.Bullet("Passo 4 (Demonstracao do Arrasto)", "Ao clicar e arrastar qualquer objeto da mesa, vejam que ele levita um pouco (ALTURA_ELEVACAO = 0.25). Imediatamente vemos a sombra projetada no chao com o formato exato da peca!")
$doc.Bullet("Passo 5 (Conclusao Tecnica)", "A sombra usa a tecnica planar projetada com matriz de escala Y minima, e a iluminacao calcula normais por derivadas de tela com nossa funcao manual, mantendo o codigo leve, limpo e profissional.")
$doc.y -= 8

$doc.NoteBox(
    "Resumo Final em Uma Frase",
    "A iluminacao diz para o olho onde a peca esta virada; a sombra diz para o olho onde a peca esta pisando!"
)

$doc.Save($pdfPath)
Write-Host "PDF gerado com sucesso em: $pdfPath"
Write-Host "Total de paginas: $($doc.pages.Count)"
