# Modulos utilizados
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, KeepTogether
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
    canvas.drawCentredString(largura_pagina / 2, 50, "Av. Rio Branco s/n°, Centro, CEP: 65.924-000.")
    canvas.drawCentredString(largura_pagina / 2, 38, "https://www.cmvilanovadosmartirios.ma.gov.br/")
    canvas.drawCentredString(largura_pagina / 2, 26, "Email: cmvnmratirios@hotmail.com")

    canvas.restoreState()

# Junta Cabeçalho e Rodapé em uma única função
def cabecalho_rodape(canvas, doc):
    cabecalho(canvas, doc)
    rodape(canvas, doc)

# Função que concatena o nome dos autores
def formatar_nomes(lista_nomes):
    if not lista_nomes:
        return ""
    if len(lista_nomes) == 1:
        return lista_nomes[0]
    return ", ".join(lista_nomes[:-1]) + " e " + lista_nomes[-1]

# Função principal para gerar a indicação
def gerar_indicacao(dados, nome_arquivo):

    # Definição do documento
    doc = BaseDocTemplate(nome_arquivo, pagesize=A4)

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

    # Conjunta ou não
    autores = dados.get('autores_selecionados', [])
    if len(autores) > 1:
        titulo_proposicao = f"<b>Indicação Conjunta n° {dados['numero']}/{dados['ano']}</b>"
    else:
        titulo_proposicao = f"<b>Indicação n° {dados['numero']}/{dados['ano']}</b>"

    story.append(Paragraph(titulo_proposicao, normal_justificado)) # Proposição
    story.append(Spacer(1, 2/3 * cm)) # Espaço
    story.append(Paragraph(f"Vila Nova dos Martírios, {dados['data']}.", right_aligned_style)) # Data

    # Dicionários de nomes e cargos
    VEREADORES = {
    "Josemar Rodrigues da Silva":       {"titulo": "Presidente da Mesa Diretora", "genero": "M"},
    "José Givanildo de Sousa Matias":   {"titulo": "Vice-Presidente da Mesa Diretora", "genero": "M"},
    "Ricardo Viana Matos":              {"titulo": "1º Secretário da Mesa Diretora", "genero": "M"},
    "Maria José Ferreira de Sousa":     {"titulo": "2ª Secretária da Mesa Diretora", "genero": "F"},
    "Alione Farias de Almeida":         {"titulo": "Vereadora", "genero": "F"},
    "Elson Gomes da Silva":             {"titulo": "Vereador", "genero": "M"},
    "Isac Soares de Araújo":            {"titulo": "Vereador", "genero": "M"},
    "João Fredson Alves de Carvalho":   {"titulo": "Vereador", "genero": "M"},
    "Manoel Ferreira da Silva":         {"titulo": "Vereador", "genero": "M"}}

    # Autores
    story.append(Spacer(1, cm)) # Espaço
    autores = dados.get('autores_selecionados', [])
    texto_autoria = ""

    # Caso 1: Autoria única
    if len(autores) <= 1:
        nome_autor = dados.get('vereador_nome', '')
        info_autor = VEREADORES.get(nome_autor)
        texto_autoria = ""
    
        if info_autor and info_autor.get("genero") == 'F':
            texto_autoria = f"AUTORIA DA SENHORA VEREADORA {nome_autor.upper()}"
        else:
            texto_autoria = f"AUTORIA DO SENHOR VEREADOR {nome_autor.upper()}"
        
        linha_autoria_final = f"<b>{texto_autoria}</b>"

    # Caso 2: Autoria conjunta
    else:
        vereadores_homens = []
        vereadoras_mulheres = []

        # Separa os autores em listas por gênero
        for nome in autores:
            info = VEREADORES.get(nome)
            if info and info.get('genero') == 'F':
                vereadoras_mulheres.append(nome)
            else:
                vereadores_homens.append(nome)

        # Formata as listas de nomes usando a função auxiliar
        nomes_homens_str = formatar_nomes(vereadores_homens)
        nomes_mulheres_str = formatar_nomes(vereadoras_mulheres)

        partes_autoria = []
        # Cria a parte do texto para os homens, se houver algum
        if nomes_homens_str:
            partes_autoria.append(f"DOS SENHORES VEREADORES {nomes_homens_str.upper()}")
    
        # Cria a parte do texto para as mulheres, se houver alguma
        if nomes_mulheres_str:
            partes_autoria.append(f"DAS SENHORAS VEREADORAS {nomes_mulheres_str.upper()}")

        # Junta as partes com " E "
        texto_final_autoria = " E ".join(partes_autoria)
        
        linha_autoria_final = f"<b>AUTORIA {texto_final_autoria}</b>"

    story.append(Paragraph(linha_autoria_final, normal_justificado))

    # Assunto
    story.append(Spacer(1, 2/3 * cm)) # Espaço
    story.append(Paragraph(f"<b>ASSUNTO: {dados['assunto'].upper()}</b>", normal_justificado))

    # Introdução
    story.append(Spacer(1, 2/3 *cm)) # Espaço
    story.append(Paragraph("Ao Exmo. Sr. Vereador Josemar Rodrigues da Silva,", normal_justificado))

    story.append(Spacer(1, 2/3 *cm)) # Espaço
    story.append(Paragraph("Em concordância ao Regimento Interno da Câmara Municipal de Vereadores de Vila Nova dos Martírios (Art. 140) e por ser um legítimo Representante do povo desta municipalidade, faço a seguinte indicação para leitura, discussão e votação em Plenário:", normal_justificado))

    # Solicitação
    story.append(Spacer(1, 2/3 *cm)) # Espaço
    story.append(Paragraph(f"<b>SOLICITAÇÃO: {dados['solicitacao'].upper()}</b>", normal_justificado))

    # Justificativa
    story.append(Spacer(1, 2/3 * cm)) # Espaço
    story.append(Paragraph(f"""<b>JUSTIFICATIVA: {dados['justificativa']}</b>""", normal_justificado))

    # Conclusão
    story.append(Spacer(1, 2/3 * cm)) # Espaço
    story.append(Paragraph(f"Sala das Sessões da Câmara Municipal de Vila Nova dos Martírios - MA. Plenátio Aulindo Batista da Cruz, {dados['data']}.", normal_justificado))
    story.append(Spacer(1, cm)) # Espaço antes das assinaturas
    
    # Testa a quantidade de autores 
    if not autores:
        nome_unico = dados.get('vereador_nome')
        if nome_unico:
            autores = [nome_unico]

    # Escolhe as configurações gerais para a assinatura
    linha_assinatura = Table([['_' * 45]], colWidths=[8*cm])
    linha_assinatura.setStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'),
                               ('LEFTPADDING', (0,0), (-1,-1), 0),
                               ('RIGHTPADDING', (0,0), (-1,-1), 0)])
    
    # Gera a assinatura para cada autor selecionado
    for nome in autores:
        # Busca o cargo do vereador no dicionário. Se não encontrar, usa "Vereador(a)" como padrão.
        # Busca as informações do vereador, com um valor padrão caso não encontre
        info_vereador = VEREADORES.get(nome, {"titulo": "Vereador(a)", "genero": "M"})
        cargo = info_vereador.get("titulo")

        bloco_assinatura = KeepTogether([
            Spacer(1, 1.5 * cm), # Espaço entre as assinaturas
            linha_assinatura,
            Paragraph(f"<b>{nome}</b>", normal_centralizado),
            Paragraph(f"<i>{cargo}</i>", normal_centralizado)
            ])
        story.append(bloco_assinatura)

    doc.build(story)

    ## Soli Deo Gloria ##
