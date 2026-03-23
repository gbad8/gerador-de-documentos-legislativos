import pytest
from django.db import IntegrityError
from orgaos.models import Orgao

pytestmark = pytest.mark.django_db

def test_orgao_str(camara):
    orgao = Orgao.objects.create(camara=camara, nome="Gabinete")
    assert str(orgao) == "Gabinete"

def test_orgao_unique_together(camara):
    Orgao.objects.create(camara=camara, nome="Mesa")
    with pytest.raises(IntegrityError):
        Orgao.objects.create(camara=camara, nome="Mesa")

def test_orgao_ordering(camara):
    Orgao.objects.create(camara=camara, nome="C")
    Orgao.objects.create(camara=camara, nome="A")
    Orgao.objects.create(camara=camara, nome="B")
    
    orgaos = Orgao.objects.filter(camara=camara)
    assert list(orgaos.values_list('nome', flat=True)) == ["A", "B", "C"]
