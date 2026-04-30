"""Testes para indicacoes.views"""
import pytest
from datetime import date
from unittest.mock import patch, MagicMock

from django.urls import reverse
from django.contrib.auth import get_user_model

from autores.models import Autor
from core.models import Numeracao
from indicacoes.models import Indicacao
from orgaos.models import Orgao

User = get_user_model()


@pytest.fixture
def orgao(camara):
    """Órgão de teste."""
    return Orgao.objects.create(
        camara=camara,
        nome="Secretaria de Governo",
        abreviatura="SG"
    )


@pytest.fixture
def presidente(camara):
    """Autor com cargo de presidente."""
    return Autor.objects.create(
        nome="José Presidente",
        cargo=Autor.Cargo.PRESIDENTE,
        camara=camara,
    )


@pytest.fixture
def indicacao(camara, autor, orgao):
    """Indicação de teste."""
    return Indicacao.objects.create(
        camara=camara,
        autor=autor,
        orgao=orgao,
        numero="001/2026",
        data=date(2026, 1, 15),
        assunto="Teste de Indicação",
        solicitacao="Solicitação teste",
        justificativa="Justificativa teste",
    )


@pytest.fixture
def indicacao_list(camara, autor, orgao):
    """Lista de indicações para testes de paginação."""
    indicacoes = []
    for i in range(1, 8):  # 7 indicações para testar paginação (5 por página)
        ind = Indicacao.objects.create(
            camara=camara,
            autor=autor,
            orgao=orgao,
            numero=f"{i:03d}/2026",
            data=date(2026, 1, i),
            assunto=f"Indicação {i}",
            solicitacao=f"Solicitação {i}",
            justificativa=f"Justificativa {i}",
        )
        indicacoes.append(ind)
    return indicacoes


class TestIndicacaoListView:
    """Testes para indicacao_list view."""

    def test_list_requires_login(self, client):
        """GET sem autenticação redireciona para login."""
        url = reverse("indicacoes:list")
        response = client.get(url)
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_list_returns_200(self, user_logado, camara, indicacao):
        """GET autenticado retorna status 200."""
        url = reverse("indicacoes:list")
        response = user_logado.get(url)
        assert response.status_code == 200

    def test_list_uses_correct_template(self, user_logado, camara, indicacao):
        """GET usa template correto."""
        url = reverse("indicacoes:list")
        response = user_logado.get(url)
        assert "indicacoes/indicacao_list.html" in [t.name for t in response.templates]

    def test_list_pagination_default(self, user_logado, indicacao_list):
        """Lista com paginação mostra 5 itens por página."""
        url = reverse("indicacoes:list")
        response = user_logado.get(url)
        
        page_obj = response.context["page_obj"]
        assert page_obj.paginator.per_page == 5
        assert len(page_obj.object_list) == 5  # 5 na primeira página
        assert page_obj.paginator.num_pages == 2  # 7 items = 2 páginas

    def test_list_pagination_second_page(self, user_logado, indicacao_list):
        """Segunda página mostra itens restantes."""
        url = reverse("indicacoes:list") + "?page=2"
        response = user_logado.get(url)
        
        page_obj = response.context["page_obj"]
        assert len(page_obj.object_list) == 2  # 2 na segunda página

    def test_list_orders_by_newest_first(self, user_logado, indicacao_list):
        """Lista ordenada por data decrescente (mais recente primeiro)."""
        url = reverse("indicacoes:list")
        response = user_logado.get(url)
        
        page_obj = response.context["page_obj"]
        dates = [ind.data for ind in page_obj.object_list]
        assert dates == sorted(dates, reverse=True)

    def test_list_filters_by_camara(self, client, user, camara, outra_camara):
        """Lista mostra apenas indicações da câmara do usuário (tenancy)."""
        from core.models import UsuarioPerfil
        
        # Criar indicações em ambas câmaras
        orgao1 = Orgao.objects.create(camara=camara, nome="Orgão 1")
        orgao2 = Orgao.objects.create(camara=outra_camara, nome="Orgão 2")
        
        autor1 = Autor.objects.create(camara=camara, nome="Autor 1", cargo=Autor.Cargo.VEREADOR)
        autor2 = Autor.objects.create(camara=outra_camara, nome="Autor 2", cargo=Autor.Cargo.VEREADOR)
        
        ind1 = Indicacao.objects.create(
            camara=camara, autor=autor1, orgao=orgao1,
            numero="001/2026", data=date(2026, 1, 1),
            assunto="Indicação 1", solicitacao="Sol", justificativa="Just"
        )
        ind2 = Indicacao.objects.create(
            camara=outra_camara, autor=autor2, orgao=orgao2,
            numero="002/2026", data=date(2026, 1, 2),
            assunto="Indicação 2", solicitacao="Sol", justificativa="Just"
        )
        
        # Autenticar com primeira câmara
        UsuarioPerfil.objects.create(
            user=user, camara=camara, nome="User", cargo=UsuarioPerfil.Cargo.PARLAMENTAR
        )
        client.login(username="testuser", password="testpass123")
        
        url = reverse("indicacoes:list")
        response = client.get(url)
        
        page_obj = response.context["page_obj"]
        indicacoes_ids = [ind.id for ind in page_obj.object_list]
        assert ind1.id in indicacoes_ids
        assert ind2.id not in indicacoes_ids


