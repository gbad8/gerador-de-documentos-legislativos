import pytest
from datetime import date
from django.urls import reverse
from legislaturas.models import Legislatura
from core.models import Camara, UsuarioPerfil

pytestmark = pytest.mark.django_db

@pytest.fixture
def camara_a():
    return Camara.objects.create(nome="Câmara A", estado="MA", cnpj="11")

@pytest.fixture
def camara_b():
    return Camara.objects.create(nome="Câmara B", estado="PI", cnpj="22")

@pytest.fixture
def user_a(django_user_model, camara_a):
    user = django_user_model.objects.create_user(username="user_a", password="pass")
    UsuarioPerfil.objects.create(user=user, camara=camara_a, role=UsuarioPerfil.Role.ADMIN, nome="Admin A", cargo="PA")
    return user

@pytest.fixture
def user_b(django_user_model, camara_b):
    user = django_user_model.objects.create_user(username="user_b", password="pass")
    UsuarioPerfil.objects.create(user=user, camara=camara_b, role=UsuarioPerfil.Role.ADMIN, nome="Admin B", cargo="PA")
    return user


class TestLegislaturasCRUD:
    def test_list_isolamento_tenant(self, client, user_a, user_b, camara_a, camara_b):
        Legislatura.objects.create(numero=1, data_eleicao=date(2020, 1, 1), data_inicio=date(2021, 1, 1), data_fim=date(2024, 12, 31), camara=camara_a)
        Legislatura.objects.create(numero=2, data_eleicao=date(2024, 1, 1), data_inicio=date(2025, 1, 1), data_fim=date(2028, 12, 31), camara=camara_b)
        
        client.force_login(user_a)
        response = client.get(reverse("legislatura_list"))
        assert response.status_code == 200
        assert "1ª Legislatura" in response.content.decode()
        assert "2ª Legislatura" not in response.content.decode()

    def test_create_legislatura(self, client, user_a, camara_a):
        client.force_login(user_a)
        url = reverse("legislatura_create")
        data = {
            "numero": 8,
            "data_eleicao": "2020-11-15",
            "data_inicio": "2021-01-01",
            "data_fim": "2024-12-31"
        }
        response = client.post(url, data)
        assert response.status_code == 302
        
        leg = Legislatura.objects.get(numero=8)
        assert leg.camara == camara_a

    def test_delete_legislatura(self, client, user_a, camara_a):
        leg = Legislatura.objects.create(numero=1, data_eleicao=date(2020, 1, 1), data_inicio=date(2021, 1, 1), data_fim=date(2024, 12, 31), camara=camara_a)
        client.force_login(user_a)
        url = reverse("legislatura_delete", kwargs={"pk": leg.pk})
        
        response = client.get(url)
        assert response.status_code == 200
        
        response = client.post(url)
        assert response.status_code == 302
        assert not Legislatura.objects.filter(pk=leg.pk).exists()
