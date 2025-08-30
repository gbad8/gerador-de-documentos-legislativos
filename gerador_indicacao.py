# Modulos utilizados
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_JUSTIFY, TA_CENTER #constante para alinhamento à direita
from reportlab.lib.units import cm
from reportlab.graphics.shapes import Drawing, Line

# Estlios personalizados para o documento
styles = getSampleStyleSheet()

normal_justificado = ParagraphStyle( # justificado para o corpo
        "NormalJustificado",
        parent=styles["Normal"],
        fontName="Times-Roman",
        alignment=TA_JUSTIFY,
        fontSize=12,
        leading=14
        )

normal_centralizado = ParagraphStyle( # centralizado para assinaturas
        "NormalCentralizado",
        parent=styles["Normal"],
        fontName="Times-Roman",
        alignment=TA_CENTER,
        fontSize=12,
        leading = 14
        )

right_aligned_style = ParagraphStyle( # à direita para órgão e data
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

    # Variáveis para o logo
    largura_imagem = 50
    altura_imagem = 50
    x = (largura_pagina - largura_imagem) / 2
    y = 753

    # Logo
    canvas.drawImage("logo.png", x, y, width=largura_imagem, height=altura_imagem, preserveAspectRatio=True, mask='auto') # logo da casa legislativa
    # Texto 
    canvas.setFont('Times-Bold', 10)
    canvas.drawCentredString(largura_pagina / 2, y - 20, "ESTADO DO MARANHÃO")
    canvas.drawCentredString(largura_pagina / 2, y - 32, "PODER LEGISLATIVO") 
    canvas.drawCentredString(largura_pagina / 2, y - 44, "CÂMARA MUNICIPAL DE VILA NOVA DOS MARTÍRIOS") 
    # Linha divisóaria
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
    canvas.drawCentredString(largura_pagina / 2, 50, "Av. Rio Branco s/n°, Centro, CEP: 65.924-000.")
    canvas.drawCentredString(largura_pagina / 2, 38, "https://www.cmvilanovadosmartirios.ma.gov.br/")
    canvas.drawCentredString(largura_pagina / 2, 26, "Email: cmvnmratirios@hotmail.com")

    canvas.restoreState()

# Junta Cabeçalho e Rodapé em uma única função
def cabecalho_rodape(canvas, doc):
    cabecalho(canvas, doc)
    rodape(canvas, doc)

# Função reutilizável
def gerar_indicacao():

    # Definição do documento
    doc = BaseDocTemplate("oficio.pdf", pagesize=A4)

    # Área útil do texto
    frame = Frame(85, 80, largura_pagina - 170, altura_pagina - 230, id='normal')

    # Template de página com cabeçalho
    doc.addPageTemplates([
        PageTemplate(id='modelo', frames=frame, onPage=cabecalho_rodape)
    ])

    # Preâmbulo
    story =[]
    story.append(Paragraph("<b>Secretaria Legislativa</b>", right_aligned_style)) # Órgão
    story.append(Spacer(1, 1/2 * cm)) # Espaço
    story.append(Paragraph("<b>Indicação n° 41/2025</b>", normal_justificado)) # Proposição
    story.append(Spacer(1, 2/3 * cm)) # Espaço
    story.append(Paragraph("Vila Nova dos Martírios, 27 de agosto de 2025.", right_aligned_style)) # Data

    # Autores
    story.append(Spacer(1, cm)) # Espaço
    story.append(Paragraph("<b>AUTORIA DOS(AS) EXMOS(AS) SENHORES(AS) VEREADORES(AS) ALIONE FARIAS DE ALMEIDA, ELSON GOMES DA SILVA, ISAC SOARES DE ARAÚJO, JOÃO FREDSON ALVES DE CARVALHO, JOSÉ GIVANILDO DE SOUSA MATIAS, JOSEMAR RODRIGUES DA SILVA, MARIA JOSÉ FERREIRA DE SOUSA, MANOEL FERREIRA DA SILVA E RICARDO VIANA MATOS,</b>", normal_justificado))

    # Assunto
    story.append(Spacer(1, 2/3 * cm)) # Espaço
    story.append(Paragraph("<b>ASSUNTO: CONSTRUÇÃO DE UMA PRAÇA NO POVOADO PARAÍSO.</b>", normal_justificado))

    # Introdução
    story.append(Spacer(1, 2/3 *cm)) # Espaço
    story.append(Paragraph("Ao Exmo. Sr. Vereador Josemar Rodrigues da Silva,", normal_justificado))

    story.append(Spacer(1, 2/3 *cm)) # Espaço
    story.append(Paragraph("Em concordância ao Regimento Interno da Câmara Municipal de Vereadores de Vila Nova dos Martírios (Art. 140) e por ser um legítimo Representante do povo desta municipalidade, faço a seguinte indicação para leitura, discussão e votação em Plenário:", normal_justificado))

    # Solicitação
    story.append(Spacer(1, 2/3 *cm)) # Espaço
    story.append(Paragraph("<b>SOLICITAÇÃO: QUE A PREFEITURA MUNICIPAL EMPREGUE OS MEIOS NECESSÁRIOS PARA A CONSTRUÇÃO DE UMA PRAÇA NO POVOADO PARAÍSO.</b>", normal_justificado))

    # Justificativa
    story.append(Spacer(1, 2/3 * cm)) # Espaço
    story.append(Paragraph("""<b>JUSTIFICATIVA</b>: A construção de uma praça no povoado Paraíso é uma necessidade evidente da comunidade, que atualmente carece de um espaço público que promova o convívio social, o lazer e a realização de atividades culturais e recreativas. A implantação desse equipamento proporcionará um ambiente saudável para crianças, jovens, adultos e idosos, favorecendo a integração entre as famílias e o fortalecimento dos laços comunitários. 
    Além disso, a praça representará um espaço de valorização do povoado, trazendo mais qualidade de vida aos moradores e contribuindo para a inclusão social. Trata-se de uma iniciativa que estimula o bem-estar coletivo, a prática de atividades ao ar livre e a cidadania.
     Diante disso, os vereadores desta Casa Legislativa apresentam a presente indicação, conf iando que a Prefeitura Municipal envidará os esforços necessários para sua concretização, em benefício de toda a população do povoado Paraíso.""", normal_justificado))

    # Conclusão
    story.append(Spacer(1, 2/3 * cm)) # Espaço
    story.append(Paragraph("Sala das Sessões da Câmara Municipal de Vereadores de Vila Nova dos Martírios - MA", normal_justificado))
    story.append(Paragraph("Plenário Aulindo Batista da Cruz, 27 de agosto de 2025.", normal_justificado))

    # Assinaturas
    # Variáveis gerais
    largura_linha = 8 * cm
    drawing_line = Drawing(largura_linha, 1)
    drawing_line.add(Line(0, 0, largura_linha, 0))

    table_line = Table([[drawing_line]], colWidths=[largura_linha])
    table_line.hAlign = "CENTER"
    story.append(Spacer(1, 0.5 * cm)) #Espaço antes de todas as assinaturas

    # Assinatura em si
    story.append(Spacer(1, 1.5 * cm)) # Espaço
    story.append(table_line)
    story.append(Paragraph("<b>Josemar Rodrigues da Silva</b>", normal_centralizado))
    story.append(Paragraph("<i>Presidente da Mesa Diretora</i>", normal_centralizado))
    story.append(Spacer(1, 1.5 * cm)) # Espaço
    story.append(table_line)
    story.append(Paragraph("<b>José Givanildo de Sousa Matias</b>", normal_centralizado))
    story.append(Paragraph("<i>Vice-Presidente da Mesa Diretora</i>", normal_centralizado))
    story.append(Spacer(1, 1.5 * cm)) # Espaço
    story.append(table_line)
    story.append(Paragraph("<b>Ricardo Viana Matos</b>", normal_centralizado))
    story.append(Paragraph("<i>1º Secretário da Mesa Diretora</i>", normal_centralizado))
    story.append(Spacer(1, 1.5 * cm)) # Espaço
    story.append(table_line)
    story.append(Paragraph("<b>Maria José Ferreira de Sousa</b>", normal_centralizado))
    story.append(Paragraph("<i>2ª Secretária da Mesa Diretora</i>", normal_centralizado))
    story.append(Spacer(1, 1.5 * cm)) # Espaço
    story.append(table_line)
    story.append(Paragraph("<b>Alione Farias de Almeida</b>", normal_centralizado))
    story.append(Paragraph("<i>Vereadora</i>", normal_centralizado))

    story.append(Spacer(1, 1.5 * cm)) # Espaço
    story.append(table_line)
    story.append(Paragraph("<b>Elson Gomes da Silva</b>", normal_centralizado))
    story.append(Paragraph("<i>Vereador</i>", normal_centralizado))

    story.append(Spacer(1, 1.5 * cm)) # Espaço
    story.append(table_line)
    story.append(Paragraph("<b>Isac Soares de Araújo</b>", normal_centralizado))
    story.append(Paragraph("<i>Vereador</i>", normal_centralizado))
    story.append(Spacer(1, 1.5 * cm)) # Espaço
    story.append(table_line)
    story.append(Paragraph("<b>João Fredson Alves de Carvalho</b>", normal_centralizado))
    story.append(Paragraph("<i>Vereador</i>", normal_centralizado))
    story.append(Spacer(1, 1.5 * cm)) # Espaço
    story.append(table_line)
    story.append(Paragraph("<b>Manoel Ferreira da Silva</b>", normal_centralizado))
    story.append(Paragraph("<i>Vereador</i>", normal_centralizado))
    doc.build(story)