class TestIndicacaoCreateView:
    """Testes para indicacao_create view."""

    def test_create_requires_login(self, client):
        """GET sem autenticação redireciona para login."""
        url = reverse("indicacoes:create")
        response = client.get(url)
        assert response.status_code == 302

    def test_create_get_returns_form(self, user_logado):
        """GET retorna formulário vazio."""
        url = reverse("indicacoes:create")
        response = user_logado.get(url)
        
        assert response.status_code == 200
        assert "indicacoes/indicacao_form.html" in [t.name for t in response.templates]
        assert "form" in response.context
        form = response.context["form"]
        assert form["assunto"].value() is None

    def test_create_with_auto_numbering(self, user_logado, camara, autor, orgao):
        """POST com numeração automática cria indicação e redireciona."""
        url = reverse("indicacoes:create")
        
        data = {
            "tipo_numeracao": "auto",
            "orgao": orgao.id,
            "autor": autor.id,
            "data": "2026-01-15",
            "assunto": "Nova Indicação",
            "solicitacao": "Solicitação teste",
            "justificativa": "Justificativa teste",
            "e_conjunto": False,
        }
        
        response = user_logado.post(url, data)
        
        assert response.status_code == 302
        assert Indicacao.objects.filter(assunto="Nova Indicação").exists()
        
        ind = Indicacao.objects.get(assunto="Nova Indicação")
        assert ind.numero == "001/2026"
        assert ind.camara == camara

    def test_create_with_manual_numbering_valid(self, user_logado, camara, autor, orgao):
        """POST com numeração manual (válida) cria indicação."""
        url = reverse("indicacoes:create")
        
        data = {
            "tipo_numeracao": "manual",
            "numero_manual": "005",
            "orgao": orgao.id,
            "autor": autor.id,
            "data": "2026-01-15",
            "assunto": "Indicação Manual",
            "solicitacao": "Solicitação",
            "justificativa": "Justificativa",
            "e_conjunto": False,
        }
        
        response = user_logado.post(url, data)
        
        assert response.status_code == 302
        ind = Indicacao.objects.get(assunto="Indicação Manual")
        assert ind.numero == "005/2026"

    def test_create_with_manual_numbering_missing_number(self, user_logado, camara, autor, orgao):
        """POST com numeração manual sem número mostra erro."""
        url = reverse("indicacoes:create")
        
        data = {
            "tipo_numeracao": "manual",
            "numero_manual": "",  # Sem número
            "orgao": orgao.id,
            "autor": autor.id,
            "data": "2026-01-15",
            "assunto": "Indicação Manual",
            "solicitacao": "Solicitação",
            "justificativa": "Justificativa",
            "e_conjunto": False,
        }
        
        response = user_logado.post(url, data)
        
        assert response.status_code == 200  # Re-render form
        assert "form" in response.context
        form = response.context["form"]
        assert form.errors  # Tem erros

    def test_create_with_coautores(self, user_logado, camara, autor, outro_autor, orgao):
        """POST com coautores salva relação."""
        url = reverse("indicacoes:create")
        
        data = {
            "tipo_numeracao": "auto",
            "orgao": orgao.id,
            "autor": autor.id,
            "data": "2026-01-15",
            "assunto": "Com Coautores",
            "solicitacao": "Solicitação",
            "justificativa": "Justificativa",
            "e_conjunto": True,
            "coautores": [outro_autor.id],
        }
        
        response = user_logado.post(url, data)
        
        assert response.status_code == 302
        ind = Indicacao.objects.get(assunto="Com Coautores")
        assert ind.e_conjunto is True
        assert outro_autor in ind.coautores.all()


