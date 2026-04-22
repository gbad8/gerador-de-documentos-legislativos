"""Fixtures compartilhadas para todos os testes."""

import pytest
from django.contrib.auth import get_user_model

from autores.models import Autor
from core.models import Camara, UsuarioPerfil

User = get_user_model()


@pytest.fixture(autouse=True)
def _use_default_staticfiles_storage(settings):
    """Usa o storage padrão do Django nos testes (sem WhiteNoise manifest)."""
    settings.STORAGES = {
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }


@pytest.fixture
def camara(db):
    """Câmara de teste."""
    return Camara.objects.create(
        nome="Câmara Municipal de Teste",
        estado="MA",
        cnpj="00.000.000/0001-00",
        endereco="Rua Teste, 123",
        telefone="(99) 9999-9999",
    )


@pytest.fixture
def outra_camara(db):
    """Segunda câmara para testes de isolamento tenant."""
    return Camara.objects.create(
        nome="Câmara Municipal de Outra Cidade",
        estado="SP",
        cnpj="11.111.111/0001-11",
        endereco="Av. Outra, 456",
    )


@pytest.fixture
def autor(camara):
    """Autor vinculado à câmara de teste."""
    return Autor.objects.create(
        nome="João da Silva",
        cargo=Autor.Cargo.VEREADOR,
        camara=camara,
    )


@pytest.fixture
def outro_autor(camara):
    """Segundo autor na mesma câmara."""
    return Autor.objects.create(
        nome="Maria Souza",
        cargo=Autor.Cargo.VEREADOR,
        camara=camara,
    )


@pytest.fixture
def legislatura(camara):
    """Legislatura de teste."""
    from legislaturas.models import Legislatura
    from datetime import date
    return Legislatura.objects.create(
        numero=8,
        data_eleicao=date(2020, 11, 15),
        data_inicio=date(2021, 1, 1),
        data_fim=date(2024, 12, 31),
        camara=camara,
    )


@pytest.fixture
def user(db):
    """Usuário Django básico."""
    return User.objects.create_user(username="testuser", password="testpass123")


@pytest.fixture
def user_logado(client, user, camara):
    """Client já autenticado com câmara associada via UsuarioPerfil."""
    UsuarioPerfil.objects.create(
        user=user,
        camara=camara,
        nome="Usuário Teste",
        cargo=UsuarioPerfil.Cargo.PARLAMENTAR,
    )
    client.login(username="testuser", password="testpass123")
    return client


@pytest.fixture
def sessao(camara, legislatura):
    """Sessão legislativa de teste."""
    from sessoes.models import SessaoLegislativa
    from datetime import date
    return SessaoLegislativa.objects.create(
        legislatura=legislatura,
        numero=1,
        categoria="ORDINARIA",
        data=date(2021, 2, 1),
        camara=camara,
    )
