"""Testes para o OficioForm."""

import pytest
from datetime import date

from oficios.forms import OficioForm


class TestOficioForm:
    @pytest.fixture
    def dados_validos(self, autor):
        return {
            "autor": autor.pk,
            "assunto": "Solicitação de melhorias",
            "corpo": "Venho por meio deste solicitar...",
            "data": date(2026, 3, 15),
            "destinatario_nome": "Sr. José Santos",
            "destinatario_cargo": "Prefeito Municipal",
            "destinatario_orgao": "Prefeitura Municipal",
            "destinatario_endereco": "Rua Central, 1",
            "destinatario_pronome": "Excelentíssimo",
        }

    def test_form_valido(self, camara, dados_validos):
        form = OficioForm(data=dados_validos, camara=camara)
        assert form.is_valid(), form.errors

    def test_assunto_vazio(self, camara, dados_validos):
        dados_validos["assunto"] = ""
        form = OficioForm(data=dados_validos, camara=camara)
        assert not form.is_valid()
        assert "assunto" in form.errors

    def test_corpo_vazio(self, camara, dados_validos):
        dados_validos["corpo"] = ""
        form = OficioForm(data=dados_validos, camara=camara)
        assert not form.is_valid()
        assert "corpo" in form.errors

    def test_destinatario_incompleto(self, camara, dados_validos):
        dados_validos["destinatario_nome"] = ""
        form = OficioForm(data=dados_validos, camara=camara)
        assert not form.is_valid()
        assert "destinatario_nome" in form.errors

    def test_filtra_autores_por_camara(self, camara, autor, outra_camara):
        from autores.models import Autor

        autor_outra = Autor.objects.create(
            nome="Outro", cargo=Autor.Cargo.VEREADOR, camara=outra_camara
        )
        form = OficioForm(camara=camara)
        queryset = form.fields["autor"].queryset
        assert autor in queryset
        assert autor_outra not in queryset
