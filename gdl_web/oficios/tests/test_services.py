"""Testes para NumeracaoService e PdfService."""

import pytest
from datetime import date
from unittest.mock import patch

from core.models import Numeracao
from oficios.models import Oficio
from oficios.services import NumeracaoService, PdfService


class TestNumeracaoService:
    def test_proximo_numero_sequencial(self, camara, autor):
        numero = NumeracaoService.proximo_numero(camara, None, autor)
        ano = date.today().year
        assert numero == f"001/{ano}"

    def test_proximo_numero_incrementa(self, camara, autor):
        NumeracaoService.proximo_numero(camara, None, autor)
        numero = NumeracaoService.proximo_numero(camara, None, autor)
        ano = date.today().year
        assert numero == f"002/{ano}"

    def test_proximo_numero_autor_diferente(self, camara, autor, outro_autor):
        NumeracaoService.proximo_numero(camara, None, autor)
        numero = NumeracaoService.proximo_numero(camara, None, outro_autor)
        ano = date.today().year
        # Autores diferentes têm numeração independente
        assert numero == f"001/{ano}"

    def test_registrar_numero_manual_valido(self, camara, autor):
        numero = NumeracaoService.registrar_numero_manual(camara, None, autor, 10)
        ano = date.today().year
        assert numero == f"010/{ano}"

    def test_registrar_numero_manual_atualiza_ultimo(self, camara, autor):
        NumeracaoService.registrar_numero_manual(camara, None, autor, 10)
        ano = date.today().year
        numeracao = Numeracao.objects.get(camara=camara, orgao=None, autor=autor, ano=ano)
        assert numeracao.ultimo_numero == 10

    def test_registrar_numero_manual_igual_rejeita(self, camara, autor):
        NumeracaoService.proximo_numero(camara, None, autor)  # ultimo_numero = 1
        with pytest.raises(ValueError, match="não é válido"):
            NumeracaoService.registrar_numero_manual(camara, None, autor, 1)

    def test_registrar_numero_manual_menor_rejeita(self, camara, autor):
        NumeracaoService.registrar_numero_manual(camara, None, autor, 10)
        with pytest.raises(ValueError, match="último número registrado"):
            NumeracaoService.registrar_numero_manual(camara, None, autor, 5)


class TestPdfService:
    @pytest.fixture
    def oficio(self, camara, autor):
        return Oficio.objects.create(
            camara=camara, autor=autor, numero="001/2026",
            assunto="Teste PDF", corpo="Corpo do ofício para PDF.",
            data=date(2026, 3, 15),
            destinatario_nome="Sr. Fulano",
            destinatario_cargo="Prefeito",
            destinatario_orgao="Prefeitura",
            destinatario_endereco="Rua X, 123",
            destinatario_pronome="Excelentíssimo",
        )

    def test_pdf_gera_sem_erro(self, oficio, camara):
        pdf = PdfService.gerar_oficio(oficio, camara)
        assert isinstance(pdf, bytes)
        assert len(pdf) > 0

    def test_pdf_contem_dados(self, oficio, camara):
        pdf = PdfService.gerar_oficio(oficio, camara)
        # PDFs começam com %PDF
        assert pdf[:5] == b"%PDF-"
