import pytest
from django.urls import reverse
from autores.models import Autor
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

class TestAutoresCRUD:
    def test_list_isolamento_tenant(self, client, user_a, user_b, camara_a, camara_b):
        # Cria autores em ambas as câmaras
        Autor.objects.create(nome="Vereador A", camara=camara_a)
        Autor.objects.create(nome="Vereador B", camara=camara_b)
        
        # User A sê apenas o A
        client.force_login(user_a)
        response = client.get(reverse("autor_list"))
        assert response.status_code == 200
        assert "Vereador A" in response.content.decode()
        assert "Vereador B" not in response.content.decode()

    def test_create_autor_associa_camara_correta(self, client, user_a, camara_a):
        client.force_login(user_a)
        url = reverse("autor_create")
        data = {"nome": "Novo Vereador", "cargo": "VER"}
        response = client.post(url, data)
        assert response.status_code == 302
        
        autor = Autor.objects.get(nome="Novo Vereador")
        assert autor.camara == camara_a

    def test_edit_autor_bloqueia_outra_camara(self, client, user_a, user_b, camara_b):
        autor_b = Autor.objects.create(nome="Vereador B", camara=camara_b)
        
        # User A tenta editar autor da Câmara B
        client.force_login(user_a)
        url = reverse("autor_edit", kwargs={"pk": autor_b.pk})
        response = client.get(url)
        assert response.status_code == 404 # TenantManager faz ele nem "encontrar" o objeto

    def test_delete_autor_sucesso(self, client, user_a, camara_a):
        autor = Autor.objects.create(nome="Para Deletar", camara=camara_a)
        client.force_login(user_a)
        url = reverse("autor_delete", kwargs={"pk": autor.pk})
        
        # GET mostra confirmação
        response = client.get(url)
        assert response.status_code == 200
        
        # POST deleta
        response = client.post(url)
        assert response.status_code == 302
        assert not Autor.objects.filter(pk=autor.pk).exists()
