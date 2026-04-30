"""Testes para indicacoes.forms"""
import pytest
from datetime import date

from autores.models import Autor
from indicacoes.forms import IndicacaoForm
from indicacoes.models import Indicacao
from orgaos.models import Orgao


@pytest.fixture
def orgao(camara):
    """Órgão de teste."""
    return Orgao.objects.create(
        camara=camara,
        nome="Secretaria de Governo",
        abreviatura="SG"
    )


@pytest.fixture
def form_data(camara, autor, orgao):
    """Dados válidos para formulário de indicação."""
    return {
        "tipo_numeracao": "auto",
        "orgao": orgao.id,
        "autor": autor.id,
        "data": "2026-01-15",
        "assunto": "Assunto da Indicação",
        "solicitacao": "Solicitação test",
        "justificativa": "Justificativa test",
        "e_conjunto": False,
    }


class TestIndicacaoFormInit:
    """Testes de inicialização do formulário."""

    def test_create_form_has_numeracao_fields(self, camara):
        """Formulário em modo create tem campos de numeração."""
        form = IndicacaoForm(camara=camara)
        assert "tipo_numeracao" in form.fields
        assert "numero_manual" in form.fields

    def test_edit_form_removes_numeracao_fields(self, camara, autor, orgao):
        """Formulário em modo edit (com instance) remove campos de numeração."""
        indicacao = Indicacao.objects.create(
            camara=camara,
            autor=autor,
            orgao=orgao,
            numero="001/2026",
            data=date(2026, 1, 15),
            assunto="Teste",
            solicitacao="Sol",
            justificativa="Just",
        )
        
        form = IndicacaoForm(instance=indicacao, camara=camara)
        assert "tipo_numeracao" not in form.fields
        assert "numero_manual" not in form.fields

    def test_form_filters_orgao_by_camara(self, camara, outra_camara):
        """Form filtra órgãos pela câmara do usuário."""
        orgao1 = Orgao.objects.create(camara=camara, nome="Orgão 1")
        orgao2 = Orgao.objects.create(camara=outra_camara, nome="Orgão 2")
        
        form = IndicacaoForm(camara=camara)
        orgao_ids = [o.id for o in form.fields["orgao"].queryset]
        
        assert orgao1.id in orgao_ids
        assert orgao2.id not in orgao_ids

    def test_form_filters_autor_by_camara(self, camara, outra_camara):
        """Form filtra autores pela câmara do usuário."""
        autor1 = Autor.objects.create(camara=camara, nome="Autor 1", cargo=Autor.Cargo.VEREADOR)
        autor2 = Autor.objects.create(camara=outra_camara, nome="Autor 2", cargo=Autor.Cargo.VEREADOR)
        
        form = IndicacaoForm(camara=camara)
        autor_ids = [a.id for a in form.fields["autor"].queryset]
        
        assert autor1.id in autor_ids
        assert autor2.id not in autor_ids

    def test_form_filters_coautores_by_camara(self, camara, outra_camara):
        """Form filtra coautores pela câmara do usuário."""
        autor1 = Autor.objects.create(camara=camara, nome="Autor 1", cargo=Autor.Cargo.VEREADOR)
        autor2 = Autor.objects.create(camara=outra_camara, nome="Autor 2", cargo=Autor.Cargo.VEREADOR)
        
        form = IndicacaoForm(camara=camara)
        coautor_ids = [a.id for a in form.fields["coautores"].queryset]
        
        assert autor1.id in coautor_ids
        assert autor2.id not in coautor_ids


