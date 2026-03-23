from django.contrib import admin

from autores.models import Autor


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ("nome", "cargo", "camara")
    list_filter = ("camara",)
    search_fields = ("nome",)
