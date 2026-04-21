from django.urls import path
from . import views

urlpatterns = [
    path("", views.sessao_list, name="sessao_list"),
    path("novo/", views.sessao_create, name="sessao_create"),
    path("<int:pk>/editar/", views.sessao_edit, name="sessao_edit"),
    path("<int:pk>/excluir/", views.sessao_delete, name="sessao_delete"),
]
