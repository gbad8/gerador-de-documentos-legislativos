from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html

from core.models import Camara, UsuarioPerfil


class CamaraAdminForm(forms.ModelForm):
    upload_logomarca = forms.ImageField(
        required=False,
        help_text="Faça o upload de uma nova logomarca (será salva redimensionada/otimizada internamente nas próximas versões, por enquanto salva os bytes originais)."
    )

    class Meta:
        model = Camara
        fields = "__all__"

    def save(self, commit=True):
        instance = super().save(commit=False)
        uploaded_file = self.cleaned_data.get("upload_logomarca")
        if uploaded_file:
            instance.logomarca = uploaded_file.read()
        
        if commit:
            instance.save()
        return instance


@admin.register(Camara)
class CamaraAdmin(admin.ModelAdmin):
    form = CamaraAdminForm
    list_display = ("nome", "estado", "cnpj", "telefone")
    search_fields = ("nome", "cnpj")
    readonly_fields = ("preview_logo",)
    
    def get_fieldsets(self, request, obj=None):
        return (
            (None, {
                "fields": ("nome", "estado", "cnpj", "endereco", "cep", "telefone")
            }),
            ("Logomarca", {
                "fields": ("preview_logo", "upload_logomarca")
            }),
        )

    def preview_logo(self, obj):
        if obj and obj.logomarca_base64:
            return format_html(
                '<img src="data:image/png;base64,{}" style="max-height: 100px;"/>',
                obj.logomarca_base64
            )
        return "Sem logomarca"
    preview_logo.short_description = "Logomarca Atual"


class UsuarioPerfilInline(admin.StackedInline):
    model = UsuarioPerfil
    can_delete = False
    verbose_name_plural = "Perfis de Usuário"


class UserAdmin(BaseUserAdmin):
    inlines = (UsuarioPerfilInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(UsuarioPerfil)
class UsuarioPerfilAdmin(admin.ModelAdmin):
    list_display = ("nome", "camara", "role", "user")
    list_filter = ("camara", "role")
    search_fields = ("nome", "role", "user__username")
