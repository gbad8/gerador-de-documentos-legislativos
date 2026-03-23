import pytest
from django.urls import reverse
from orgaos.models import Orgao

pytestmark = pytest.mark.django_db

def test_orgao_list_view(user_logado, camara, outra_camara):
    Orgao.objects.create(camara=camara, nome="Orgao 1")
    Orgao.objects.create(camara=outra_camara, nome="Orgao Outra")
    
    url = reverse("orgao_list")
    response = user_logado.get(url)
    
    assert response.status_code == 200
    assert "Orgao 1" in response.content.decode()
    assert "Orgao Outra" not in response.content.decode()

def test_orgao_create_view_post(user_logado, camara):
    url = reverse("orgao_create")
    data = {"nome": "Gabinete 1", "abreviatura": "gab1"}
    response = user_logado.post(url, data)
    
    assert response.status_code == 302
    assert Orgao.objects.filter(nome="Gabinete 1", camara=camara).exists()

def test_orgao_edit_view(user_logado, camara):
    orgao = Orgao.objects.create(camara=camara, nome="Antigo")
    url = reverse("orgao_edit", args=[orgao.pk])
    data = {"nome": "Novo Nome", "abreviatura": "novo"}
    response = user_logado.post(url, data)
    
    assert response.status_code == 302
    orgao.refresh_from_db()
    assert orgao.nome == "Novo Nome"

def test_orgao_delete_view_post(user_logado, camara):
    orgao = Orgao.objects.create(camara=camara, nome="Para Deletar")
    url = reverse("orgao_delete", args=[orgao.pk])
    response = user_logado.post(url)
    
    assert response.status_code == 302
    assert not Orgao.objects.filter(pk=orgao.pk).exists()

def test_orgao_edit_view_access_denied(user_logado, outra_camara):
    orgao_outro = Orgao.objects.create(camara=outra_camara, nome="Alheio")
    url = reverse("orgao_edit", args=[orgao_outro.pk])
    response = user_logado.get(url)
    
    assert response.status_code == 404
