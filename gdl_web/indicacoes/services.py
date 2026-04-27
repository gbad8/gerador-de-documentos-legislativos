from django.template.loader import render_to_string

class PdfService:
    @staticmethod
    def gerar_indicacao(indicacao, camara):
        from weasyprint import HTML

        html_string = render_to_string("indicacoes/indicacao_pdf.html", {
            "indicacao": indicacao,
            "camara": camara,
        })
        return HTML(string=html_string).write_pdf()
