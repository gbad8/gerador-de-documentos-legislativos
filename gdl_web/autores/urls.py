from django.urls import path
from . import views

urlpatterns = [
    path("", views.autor_list, name="autor_list"),
    path("novo/", views.autor_create, name="autor_create"),
    path("<int:pk>/editar/", views.autor_edit, name="autor_edit"),
    path("<int:pk>/excluir/", views.autor_delete, name="autor_delete"),
]
