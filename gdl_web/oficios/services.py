from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone

from oficios.models import Numeracao


class NumeracaoService:
    @staticmethod
    def proximo_numero(camara, orgao, autor):
        ano = timezone.now().year

        with transaction.atomic():
            numeracao, _ = Numeracao.objects.select_for_update().get_or_create(
                camara=camara,
                orgao=orgao,
                autor=autor,
                ano=ano,
                defaults={"ultimo_numero": 0},
            )
            numeracao.ultimo_numero += 1
            numeracao.save()

        return f"{numeracao.ultimo_numero:03d}/{ano}"


class PdfService:
    @staticmethod
    def gerar_oficio(oficio, camara):
        from weasyprint import HTML

        html_string = render_to_string("oficios/oficio_pdf.html", {
            "oficio": oficio,
            "camara": camara,
        })
        return HTML(string=html_string).write_pdf()
