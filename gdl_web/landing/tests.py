"""Testes para o app landing."""

import pytest
from django.urls import reverse

from landing.models import SolicitacaoAcesso

pytestmark = pytest.mark.django_db


class TestLandingPage:
    url = reverse("landing:index")

    def test_get_retorna_200_com_form(self, client):
        response = client.get(self.url)
        assert response.status_code == 200
        assert "form" in response.context

    def test_post_valido_cria_solicitacao_e_redireciona(self, client):
        data = {
            "nome_camara": "Câmara de Teste",
            "nome_solicitante": "Fulano de Tal",
            "cargo_solicitante": "Presidente",
            "email": "fulano@camara.leg.br",
            "telefone": "(99) 99999-9999",
        }
        response = client.post(self.url, data)
        assert response.status_code == 302
        assert SolicitacaoAcesso.objects.count() == 1

    def test_post_invalido_retorna_form_com_erros(self, client):
        response = client.post(self.url, {"nome_camara": ""})
        assert response.status_code == 200
        assert response.context["form"].errors

    def test_usuario_autenticado_acessa_normalmente(self, client, user):
        client.force_login(user)
        response = client.get(self.url)
        assert response.status_code == 200


class TestSolicitacaoAcessoModel:
    def test_str(self):
        s = SolicitacaoAcesso.objects.create(
            nome_camara="Câmara X",
            nome_solicitante="Maria",
            cargo_solicitante="Vereadora",
            email="maria@camara.leg.br",
            telefone="1199999",
        )
        assert str(s) == "Câmara X - Maria"
