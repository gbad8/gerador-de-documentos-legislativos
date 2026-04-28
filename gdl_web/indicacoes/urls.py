from django.urls import path

from indicacoes import views

app_name = "indicacoes"

urlpatterns = [
    path("", views.indicacao_list, name="list"),
    path("novo/", views.indicacao_create, name="create"),
    path("<int:pk>/editar/", views.indicacao_edit, name="edit"),
    path("<int:pk>/preview/", views.indicacao_preview, name="preview"),
    path("<int:pk>/pdf/", views.indicacao_generate_pdf, name="generate_pdf"),
    path("<int:pk>/excluir/", views.indicacao_delete, name="delete"),
    path("busca/", views.indicacao_search, name="search"),
]
