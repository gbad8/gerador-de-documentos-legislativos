import pytest
from django.urls import reverse
from sessoes.models import SessaoLegislativa
from datetime import date

pytestmark = pytest.mark.django_db


class TestSessaoViews:
    def test_list_requires_login(self, client):
        url = reverse("sessao_list")
        response = client.get(url)
        assert response.status_code == 302
        assert "login" in response.url

    def test_list_view(self, user_logado, sessao):
        url = reverse("sessao_list")
        response = user_logado.get(url)
        assert response.status_code == 200
        assert sessao in response.context["page_obj"].object_list

    def test_create_view_get(self, user_logado):
        url = reverse("sessao_create")
        response = user_logado.get(url)
        assert response.status_code == 200

    def test_create_view_post(self, user_logado, camara, legislatura):
        url = reverse("sessao_create")
        data = {
            "legislatura": legislatura.pk,
            "categoria": "EXTRAORDINARIA",
            "numero": 2,
            "data": date(2021, 3, 1).isoformat(),
        }
        response = user_logado.post(url, data)
        assert response.status_code == 302
        assert response.url == reverse("sessao_list")
        assert SessaoLegislativa.objects.filter(numero=2, categoria="EXTRAORDINARIA").exists()

    def test_edit_view_post(self, user_logado, sessao):
        url = reverse("sessao_edit", args=[sessao.pk])
        data = {
            "legislatura": sessao.legislatura.pk,
            "categoria": "SOLENE",
            "numero": sessao.numero,
            "data": sessao.data.isoformat(),
        }
        response = user_logado.post(url, data)
        assert response.status_code == 302
        sessao.refresh_from_db()
        assert sessao.categoria == "SOLENE"

    def test_delete_view_post(self, user_logado, sessao):
        url = reverse("sessao_delete", args=[sessao.pk])
        response = user_logado.post(url)
        assert response.status_code == 302
        assert not SessaoLegislativa.objects.filter(pk=sessao.pk).exists()