class TestIndicacaoEditView:
    """Testes para indicacao_edit view."""

    def test_edit_requires_login(self, client, indicacao):
        """GET sem autenticação redireciona para login."""
        url = reverse("indicacoes:edit", kwargs={"pk": indicacao.pk})
        response = client.get(url)
        assert response.status_code == 302

    def test_edit_returns_404_for_other_camara(self, client, user, camara, outra_camara, indicacao):
        """GET para indicação de outra câmara retorna 404."""
        from core.models import UsuarioPerfil
        
        # Usuário de outra câmara
        UsuarioPerfil.objects.create(
            user=user, camara=outra_camara, nome="User", cargo=UsuarioPerfil.Cargo.PARLAMENTAR
        )
        client.login(username="testuser", password="testpass123")
        
        url = reverse("indicacoes:edit", kwargs={"pk": indicacao.pk})
        response = client.get(url)
        assert response.status_code == 404

    def test_edit_get_prefills_form(self, user_logado, indicacao):
        """GET preenche formulário com dados existentes."""
        url = reverse("indicacoes:edit", kwargs={"pk": indicacao.pk})
        response = user_logado.get(url)
        
        assert response.status_code == 200
        form = response.context["form"]
        assert form["assunto"].value() == indicacao.assunto
        assert form["solicitacao"].value() == indicacao.solicitacao

    def test_edit_post_updates_indicacao(self, user_logado, indicacao, orgao):
        """POST atualiza campos da indicação."""
        url = reverse("indicacoes:edit", kwargs={"pk": indicacao.pk})
        
        data = {
            "orgao": orgao.id,
            "autor": indicacao.autor.id,
            "data": "2026-02-20",
            "assunto": "Assunto Atualizado",
            "solicitacao": "Solicitação Atualizada",
            "justificativa": "Justificativa Atualizada",
            "e_conjunto": False,
        }
        
        response = user_logado.post(url, data)
        
        assert response.status_code == 302
        indicacao.refresh_from_db()
        assert indicacao.assunto == "Assunto Atualizado"
        assert indicacao.data == date(2026, 2, 20)

    def test_edit_post_invalid_rerenders(self, user_logado, indicacao):
        """POST inválido (sem autor) re-renderiza formulário com erros."""
        url = reverse("indicacoes:edit", kwargs={"pk": indicacao.pk})
        
        data = {
            "orgao": indicacao.orgao.id,
            # Falta: autor (obrigatório)
            "data": "2026-02-20",
            "assunto": "Assunto",
            "solicitacao": "Solicitação",
            "justificativa": "Justificativa",
            "e_conjunto": False,
        }
        
        response = user_logado.post(url, data)
        
        assert response.status_code == 200
        assert response.context["form"].errors
        assert "autor" in response.context["form"].errors

    def test_edit_removes_numeracao_fields(self, user_logado, indicacao):
        """Formulário em modo edit remove campos de numeração."""
        url = reverse("indicacoes:edit", kwargs={"pk": indicacao.pk})
        response = user_logado.get(url)
        
        form = response.context["form"]
        assert "tipo_numeracao" not in form.fields
        assert "numero_manual" not in form.fields


