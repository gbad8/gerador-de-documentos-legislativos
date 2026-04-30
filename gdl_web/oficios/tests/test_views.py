"""Testes para as views do app oficios."""

import pytest
from datetime import date

from oficios.models import Oficio


@pytest.fixture
def oficio(camara, autor):
    return Oficio.objects.create(
        camara=camara, autor=autor, numero="001/2026",
        assunto="Teste", corpo="Corpo do ofício",
        data=date(2026, 1, 15),
        destinatario_nome="Fulano", destinatario_cargo="Prefeito",
        destinatario_orgao="Prefeitura", destinatario_endereco="Rua X",
        destinatario_pronome="Excelentíssimo",
    )


@pytest.fixture
def dados_post(autor):
    return {
        "tipo_numeracao": "auto",
        "autor": autor.pk,
        "assunto": "Novo ofício",
        "corpo": "Corpo do novo ofício.",
        "data": "2026-03-15",
        "destinatario_nome": "Sr. José",
        "destinatario_cargo": "Prefeito",
        "destinatario_orgao": "Prefeitura",
        "destinatario_endereco": "Rua Y, 456",
        "destinatario_pronome": "Excelentíssimo",
        "selecao_destino": "manual",
    }


class TestOficioList:
    def test_requer_login(self, client):
        response = client.get("/painel/oficios/")
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_exibe_oficios(self, user_logado, oficio):
        response = user_logado.get("/painel/oficios/")
        assert response.status_code == 200
        assert "Teste" in response.content.decode()


class TestOficioCreate:
    def test_post_valido_cria_e_redireciona(self, user_logado, dados_post):
        response = user_logado.post("/painel/oficios/novo/?tipo=livre", dados_post)
        assert response.status_code == 302
        assert Oficio.objects.count() == 1

    def test_post_com_numero_manual_valido(self, user_logado, dados_post):
        dados_post["tipo_numeracao"] = "manual"
        dados_post["numero_manual"] = 5
        response = user_logado.post("/painel/oficios/novo/?tipo=livre", dados_post)
        assert response.status_code == 302
        oficio = Oficio.objects.first()
        assert "005/" in oficio.numero

    def test_post_com_numero_manual_invalido(self, user_logado, dados_post):
        # Criar um ofício primeiro para estabelecer ultimo_numero = 1
        user_logado.post("/painel/oficios/novo/?tipo=livre", dados_post)
        dados_post["tipo_numeracao"] = "manual"
        dados_post["numero_manual"] = 1  # igual ao ultimo_numero
        response = user_logado.post("/painel/oficios/novo/?tipo=livre", dados_post)
        assert response.status_code == 200
        assert "form" in response.context

    def test_post_invalido_retorna_form(self, user_logado, dados_post):
        dados_post["assunto"] = ""
        response = user_logado.post("/painel/oficios/novo/?tipo=livre", dados_post)
        assert response.status_code == 200
        assert "form" in response.context


class TestOficioEdit:
    def test_edita_e_redireciona(self, user_logado, oficio, dados_post):
        dados_post["assunto"] = "Assunto editado"
        response = user_logado.post(f"/painel/oficios/{oficio.pk}/editar/", dados_post)
        assert response.status_code == 302
        oficio.refresh_from_db()
        assert oficio.assunto == "Assunto editado"


class TestOficioPreview:
    def test_preview_html(self, user_logado, oficio):
        response = user_logado.get(f"/painel/oficios/{oficio.pk}/preview/")
        assert response.status_code == 200
        assert "oficio" in response.context

    def test_preview_htmx(self, user_logado, oficio):
        response = user_logado.get(
            f"/painel/oficios/{oficio.pk}/preview/",
            HTTP_HX_REQUEST="true",
        )
        assert response.status_code == 200
        # HTMX retorna o partial (sem base.html completo)
        content = response.content.decode()
        assert "<!DOCTYPE html>" not in content


class TestOficioSearch:
    def test_filtra_por_assunto(self, user_logado, oficio):
        response = user_logado.get("/painel/oficios/busca/", {"q": "Teste"})
        assert response.status_code == 200
        assert "Teste" in response.content.decode()

    def test_busca_sem_resultado(self, user_logado, oficio):
        response = user_logado.get("/painel/oficios/busca/", {"q": "inexistente"})
        assert response.status_code == 200
        assert "Nenhum ofício encontrado" in response.content.decode()


class TestIsolamentoTenant:
    def test_usuario_nao_ve_oficios_outra_camara(
        self, user_logado, outra_camara, autor
    ):
        from autores.models import Autor as AutorModel

        autor_outra = AutorModel.objects.create(
            nome="Outro", cargo=AutorModel.Cargo.VEREADOR, camara=outra_camara
        )
        Oficio.objects.create(
            camara=outra_camara, autor=autor_outra, numero="001/2026",
            assunto="Ofício oculto", corpo="Não deveria aparecer",
            data=date(2026, 1, 1),
            destinatario_nome="X", destinatario_cargo="Y",
            destinatario_orgao="Z", destinatario_endereco="W",
            destinatario_pronome="V",
        )
        response = user_logado.get("/painel/oficios/")
        assert "Ofício oculto" not in response.content.decode()
