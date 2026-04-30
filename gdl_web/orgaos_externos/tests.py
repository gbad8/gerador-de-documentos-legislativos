"""Testes para orgaos_externos.views"""
import pytest
from django.urls import reverse
from orgaos_externos.models import OrgaoExterno


@pytest.fixture
def orgao_externo(camara):
    """Órgão externo de teste."""
    return OrgaoExterno.objects.create(
        camara=camara,
        nome="Prefeitura Municipal",
        responsavel="João Silva",
        cargo="Prefeito",
        endereco="Rua Principal, 100",
        sexo="M",
        pronome_tratamento="Sr.",
    )


@pytest.fixture
def orgao_externo_list(camara):
    """Lista de órgãos externos para teste de paginação."""
    orgaos = []
    for i in range(1, 8):
        org = OrgaoExterno.objects.create(
            camara=camara,
            nome=f"Órgão {i}",
            responsavel=f"Responsável {i}",
            cargo=f"Cargo {i}",
            endereco=f"Rua {i}, {i*10}",
            sexo="M" if i % 2 == 0 else "F",
            pronome_tratamento="Sr." if i % 2 == 0 else "Sra.",
        )
        orgaos.append(org)
    return orgaos


class TestOrgaoExternoListView:
    """Testes para lista de órgãos externos."""

    def test_list_requires_login(self, client):
        """GET sem autenticação redireciona para login."""
        url = reverse("orgao_externo_list")
        response = client.get(url)
        assert response.status_code == 302

    def test_list_returns_200(self, user_logado, orgao_externo):
        """GET autenticado retorna status 200."""
        url = reverse("orgao_externo_list")
        response = user_logado.get(url)
        assert response.status_code == 200

    def test_list_uses_correct_template(self, user_logado, orgao_externo):
        """GET usa template correto."""
        url = reverse("orgao_externo_list")
        response = user_logado.get(url)
        assert "orgaos_externos/orgao_externo_list.html" in [t.name for t in response.templates]

    def test_list_pagination(self, user_logado, orgao_externo_list):
        """Lista com paginação mostra 5 items por página."""
        url = reverse("orgao_externo_list")
        response = user_logado.get(url)
        
        page_obj = response.context["page_obj"]
        assert page_obj.paginator.per_page == 5
        assert len(page_obj.object_list) == 5
        assert page_obj.paginator.num_pages == 2

    def test_list_pagination_second_page(self, user_logado, orgao_externo_list):
        """Segunda página mostra items restantes."""
        url = reverse("orgao_externo_list") + "?page=2"
        response = user_logado.get(url)
        
        page_obj = response.context["page_obj"]
        assert len(page_obj.object_list) == 2

    def test_list_filters_by_camara(self, client, user, camara, outra_camara):
        """Lista mostra apenas órgãos da câmara do usuário."""
        from core.models import UsuarioPerfil
        
        org1 = OrgaoExterno.objects.create(
            camara=camara, nome="Org 1", responsavel="R1", cargo="C1",
            endereco="E1", sexo="M", pronome_tratamento="Sr."
        )
        org2 = OrgaoExterno.objects.create(
            camara=outra_camara, nome="Org 2", responsavel="R2", cargo="C2",
            endereco="E2", sexo="F", pronome_tratamento="Sra."
        )
        
        UsuarioPerfil.objects.create(
            user=user, camara=camara, nome="User", cargo=UsuarioPerfil.Cargo.PARLAMENTAR
        )
        client.login(username="testuser", password="testpass123")
        
        url = reverse("orgao_externo_list")
        response = client.get(url)
        
        page_obj = response.context["page_obj"]
        orgao_ids = [o.id for o in page_obj.object_list]
        assert org1.id in orgao_ids
        assert org2.id not in orgao_ids


class TestOrgaoExternoCreateView:
    """Testes para criação de órgão externo."""

    def test_create_requires_login(self, client):
        """GET sem autenticação redireciona para login."""
        url = reverse("orgao_externo_create")
        response = client.get(url)
        assert response.status_code == 302

    def test_create_get_returns_form(self, user_logado):
        """GET retorna formulário vazio."""
        url = reverse("orgao_externo_create")
        response = user_logado.get(url)
        
        assert response.status_code == 200
        assert "orgaos_externos/orgao_externo_form.html" in [t.name for t in response.templates]
        assert "form" in response.context

    def test_create_post_valid(self, user_logado, camara):
        """POST com dados válidos cria órgão externo."""
        url = reverse("orgao_externo_create")
        
        data = {
            "nome": "Câmara de Vereadores",
            "abreviatura": "CV",
            "responsavel": "João Silva",
            "cargo": "Vereador",
            "endereco": "Rua Central, 50",
            "sexo": "M",
            "pronome_tratamento": "Vossa Senhoria / V.Sa.",
        }
        
        response = user_logado.post(url, data)
        
        assert response.status_code == 302
        orgao = OrgaoExterno.objects.filter(nome="Câmara de Vereadores").first()
        assert orgao is not None
        assert orgao.responsavel == "João Silva"
        assert orgao.camara == camara

    def test_create_post_invalid_rerenders(self, user_logado):
        """POST com dados inválidos (sem nome) re-renderiza com erros."""
        url = reverse("orgao_externo_create")
        
        data = {
            # Falta: nome
            "responsavel": "João",
            "cargo": "Cargo",
            "endereco": "Rua 1",
            "sexo": "M",
            "pronome_tratamento": "Vossa Senhoria / V.Sa.",
        }
        
        response = user_logado.post(url, data)
        
        assert response.status_code == 200
        assert response.context["form"].errors


