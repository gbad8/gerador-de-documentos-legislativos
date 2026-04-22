from django import forms

from autores.models import Autor
from oficios.models import Oficio


TIPO_NUMERACAO_CHOICES = [("auto", "Automático"), ("manual", "Manual")]


class OficioForm(forms.ModelForm):
    tipo_numeracao = forms.ChoiceField(
        choices=TIPO_NUMERACAO_CHOICES,
        initial="auto",
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        label="Numeração",
    )

    numero_manual = forms.IntegerField(
        required=False,
        min_value=1,
        label="Número do Ofício",
        widget=forms.NumberInput(attrs={"class": "form-control", "style": "max-width: 120px;"}),
    )

    class Meta:
        model = Oficio
        fields = [
            "orgao",
            "autor",
            "e_conjunto",
            "coautores",
            "assunto",
            "corpo",
            "data",
            "destinatario_nome",
            "destinatario_cargo",
            "destinatario_orgao",
            "destinatario_endereco",
            "destinatario_pronome",
        ]
        widgets = {
            "orgao": forms.Select(attrs={"class": "form-select"}),
            "autor": forms.Select(attrs={"class": "form-select"}),
            "e_conjunto": forms.CheckboxInput(attrs={"class": "form-check-input", "role": "switch"}),
            "coautores": forms.SelectMultiple(attrs={"class": "form-select select2"}),
            "assunto": forms.TextInput(attrs={"class": "form-control"}),
            "data": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "corpo": forms.Textarea(attrs={"rows": 10, "class": "form-control", "placeholder": "Digite o texto principal do ofício aqui."}),
            "destinatario_nome": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Sr. João da Silva"}),
            "destinatario_cargo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Prefeito Municipal"}),
            "destinatario_orgao": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Prefeitura Municipal"}),
            "destinatario_endereco": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "destinatario_pronome": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Excelentíssimo(a)"}),
        }

    def __init__(self, *args, camara=None, **kwargs):
        super().__init__(*args, **kwargs)
        if camara:
            from orgaos.models import Orgao
            self.fields["orgao"].queryset = Orgao.objects.for_camara(camara)
            self.fields["autor"].queryset = Autor.objects.for_camara(camara)
            self.fields["coautores"].queryset = Autor.objects.for_camara(camara)

        # Na edição, remover os campos de numeração (número é imutável)
        if self.instance and self.instance.pk:
            del self.fields["tipo_numeracao"]
            del self.fields["numero_manual"]

    def clean(self):
        cleaned_data = super().clean()
        e_conjunto = cleaned_data.get("e_conjunto")
        autor = cleaned_data.get("autor")
        coautores = cleaned_data.get("coautores")

        if e_conjunto and autor and coautores:
            if autor in coautores:
                self.add_error("coautores", "O autor principal não pode estar na lista de coautores.")

        # Validar numeração manual
        tipo_numeracao = cleaned_data.get("tipo_numeracao")
        if tipo_numeracao == "manual" and not cleaned_data.get("numero_manual"):
            self.add_error("numero_manual", "Informe o número do ofício.")

        # Validar assunto e corpo (Ofício Livre exige)
        if not cleaned_data.get("assunto"):
            self.add_error("assunto", "Este campo é obrigatório.")
        if not cleaned_data.get("corpo"):
            self.add_error("corpo", "Este campo é obrigatório.")

        return cleaned_data


class EncaminhamentoCriacaoForm(forms.Form):
    # Base fields
    tipo_numeracao = forms.ChoiceField(
        choices=TIPO_NUMERACAO_CHOICES, initial="auto", 
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}), label="Numeração"
    )
    numero_manual = forms.IntegerField(
        required=False, min_value=1, label="Número do Ofício",
        widget=forms.NumberInput(attrs={"class": "form-control", "style": "max-width: 120px;"})
    )
    orgao = forms.ModelChoiceField(
        queryset=None, widget=forms.Select(attrs={"class": "form-select"}), required=False, label="Órgão"
    )
    data = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}), label="Data do Ofício")
    
    destinatario_nome = forms.CharField(
        max_length=200, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Prefeitura Municipal"}),
        initial="Prefeitura Municipal", label="Nome do Destinatário"
    )
    destinatario_cargo = forms.CharField(
        max_length=200, required=False, widget=forms.TextInput(attrs={"class": "form-control"}), 
        initial="Prefeito(a)", label="Cargo do Destinatário"
    )
    destinatario_orgao = forms.CharField(
        max_length=200, required=False, widget=forms.TextInput(attrs={"class": "form-control"}),
        initial="Prefeitura", label="Órgão do Destinatário"
    )
    destinatario_endereco = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 2, "class": "form-control"}), required=False, label="Endereço"
    )
    destinatario_pronome = forms.CharField(
        max_length=50, widget=forms.TextInput(attrs={"class": "form-control"}), 
        initial="Excelentíssimo(a)", label="Pronome de Tratamento"
    )
    
    # Encaminhamento Fields
    from oficios.models import OficioEncaminhamento
    sessao = forms.ModelChoiceField(
        queryset=None, widget=forms.Select(attrs={"class": "form-select"}), label="Sessão Legislativa"
    )
    votacao = forms.ChoiceField(
        choices=OficioEncaminhamento.Votacao.choices, widget=forms.Select(attrs={"class": "form-select"}), label="Votação / Aprovação"
    )
    proposicao = forms.CharField(
        max_length=200, widget=forms.TextInput(attrs={"class": "form-control"}), label="Indicação / Proposição", help_text="Ex: Indicação n° 13"
    )
    autor_proposicao = forms.ModelChoiceField(
        queryset=None, widget=forms.Select(attrs={"class": "form-select"}), label="Autor da Proposição"
    )

    def __init__(self, *args, camara=None, **kwargs):
        is_edit = kwargs.pop('is_edit', False)
        super().__init__(*args, **kwargs)
        if camara:
            from orgaos.models import Orgao
            from sessoes.models import SessaoLegislativa
            from autores.models import Autor
            self.fields["orgao"].queryset = Orgao.objects.for_camara(camara)
            self.fields["sessao"].queryset = SessaoLegislativa.objects.for_camara(camara)
            self.fields["autor_proposicao"].queryset = Autor.objects.for_camara(camara)
            
        if is_edit:
            del self.fields["tipo_numeracao"]
            del self.fields["numero_manual"]

    def clean(self):
        cleaned_data = super().clean()
        tipo_numeracao = cleaned_data.get("tipo_numeracao")
        if tipo_numeracao == "manual" and not cleaned_data.get("numero_manual"):
            self.add_error("numero_manual", "Informe o número do ofício.")
        return cleaned_data

