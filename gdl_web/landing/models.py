from django.db import models

class SolicitacaoAcesso(models.Model):
    nome_camara = models.CharField("Nome da Câmara Municipal", max_length=200)
    nome_solicitante = models.CharField("Nome do Solicitante", max_length=150)
    cargo_solicitante = models.CharField("Cargo", max_length=100)
    email = models.EmailField("E-mail corporativo")
    telefone = models.CharField("Telefone/WhatsApp", max_length=20)
    data_solicitacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Solicitação de Acesso"
        verbose_name_plural = "Solicitações de Acesso"
        ordering = ["-data_solicitacao"]

    def __str__(self):
        return f"{self.nome_camara} - {self.nome_solicitante}"
