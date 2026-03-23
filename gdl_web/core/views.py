from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core.forms import CamaraSettingsForm


@login_required
def configuracoes(request):
    """View hub para as configurações do sistema."""
    return render(request, "core/configuracoes.html")


@login_required
def camara_edit(request):
    """View para edição dos dados da Câmara do usuário atual."""
    camara = getattr(request.user.perfil, "camara", None)
    
    if request.method == "POST":
        form = CamaraSettingsForm(request.POST, request.FILES, instance=camara)
        if form.is_valid():
            camara_atualizada = form.save()
            request.camara = camara_atualizada
            messages.success(request, "Dados da Casa Legislativa atualizados com sucesso!")
            return render(request, "core/camara_form.html", {"form": form})
            return render(request, "core/camara_form.html", {"form": form})
    else:
        form = CamaraSettingsForm(instance=camara)

    return render(request, "core/camara_form.html", {"form": form})


@login_required
def perfil_edit(request):
    """View para edição do perfil (username, email, nome, cargo) do usuário logado."""
    user = request.user
    perfil = getattr(user, "perfil", None)

    from core.forms import UserForm, UsuarioPerfilForm

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=user)
        # Se o perfil não existir, não podemos atualizá-lo facilmente aqui sem a camara, 
        # mas na arquitetura atual todo usuário tem perfil.
        perfil_form = UsuarioPerfilForm(request.POST, instance=perfil) if perfil else None

        if user_form.is_valid() and (not perfil_form or perfil_form.is_valid()):
            user_form.save()
            if perfil_form:
                perfil_form.save()
            messages.success(request, "Seu perfil foi atualizado com sucesso!")
            return render(request, "core/perfil_form.html", {
                "user_form": user_form,
                "perfil_form": perfil_form,
            })
    else:
        user_form = UserForm(instance=user)
        perfil_form = UsuarioPerfilForm(instance=perfil) if perfil else None

    return render(request, "core/perfil_form.html", {
        "user_form": user_form,
        "perfil_form": perfil_form,
    })
