from django import forms
from .models import Indicacao

class IndicacaoForm(forms.ModelForm):
    # Base fields
    TIPO_NUMERACAO_CHOICES = [("auto", "Automático"), ("manual", "Manual")]
    tipo_numeracao = forms.ChoiceField(
        choices=TIPO_NUMERACAO_CHOICES, initial="auto", 
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}), label="Numeração"
    )
    numero_manual = forms.IntegerField(
        required=False, min_value=1, label="Número da Indicação",
        widget=forms.NumberInput(attrs={"class": "form-control", "style": "max-width: 120px;"})
    )

    class Meta:
        model = Indicacao
        fields = [
            'orgao', 'autor', 'data', 'assunto', 'solicitacao', 
            'justificativa', 'e_conjunto', 'coautores'
        ]
        widgets = {
            'orgao': forms.Select(attrs={'class': 'form-select'}),
            'autor': forms.Select(attrs={'class': 'form-select'}),
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'assunto': forms.TextInput(attrs={'class': 'form-control'}),
            'solicitacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'justificativa': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'e_conjunto': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
            'coautores': forms.SelectMultiple(attrs={'class': 'form-select select2'})
        }

    def __init__(self, *args, camara=None, **kwargs):
        super().__init__(*args, **kwargs)
        if camara:
            from autores.models import Autor
            from orgaos.models import Orgao
            self.fields["orgao"].queryset = Orgao.objects.for_camara(camara)
            self.fields["autor"].queryset = Autor.objects.for_camara(camara)
            self.fields["coautores"].queryset = Autor.objects.for_camara(camara)
            
        if self.instance and self.instance.pk:
            del self.fields["tipo_numeracao"]
            del self.fields["numero_manual"]

    def clean(self):
        cleaned_data = super().clean()
        
        # Validar numeração manual
        tipo_numeracao = cleaned_data.get("tipo_numeracao")
        if tipo_numeracao == "manual" and not cleaned_data.get("numero_manual"):
            self.add_error("numero_manual", "Informe o número da indicação.")

        return cleaned_data
