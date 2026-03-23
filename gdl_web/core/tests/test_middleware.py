"""Testes para o TenantMiddleware."""

import pytest
from django.test import RequestFactory

from core.middleware import TenantMiddleware
from core.models import UsuarioPerfil


class TestTenantMiddleware:
    def test_injeta_camara_para_usuario_logado(self, user, camara):
        UsuarioPerfil.objects.create(
            user=user,
            camara=camara,
            nome="Teste",
            cargo=UsuarioPerfil.Cargo.PARLAMENTAR,
        )
        factory = RequestFactory()
        request = factory.get("/")
        request.user = user

        middleware = TenantMiddleware(lambda r: r)
        response = middleware(request)

        assert response.camara == camara
        assert response.role == UsuarioPerfil.Role.OPERADOR

    def test_sem_login_camara_none(self, db):
        from django.contrib.auth.models import AnonymousUser

        factory = RequestFactory()
        request = factory.get("/")
        request.user = AnonymousUser()

        middleware = TenantMiddleware(lambda r: r)
        response = middleware(request)

        assert response.camara is None
        assert response.role is None

    def test_usuario_logado_sem_perfil(self, user):
        """Usuário autenticado sem UsuarioPerfil → camara e role ficam None."""
        factory = RequestFactory()
        request = factory.get("/")
        request.user = user

        middleware = TenantMiddleware(lambda r: r)
        response = middleware(request)

        assert response.camara is None
        assert response.role is None
