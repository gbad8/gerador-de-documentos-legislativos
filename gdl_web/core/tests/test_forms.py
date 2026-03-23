import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from core.forms import CamaraSettingsForm

pytestmark = pytest.mark.django_db

def test_camara_settings_form_valid():
    form_data = {
        "nome": "Câmara Teste",
        "cidade": "Cidade Teste",
        "estado": "SP",
        "cnpj": "12.345.678/0001-90",
        "endereco": "Rua Teste, 123",
        "cep": "12345-678",
        "telefone": "(11) 9999-9999",
    }
    form = CamaraSettingsForm(data=form_data)
    assert form.is_valid()
    
def test_camara_settings_form_invalid_missing_required():
    form_data = {
        "nome": "",  # Missing required
        "estado": "SP",
        "cnpj": "12.345.678/0001-90",
        "endereco": "Rua Teste, 123",
    }
    form = CamaraSettingsForm(data=form_data)
    assert not form.is_valid()
    assert "nome" in form.errors

def test_camara_settings_form_save_with_logomarca():
    form_data = {
        "nome": "Câmara Teste",
        "cidade": "Cidade Teste",
        "estado": "SP",
        "cnpj": "12.345.678/0001-90",
        "endereco": "Rua Teste, 123",
    }
    # Conteúdo binário de um GIF 1x1 transparente válido
    # para passar na validação do Pillow/Django ImageField
    file_data = (
        b"GIF89a\x01\x00\x01\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00"
        b",\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
    )
    upload = SimpleUploadedFile("logo.gif", file_data, content_type="image/gif")
    
    form = CamaraSettingsForm(data=form_data, files={"upload_logomarca": upload})
    
    if not form.is_valid():
        print(f"ERROS DO FORMULÁRIO: {form.errors}")
        
    assert form.is_valid()
    
    camara = form.save()
    assert camara.nome == "Câmara Teste"
    assert camara.logomarca == file_data
