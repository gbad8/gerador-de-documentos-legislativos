from django.db import models

from autores.models import Autor
from core.models import DocumentoLegislativoBase
from core.mixins import CoautoriaMixin


class Indicacao(DocumentoLegislativoBase, CoautoriaMixin):
    assunto = models.CharField(max_length=500, blank=True)
    solicitacao = models.TextField(blank=True)
    justificativa = models.TextField(blank=True)

    class Meta:
        verbose_name = "Indicação"
        verbose_name_plural = "Indicações"

    def _campos_completos(self):
        """Retorna True se todos os campos obrigatórios para finalização estão preenchidos."""
        basicos = bool(self.autor_id and self.data)
        if not basicos: return False
        
        return bool(self.assunto and self.solicitacao and self.justificativa)
        
    def __str__(self):
        return f"Indicação n° {self.numero} — {self.autor}"
