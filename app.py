from flask import Flask, render_template, request, send_file
from jinja2 import Environment, FileSystemLoader
from datetime import date
import subprocess
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        dados = {
            "numero": request.form["numero"],
            "destinatario": request.form["destinatario"],
            "mensagem": request.form["mensagem"],
            "remetente": request.form["remetente"],
            "data": date.today().strftime('%d/%m/%Y'),
            "ano": date.today().year
        }

        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('modelo.tex')
        conteudo = template.render(dados)

        with open("oficio_preenchido.tex", "w", encoding="utf-8") as f:
            f.write(conteudo)

        subprocess.run(["pdflatex", "oficio_preenchido.tex"])

        return send_file("oficio_preenchido.pdf", as_attachment=True)

    return render_template("formulario.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

