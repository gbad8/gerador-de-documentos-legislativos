# Modulos utilizados
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_JUSTIFY, TA_CENTER
from reportlab.lib.units import cm
import os

# --- REGISTRO DE FONTES UTF-8 ---
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

base_dir = os.path.dirname(os.path.abspath(__file__))
fonts_path = os.path.join(base_dir, "fonts")

try:
    pdfmetrics.registerFont(TTFont('Times', os.path.join(fonts_path, 'times.ttf')))
    pdfmetrics.registerFont(TTFont('Times-Bold', os.path.join(fonts_path, 'timesbd.ttf')))
    pdfmetrics.registerFont(TTFont('Times-Italic', os.path.join(fonts_path, 'timesi.ttf')))
    pdfmetrics.registerFont(TTFont('Times-BoldItalic', os.path.join(fonts_path, 'timesbi.ttf')))
    pdfmetrics.registerFontFamily('Times', normal='Times', bold='Times-Bold', italic='Times-Italic', boldItalic='Times-BoldItalic')
    FONT_NAME = "Times"
except Exception as e:
    print(f"AVISO: Fontes TTF não encontradas. Usando fonte padrão. Erro: {e}")
    FONT_NAME = "Times-Roman"


# --- ESTILOS ---
styles = getSampleStyleSheet()
normal_justificado = ParagraphStyle("NormalJustificado", parent=styles["Normal"], fontName=FONT_NAME, alignment=TA_JUSTIFY, fontSize=12, leading=14)
normal_centralizado = ParagraphStyle("NormalCentralizado", parent=styles["Normal"], fontName=FONT_NAME, alignment=TA_CENTER, fontSize=12, leading=14)
right_aligned_style = ParagraphStyle('RightAligned', parent=styles['Normal'], fontName=FONT_NAME, fontSize=12, alignment=TA_RIGHT)

# Variaveis de dimensão
altura_pagina = A4[1]
largura_pagina = A4[0]

# Dicionário para buscar o cargo do autor
VEREADORES = {
    "Josemar Rodrigues da Silva":       {"titulo": "Presidente da Câmara Municipal", "genero": "M"},
    "José Givanildo de Sousa Matias":   {"titulo": "Vice-Presidente da Mesa Diretora", "genero": "M"},
    "Ricardo Viana Matos":              {"titulo": "1º Secretário da Mesa Diretora", "genero": "M"},
    "Maria José Ferreira de Sousa":     {"titulo": "2ª Secretária da Mesa Diretora", "genero": "F"},
    "Alione Farias de Almeida":         {"titulo": "Vereadora", "genero": "F"},
    "Elson Gomes da Silva":             {"titulo": "Vereador", "genero": "M"},
    "Isac Soares de Araújo":            {"titulo": "Vereador", "genero": "M"},
    "João Fredson Alves de Carvalho":   {"titulo": "Vereador", "genero": "M"},
    "Manoel Ferreira da Silva":         {"titulo": "Vereador", "genero": "M"},
    "Jorge Vieira dos Santos Filho":    {"titulo": "Prefeito Municipal", "genero": "M"}
}

# --- FUNÇÃO AUXILIAR ---
def definir_tratamento(cargo):
    """Define o vocativo correto com base no cargo."""
    cargo_lower = cargo.lower()
    
    # Listas de palavras-chave
    cargos_excelentissimo = [
        'prefeito', 'prefeita', 'governador', 'governadora', 'presidente', 
        'juiz', 'juíza', 'deputado', 'deputada', 'senador', 'senadora', 
        'ministro', 'ministra', 'secretário', 'secretária'
    ]
    palavras_femininas = [
        'prefeita', 'governadora', 'presidenta', 'juíza', 'deputada', 
        'senadora', 'ministra', 'secretária', 'vereadora', 'diretora', 'gerente'
    ]

    is_excelentissimo = any(termo in cargo_lower for termo in cargos_excelentissimo)
    is_feminino = any(termo in cargo_lower for termo in palavras_femininas)

    # Constrói o vocativo correto
    if is_excelentissimo:
        if is_feminino:
            return "Excelentíssima Senhora"
        else:
            return "Excelentíssimo Senhor"
    else:  # Ilustríssimo
        if is_feminino:
            return "Ilustríssima Senhora"
        else:
            return "Ilustríssimo Senhor"

