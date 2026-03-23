"""Testes para os models do app autores."""

import pytest

from autores.models import Autor


class TestAutor:
    def test_str(self, autor):
        assert str(autor) == "João da Silva"

    def test_for_camara(self, autor, outra_camara):
        autor_outra = Autor.objects.create(
            nome="Pedro Santos",
            cargo=Autor.Cargo.VEREADOR,
            camara=outra_camara,
        )
        qs = Autor.objects.for_camara(autor.camara)
        assert autor in qs
        assert autor_outra not in qs
