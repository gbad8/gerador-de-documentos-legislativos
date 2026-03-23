from django.conf import settings
from django.db import models

from core.managers import TenantManager


class Camara(models.Model):
    class Estado(models.TextChoices):
        AC = "AC", "Acre"
        AL = "AL", "Alagoas"
        AP = "AP", "Amapá"
        AM = "AM", "Amazonas"
        BA = "BA", "Bahia"
        CE = "CE", "Ceará"
        DF = "DF", "Distrito Federal"
        ES = "ES", "Espírito Santo"
        GO = "GO", "Goiás"
        MA = "MA", "Maranhão"
        MT = "MT", "Mato Grosso"
        MS = "MS", "Mato Grosso do Sul"
        MG = "MG", "Minas Gerais"
        PA = "PA", "Pará"
        PB = "PB", "Paraíba"
        PR = "PR", "Paraná"
        PE = "PE", "Pernambuco"
        PI = "PI", "Piauí"
        RJ = "RJ", "Rio de Janeiro"
        RN = "RN", "Rio Grande do Norte"
        RS = "RS", "Rio Grande do Sul"
        RO = "RO", "Rondônia"
        RR = "RR", "Roraima"
        SC = "SC", "Santa Catarina"
        SP = "SP", "São Paulo"
        SE = "SE", "Sergipe"
        TO = "TO", "Tocantins"

    nome = models.CharField(max_length=200)
    cidade = models.CharField(max_length=200)
    estado = models.CharField(max_length=2, choices=Estado.choices)
    cnpj = models.CharField(max_length=18)
    endereco = models.TextField()
    cep = models.CharField("CEP", max_length=9, blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    logomarca = models.BinaryField("Logomarca (Bytes)", blank=True, null=True, editable=True)

    @property
    def logomarca_base64(self):
        import base64
        if self.logomarca:
            return base64.b64encode(self.logomarca).decode('utf-8')
        return None

    @property
    def preposicao_estado(self):
        """Retorna a preposição correta (do/de/da) com base no estado."""
        de = ["AL", "GO", "MT", "MS", "MG", "PE", "SC", "SP", "SE"]
        da = ["BA", "PB"]
        
        if self.estado in de:
            return "de"
        elif self.estado in da:
            return "da"
        return "do"

    class Meta:
        verbose_name = "Câmara"
        verbose_name_plural = "Câmaras"

    def __str__(self):
        return self.nome


class UsuarioPerfil(models.Model):
    class Role(models.TextChoices):
        ADMIN = "ADM", "Administrador"
        OPERADOR = "OPR", "Operador"

    class Cargo(models.TextChoices):
        PARLAMENTAR = "PA", "Parlamentar"
        ASSESSOR_PARLAMENTAR = "AP", "Assessor Parlamentar"
        ASSESSOR_JURIDICO = "AJ", "Assessor Jurídico"
        ASSESSOR_CONTABIL = "AC", "Assessor Contábil"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
    )
    camara = models.ForeignKey(Camara, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=3,
        choices=Role.choices,
        default=Role.OPERADOR,
    )
    nome = models.CharField(max_length=200)
    cargo = models.CharField(max_length=30, choices=Cargo.choices)

    objects = TenantManager()

    class Meta:
        verbose_name = "Perfil de usuário"
        verbose_name_plural = "Perfis de usuários"

    def __str__(self):
        return self.nome
