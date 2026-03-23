from django import forms

from autores.models import Autor
from oficios.models import Oficio


class OficioForm(forms.ModelForm):
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

    def clean(self):
        cleaned_data = super().clean()
        e_conjunto = cleaned_data.get("e_conjunto")
        autor = cleaned_data.get("autor")
        coautores = cleaned_data.get("coautores")

        if e_conjunto and autor and coautores:
            if autor in coautores:
                self.add_error("coautores", "O autor principal não pode estar na lista de coautores.")
        
        return cleaned_data
