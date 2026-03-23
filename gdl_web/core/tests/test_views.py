import pytest
from django.urls import reverse
from core.models import Camara, UsuarioPerfil

pytestmark = pytest.mark.django_db

@pytest.fixture
def camara():
    return Camara.objects.create(
        nome="Câmara de Teste",
        cidade="Cidade de Teste",
        estado="SP",
        cnpj="12345678000190",
        endereco="Rua Teste, 123",
        telefone="11999999999"
    )

@pytest.fixture
def user(django_user_model, camara):
    user = django_user_model.objects.create_user(username="testuser", password="password")
    UsuarioPerfil.objects.create(
        user=user,
        camara=camara,
        role=UsuarioPerfil.Role.ADMIN,
        nome="Usuário Teste",
        cargo="Admin"
    )
    return user

class TestConfiguracoesView:
    def test_requer_login(self, client):
        url = reverse("configuracoes")
        response = client.get(url)
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_acesso_permitido(self, client, user):
        client.force_login(user)
        url = reverse("configuracoes")
        response = client.get(url)
        assert response.status_code == 200
        assert "core/configuracoes.html" in [t.name for t in response.templates]

class TestCamaraEditView:
    def test_requer_login(self, client):
        url = reverse("camara_edit")
        response = client.get(url)
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_get_retorna_form_preenchido(self, client, user, camara):
        client.force_login(user)
        url = reverse("camara_edit")
        response = client.get(url)
        assert response.status_code == 200
        assert "core/camara_form.html" in [t.name for t in response.templates]
        assert response.context["form"].instance == camara

    def test_post_valido_salva_e_mostra_mensagem(self, client, user, camara):
        client.force_login(user)
        url = reverse("camara_edit")
        data = {
            "nome": "Câmara Alterada",
            "cidade": "Cidade Alterada",
            "estado": "SP",
            "cnpj": camara.cnpj,
            "endereco": camara.endereco,
            "cep": "12345-678",
            "telefone": camara.telefone,
            "email": "test@example.com",
        }
        response = client.post(url, data)
        assert response.status_code == 200
        camara.refresh_from_db()
        assert camara.nome == "Câmara Alterada"
        assert camara.cep == "12345-678"
        
        messages = list(response.context["messages"])
        assert len(messages) == 1
        assert "sucesso" in str(messages[0]).lower()

    def test_post_invalido_retorna_form_com_erros(self, client, user, camara):
        client.force_login(user)
        url = reverse("camara_edit")
        data = {
            "nome": "",  # campo obrigatório faltando
            "cidade": camara.cidade,
            "estado": "SP",
            "cnpj": camara.cnpj,
            "endereco": camara.endereco,
        }
        response = client.post(url, data)
        assert response.status_code == 200
        form = response.context["form"]
        assert form.errors
        assert "nome" in form.errors
        camara.refresh_from_db()
        assert camara.nome == "Câmara de Teste"


class TestPerfilEditView:
    def test_requer_login(self, client):
        url = reverse("perfil_edit")
        response = client.get(url)
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_get_retorna_forms(self, client, user):
        client.force_login(user)
        url = reverse("perfil_edit")
        response = client.get(url)
        assert response.status_code == 200
        assert "user_form" in response.context
        assert "perfil_form" in response.context

    def test_post_valido_salva_perfil(self, client, user, camara):
        client.force_login(user)
        url = reverse("perfil_edit")
        data = {
            "username": "novousername",
            "email": "novo@email.com",
            "nome": "Novo Nome",
            "cargo": "PA",
        }
        response = client.post(url, data)
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.username == "novousername"
        user.perfil.refresh_from_db()
        assert user.perfil.nome == "Novo Nome"

        messages = list(response.context["messages"])
        assert len(messages) == 1
        assert "sucesso" in str(messages[0]).lower()

    def test_post_invalido_retorna_form_com_erros(self, client, user, camara):
        client.force_login(user)
        url = reverse("perfil_edit")
        data = {
            "username": "",  # campo obrigatório
            "email": "",
            "nome": "Nome",
            "cargo": "PA",
        }
        response = client.post(url, data)
        assert response.status_code == 200
        form = response.context["user_form"]
        assert form.errors
