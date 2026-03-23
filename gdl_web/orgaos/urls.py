from django.urls import path
from . import views

urlpatterns = [
    path("", views.orgao_list, name="orgao_list"),
    path("novo/", views.orgao_create, name="orgao_create"),
    path("<int:pk>/editar/", views.orgao_edit, name="orgao_edit"),
    path("<int:pk>/excluir/", views.orgao_delete, name="orgao_delete"),
]