class TestIndicacaoPreviewView:
    """Testes para indicacao_preview view."""

    def test_preview_requires_login(self, client, indicacao):
        """GET sem autenticação redireciona para login."""
        url = reverse("indicacoes:preview", kwargs={"pk": indicacao.pk})
        response = client.get(url)
        assert response.status_code == 302

    def test_preview_returns_404_for_other_camara(self, client, user, camara, outra_camara, indicacao):
        """GET para indicação de outra câmara retorna 404."""
        from core.models import UsuarioPerfil
        
        UsuarioPerfil.objects.create(
            user=user, camara=outra_camara, nome="User", cargo=UsuarioPerfil.Cargo.PARLAMENTAR
        )
        client.login(username="testuser", password="testpass123")
        
        url = reverse("indicacoes:preview", kwargs={"pk": indicacao.pk})
        response = client.get(url)
        assert response.status_code == 404

    def test_preview_full_page(self, user_logado, indicacao):
        """GET sem HTMX retorna página completa."""
        url = reverse("indicacoes:preview", kwargs={"pk": indicacao.pk})
        response = user_logado.get(url)
        
        assert response.status_code == 200
        assert "indicacoes/indicacao_detail.html" in [t.name for t in response.templates]
        assert response.context["indicacao"] == indicacao

    def test_preview_htmx_partial(self, user_logado, indicacao):
        """GET com header HTMX retorna fragmento."""
        url = reverse("indicacoes:preview", kwargs={"pk": indicacao.pk})
        response = user_logado.get(url, HTTP_HX_REQUEST="true")
        
        assert response.status_code == 200
        assert "indicacoes/_preview.html" in [t.name for t in response.templates]
        assert response.context["indicacao"] == indicacao


class TestIndicacaoPdfView:
    """Testes para indicacao_generate_pdf view."""

    def test_pdf_requires_login(self, client, indicacao):
        """GET sem autenticação redireciona para login."""
        url = reverse("indicacoes:generate_pdf", kwargs={"pk": indicacao.pk})
        response = client.get(url)
        assert response.status_code == 302

    def test_pdf_returns_404_for_other_camara(self, client, user, camara, outra_camara, indicacao):
        """GET para indicação de outra câmara retorna 404."""
        from core.models import UsuarioPerfil
        
        UsuarioPerfil.objects.create(
            user=user, camara=outra_camara, nome="User", cargo=UsuarioPerfil.Cargo.PARLAMENTAR
        )
        client.login(username="testuser", password="testpass123")
        
        url = reverse("indicacoes:generate_pdf", kwargs={"pk": indicacao.pk})
        response = client.get(url)
        assert response.status_code == 404

    @patch("indicacoes.services.PdfService.gerar_indicacao")
    def test_pdf_returns_pdf_content(self, mock_pdf, user_logado, indicacao):
        """GET retorna PDF com content-type correto."""
        mock_pdf.return_value = b"%PDF-1.4 fake pdf content"
        
        url = reverse("indicacoes:generate_pdf", kwargs={"pk": indicacao.pk})
        response = user_logado.get(url)
        
        assert response.status_code == 200
        assert response["Content-Type"] == "application/pdf"
        assert b"%PDF" in response.content

    @patch("indicacoes.services.PdfService.gerar_indicacao")
    def test_pdf_filename_in_header(self, mock_pdf, user_logado, indicacao):
        """GET define filename correto no header."""
        mock_pdf.return_value = b"%PDF-1.4 fake"
        
        url = reverse("indicacoes:generate_pdf", kwargs={"pk": indicacao.pk})
        response = user_logado.get(url)
        
        disposition = response["Content-Disposition"]
        assert "inline" in disposition
        assert f"indicacao_{indicacao.numero}" in disposition


