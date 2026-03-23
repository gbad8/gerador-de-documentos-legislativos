"""Testes para os models do app oficios."""

import pytest
from datetime import date

from autores.models import Autor
from oficios.models import Oficio


class TestOficio:
    @pytest.fixture
    def oficio(self, camara, autor):
        return Oficio.objects.create(
            camara=camara,
            autor=autor,
            numero="001/2026",
            assunto="Teste de assunto",
            corpo="Corpo do ofício de teste.",
            data=date(2026, 1, 15),
            destinatario_nome="Sr. Fulano",
            destinatario_cargo="Prefeito",
            destinatario_orgao="Prefeitura Municipal",
            destinatario_endereco="Rua X, 123",
            destinatario_pronome="Excelentíssimo",
        )

    def test_str(self, oficio):
        assert "Ofício n°" in str(oficio)
        assert "001/2026" in str(oficio)
        assert "João da Silva" in str(oficio)

    def test_status_default(self, oficio):
        assert oficio.status == Oficio.Status.RASCUNHO

    def test_ordering(self, camara, autor):
        o1 = Oficio.objects.create(
            camara=camara, autor=autor, numero="001/2026",
            assunto="Primeiro", corpo="Corpo", data=date(2026, 1, 1),
            destinatario_nome="A", destinatario_cargo="B",
            destinatario_orgao="C", destinatario_endereco="D",
            destinatario_pronome="E",
        )
        o2 = Oficio.objects.create(
            camara=camara, autor=autor, numero="002/2026",
            assunto="Segundo", corpo="Corpo", data=date(2026, 1, 2),
            destinatario_nome="A", destinatario_cargo="B",
            destinatario_orgao="C", destinatario_endereco="D",
            destinatario_pronome="E",
        )
        oficios = list(Oficio.objects.for_camara(camara))
        # Mais recente primeiro (ordering = -criado_em)
        assert oficios[0] == o2
        assert oficios[1] == o1
