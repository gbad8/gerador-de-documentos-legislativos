from django.urls import path

from oficios import views

app_name = "oficios"

urlpatterns = [
    path("", views.oficio_list, name="list"),
    path("novo/", views.oficio_create, name="create"),
    path("<int:pk>/editar/", views.oficio_edit, name="edit"),
    path("<int:pk>/preview/", views.oficio_preview, name="preview"),
    path("<int:pk>/pdf/", views.oficio_generate_pdf, name="generate_pdf"),
    path("<int:pk>/excluir/", views.oficio_delete, name="delete"),
    path("busca/", views.oficio_search, name="search"),
]
