from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q

from core.managers import TenantManager
from core.models import Camara
from legislaturas.models import Legislatura


class SessaoLegislativa(models.Model):
    CATEGORIA_CHOICES = [
        ("ORDINARIA", "Ordinária"),
        ("EXTRAORDINARIA", "Extraordinária"),
        ("SOLENE", "Solene"),
    ]

    legislatura = models.ForeignKey(Legislatura, on_delete=models.CASCADE, related_name="sessoes")
    categoria = models.CharField("Categoria", max_length=20, choices=CATEGORIA_CHOICES)
    numero = models.PositiveIntegerField("Número")
    data = models.DateField("Data")
    
    camara = models.ForeignKey(Camara, on_delete=models.CASCADE)

    objects = TenantManager()

    class Meta:
        verbose_name = "Sessão Legislativa"
        verbose_name_plural = "Sessões Legislativas"
        ordering = ["-data", "-numero"]
        constraints = [
            models.UniqueConstraint(
                fields=["legislatura", "numero", "categoria"],
                name="unique_sessao_por_legislatura"
            )
        ]

    def __str__(self):
        ordinal = f"{self.numero}ª"
        categoria_display = self.get_categoria_display()
        return f"{ordinal} Sessão {categoria_display} da {self.legislatura}"
