from django import forms
from .models import Orgao

class OrgaoForm(forms.ModelForm):
    class Meta:
        model = Orgao
        fields = ["nome", "abreviatura"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Mesa Diretora, Gabinete do Presidente"}),
            "abreviatura": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "Ex: MESA, GAPRE",
                "style": "text-transform: uppercase"
            }),
        }

    def __init__(self, *args, **kwargs):
        self.camara = kwargs.pop("camara", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        nome = cleaned_data.get("nome")

        if nome and self.camara:
            queryset = Orgao.objects.filter(
                camara=self.camara,
                nome__iexact=nome
            )
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError(
                    "Já existe um órgão cadastrado com este nome na sua Câmara."
                )
        return cleaned_data

    def clean_abreviatura(self):
        abreviatura = self.cleaned_data.get("abreviatura")
        if abreviatura:
            return abreviatura.upper()
        return abreviatura
