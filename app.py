# Copyright (c) 2025 Câmara Municipal de Vila Nova dos Martírios
#
# Este trabalho está licenciado sob uma Licença Creative Commons Atribuição-CompartilhaIgual 4.0 Internacional.
# Para visualizar uma cópia desta licença, visite http://creativecommons.org/licenses/by-sa/4.0/
# ou envie uma carta para Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from datetime import datetime
import locale
import tempfile
import os
from functools import wraps
from gerador_indicacao import gerar_indicacao
from gerador_oficio import gerar_oficio # <- Importa a nova função

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'chave-padrao')

try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
except locale.Error:
    print("Aviso: O locale 'pt_BR.utf8' não foi encontrado. Usando o locale padrão (inglês).")

# Configurando usuários
USERS = {
        "guilherme": "1516170224",
        "emerson": "marjose1997"
        }

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
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
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/oficio-padrao', methods=['GET', 'POST'])
@login_required
def oficio_padrao():
    if request.method == 'POST':
        data_str = request.form.get('data')
        data_obj = datetime.strptime(data_str, '%Y-%m-%d')
        
        is_conjunta = 'conjunta_check' in request.form
        autores_selecionados = ""
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
            'data': data_obj.strftime('%d de %B de %Y'),
            'assunto': request.form['assunto'],
            'proposicao': request.form['proposicao'],
            'n-indicacao': request.form['n-indicacao'],
            'vereador': vereador_final,
            'resultado': request.form['resultado'],
            'sessao': request.form['sessao'],
            'autores_selecionados': autores_selecionados
        }

        # --- LÓGICA DE GERAÇÃO COM REPORTLAB ---
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
            'data': data_obj.strftime('%d de %B de %Y'),
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

## Soli Deo Gloria ##