# Cabeçalho e Rodapé
def cabecalho(canvas, doc):
    canvas.saveState()
    largura_imagem = 50
    altura_imagem = 50
    x = (largura_pagina - largura_imagem) / 2
    y = 753
    caminho_logo = os.path.join(base_dir, "static", "img", "logo.png")
    if os.path.exists(caminho_logo):
        canvas.drawImage(caminho_logo, x, y, width=largura_imagem, height=altura_imagem, preserveAspectRatio=True, mask='auto')
    canvas.setFont('Times-Bold', 10)
    canvas.drawCentredString(largura_pagina / 2, y - 20, "ESTADO DO MARANHÃO")
    canvas.drawCentredString(largura_pagina / 2, y - 32, "PODER LEGISLATIVO")
    canvas.drawCentredString(largura_pagina / 2, y - 44, "CÂMARA MUNICIPAL DE VILA NOVA DOS MARTÍRIOS")
    canvas.setLineWidth(0.5)
    ultima_altura = y - 20 - 32
    canvas.line(90, ultima_altura, largura_pagina - 90, ultima_altura)
    canvas.restoreState()

def rodape(canvas, doc):
    canvas.saveState()
    canvas.setLineWidth(0.5)
    canvas.line(90, 64, largura_pagina - 90, 64)
    canvas.setFont("Times-Bold", 7.7)
    canvas.drawCentredString(largura_pagina / 2, 50, "Av. Rio Branco s/nº Centro, CEP: 65.924-000.")
    canvas.drawCentredString(largura_pagina / 2, 38, "https://www.cmvilanovadosmartirios.ma.gov.br/")
    canvas.drawCentredString(largura_pagina / 2, 26, "Email: cmvnmartirios@hotmail.com")
    canvas.restoreState()

def cabecalho_rodape(canvas, doc):
    cabecalho(canvas, doc)
    rodape(canvas, doc)

# Função principal
def gerar_oficio_livre(dados, nome_arquivo):
    doc = BaseDocTemplate(nome_arquivo, pagesize=A4)
    frame = Frame(85, 80, largura_pagina - 170, altura_pagina - 230, id='normal')
    doc.addPageTemplates([PageTemplate(id='modelo', frames=frame, onPage=cabecalho_rodape)])

    story = []

    # Preâmbulo
    story.append(Paragraph(f"<b>{dados['orgao']}</b>", right_aligned_style))
    story.append(Paragraph(f"<b>Ofício n° {dados['numero']}/{dados['ano']}</b>", normal_justificado))
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph(f"Vila Nova dos Martírios, {dados['data']}.", right_aligned_style))
    story.append(Spacer(1, 1.5 * cm))

    # Destinatário
    tratamento = definir_tratamento(dados['cargo'])
    story.append(Paragraph(tratamento, normal_justificado))
    story.append(Paragraph(f"<b>{dados['destinatario']}</b>", normal_justificado))
    story.append(Paragraph(f"<i>{dados['cargo']}</i>", normal_justificado))
    story.append(Spacer(1, 1.5 * cm))

    # Assunto
    story.append(Paragraph(f"<b>ASSUNTO: {dados['assunto'].upper()}</b>", normal_justificado))
    story.append(Spacer(1, 1 * cm))

    # Corpo do Ofício
    corpo_formatado = dados['corpo_oficio'].replace('\r\n', '<br/>').replace('\n', '<br/>')
    story.append(Paragraph(corpo_formatado, normal_justificado))
    story.append(Spacer(1, 1.5 * cm))

    # Desfecho
    story.append(Paragraph("Atenciosamente,", normal_centralizado))
    story.append(Spacer(1, 1.5 * cm))

    # Assinatura
    autores = dados.get('autores_selecionados', [])
    if not autores: # Se não for conjunta, usa o autor único
        autor_unico = dados.get('vereador')
        if autor_unico:
            autores = [autor_unico]

    linha_assinatura = Paragraph('_' * 45, normal_centralizado)

    for nome in autores:
        info_autor = VEREADORES.get(nome, {"titulo": "Vereador(a)"})
        cargo_autor = info_autor.get("titulo")

        bloco_assinatura = KeepTogether([
            linha_assinatura,
            Paragraph(f"<b>{nome}</b>", normal_centralizado),
            Paragraph(f"<i>{cargo_autor}</i>", normal_centralizado),
            Spacer(1, 1.5 * cm) # Espaço entre assinaturas
        ])
        story.append(bloco_assinatura)
        
    doc.build(story)


