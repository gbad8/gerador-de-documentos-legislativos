# Copyright (c) 2025 Câmara Municipal de Vila Nova dos Martírios
#
# Este trabalho está licenciado sob uma Licença Creative Commons Atribuição-CompartilhaIgual 4.0 Internacional.
# Para visualizar uma cópia desta licença, visite http://creativecommons.org/licenses/by-sa/4.0/
# ou envie uma carta para Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from datetime import datetime
import tempfile
import os
from functools import wraps
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

from gerador_indicacao import gerar_indicacao
from gerador_oficio import gerar_oficio
from gerador_oficio_livre import gerar_oficio_livre

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'chave-padrao-para-desenvolvimento')

try:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("AVISO: A variável de ambiente GEMINI_API_KEY não foi encontrada.")
    else:
        genai.configure(api_key=api_key)
except Exception as e:
    print(f"AVISO: Falha ao configurar a API do Gemini. Funcionalidades de IA estarão desabilitadas. Erro: {e}")

USERS = { "guilherme": "1516170224", "emerson": "marjose1997" }

def traduzir_data(data_obj):
    meses_pt = {
        "January": "Janeiro", "February": "Fevereiro", "March": "Março",
        "April": "Abril", "May": "Maio", "June": "Junho",
        "July": "Julho", "August": "Agosto", "September": "Setembro",
        "October": "Outubro", "November": "Novembro", "December": "Dezembro"
    }
    data_em_ingles = data_obj.strftime('%d de %B de %Y')
    for mes_en, mes_pt in meses_pt.items():
        if mes_en in data_em_ingles:
            return data_em_ingles.replace(mes_en, mes_pt)
    return data_em_ingles

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- ROTAS ---

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS and USERS[username] == password:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha incorretos!')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/gerar-corpo-oficio', methods=['POST'])
@login_required
def gerar_corpo_oficio_route():
    try:
        topico = request.json.get('topico')
        if not topico:
            return jsonify({'error': 'Tópico não fornecido.'}), 400
        prompt = f"""
        Aja como um assessor legislativo experiente da Câmara Municipal de Vila Nova dos Martírios - MA.
        Sua tarefa é redigir o corpo de um ofício. O texto deve ser formal, claro, conciso e respeitoso,
        seguindo a norma culta da língua portuguesa e o padrão de documentos oficiais.
        O texto deve conter parágrafos bem estruturados e não deve incluir cabeçalho, destinatário, assunto ou assinatura, apenas o texto principal.
        O tópico do ofício é: "{topico}"
        """
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        return jsonify({'corpo_oficio': response.text})
    except Exception as e:
        print(f"Erro ao chamar a API do Gemini: {e}")
        return jsonify({'error': 'Não foi possível gerar o texto no momento.'}), 500

@app.route('/oficio_livre', methods=['GET', 'POST'])
@login_required
def oficio_livre():
    if request.method == 'POST':
        data_str = request.form.get('data')
        data_obj = datetime.strptime(data_str, '%Y-%m-%d')
        
        is_conjunta = 'conjunta_check' in request.form
        autores_selecionados = request.form.getlist('autores_selecionados[]') if is_conjunta else []
        
        # Define o autor principal ou a lista de autores para os dados
        autor_principal = request.form.get('vereador') if not is_conjunta else None

        dados = {
            'numero': request.form['numero'],
            'ano': str(data_obj.year),
            'data': traduzir_data(data_obj),
            'assunto': request.form['assunto'],
            'vereador': autor_principal,
            'autores_selecionados': autores_selecionados,
            'orgao': request.form['orgao'],
            'destinatario': request.form['destinatario'],
            'cargo': request.form['cargo'],
            'corpo_oficio': request.form['corpo_oficio']
        }

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp.close()
        try:
            gerar_oficio_livre(dados, tmp.name)
            return send_file(
                tmp.name,
                as_attachment=True,
                download_name=f"Oficio_Livre_{dados['numero']}_{dados['ano']}.pdf"
            )
        finally:
            os.remove(tmp.name)
    else:
        return render_template('form_oficio_livre.html')

