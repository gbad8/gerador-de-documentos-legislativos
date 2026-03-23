import pytest
from orgaos.forms import OrgaoForm
from orgaos.models import Orgao

pytestmark = pytest.mark.django_db

def test_orgao_form_valid(camara):
    data = {"nome": "Novo Órgão", "abreviatura": "nova"}
    form = OrgaoForm(data=data, camara=camara)
    assert form.is_valid()
    orgao = form.save(commit=False)
    orgao.camara = camara
    orgao.save()
    assert orgao.abreviatura == "NOVA"

def test_orgao_form_duplicate_nome(camara):
    Orgao.objects.create(camara=camara, nome="Existente")
    data = {"nome": "Existente", "abreviatura": "EXT"}
    form = OrgaoForm(data=data, camara=camara)
    assert not form.is_valid()
    assert "Já existe um órgão cadastrado com este nome na sua Câmara." in str(form.errors)

def test_orgao_form_duplicate_nome_case_insensitive(camara):
    Orgao.objects.create(camara=camara, nome="Mesa")
    data = {"nome": "mesa", "abreviatura": "MESA"}
    form = OrgaoForm(data=data, camara=camara)
    assert not form.is_valid()

def test_orgao_form_edit_same_name(camara):
    orgao = Orgao.objects.create(camara=camara, nome="Original")
    data = {"nome": "Original", "abreviatura": "ORIG"}
    form = OrgaoForm(data=data, instance=orgao, camara=camara)
    assert form.is_valid()
