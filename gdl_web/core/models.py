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


class DocumentoStatus(models.TextChoices):
    RASCUNHO = "rascunho"
    FINALIZADO = "finalizado"
    MODIFICADO = "modificado"


class DocumentoLegislativoBase(models.Model):
    camara = models.ForeignKey(Camara, on_delete=models.CASCADE)
    orgao = models.ForeignKey("orgaos.Orgao", on_delete=models.PROTECT, null=True, blank=True)
    autor = models.ForeignKey("autores.Autor", on_delete=models.PROTECT)
    numero = models.CharField(max_length=10)
    data = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=DocumentoStatus.choices,
        default=DocumentoStatus.RASCUNHO,
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    objects = TenantManager()

    class Meta:
        abstract = True
        ordering = ["-criado_em"]
        indexes = [
            models.Index(fields=["camara", "-criado_em"]),
            models.Index(fields=["camara", "orgao"]),
            models.Index(fields=["camara", "autor"]),
            models.Index(fields=["camara", "status"]),
        ]

    def _campos_completos(self):
        """Método a ser sobrescrito nas classes filhas"""
        return False

    def calcular_status(self):
        """Calcula o status do documento automaticamente."""
        if not self._campos_completos():
            return DocumentoStatus.RASCUNHO

        if self.pk and self.status == DocumentoStatus.FINALIZADO:
            return DocumentoStatus.MODIFICADO

        if self.status == DocumentoStatus.MODIFICADO:
            return DocumentoStatus.MODIFICADO

        return DocumentoStatus.FINALIZADO

    def save(self, *args, **kwargs):
        self.status = self.calcular_status()
        super().save(*args, **kwargs)


class Numeracao(models.Model):
    class TipoDocumento(models.TextChoices):
        OFICIO = "oficio", "Ofício"
        INDICACAO = "indicacao", "Indicação"
        REQUERIMENTO = "requerimento", "Requerimento"
        PROJETO_LEI = "projeto_lei", "Projeto de Lei"
        PARECER = "parecer", "Parecer"
        PORTARIA = "portaria", "Portaria"

    tipo_documento = models.CharField(
        max_length=20, 
        choices=TipoDocumento.choices, 
        default=TipoDocumento.OFICIO
    )
    camara = models.ForeignKey(Camara, on_delete=models.CASCADE)
    orgao = models.ForeignKey("orgaos.Orgao", on_delete=models.CASCADE, null=True, blank=True)
    autor = models.ForeignKey("autores.Autor", on_delete=models.CASCADE)
    ano = models.IntegerField()
    ultimo_numero = models.IntegerField(default=0)

    objects = TenantManager()

    class Meta:
        db_table = "oficios_numeracao"  # Mantém a tabela atual de numeração do Ofício
        unique_together = ("camara", "orgao", "autor", "ano", "tipo_documento")
        verbose_name = "Numeração"
        verbose_name_plural = "Numerações"

    def __str__(self):
        return f"{self.get_tipo_documento_display()} - {self.orgao} / {self.autor} — {self.ano}: {self.ultimo_numero}"
