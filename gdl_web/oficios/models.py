from django.db import models

from autores.models import Autor
from core.models import Camara
from core.managers import TenantManager


class Oficio(models.Model):
    class Status(models.TextChoices):
        RASCUNHO = "rascunho"
        FINALIZADO = "finalizado"
        MODIFICADO = "modificado"

    class Tipo(models.TextChoices):
        LIVRE = "livre", "Ofício Livre"
        ENCAMINHAMENTO = "encaminhamento", "Encaminhamento de Proposições Aprovadas"

    tipo = models.CharField(
        max_length=30,
        choices=Tipo.choices,
        default=Tipo.LIVRE,
    )

    camara = models.ForeignKey(Camara, on_delete=models.CASCADE)
    orgao = models.ForeignKey("orgaos.Orgao", on_delete=models.PROTECT, null=True, blank=True)
    autor = models.ForeignKey(Autor, on_delete=models.PROTECT)
    numero = models.CharField(max_length=10)
    assunto = models.CharField(max_length=500, blank=True)
    corpo = models.TextField(blank=True)
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
        basicos = bool(self.autor_id and self.orgao_id and self.data and self.destinatario_nome and self.destinatario_pronome)
        if not basicos: return False
        
        if self.tipo == self.Tipo.LIVRE:
            return bool(self.assunto and self.corpo)
        elif self.tipo == self.Tipo.ENCAMINHAMENTO:
            return hasattr(self, 'encaminhamento')
            
        return False

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
