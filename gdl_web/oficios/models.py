from django.db import models

from autores.models import Autor
from core.models import Camara
from core.managers import TenantManager


class Oficio(models.Model):
    class Status(models.TextChoices):
        RASCUNHO = "rascunho"
        FINALIZADO = "finalizado"
        MODIFICADO = "modificado"

    camara = models.ForeignKey(Camara, on_delete=models.CASCADE)
    orgao = models.ForeignKey("orgaos.Orgao", on_delete=models.PROTECT, null=True, blank=True)
    autor = models.ForeignKey(Autor, on_delete=models.PROTECT)
    numero = models.CharField(max_length=10)
    assunto = models.CharField(max_length=500)
    corpo = models.TextField()
    data = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RASCUNHO,
    )
    e_conjunto = models.BooleanField("Ofício Conjunto", default=False)
    coautores = models.ManyToManyField(Autor, related_name="oficios_coautoria", blank=True)

    destinatario_nome = models.CharField("nome do destinatário", max_length=200)
    destinatario_cargo = models.CharField("cargo do destinatário", max_length=200, null=True, blank=True)
    destinatario_orgao = models.CharField("órgão do destinatário", max_length=200, null=True, blank=True)
    destinatario_endereco = models.TextField("endereço do destinatário", null=True, blank=True)
    destinatario_pronome = models.CharField(
        "pronome de tratamento",
        max_length=50,
        help_text="Ex: Excelentíssimo(a), Ilustríssimo(a)",
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    objects = TenantManager()

    class Meta:
        ordering = ["-criado_em"]
        indexes = [
            models.Index(fields=["camara", "-criado_em"]),
            models.Index(fields=["camara", "orgao"]),
            models.Index(fields=["camara", "autor"]),
            models.Index(fields=["camara", "status"]),
        ]

    def __str__(self):
        return f"Ofício n° {self.numero} — {self.autor}"

    CAMPOS_OBRIGATORIOS = [
        "autor_id", "orgao_id", "data", "assunto", "corpo",
        "destinatario_nome", "destinatario_pronome",
    ]

    def _campos_completos(self):
        """Retorna True se todos os campos obrigatórios para finalização estão preenchidos."""
        return all(getattr(self, campo) for campo in self.CAMPOS_OBRIGATORIOS)

    def calcular_status(self):
        """Calcula o status do ofício automaticamente."""
        if not self._campos_completos():
            return self.Status.RASCUNHO

        if self.pk and self.status == self.Status.FINALIZADO:
            return self.Status.MODIFICADO

        if self.status == self.Status.MODIFICADO:
            return self.Status.MODIFICADO

        return self.Status.FINALIZADO

    def save(self, *args, **kwargs):
        self.status = self.calcular_status()
        super().save(*args, **kwargs)

    @property
    def autores_ordenados(self):
        """
        Retorna uma lista contendo o autor principal e coautores ordenados por:
        1. Cargo (Presidente, Vice-Presidente, 1º Secretário, 2º Secretário, Vereador)
        2. Nome (em ordem alfabética, apenas para Vereadores)
        """
        autores = [self.autor]
        if self.e_conjunto:
            autores.extend(self.coautores.all())
        
        # Atribuímos um peso para cada cargo para facilitar a ordenação
        # PR=0, VP=1, 1S=2, 2S=3, VER=4
        pesos = {
            Autor.Cargo.PRESIDENTE: 0,
            Autor.Cargo.VICE_PRESIDENTE: 1,
            Autor.Cargo.PRIMEIRO_SECRETARIO: 2,
            Autor.Cargo.SEGUNDO_SECRETARIO: 3,
            Autor.Cargo.VEREADOR: 4,
        }

        # Ordenar primeiro pelo peso do cargo, depois pelo nome
        return sorted(autores, key=lambda a: (pesos.get(a.cargo, 99), a.nome))


class Numeracao(models.Model):
    camara = models.ForeignKey(Camara, on_delete=models.CASCADE)
    orgao = models.ForeignKey("orgaos.Orgao", on_delete=models.CASCADE, null=True, blank=True)
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE)
    ano = models.IntegerField()
    ultimo_numero = models.IntegerField(default=0)

    objects = TenantManager()

    class Meta:
        unique_together = ("camara", "orgao", "autor", "ano")
        verbose_name = "Numeração"
        verbose_name_plural = "Numerações"

    def __str__(self):
        return f"{self.orgao} / {self.autor} — {self.ano}: {self.ultimo_numero}"