class TestOrgaoExternoEditView:
    """Testes para edição de órgão externo."""

    def test_edit_requires_login(self, client, orgao_externo):
        """GET sem autenticação redireciona para login."""
        url = reverse("orgao_externo_edit", kwargs={"pk": orgao_externo.pk})
        response = client.get(url)
        assert response.status_code == 302

    def test_edit_returns_404_for_other_camara(self, client, user, camara, outra_camara, orgao_externo):
        """GET para órgão de outra câmara retorna 404."""
        from core.models import UsuarioPerfil
        
        UsuarioPerfil.objects.create(
            user=user, camara=outra_camara, nome="User", cargo=UsuarioPerfil.Cargo.PARLAMENTAR
        )
        client.login(username="testuser", password="testpass123")
        
        url = reverse("orgao_externo_edit", kwargs={"pk": orgao_externo.pk})
        response = client.get(url)
        assert response.status_code == 404

    def test_edit_get_prefills_form(self, user_logado, orgao_externo):
        """GET preenche formulário com dados existentes."""
        url = reverse("orgao_externo_edit", kwargs={"pk": orgao_externo.pk})
        response = user_logado.get(url)
        
        assert response.status_code == 200
        form = response.context["form"]
        assert form["nome"].value() == orgao_externo.nome
        assert form["responsavel"].value() == orgao_externo.responsavel

    def test_edit_post_updates(self, user_logado, orgao_externo):
        """POST atualiza órgão externo."""
        url = reverse("orgao_externo_edit", kwargs={"pk": orgao_externo.pk})
        
        data = {
            "nome": "Prefeitura Atualizada",
            "abreviatura": "PA",
            "responsavel": "Maria Silva",
            "cargo": "Prefeita",
            "endereco": "Rua Nova, 200",
            "sexo": "F",
            "pronome_tratamento": "Vossa Excelência / V.Ex.ª",
        }
        
        response = user_logado.post(url, data)
        
        assert response.status_code == 302
        orgao_externo.refresh_from_db()
        assert orgao_externo.nome == "Prefeitura Atualizada"
        assert orgao_externo.responsavel == "Maria Silva"

    def test_edit_post_invalid_rerenders(self, user_logado, orgao_externo):
        """POST inválido re-renderiza formulário com erros."""
        url = reverse("orgao_externo_edit", kwargs={"pk": orgao_externo.pk})
        
        data = {
            "nome": "",  # Inválido
            "responsavel": "João",
            "cargo": "Cargo",
            "endereco": "Rua 1",
            "sexo": "M",
            "pronome_tratamento": "Vossa Senhoria / V.Sa.",
        }
        
        response = user_logado.post(url, data)
        
        assert response.status_code == 200
        assert response.context["form"].errors


class TestOrgaoExternoDeleteView:
    """Testes para deleção de órgão externo."""

    def test_delete_requires_login(self, client, orgao_externo):
        """GET sem autenticação redireciona para login."""
        url = reverse("orgao_externo_delete", kwargs={"pk": orgao_externo.pk})
        response = client.get(url)
        assert response.status_code == 302

    def test_delete_get_shows_confirmation(self, user_logado, orgao_externo):
        """GET mostra página de confirmação."""
        url = reverse("orgao_externo_delete", kwargs={"pk": orgao_externo.pk})
        response = user_logado.get(url)
        
        assert response.status_code == 200
        assert "orgaos_externos/orgao_externo_confirm_delete.html" in [t.name for t in response.templates]

    def test_delete_post_deletes(self, user_logado, orgao_externo):
        """POST deleta órgão externo."""
        pk = orgao_externo.pk
        url = reverse("orgao_externo_delete", kwargs={"pk": pk})
        
        response = user_logado.post(url)
        
        assert response.status_code == 302
        assert not OrgaoExterno.objects.filter(pk=pk).exists()

    def test_delete_post_success_message(self, user_logado, orgao_externo):
        """POST deleta e exibe mensagem de sucesso."""
        url = reverse("orgao_externo_delete", kwargs={"pk": orgao_externo.pk})
        nome = orgao_externo.nome
        
        response = user_logado.post(url, follow=True)
        
        messages = list(response.context["messages"])
        assert len(messages) == 1
        assert "removido" in str(messages[0]).lower()

    def test_delete_redirects_to_list(self, user_logado, orgao_externo):
        """POST após delete redireciona para lista."""
        url = reverse("orgao_externo_delete", kwargs={"pk": orgao_externo.pk})
        response = user_logado.post(url, follow=True)
        
        assert response.resolver_match.url_name == "orgao_externo_list"
