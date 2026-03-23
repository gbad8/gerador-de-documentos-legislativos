from django.urls import path

from . import views

urlpatterns = [
    path("", views.configuracoes, name="configuracoes"),
    path("camara/", views.camara_edit, name="camara_edit"),
    path("perfil/", views.perfil_edit, name="perfil_edit"),
]
