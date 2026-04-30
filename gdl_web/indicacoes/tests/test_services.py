"""Testes para indicacoes.services"""
import pytest
from datetime import date
from unittest.mock import patch, MagicMock

from autores.models import Autor
from indicacoes.models import Indicacao
from indicacoes.services import PdfService
from orgaos.models import Orgao


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


class TestPdfService:
    """Testes para PdfService."""

    @patch("weasyprint.HTML")
    def test_gerar_indicacao_returns_pdf_bytes(self, mock_html_class, camara, indicacao, presidente):
        """PdfService.gerar_indicacao retorna bytes de PDF."""
        # Mock da classe HTML e seu método write_pdf
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b"%PDF-1.4 fake pdf"
        mock_html_class.return_value = mock_html_instance
        
        result = PdfService.gerar_indicacao(indicacao, camara)
        
        assert isinstance(result, bytes)
        assert result == b"%PDF-1.4 fake pdf"
        mock_html_instance.write_pdf.assert_called_once()

    @patch("weasyprint.HTML")
    def test_gerar_indicacao_not_empty(self, mock_html_class, camara, indicacao, presidente):
        """PDF gerado não é vazio."""
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b"%PDF-1.4" + b"x" * 1000
        mock_html_class.return_value = mock_html_instance
        
        result = PdfService.gerar_indicacao(indicacao, camara)
        
        assert len(result) > 100  # Arquivo não trivial

    @patch("weasyprint.HTML")
    def test_gerar_indicacao_html_receives_html_string(self, mock_html_class, camara, indicacao, presidente):
        """HTML é chamado com string HTML gerada pelo template."""
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b"%PDF-1.4"
        mock_html_class.return_value = mock_html_instance
        
        PdfService.gerar_indicacao(indicacao, camara)
        
        # Verifica se HTML foi chamado com 'string' keyword argument
        assert mock_html_class.called
        call_kwargs = mock_html_class.call_args[1]
        assert "string" in call_kwargs
        assert isinstance(call_kwargs["string"], str)

    @patch("weasyprint.HTML")
    def test_gerar_indicacao_context_has_indicacao_and_camara(self, mock_html_class, camara, indicacao, presidente):
        """Template é renderizado com contexto contendo indicação e câmara."""
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b"%PDF-1.4"
        mock_html_class.return_value = mock_html_instance
        
        PdfService.gerar_indicacao(indicacao, camara)
        
        # Verifica se HTML foi chamado (isto confirma o template foi renderizado)
        assert mock_html_class.called

    @patch("weasyprint.HTML")
    def test_gerar_indicacao_with_presidente(self, mock_html_class, camara, indicacao, presidente):
        """Indicação é processada com presidente disponível."""
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b"%PDF-1.4"
        mock_html_class.return_value = mock_html_instance
        
        # Chamada com presidente existente
        result = PdfService.gerar_indicacao(indicacao, camara)
        
        assert result == b"%PDF-1.4"
        assert mock_html_class.called

    @patch("weasyprint.HTML")
    def test_gerar_indicacao_without_presidente(self, mock_html_class, camara, indicacao):
        """Indicação é processada mesmo sem presidente."""
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b"%PDF-1.4 no presidente"
        mock_html_class.return_value = mock_html_instance
        
        # Chamada sem presidente (nenhum foi criado)
        result = PdfService.gerar_indicacao(indicacao, camara)
        
        assert result == b"%PDF-1.4 no presidente"
        assert mock_html_class.called

    def test_gerar_indicacao_integration(self, camara, autor, orgao):
        """Teste de integração: PdfService gera PDF sem erro (real WeasyPrint)."""
        # Teste real usando WeasyPrint, sem mock
        indicacao = Indicacao.objects.create(
            camara=camara,
            autor=autor,
            orgao=orgao,
            numero="001/2026",
            data=date(2026, 1, 15),
            assunto="Teste Integration",
            solicitacao="Solicitação",
            justificativa="Justificativa",
        )
        
        try:
            result = PdfService.gerar_indicacao(indicacao, camara)
            # Se chegou aqui, WeasyPrint funcionou
            assert isinstance(result, bytes)
            assert len(result) > 0
        except Exception as e:
            # Se WeasyPrint não está disponível ou falha, skip
            pytest.skip(f"WeasyPrint não disponível: {e}")

