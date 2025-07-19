# Copyright (c) 2025 Câmara Municipal de Vila Nova dos Martírios
#
# Este trabalho está licenciado sob uma Licença Creative Commons Atribuição-CompartilhaIgual 4.0 Internacional.
# Para visualizar uma cópia desta licença, visite http://creativecommons.org/licenses/by-sa/4.0/
# ou envie uma carta para Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

from flask import Flask, render_template, request, send_file
from datetime import datetime
import locale
import subprocess
import tempfile
import shutil
import os
import re

app = Flask(__name__)
locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/oficio-padrao', methods=['GET', 'POST'])
def oficio_padrao():
    if request.method == 'POST':
        data_str = request.form.get('data')
        data_obj = datetime.strptime(data_str, '%Y-%m-%d')
        
        is_conjunta = 'conjunta_check' in request.form # Confere se o checkbox foi marcado
        
        vereador_final = ""
        
        if is_conjunta: # Se for autoria conjunta
            # Se for autoria conjunta, pega todos os vereadores selecionados
            autores_selecionados = request.form.getlist('autores_selecionados[]')
            # Formata a lista de autores como uma string para o .tex
            if autores_selecionados:
                if len(autores_selecionados) > 1:
                    # Junta todos, exceto o último, com vírgula e o último com "e"
                    vereador_final = ", ".join(autores_selecionados[:-1]) + " e " + autores_selecionados[-1]
                else:
                    vereador_final = autores_selecionados[0]
            else:
                vereador_final = "Nenhum autor selecionado" # Caso nenhum seja selecionado
            
            # Adiciona "Vereadores" se houver mais de um, ou apenas "Vereador" se for um só.
            if len(autores_selecionados) > 1:
                vereador_final = "dos(as) Exmos(as). Senhores(as) Vereadores(as) " + vereador_final
            elif len(autores_selecionados) == 1:
                vereador_final = "do(a) Exmo(a). Senhor(a) Vereador(a) " + vereador_final
            else:
                vereador_final = "Nenhum autor selecionado" # ou "Vereador Não Informado"
                
        else: # Se não for autoria conjunta, usar o campo singular
            vereador_final = request.form.get('vereador')
            if vereador_final == "Jorge Vieira dos Santos Filho": # Se for o prefeito
                vereador_final = "do Exmo. Senhor Prefeito " + vereador_final
            elif vereador_final == "Alione Farias de Almeida" or vereador_final == "Maria José Ferreira de Sousa": # Se for mulher
                vereador_final = "da Exma. Senhora Vereadora " + vereador_final
            elif vereador_final: # Se for homem
                vereador_final = "do Exmo. Senhor Vereador " + vereador_final
            else:
                vereador_final = "Vereador Não Informado " # Fallback se nada for selecionado
        
        dados = {
            'numero': request.form['numero'],
            'ano': str(data_obj.year),
            'data': data_obj.strftime('%d de %B de %Y'),
            'assunto': request.form['assunto'],
            'proposicao': request.form['proposicao'],
            'n-indicacao': request.form['n-indicacao'],
            'vereador': vereador_final, # Este campo agora conterá o autor/autores formatado(s)
            'resultado': request.form['resultado'],
            'sessao': request.form['sessao'],
        }

        # Lê o modelo original
        with open('modelo.tex', 'r', encoding='utf-8') as f:
            conteudo = f.read()

        # Substitui os marcadores
        for chave, valor in dados.items():
            # Usar re.escape para chaves que podem conter caracteres especiais para regex, embora {{chave}} já ajude
            conteudo = conteudo.replace(f'{{{{{chave}}}}}', valor)

        # Cria um diretório temporário para gerar os arquivos
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_tex = os.path.join(tmpdir, 'documento.tex')

            # Escreve o conteúdo temporário
            with open(caminho_tex, 'w', encoding='utf-8') as f:
                f.write(conteudo)

            # Verificação de marcadores não substituídos
            faltando = re.findall(r'{{.*?}}', conteudo)
            if faltando:
                # Pode levantar um erro ou apenas logar
                print(f"ATENÇÃO: Marcadores não substituídos encontrados: {faltando}")

            # Compila para PDF
            try:
                result = subprocess.run(['pdflatex', '-interaction=nonstopmode', '-output-directory', tmpdir, caminho_tex], capture_output=True, encoding='latin1', text=True, check=True)
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
            except subprocess.CalledProcessError as e:
                print(f"Erro na compilação do LaTeX: {e}")
                print("Output LaTeX (STDOUT):", e.stdout)
                print("Output LaTeX (STDERR):", e.stderr)
                return f"Erro ao gerar PDF. Verifique o log do servidor para detalhes. LaTeX Erro: {e.stderr}", 500


            # Caminho do PDF gerado
            caminho_pdf = os.path.join(tmpdir, 'documento.pdf')

            # Nome final do arquivo
            nome_arquivo = f"Oficio_{dados['numero']}_{dados['ano']}.pdf"
            caminho_final = os.path.join(tmpdir, nome_arquivo)
            shutil.copy(caminho_pdf, caminho_final)


            # Envia o PDF gerado
            return send_file(caminho_final, as_attachment=True)

    # Renderiza o formulário se o método for GET
    else:
        return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True)