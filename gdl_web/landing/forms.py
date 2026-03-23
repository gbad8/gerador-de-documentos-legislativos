from django import forms
from .models import SolicitacaoAcesso

class SolicitacaoAcessoForm(forms.ModelForm):
    class Meta:
        model = SolicitacaoAcesso
        fields = ["nome_camara", "nome_solicitante", "cargo_solicitante", "email", "telefone"]
        widgets = {
            "nome_camara": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Câmara Municipal de São Paulo"}),
            "nome_solicitante": forms.TextInput(attrs={"class": "form-control", "placeholder": "Seu nome completo"}),
            "cargo_solicitante": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Presidente, Diretor Geral, Vereador"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "email@camara.leg.br"}),
            "telefone": forms.TextInput(attrs={"class": "form-control", "placeholder": "(11) 99999-9999"}),
        }
