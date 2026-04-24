from django.db import models
from django.db.models import UniqueConstraint

from core.managers import TenantManager
from core.models import Camara

class OrgaoExterno(models.Model):
    SEXO_CHOICES = [
        ("M", "Masculino"),
        ("F", "Feminino"),
        ("N", "Não Informar"),
    ]

    PRONOME_CHOICES = [
        ("Vossa Senhoria / V.Sa.", "Vossa Senhoria / V.Sa."),
        ("Vossa Excelência / V.Ex.ª", "Vossa Excelência / V.Ex.ª"),
        ("Vossa Magnificência / V.Mag.ª", "Vossa Magnificência / V.Mag.ª"),
        ("Vossa Eminência / V.Ema.", "Vossa Eminência / V.Ema."),
    ]

    nome = models.CharField("Nome do Órgão", max_length=200)
    abreviatura = models.CharField("Abreviatura / Sigla", max_length=50)
    
    responsavel = models.CharField("Nome do Responsável", max_length=150)
    sexo = models.CharField("Sexo", max_length=1, choices=SEXO_CHOICES, default="M")
    cargo = models.CharField("Cargo do Responsável", max_length=100)
    pronome_tratamento = models.CharField(
        "Pronome de Tratamento", max_length=100, choices=PRONOME_CHOICES
    )
    endereco = models.TextField("Endereço", blank=True, null=True)

    camara = models.ForeignKey(Camara, on_delete=models.CASCADE, related_name="orgaos_externos")
    
    objects = TenantManager()

    class Meta:
        verbose_name = "Órgão Externo"
        verbose_name_plural = "Órgãos Externos"
        ordering = ["nome"]
        constraints = [
            UniqueConstraint(fields=["camara", "nome"], name="unique_orgao_externo_por_camara")
        ]

    def __str__(self):
        return self.nome
