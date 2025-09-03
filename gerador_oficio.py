# Modulos utilizados
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_JUSTIFY, TA_CENTER #constante para alinhamento à direita
from reportlab.lib.units import cm
from reportlab.graphics.shapes import Drawing, Line

# Estilos personalizados para o documento
styles = getSampleStyleSheet()

normal_justificado = ParagraphStyle(
    "NormalJustificado",
    parent=styles["Normal"],
    fontName="Times-Roman",
    alignment=TA_JUSTIFY,
    fontSize=12,
    leading=14
)

normal_centralizado = ParagraphStyle(
    "NormalCentralizado",
    parent=styles["Normal"],
    fontName="Times-Roman",
    alignment=TA_CENTER,
    fontSize=12,
    leading=14
)

right_aligned_style = ParagraphStyle(
    'RightAligned',
    parent=styles['Normal'],
    fontName="Times-Roman",
    fontSize=12,
    alignment=TA_RIGHT
)

# Variaveis de dimensão do papel A4
altura_pagina = A4[1]
largura_pagina = A4[0]

# Cabeçalho
def cabecalho(canvas, doc):
    canvas.saveState()

    # Variáveis  para a logo
    largura_imagem = 50
    altura_imagem = 50
    x = (largura_pagina - largura_imagem) / 2
    y = 753

    # Logo
    canvas.drawImage("static/img/logo.png", x, y, width=largura_imagem, height=altura_imagem, preserveAspectRatio=True, mask='auto')

    # Texto
    canvas.setFont('Times-Bold', 10)
    canvas.drawCentredString(largura_pagina / 2, y - 20, "ESTADO DO MARANHÃO")
    canvas.drawCentredString(largura_pagina / 2, y - 32, "PODER LEGISLATIVO")
    canvas.drawCentredString(largura_pagina / 2, y - 44, "CÂMARA MUNICIPAL DE VILA NOVA DOS MARTÍRIOS")

    # Linha divisória
    canvas.setLineWidth(0.5)
    ultima_altura = y - 20 - 32
    canvas.line(90, ultima_altura, largura_pagina - 90, ultima_altura)
    
    canvas.restoreState()

# Rodapé
def rodape(canvas, doc):
    canvas.saveState()
    
    canvas.setLineWidth(0.5)
    canvas.line(90, 64, largura_pagina - 90, 64)
    canvas.setFont("Times-Bold", 7.7)
    canvas.drawCentredString(largura_pagina / 2, 50, "Av. Rio Branco s/nº Centro, CEP: 65.924-000.")
    canvas.drawCentredString(largura_pagina / 2, 38, "https://www.cmvilanovadosmartirios.ma.gov.br/")
    canvas.drawCentredString(largura_pagina / 2, 26, "Email: cmvnmartirios@hotmail.com")
    canvas.restoreState()

# Junta Cabeçalho e Rodapé em uma única função
def cabecalho_rodape(canvas, doc):
    cabecalho(canvas, doc)
    rodape(canvas, doc)

# Função principal para gerar o ofício
def gerar_oficio(dados, nome_arquivo):
    
    # Definição do documento
    doc = BaseDocTemplate(nome_arquivo, pagesize=A4) 

    # Área útil do texto
    frame = Frame(85,80, largura_pagina - 170, altura_pagina - 230, id='normal')

    # Template de página com cabeçalho
    doc.addPageTemplates([
        PageTemplate(id='modelo', frames=frame, onPage=cabecalho_rodape)
    ])


    # Preâmbulo
    story = []
    story.append(Paragraph("<b>Secretaria Legislativa</b>", right_aligned_style)) # Órgão
    story.append(Paragraph(f"<b>Ofício n° {dados['numero']}/{dados['ano']}</b>", normal_justificado)) # Nome da correspondência
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph(f"Vila Nova dos Martírios, {dados['data']}.", right_aligned_style)) # Local e data
    story.append(Spacer(1, 1 * cm))

    # Destinatário
    story.append(Paragraph("Ao Exmo. Prefeito Municipal", normal_justificado))
    story.append(Paragraph("Sr. Jorge Vieira dos Santos Filho", normal_justificado))
    story.append(Spacer(1, 1.5 * cm))

    # Assunto
    story.append(Paragraph(f"<b>ASSUNTO: {dados['assunto'].upper()}</b>", normal_justificado))
    story.append(Spacer(1, 1 * cm))

    # Verifica a quantidade de autores para definir o termo correto
    autores = dados.get('autores_selecionados', [])
    if len(autores) > 1:
        # A variável 'proposicao' do formulário é usada como base
        tipo_proposicao = f"{dados['proposicao']} Conjunta"
    else:
        tipo_proposicao = dados['proposicao']

    corpo_texto = f"""
        A Câmara Municipal de Vereadores de Vila Nova dos Martírios - MA, por meio de seu Presidente,
        Josemar Rodrigues da Silva, vem, mui respeitosamente, encaminhar à Prefeitura a cópia 
        {tipo_proposicao} n° {dados['n-indicacao']}/{dados['ano']}, de autoria {dados['vereador']}.
        A referida proposição foi aprovada por {dados['resultado']} nesta Casa Legislativa,
        na {dados['sessao']}, realizada em {dados['data']}.
    """

    story.append(Paragraph(corpo_texto, normal_justificado))
    story.append(Spacer(1, 1 * cm))

    # Desfecho
    desfecho_texto = """
        Sendo o que se apresenta para o momento, confiantes na atenção e empenho de
        Vossa Excelência, agradecemos antecipadamente e renovamos nossos votos de
        elevada estima e consideração.
    """
    story.append(Paragraph(desfecho_texto, normal_justificado))
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph("Atenciosamente,", normal_justificado))
    story.append(Spacer(1, 1.5 * cm))

    # Modelo de linha para assinatura
    linha_assinatura = Table([['_' * 45]], colWidths=[8*cm])
    linha_assinatura.setStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'),                                  ('LEFTPADDING', (0,0), (-1,-1), 0),                                   ('RIGHTPADDING', (0,0), (-1,-1), 0)])

    # Assinatura em si
    assinatura_bloco = [
        linha_assinatura,
        Spacer(1, 0.2 * cm),
        Paragraph("<b>Josemar Rodrigues da Silva</b>", normal_centralizado),
        Paragraph("<i>Presidente da Câmara Municipal</i>", normal_centralizado)
    ]
    story.extend(assinatura_bloco)
    
    doc.build(story)

## Soli Deo Gloria ##
