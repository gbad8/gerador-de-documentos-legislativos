from django.urls import path
from . import views

urlpatterns = [
    path("", views.legislatura_list, name="legislatura_list"),
    path("novo/", views.legislatura_create, name="legislatura_create"),
    path("<int:pk>/editar/", views.legislatura_edit, name="legislatura_edit"),
    path("<int:pk>/excluir/", views.legislatura_delete, name="legislatura_delete"),
]