@app.route('/oficio-padrao', methods=['GET', 'POST'])
@login_required
def oficio_padrao():
    if request.method == 'POST':
        data_str = request.form.get('data')
        data_obj = datetime.strptime(data_str, '%Y-%m-%d')
        is_conjunta = 'conjunta_check' in request.form
        autores_selecionados = []
        vereador_final = ""
        if is_conjunta:
            autores_selecionados = request.form.getlist('autores_selecionados[]')
            if autores_selecionados:
                if len(autores_selecionados) > 1:
                    vereador_final = ", ".join(autores_selecionados[:-1]) + " e " + autores_selecionados[-1]
                else:
                    vereador_final = autores_selecionados[0]
            else:
                vereador_final = "Nenhum autor selecionado"
            if len(autores_selecionados) > 1:
                vereador_final = "dos(as) Exmos(as). Senhores(as) Vereadores(as) " + vereador_final
            elif len(autores_selecionados) == 1:
                vereador_final = "do(a) Exmo(a). Senhor(a) Vereador(a) " + vereador_final
        else:
            vereador_final_nome = request.form.get('vereador')
            if vereador_final_nome == "Jorge Vieira dos Santos Filho":
                vereador_final = "do Exmo. Senhor Prefeito " + vereador_final_nome
            elif vereador_final_nome in ["Alione Farias de Almeida", "Maria José Ferreira de Sousa"]:
                vereador_final = "da Exma. Senhora Vereadora " + vereador_final_nome
            else:
                vereador_final = "do Exmo. Senhor Vereador " + vereador_final_nome
        dados = {
            'numero': request.form['numero'],
            'ano': str(data_obj.year),
            'data': traduzir_data(data_obj),
            'assunto': request.form['assunto'],
            'proposicao': request.form['proposicao'],
            'n-indicacao': request.form['n-indicacao'],
            'vereador': vereador_final,
            'resultado': request.form['resultado'],
            'sessao': request.form['sessao'],
            'autores_selecionados': autores_selecionados
        }
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp.close()
        try:
            gerar_oficio(dados, tmp.name)
            return send_file(
                tmp.name,
                as_attachment=True,
                download_name=f"Oficio_{dados['numero']}_{dados['ano']}.pdf"
            )
        finally:
            os.remove(tmp.name)
    else:
        return render_template('form.html')

@app.route('/indicacao', methods=['GET', 'POST'])
@login_required
def indicacao():
    if request.method == 'POST':
        data_str = request.form.get('data')
        data_obj = datetime.strptime(data_str, '%Y-%m-%d')
        is_conjunta = 'conjunta_check' in request.form
        autores_selecionados = request.form.getlist('autores_selecionados[]') if is_conjunta else []
        vereador_final = ""
        vereador_nome = ""
        if is_conjunta:
            if len(autores_selecionados) > 1:
                vereador_nome = ", ".join(autores_selecionados[:-1]) + " e " + autores_selecionados[-1]
                vereador_final = "dos(as) Exmos(as). Senhores(as) Vereadores(as) " + vereador_nome
            elif len(autores_selecionados) == 1:
                vereador_nome = autores_selecionados[0]
                vereador_final = "do(a) Exmo(a). Senhor(a) Vereador(a) " + vereador_nome
        else:
            vereador_nome = request.form.get('vereador')
            if vereador_nome == "Jorge Vieira dos Santos Filho":
                vereador_final = "do Exmo. Senhor Prefeito " + vereador_nome
            elif vereador_nome in ["Alione Farias de Almeida", "Maria José Ferreira de Sousa"]:
                vereador_final = "da Exma. Senhora Vereadora " + vereador_nome
            else:
                vereador_final = "do Exmo. Senhor Vereador " + vereador_nome
        dados = {
            'numero': request.form['numero'],
            'ano': str(data_obj.year),
            'data': traduzir_data(data_obj),
            'assunto': request.form['assunto'],
            'solicitacao': request.form['solicitacao'],
            'justificativa': request.form['justificativa'],
            'vereador': vereador_final,
            'vereador_nome': vereador_nome,
            'autores_selecionados': autores_selecionados
        }
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp.close()
        try:
            gerar_indicacao(dados, tmp.name)
            return send_file(tmp.name, as_attachment=True, download_name=f"Indicacao_{dados['numero']}_{dados['ano']}.pdf")
        finally:
            os.remove(tmp.name)
    else:
        return render_template('form_indicacao.html')

if __name__ == '__main__':
    app.run(debug=True)


