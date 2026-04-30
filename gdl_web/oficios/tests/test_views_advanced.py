"""Testes avançados para oficios.views - cobrindo paths complexos"""
import pytest
from datetime import date
from unittest.mock import patch, MagicMock

from django.urls import reverse
from django.contrib.auth import get_user_model

from autores.models import Autor
from core.models import Numeracao
from oficios.models import Oficio, OficioEncaminhamento
from orgaos.models import Orgao
from orgaos_externos.models import OrgaoExterno
from sessoes.models import SessaoLegislativa
from legislaturas.models import Legislatura

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
def sessao_legislativa(camara):
    """Sessão legislativa de teste."""
    leg = Legislatura.objects.create(
        numero=8,
        data_eleicao=date(2020, 11, 15),
        data_inicio=date(2021, 1, 1),
        data_fim=date(2024, 12, 31),
        camara=camara,
    )
    return SessaoLegislativa.objects.create(
        legislatura=leg,
        numero=1,
        categoria="ORDINARIA",
        data=date(2026, 2, 1),
        camara=camara,
    )


@pytest.fixture
def orgao_externo(camara):
    """Órgão externo para teste de catálogo."""
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
def oficio_livre(camara, autor, orgao):
    """Ofício livre de teste."""
    return Oficio.objects.create(
        camara=camara,
        tipo=Oficio.Tipo.LIVRE,
        autor=autor,
        orgao=orgao,
        numero="001/2026",
        data=date(2026, 1, 15),
        corpo="Corpo do ofício",
        destinatario_nome="Destinatário",
        destinatario_cargo="Cargo",
        destinatario_orgao="Órgão",
        assunto="Assunto teste",
    )


@pytest.fixture
def oficio_encaminhamento(camara, presidente, orgao, sessao_legislativa, outro_autor):
    """Ofício de encaminhamento de teste."""
    oficio = Oficio.objects.create(
        camara=camara,
        tipo=Oficio.Tipo.ENCAMINHAMENTO,
        autor=presidente,
        orgao=orgao,
        numero="002/2026",
        data=date(2026, 1, 20),
        corpo="Encaminhamento",
        destinatario_nome="Destinatário Enc",
        destinatario_cargo="Cargo Enc",
        destinatario_orgao="Órgão Enc",
        assunto="Encaminhamento",
    )
    
    OficioEncaminhamento.objects.create(
        oficio=oficio,
        sessao=sessao_legislativa,
        votacao="Votação teste",
        proposicao="PL 001/2026",
        autor_proposicao=outro_autor,
        data_aprovacao=sessao_legislativa.data,
    )
    
    return oficio


class TestOficioTypeSelector:
    """Testes para seletor de tipo de ofício."""

    def test_create_without_tipo_shows_selector(self, user_logado):
        """GET sem tipo mostra seletor."""
        url = reverse("oficios:create")
        response = user_logado.get(url)
        
        assert response.status_code == 200
        assert "oficios/tipo_select.html" in [t.name for t in response.templates]

    def test_create_with_tipo_libre_shows_form(self, user_logado, camara):
        """GET com tipo=livre mostra formulário correto."""
        url = reverse("oficios:create") + "?tipo=livre"
        response = user_logado.get(url)
        
        assert response.status_code == 200
        assert "oficios/oficio_form.html" in [t.name for t in response.templates]

    def test_create_with_tipo_encaminhamento_shows_form(self, user_logado, presidente):
        """GET com tipo=encaminhamento mostra formulário quando presidente existe."""
        url = reverse("oficios:create") + "?tipo=encaminhamento"
        response = user_logado.get(url)
        
        assert response.status_code == 200
        assert "oficios/oficio_encaminhamento_form.html" in [t.name for t in response.templates]


class TestOficioEncaminhamentoNaoPresidente:
    """Testes para error handling quando não há presidente."""

    def test_encaminhamento_requires_presidente(self, user_logado, camara):
        """GET encaminhamento sem presidente redireciona com erro."""
        # Câmara sem presidente
        url = reverse("oficios:create") + "?tipo=encaminhamento"
        response = user_logado.get(url)
        
        assert response.status_code == 302
        assert response.url == reverse("oficios:list")


