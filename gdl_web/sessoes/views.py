from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SessaoLegislativaForm
from .models import SessaoLegislativa


@login_required
def sessao_list(request):
    """Lista as sessões legislativas da câmara do usuário."""
    sessoes = SessaoLegislativa.objects.for_camara(request.camara)
    return render(request, "sessoes/sessao_list.html", {"sessoes": sessoes})


@login_required
def sessao_create(request):
    """Cria uma nova sessão legislativa para a câmara do usuário."""
    if request.method == "POST":
        form = SessaoLegislativaForm(request.POST, camara=request.camara)
        if form.is_valid():
            sessao = form.save(commit=False)
            sessao.camara = request.camara
            sessao.save()
            messages.success(request, "Sessão adicionada com sucesso!")
            return redirect("sessao_list")
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = SessaoLegislativaForm(camara=request.camara)
    
    return render(request, "sessoes/sessao_form.html", {"form": form, "title": "Nova Sessão Legislativa"})


@login_required
def sessao_edit(request, pk):
    """Edita uma sessão legislativa existente."""
    sessao = get_object_or_404(SessaoLegislativa.objects.for_camara(request.camara), pk=pk)
    if request.method == "POST":
        form = SessaoLegislativaForm(request.POST, instance=sessao, camara=request.camara)
        if form.is_valid():
            form.save()
            messages.success(request, "Sessão atualizada com sucesso!")
            return redirect("sessao_list")
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = SessaoLegislativaForm(instance=sessao, camara=request.camara)
    
    return render(request, "sessoes/sessao_form.html", {"form": form, "title": "Editar Sessão Legislativa"})


@login_required
def sessao_delete(request, pk):
    """Exclui uma sessão legislativa."""
    sessao = get_object_or_404(SessaoLegislativa.objects.for_camara(request.camara), pk=pk)
    if request.method == "POST":
        nome_str = str(sessao)
        sessao.delete()
        messages.success(request, f"Sessão '{nome_str}' removida com sucesso!")
        return redirect("sessao_list")
    
    return render(request, "sessoes/sessao_confirm_delete.html", {"sessao": sessao})
