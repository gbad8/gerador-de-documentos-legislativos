from django import forms
from .models import SessaoLegislativa
from legislaturas.models import Legislatura

class SessaoLegislativaForm(forms.ModelForm):
    class Meta:
        model = SessaoLegislativa
        fields = ["legislatura", "categoria", "numero", "data"]
        widgets = {
            "data": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "numero": forms.NumberInput(attrs={"class": "form-control"}),
            "legislatura": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        self.camara = kwargs.pop('camara', None)
        super().__init__(*args, **kwargs)
        if self.camara:
            self.fields['legislatura'].queryset = Legislatura.objects.filter(camara=self.camara)