class TestOficioLivreCrud:
    """Testes para CRUD de ofício livre."""

    def test_create_livre_auto_numbering(self, user_logado, camara, autor, orgao):
        """POST ofício livre com numeração automática."""
        url = reverse("oficios:create") + "?tipo=libre"
        
        data = {
            "tipo_numeracao": "auto",
            "selecao_destino": "manual",
            "orgao": orgao.id,
            "autor": autor.id,
            "data": "2026-03-01",
            "corpo": "Corpo do ofício",
            "destinatario_nome": "Dest",
            "destinatario_cargo": "Cargo",
            "destinatario_orgao": "Órgão",
            "destinatario_pronome": "Sr.",
            "destinatario_endereco": "Rua 1",
            "assunto": "Assunto",
            "e_conjunto": False,
        }
        
        response = user_logado.post(url, data)
        
        assert response.status_code == 302
        oficio = Oficio.objects.filter(assunto="Assunto").first()
        assert oficio is not None
        assert oficio.tipo == Oficio.Tipo.LIVRE
        assert oficio.numero == "001/2026"

    def test_create_livre_manual_numbering(self, user_logado, camara, autor, orgao):
        """POST ofício livre com numeração manual."""
        url = reverse("oficios:create") + "?tipo=libre"
        
        data = {
            "tipo_numeracao": "manual",
            "numero_manual": "010",
            "selecao_destino": "manual",
            "orgao": orgao.id,
            "autor": autor.id,
            "data": "2026-03-01",
            "corpo": "Corpo",
            "destinatario_nome": "Dest",
            "destinatario_cargo": "Cargo",
            "destinatario_orgao": "Órgão",
            "destinatario_pronome": "Sr.",
            "destinatario_endereco": "Rua 1",
            "assunto": "Manual",
            "e_conjunto": False,
        }
        
        response = user_logado.post(url, data)
        
        assert response.status_code == 302
        oficio = Oficio.objects.filter(assunto="Manual").first()
        assert oficio.numero == "010/2026"

    def test_create_livre_from_catalog(self, user_logado, camara, autor, orgao, orgao_externo):
        """POST ofício livre usando catalogo externo."""
        url = reverse("oficios:create") + "?tipo=libre"
        
        data = {
            "tipo_numeracao": "auto",
            "selecao_destino": "catalogo",
            "orgao": orgao.id,
            "autor": autor.id,
            "data": "2026-03-01",
            "corpo": "Corpo",
            "orgao_externo": orgao_externo.id,
            "assunto": "Catalogo",
            "e_conjunto": False,
        }
        
        response = user_logado.post(url, data)
        
        assert response.status_code == 302
        oficio = Oficio.objects.filter(assunto="Catalogo").first()
        assert oficio.destinatario_nome == orgao_externo.responsavel
        assert oficio.destinatario_cargo == orgao_externo.cargo

    def test_edit_livre(self, user_logado, oficio_livre):
        """POST edita ofício livre."""
        url = reverse("oficios:edit", kwargs={"pk": oficio_livre.pk})
        
        data = {
            "selecao_destino": "manual",
            "orgao": oficio_livre.orgao.id,
            "autor": oficio_livre.autor.id,
            "data": "2026-04-01",
            "corpo": "Corpo atualizado",
            "destinatario_nome": "Novo Dest",
            "destinatario_cargo": "Novo Cargo",
            "destinatario_orgao": "Novo Órgão",
            "destinatario_pronome": "Sra.",
            "destinatario_endereco": "Rua 2",
            "assunto": "Assunto novo",
            "e_conjunto": False,
        }
        
        response = user_logado.post(url, data)
        
        assert response.status_code == 302
        oficio_livre.refresh_from_db()
        assert oficio_livre.assunto == "Assunto novo"
        assert oficio_livre.destinatario_nome == "Novo Dest"


class TestOficioEncaminhamentoCrud:
    """Testes para CRUD de ofício de encaminhamento."""




class TestOficioComCoautores:
    """Testes para ofícios com coautores."""

    def test_create_livre_with_coautores(self, user_logado, camara, autor, outro_autor, orgao):
        """POST ofício livre com coautores."""
        url = reverse("oficios:create") + "?tipo=libre"
        
        data = {
            "tipo_numeracao": "auto",
            "selecao_destino": "manual",
            "orgao": orgao.id,
            "autor": autor.id,
            "data": "2026-03-01",
            "corpo": "Corpo",
            "destinatario_nome": "Dest",
            "destinatario_cargo": "Cargo",
            "destinatario_orgao": "Órgão",
            "destinatario_pronome": "Sr.",
            "destinatario_endereco": "Rua 1",
            "assunto": "Com Coautores",
            "e_conjunto": True,
            "coautores": [outro_autor.id],
        }
        
        response = user_logado.post(url, data)
        
        assert response.status_code == 302
        oficio = Oficio.objects.filter(assunto="Com Coautores").first()
        assert oficio.e_conjunto is True
        assert outro_autor in oficio.coautores.all()


