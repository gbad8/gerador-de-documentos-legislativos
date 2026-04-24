from django import forms
from .models import OrgaoExterno

class OrgaoExternoForm(forms.ModelForm):
    class Meta:
        model = OrgaoExterno
        fields = [
            "nome", "abreviatura", "responsavel", "sexo",
            "cargo", "pronome_tratamento", "endereco"
        ]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "abreviatura": forms.TextInput(attrs={"class": "form-control"}),
            "responsavel": forms.TextInput(attrs={"class": "form-control"}),
            "sexo": forms.Select(attrs={"class": "form-select"}),
            "cargo": forms.TextInput(attrs={"class": "form-control"}),
            "pronome_tratamento": forms.Select(attrs={"class": "form-select"}),
            "endereco": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, camara=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.camara = camara
