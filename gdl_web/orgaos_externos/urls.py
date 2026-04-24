from django.urls import path
from . import views

urlpatterns = [
    path("", views.orgao_externo_list, name="orgao_externo_list"),
    path("novo/", views.orgao_externo_create, name="orgao_externo_create"),
    path("<int:pk>/editar/", views.orgao_externo_edit, name="orgao_externo_edit"),
    path("<int:pk>/excluir/", views.orgao_externo_delete, name="orgao_externo_delete"),
]
