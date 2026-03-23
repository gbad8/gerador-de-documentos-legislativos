from django.db import models
from core.models import Camara
from core.managers import TenantManager

class Orgao(models.Model):
    camara = models.ForeignKey(Camara, on_delete=models.CASCADE)
    nome = models.CharField(max_length=200)
    abreviatura = models.CharField(max_length=20, null=True, blank=True)
    
    objects = TenantManager()
    
    class Meta:
        verbose_name = "Órgão"
        verbose_name_plural = "Órgãos"
        unique_together = ("camara", "nome")
        ordering = ["nome"]

    def __str__(self):
        return self.nome