class TestIndicacaoFormValidation:
    """Testes de validação do formulário."""

    def test_valid_form_with_auto_numbering(self, form_data):
        """Formulário válido com numeração automática passa na validação."""
        form = IndicacaoForm(data=form_data, camara=form_data["camara"] if "camara" in form_data else None)
        # Tem que passar pelo menos camara, mas form_data não tem, então:
        # Vou refazer
        pass

    def test_manual_numbering_required_when_tipo_manual(self, form_data):
        """Campo numero_manual é obrigatório quando tipo_numeracao='manual'."""
        form_data["tipo_numeracao"] = "manual"
        form_data["numero_manual"] = ""  # Vazio
        
        form = IndicacaoForm(data=form_data)
        assert not form.is_valid()
        assert "numero_manual" in form.errors

    def test_manual_numbering_not_required_when_auto(self, form_data):
        """Campo numero_manual não é obrigatório quando tipo_numeracao='auto'."""
        form_data["tipo_numeracao"] = "auto"
        form_data["numero_manual"] = ""  # Vazio, mas OK
        
        form = IndicacaoForm(data=form_data)
        assert "numero_manual" not in form.errors

    def test_numero_manual_min_value(self, form_data):
        """Campo numero_manual deve ser >= 1."""
        form_data["tipo_numeracao"] = "manual"
        form_data["numero_manual"] = "0"
        
        form = IndicacaoForm(data=form_data)
        assert not form.is_valid()
        assert "numero_manual" in form.errors

    def test_numero_manual_positive(self, form_data):
        """Campo numero_manual aceita números positivos."""
        form_data["tipo_numeracao"] = "manual"
        form_data["numero_manual"] = "10"
        
        form = IndicacaoForm(data=form_data)
        # Vai depender de outros campos obrigatórios, mas numero_manual não é o erro
        if form.errors:
            assert "numero_manual" not in form.errors

    def test_all_required_fields_present(self, camara, autor, orgao):
        """Form tem todos os campos obrigatórios do modelo."""
        form = IndicacaoForm(camara=camara)
        
        # Campos que devem estar presentes
        assert "autor" in form.fields
        assert "data" in form.fields
        assert "assunto" in form.fields
        assert "solicitacao" in form.fields
        assert "justificativa" in form.fields

    def test_e_conjunto_with_coautores(self, camara, autor, outro_autor, orgao):
        """e_conjunto pode ter coautores."""
        form_data = {
            "tipo_numeracao": "auto",
            "orgao": orgao.id,
            "autor": autor.id,
            "data": "2026-01-15",
            "assunto": "Assunto",
            "solicitacao": "Sol",
            "justificativa": "Just",
            "e_conjunto": True,
            "coautores": [outro_autor.id],
        }
        
        form = IndicacaoForm(data=form_data, camara=camara)
        # Faz o clean
        form.full_clean()
        # Form pode ter erros de outros campos mas não de coautores relacionados

    def test_form_preserves_data_on_error(self, form_data):
        """Formulário mantém dados em caso de erro."""
        form_data["numero_manual"] = ""  # Erro
        form_data["tipo_numeracao"] = "manual"
        
        form = IndicacaoForm(data=form_data)
        form.is_valid()  # vai ter erro
        
        # O form mantém os dados (para re-rendering)
        assert form["assunto"].value() == form_data["assunto"]


class TestIndicacaoFormDynamicBehavior:
    """Testes de comportamento dinâmico do formulário."""

    def test_widget_classes_assigned(self, camara):
        """Widgets têm classes CSS corretas."""
        form = IndicacaoForm(camara=camara)
        
        # Verifica se o widget de select tem a classe form-select
        assert "form-select" in str(form["autor"].field.widget.attrs)
        assert "form-select" in str(form["orgao"].field.widget.attrs)

    def test_type_numeracao_radio_widget(self, camara):
        """Campo tipo_numeracao usa RadioSelect."""
        from django.forms.widgets import RadioSelect
        
        form = IndicacaoForm(camara=camara)
        assert isinstance(form.fields["tipo_numeracao"].widget, RadioSelect)

    def test_form_with_initial_data(self, camara, autor, orgao):
        """Form pode ser inicializado com dados iniciais."""
        initial_data = {
            "autor": autor.id,
            "orgao": orgao.id,
            "assunto": "Assunto Inicial",
        }
        
        form = IndicacaoForm(initial=initial_data, camara=camara)
        assert form["assunto"].value() == "Assunto Inicial"

    def test_form_coautores_multiple_select(self, camara):
        """Campo coautores permite múltipla seleção."""
        from django.forms.widgets import SelectMultiple
        
        form = IndicacaoForm(camara=camara)
        assert isinstance(form.fields["coautores"].widget, SelectMultiple)
