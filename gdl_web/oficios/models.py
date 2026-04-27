from django.db import models

from autores.models import Autor
from core.models import Camara, DocumentoLegislativoBase, DocumentoStatus
from core.mixins import CoautoriaMixin, DestinatarioMixin


class Oficio(DocumentoLegislativoBase, CoautoriaMixin, DestinatarioMixin):
    Status = DocumentoStatus

    class Tipo(models.TextChoices):
        LIVRE = "livre", "Ofício Livre"
        ENCAMINHAMENTO = "encaminhamento", "Encaminhamento de Proposições Aprovadas"

    tipo = models.CharField(
        max_length=30,
        choices=Tipo.choices,
        default=Tipo.LIVRE,
    )
    assunto = models.CharField(max_length=500, blank=True)
    corpo = models.TextField(blank=True)

    def __str__(self):
        return f"Ofício n° {self.numero} — {self.autor}"

    CAMPOS_OBRIGATORIOS = [
        "autor_id", "orgao_id", "data", "assunto", "corpo",
        "destinatario_nome", "destinatario_pronome",
    ]

    def _campos_completos(self):
        """Retorna True se todos os campos obrigatórios para finalização estão preenchidos."""
        basicos = bool(self.autor_id and self.orgao_id and self.data and self.destinatario_nome and self.destinatario_pronome)
        if not basicos: return False
        
        if self.tipo == self.Tipo.LIVRE:
            return bool(self.assunto and self.corpo)
        elif self.tipo == self.Tipo.ENCAMINHAMENTO:
            return hasattr(self, 'encaminhamento')
            
        return False


class OficioEncaminhamento(models.Model):
    class Votacao(models.TextChoices):
        MAIORIA_SIMPLES = "maioria_simples", "Maioria Simples"
        MAIORIA_QUALIFICADA = "maioria_qualificada", "Maioria Qualificada"
        UNANIMIDADE = "unanimidade", "Unanimidade"

    oficio = models.OneToOneField(Oficio, on_delete=models.CASCADE, related_name="encaminhamento")
    sessao = models.ForeignKey("sessoes.SessaoLegislativa", on_delete=models.PROTECT)
    votacao = models.CharField(max_length=50, choices=Votacao.choices)
    proposicao = models.CharField("Proposição", max_length=200, help_text="Ex: Indicação n° 13")
    autor_proposicao = models.ForeignKey(Autor, on_delete=models.PROTECT, related_name="encaminhamentos_proposicao")
    data_aprovacao = models.DateField("Data de Aprovação")

    def get_corpo_gerado(self):
        camara = self.oficio.camara
        presidente = self.oficio.autor.nome
        votacao_nome = self.get_votacao_display().lower()
        
        meses = [
            "", "janeiro", "fevereiro", "março", "abril", "maio", "junho",
            "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
        ]
        dia = self.data_aprovacao.day
        mes = meses[self.data_aprovacao.month]
        ano = self.data_aprovacao.year
        data_formatada = f"{dia:02d} de {mes} de {ano}"
        
        return (
            f"A {camara.nome} - {camara.estado}, por meio de seu Presidente, {presidente}, "
            f"vem, mui respeitosamente, encaminhar à Prefeitura a cópia do(a) {self.proposicao}, "
            f"de autoria de {self.autor_proposicao.nome}. A referida proposição foi aprovada por "
            f"{votacao_nome} nesta Casa Legislativa, na {self.sessao}, "
            f"realizada em {data_formatada}."
        )

    class Meta:
        verbose_name = "Ofício de Encaminhamento"
        verbose_name_plural = "Ofícios de Encaminhamento"
