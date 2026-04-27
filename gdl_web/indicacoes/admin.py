from django.contrib import admin
from .models import Indicacao

@admin.register(Indicacao)
class IndicacaoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'camara', 'autor', 'status', 'criado_em')
    list_filter = ('camara', 'status', 'data')
    search_fields = ('numero', 'assunto')