class TestOficioListView:
    """Testes para lista de ofícios."""

    def test_list_pagination(self, user_logado, camara, autor, orgao):
        """Lista com paginação mostra 5 items por página."""
        # Criar 7 ofícios
        for i in range(1, 8):
            Oficio.objects.create(
                camara=camara,
                tipo=Oficio.Tipo.LIVRE,
                autor=autor,
                orgao=orgao,
                numero=f"{i:03d}/2026",
                data=date(2026, 1, i),
                corpo="Corpo",
                destinatario_nome="Dest",
                destinatario_cargo="Cargo",
                destinatario_orgao="Órgão",
                assunto=f"Ofício {i}",
            )
        
        url = reverse("oficios:list")
        response = user_logado.get(url)
        
        page_obj = response.context["page_obj"]
        assert len(page_obj.object_list) == 5
        assert page_obj.paginator.num_pages == 2


class TestOficioPreviewView:
    """Testes para preview."""

    def test_preview_full_page(self, user_logado, oficio_livre):
        """Preview sem HTMX retorna página completa."""
        url = reverse("oficios:preview", kwargs={"pk": oficio_livre.pk})
        response = user_logado.get(url)
        
        assert response.status_code == 200
        assert "oficios/oficio_detail.html" in [t.name for t in response.templates]

    def test_preview_htmx(self, user_logado, oficio_livre):
        """Preview com HTMX retorna fragmento."""
        url = reverse("oficios:preview", kwargs={"pk": oficio_livre.pk})
        response = user_logado.get(url, HTTP_HX_REQUEST="true")
        
        assert response.status_code == 200
        assert "oficios/_preview.html" in [t.name for t in response.templates]


class TestOficioPdfView:
    """Testes para geração de PDF."""

    @patch("weasyprint.HTML")
    def test_pdf_generation(self, mock_html_class, user_logado, oficio_livre):
        """PDF é gerado com sucesso."""
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b"%PDF-1.4 fake"
        mock_html_class.return_value = mock_html_instance
        
        url = reverse("oficios:generate_pdf", kwargs={"pk": oficio_livre.pk})
        response = user_logado.get(url)
        
        assert response.status_code == 200
        assert response["Content-Type"] == "application/pdf"


class TestOficioSearchView:
    """Testes para busca de ofícios."""

    def test_search_by_subject(self, user_logado, camara, autor, orgao):
        """Busca por assunto filtra corretamente."""
        Oficio.objects.create(
            camara=camara, tipo=Oficio.Tipo.LIVRE, autor=autor, orgao=orgao,
            numero="001/2026", data=date(2026, 1, 1),
            corpo="C", destinatario_nome="D", destinatario_cargo="C", 
            destinatario_orgao="O", assunto="Infraestrutura"
        )
        Oficio.objects.create(
            camara=camara, tipo=Oficio.Tipo.LIVRE, autor=autor, orgao=orgao,
            numero="002/2026", data=date(2026, 1, 2),
            corpo="C", destinatario_nome="D", destinatario_cargo="C",
            destinatario_orgao="O", assunto="Saúde"
        )
        
        url = reverse("oficios:search") + "?q=Infra"
        response = user_logado.get(url)
        
        page_obj = response.context["page_obj"]
        assert len(page_obj.object_list) == 1


class TestOficioDeleteView:
    """Testes para delete."""

    def test_delete_oficio(self, user_logado, oficio_livre):
        """POST deleta ofício."""
        pk = oficio_livre.pk
        url = reverse("oficios:delete", kwargs={"pk": pk})
        
        response = user_logado.post(url)
        
        assert response.status_code == 302
        assert not Oficio.objects.filter(pk=pk).exists()


class TestOficioTenancy:
    """Testes para isolamento de tenant."""

    def test_cannot_edit_other_camara_oficio(self, client, user, camara, outra_camara):
        """Não pode editar ofício de outra câmara."""
        from core.models import UsuarioPerfil
        
        # Criar ofício em camara
        autor1 = Autor.objects.create(camara=camara, nome="A1", cargo=Autor.Cargo.VEREADOR)
        orgao1 = Orgao.objects.create(camara=camara, nome="O1")
        oficio = Oficio.objects.create(
            camara=camara, tipo=Oficio.Tipo.LIVRE, autor=autor1, orgao=orgao1,
            numero="001/2026", data=date(2026, 1, 1),
            corpo="C", destinatario_nome="D", destinatario_cargo="C",
            destinatario_orgao="O", assunto="Test"
        )
        
        # Autenticar como outra_camara
        UsuarioPerfil.objects.create(
            user=user, camara=outra_camara, nome="User", cargo=UsuarioPerfil.Cargo.PARLAMENTAR
        )
        client.login(username="testuser", password="testpass123")
        
        url = reverse("oficios:edit", kwargs={"pk": oficio.pk})
        response = client.get(url)
        
        assert response.status_code == 404
