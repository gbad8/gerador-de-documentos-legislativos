"""Testes para os models do app core."""

import pytest

from core.models import Camara, UsuarioPerfil


class TestCamara:
    def test_str(self, camara):
        assert str(camara) == "Câmara Municipal de Teste"

    def test_campos_obrigatorios(self, db):
        camara = Camara.objects.create(
            nome="Teste",
            estado="MA",
            cnpj="00.000.000/0001-00",
            endereco="Rua X",
        )
        assert camara.pk is not None

    def test_telefone_opcional(self, db):
        camara = Camara.objects.create(
            nome="Sem Telefone",
            estado="SP",
            cnpj="11.111.111/0001-11",
            endereco="Rua Y",
            telefone="",
        )
        assert camara.telefone == ""


class TestUsuarioPerfil:
    def test_str(self, user, camara):
        perfil = UsuarioPerfil.objects.create(
            user=user,
            camara=camara,
            nome="Fulano de Tal",
            cargo=UsuarioPerfil.Cargo.PARLAMENTAR,
        )
        assert str(perfil) == "Fulano de Tal"
