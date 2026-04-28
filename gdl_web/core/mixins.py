from django.db import models
from autores.models import Autor


class CoautoriaMixin(models.Model):
    e_conjunto = models.BooleanField("Documento Conjunto", default=False)
    coautores = models.ManyToManyField(
        "autores.Autor", 
        related_name="%(app_label)s_%(class)s_coautoria", 
        blank=True
    )

    class Meta:
        abstract = True

    @property
    def autores_ordenados(self):
        """
        Retorna uma lista contendo o autor principal e coautores ordenados por:
        1. Cargo (Presidente, Vice-Presidente, 1º Secretário, 2º Secretário, Vereador)
        2. Nome (em ordem alfabética, apenas para Vereadores)
        """
        if not hasattr(self, 'autor'):
            return []

        autores = [self.autor]
        if self.e_conjunto:
            autores.extend(self.coautores.all())
        
        pesos = {
            Autor.Cargo.PRESIDENTE: 0,
            Autor.Cargo.VICE_PRESIDENTE: 1,
            Autor.Cargo.PRIMEIRO_SECRETARIO: 2,
            Autor.Cargo.SEGUNDO_SECRETARIO: 3,
            Autor.Cargo.VEREADOR: 4,
        }

        return sorted(autores, key=lambda a: (pesos.get(a.cargo, 99), a.nome))


class DestinatarioMixin(models.Model):
    destinatario_nome = models.CharField("nome do destinatário", max_length=200)
    destinatario_cargo = models.CharField("cargo do destinatário", max_length=200, null=True, blank=True)
    destinatario_orgao = models.CharField("órgão do destinatário", max_length=200, null=True, blank=True)
    destinatario_endereco = models.TextField("endereço do destinatário", null=True, blank=True)
    destinatario_pronome = models.CharField(
        "pronome de tratamento",
        max_length=50,
        help_text="Ex: Excelentíssimo(a), Ilustríssimo(a)",
    )

    class Meta:
        abstract = True
