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

    @staticmethod
    def registrar_numero_manual(camara, orgao, autor, numero):
        """Registra um número manual inserido pelo usuário.

        Valida que o número é maior que o ultimo_numero atual.
        Levanta ValueError se o número for menor ou igual.
        """
        ano = timezone.now().year

        with transaction.atomic():
            numeracao, _ = Numeracao.objects.select_for_update().get_or_create(
                camara=camara,
                orgao=orgao,
                autor=autor,
                ano=ano,
                defaults={"ultimo_numero": 0},
            )

            if numero <= numeracao.ultimo_numero:
                raise ValueError(
                    f"O número {numero} não é válido. "
                    f"O último número registrado para esta autoria é "
                    f"{numeracao.ultimo_numero:03d}/{ano}."
                )

            numeracao.ultimo_numero = numero
            numeracao.save()

        return f"{numero:03d}/{ano}"


class PdfService:
    @staticmethod
    def gerar_oficio(oficio, camara):
        from weasyprint import HTML

        html_string = render_to_string("oficios/oficio_pdf.html", {
            "oficio": oficio,
            "camara": camara,
        })
        return HTML(string=html_string).write_pdf()


class PronomeService:
    @staticmethod
    def flexionar_pronome(pronome_cru, sexo):
        mapping = {
            "Vossa Excelência / V.Ex.ª": {"M": "Excelentíssimo", "F": "Excelentíssima", "N": "Excelentíssimo(a)"},
            "Vossa Senhoria / V.Sa.": {"M": "Ilustríssimo", "F": "Ilustríssima", "N": "Ilustríssimo(a)"},
            "Vossa Magnificência / V.Mag.ª": {"M": "Magnífico", "F": "Magnífica", "N": "Magnífico(a)"},
            "Vossa Eminência / V.Ema.": {"M": "Eminentíssimo", "F": "Eminentíssima", "N": "Eminentíssimo(a)"},
        }
        
        base = mapping.get(pronome_cru, {}).get(sexo, pronome_cru)
        
        if pronome_cru in mapping:
            sufixo = " Senhor" if sexo == "M" else " Senhora" if sexo == "F" else " Senhor(a)"
            return f"{base}{sufixo}"
            
        return base
