from django.db import models

from core.managers import TenantManager
from core.models import Camara


class Autor(models.Model):
    class Cargo(models.TextChoices):
        PRESIDENTE = "PR", "Presidente"
        VICE_PRESIDENTE = "VP", "Vice-Presidente"
        PRIMEIRO_SECRETARIO = "1S", "1º Secretário"
        SEGUNDO_SECRETARIO = "2S", "2º Secretário"
        VEREADOR = "VER", "Vereador"

    nome = models.CharField(max_length=200)
    cargo = models.CharField(max_length=3,
                             choices=Cargo.choices,
                             default=Cargo.VEREADOR)
    camara = models.ForeignKey(Camara, on_delete=models.CASCADE)

    objects = TenantManager()

    class Meta:
        verbose_name_plural = "Autores"
        ordering = ["nome"]
        constraints = [
            models.UniqueConstraint(
                fields=["camara", "nome", "cargo"],
                name="unique_autor_por_camara"
            )
        ]
        indexes = [
            models.Index(fields=["camara"]),
        ]

    def __str__(self):
        return self.nome
