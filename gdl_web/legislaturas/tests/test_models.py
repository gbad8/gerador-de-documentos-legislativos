import pytest
from datetime import date
from django.core.exceptions import ValidationError
from legislaturas.models import Legislatura


class TestLegislatura:
    def test_str(self, legislatura):
        assert str(legislatura) == "8ª Legislatura"

    def test_for_camara(self, legislatura, outra_camara):
        legislatura_outra = Legislatura.objects.create(
            numero=9,
            data_eleicao=date(2024, 10, 6),
            data_inicio=date(2025, 1, 1),
            data_fim=date(2028, 12, 31),
            camara=outra_camara,
        )
        qs = Legislatura.objects.for_camara(legislatura.camara)
        assert legislatura in qs
        assert legislatura_outra not in qs

    def test_clean_overlapping_dates(self, legislatura):
        # Tenta criar uma legislatura que sobrepõe totalmente
        leg2 = Legislatura(
            numero=9,
            data_eleicao=date(2024, 10, 6),
            data_inicio=date(2022, 1, 1),
            data_fim=date(2023, 1, 1),
            camara=legislatura.camara,
        )
        with pytest.raises(ValidationError) as exc:
            leg2.clean()
        assert "sobrepõe ao período" in str(exc.value)

    def test_clean_invalid_start_end(self, camara):
        # Tenta criar data_inicio > data_fim
        leg = Legislatura(
            numero=10,
            data_eleicao=date(2028, 10, 1),
            data_inicio=date(2029, 12, 31),
            data_fim=date(2029, 1, 1),
            camara=camara,
        )
        with pytest.raises(ValidationError) as exc:
            leg.clean()
        assert "posterior à data de fim" in str(exc.value)
