import pytest
from datetime import date
from django.db import IntegrityError
from sessoes.models import SessaoLegislativa

pytestmark = pytest.mark.django_db

class TestSessaoLegislativa:
    def test_str(self, sessao):
        assert str(sessao) == "1ª Sessão Ordinária da 8ª Legislatura"

    def test_nome_curto(self, sessao):
        assert sessao.nome_curto == "1ª Sessão Ordinária"

    def test_for_camara_isolation(self, sessao, outra_camara, legislatura):
        """Testa o TenantManager."""
        from legislaturas.models import Legislatura
        leg_outra = Legislatura.objects.create(
            numero=9,
            data_eleicao=date(2024, 10, 6),
            data_inicio=date(2025, 1, 1),
            data_fim=date(2028, 12, 31),
            camara=outra_camara,
        )
        
        sessao_outra = SessaoLegislativa.objects.create(
            legislatura=leg_outra,
            numero=1,
            categoria="ORDINARIA",
            data=date(2025, 2, 1),
            camara=outra_camara,
        )
        qs = SessaoLegislativa.objects.for_camara(sessao.camara)
        assert sessao in qs
        assert sessao_outra not in qs

    def test_unique_constraint(self, sessao):
        with pytest.raises(IntegrityError):
            SessaoLegislativa.objects.create(
                legislatura=sessao.legislatura,
                numero=1,
                categoria="ORDINARIA",
                data=date(2021, 2, 8),
                camara=sessao.camara,
            )
