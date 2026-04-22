from django import forms
from django.core.exceptions import ValidationError
from legislaturas.models import Legislatura


class LegislaturaForm(forms.ModelForm):
    class Meta:
        model = Legislatura
        fields = ["numero", "data_eleicao", "data_inicio", "data_fim"]
        widgets = {
            "numero": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Ex: 8"}),
            "data_eleicao": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "data_inicio": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "data_fim": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        self.camara = kwargs.pop("camara", None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not field.widget.attrs.get("class"):
                field.widget.attrs["class"] = "form-control"

    def clean(self):
        cleaned_data = super().clean()
        numero = cleaned_data.get("numero")

        if numero and self.camara:
            queryset = Legislatura.objects.filter(
                camara=self.camara,
                numero=numero
            )
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError(
                    "Já existe uma legislatura cadastrada com este número."
                )
        
        # Validations for data_inicio and data_fim overapping are already handled 
        # seamlessly by instance.clean() which is called securely when ModelForm.is_valid()
        # invokes form.clean(), returning exceptions that attach to non-field or field errors appropriately.
        # Although Django 4.2+ full_clean is better, the exception from model's clean() works across ModelForm.
        
        return cleaned_data
