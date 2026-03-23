from django import forms

from core.models import Camara

class CamaraSettingsForm(forms.ModelForm):
    upload_logomarca = forms.ImageField(
        required=False,
        label="Atualizar Logomarca",
        help_text="Faça o upload de uma nova imagem para substituir a logomarca atual da Câmara."
    )

    class Meta:
        model = Camara
        fields = ["nome", "cidade", "estado", "cnpj", "endereco", "cep", "telefone", "email"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "cidade": forms.TextInput(attrs={"class": "form-control"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
            "cnpj": forms.TextInput(attrs={"class": "form-control"}),
            "endereco": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "cep": forms.TextInput(attrs={"class": "form-control"}),
            "telefone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["upload_logomarca"].widget.attrs.update({"class": "form-control"})

    def save(self, commit=True):
        instance = super().save(commit=False)
        uploaded_file = self.cleaned_data.get("upload_logomarca")
        if uploaded_file:
            instance.logomarca = uploaded_file.read()
        
        if commit:
            instance.save()
        return instance


from django.contrib.auth.models import User
from core.models import UsuarioPerfil

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }
        labels = {
            "username": "Login (Usuário)",
        }


class UsuarioPerfilForm(forms.ModelForm):
    class Meta:
        model = UsuarioPerfil
        fields = ["nome", "cargo"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "cargo": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "nome": "Nome de Exibição",
            "cargo": "Cargo/Função",
        }