class TestIndicacaoSearchView:
    """Testes para indicacao_search view."""

    def test_search_requires_login(self, client):
        """GET sem autenticação redireciona para login."""
        url = reverse("indicacoes:search")
        response = client.get(url)
        assert response.status_code == 302

    def test_search_no_query_returns_all(self, user_logado, indicacao_list):
        """GET sem query retorna todas as indicações (paginado)."""
        url = reverse("indicacoes:search")
        response = user_logado.get(url)
        
        assert response.status_code == 200
        page_obj = response.context["page_obj"]
        assert len(page_obj.object_list) == 5  # 5 por página

    def test_search_filters_by_subject(self, user_logado, camara, autor, orgao):
        """GET com query filtra por assunto (icontains)."""
        # Criar indicações com diferentes assuntos
        Indicacao.objects.create(
            camara=camara, autor=autor, orgao=orgao,
            numero="001/2026", data=date(2026, 1, 1),
            assunto="Infraestrutura Viária",
            solicitacao="Sol", justificativa="Just"
        )
        Indicacao.objects.create(
            camara=camara, autor=autor, orgao=orgao,
            numero="002/2026", data=date(2026, 1, 2),
            assunto="Saúde Pública",
            solicitacao="Sol", justificativa="Just"
        )
        
        url = reverse("indicacoes:search") + "?q=Infraestrutura"
        response = user_logado.get(url)
        
        page_obj = response.context["page_obj"]
        assert len(page_obj.object_list) == 1
        assert page_obj.object_list[0].assunto == "Infraestrutura Viária"

    def test_search_no_results(self, user_logado, indicacao_list):
        """GET com query que não encontra nada retorna lista vazia."""
        url = reverse("indicacoes:search") + "?q=XYZ999"
        response = user_logado.get(url)
        
        page_obj = response.context["page_obj"]
        assert len(page_obj.object_list) == 0

    def test_search_pagination(self, user_logado, indicacao_list):
        """Resultados de busca respeitam paginação."""
        url = reverse("indicacoes:search") + "?page=2"
        response = user_logado.get(url)
        
        page_obj = response.context["page_obj"]
        assert len(page_obj.object_list) == 2  # 7 items = 2 páginas

    def test_search_case_insensitive(self, user_logado, camara, autor, orgao):
        """Busca é case-insensitive."""
        Indicacao.objects.create(
            camara=camara, autor=autor, orgao=orgao,
            numero="001/2026", data=date(2026, 1, 1),
            assunto="EDUCAÇÃO FORMAL",
            solicitacao="Sol", justificativa="Just"
        )
        
        url = reverse("indicacoes:search") + "?q=educação"
        response = user_logado.get(url)
        
        page_obj = response.context["page_obj"]
        assert len(page_obj.object_list) == 1


class TestIndicacaoDeleteView:
    """Testes para indicacao_delete view."""

    def test_delete_requires_login(self, client, indicacao):
        """GET sem autenticação redireciona para login."""
        url = reverse("indicacoes:delete", kwargs={"pk": indicacao.pk})
        response = client.get(url)
        assert response.status_code == 302

    def test_delete_get_shows_confirmation(self, user_logado, indicacao):
        """GET mostra página de confirmação."""
        url = reverse("indicacoes:delete", kwargs={"pk": indicacao.pk})
        response = user_logado.get(url)
        
        assert response.status_code == 200
        assert "indicacoes/indicacao_confirm_delete.html" in [t.name for t in response.templates]
        assert response.context["indicacao"] == indicacao

    def test_delete_post_deletes_indicacao(self, user_logado, indicacao):
        """POST deleta indicação e redireciona."""
        pk = indicacao.pk
        url = reverse("indicacoes:delete", kwargs={"pk": pk})
        
        response = user_logado.post(url)
        
        assert response.status_code == 302
        assert not Indicacao.objects.filter(pk=pk).exists()

    def test_delete_post_shows_success_message(self, user_logado, indicacao):
        """POST deleta e exibe mensagem de sucesso."""
        url = reverse("indicacoes:delete", kwargs={"pk": indicacao.pk})
        numero = indicacao.numero
        
        response = user_logado.post(url, follow=True)
        
        messages = list(response.context["messages"])
        assert len(messages) == 1
        assert "excluída com sucesso" in str(messages[0])
        assert numero in str(messages[0])

    def test_delete_redirects_to_list(self, user_logado, indicacao):
        """POST após delete redireciona para lista."""
        url = reverse("indicacoes:delete", kwargs={"pk": indicacao.pk})
        response = user_logado.post(url, follow=True)
        
        assert response.resolver_match.url_name == "list"

    def test_delete_returns_404_for_other_camara(self, client, user, camara, outra_camara, indicacao):
        """Deletar indicação de outra câmara retorna 404."""
        from core.models import UsuarioPerfil
        
        UsuarioPerfil.objects.create(
            user=user, camara=outra_camara, nome="User", cargo=UsuarioPerfil.Cargo.PARLAMENTAR
        )
        client.login(username="testuser", password="testpass123")
        
        url = reverse("indicacoes:delete", kwargs={"pk": indicacao.pk})
        response = client.get(url)
        assert response.status_code == 404
