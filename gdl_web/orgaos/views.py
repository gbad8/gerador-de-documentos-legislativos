from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import OrgaoForm
from .models import Orgao


@login_required
def orgao_list(request):
    """Lista os órgãos da câmara do usuário."""
    # Usando o manager customizado para filtrar pela câmara atual
    orgaos_qs = Orgao.objects.for_camara(request.camara).order_by('nome')
    paginator = Paginator(orgaos_qs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "orgaos/orgao_list.html", {"page_obj": page_obj})


@login_required
def orgao_create(request):
    """Cria um novo órgão para a câmara do usuário."""
    if request.method == "POST":
        form = OrgaoForm(request.POST, camara=request.camara)
        if form.is_valid():
            orgao = form.save(commit=False)
            orgao.camara = request.camara
            orgao.save()
            messages.success(request, "Órgão adicionado com sucesso!")
            return redirect("orgao_list")
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = OrgaoForm(camara=request.camara)
    
    return render(request, "orgaos/orgao_form.html", {"form": form, "title": "Novo Órgão"})


@login_required
def orgao_edit(request, pk):
    """Edita um órgão existente."""
    orgao = get_object_or_404(Orgao.objects.for_camara(request.camara), pk=pk)
    if request.method == "POST":
        form = OrgaoForm(request.POST, instance=orgao, camara=request.camara)
        if form.is_valid():
            form.save()
            messages.success(request, "Dados do órgão atualizados com sucesso!")
            return redirect("orgao_list")
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = OrgaoForm(instance=orgao, camara=request.camara)
    
    return render(request, "orgaos/orgao_form.html", {"form": form, "title": "Editar Órgão"})


@login_required
def orgao_delete(request, pk):
    """Exclui um órgão."""
    orgao = get_object_or_404(Orgao.objects.for_camara(request.camara), pk=pk)
    if request.method == "POST":
        nome = orgao.nome
        orgao.delete()
        messages.success(request, f"Órgão '{nome}' removido com sucesso!")
        return redirect("orgao_list")
    
    return render(request, "orgaos/orgao_confirm_delete.html", {"orgao": orgao})
