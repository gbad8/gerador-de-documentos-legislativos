from django import forms
from autores.models import Autor

class AutorForm(forms.ModelForm):
    class Meta:
        model = Autor
        fields = ["nome", "cargo"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome completo do autor"}),
            "cargo": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        self.camara = kwargs.pop("camara", None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not field.widget.attrs.get("class"):
                field.widget.attrs["class"] = "form-control"

    def clean(self):
        cleaned_data = super().clean()
        nome = cleaned_data.get("nome")
        cargo = cleaned_data.get("cargo")

        if nome and cargo and self.camara:
            from autores.models import Autor
            queryset = Autor.objects.filter(
                camara=self.camara,
                nome=nome,
                cargo=cargo
            )
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError(
                    "Já existe um autor cadastrado com este nome e cargo na sua Câmara."
                )
        return cleaned_data
