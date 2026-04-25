from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import OrgaoExternoForm
from .models import OrgaoExterno


@login_required
def orgao_externo_list(request):
    """Lista os órgãos externos da câmara do usuário."""
    orgaos_qs = OrgaoExterno.objects.for_camara(request.camara).order_by('nome')
    paginator = Paginator(orgaos_qs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "orgaos_externos/orgao_externo_list.html", {"page_obj": page_obj})


@login_required
def orgao_externo_create(request):
    """Cria um novo órgão externo para a câmara do usuário."""
    if request.method == "POST":
        form = OrgaoExternoForm(request.POST, camara=request.camara)
        if form.is_valid():
            orgao = form.save(commit=False)
            orgao.camara = request.camara
            orgao.save()
            messages.success(request, "Órgão Externo adicionado com sucesso!")
            return redirect("orgao_externo_list")
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = OrgaoExternoForm(camara=request.camara)
    
    return render(request, "orgaos_externos/orgao_externo_form.html", {"form": form, "title": "Novo Órgão Externo"})


@login_required
def orgao_externo_edit(request, pk):
    """Edita um órgão externo existente."""
    orgao = get_object_or_404(OrgaoExterno.objects.for_camara(request.camara), pk=pk)
    if request.method == "POST":
        form = OrgaoExternoForm(request.POST, instance=orgao, camara=request.camara)
        if form.is_valid():
            form.save()
            messages.success(request, "Órgão Externo atualizado com sucesso!")
            return redirect("orgao_externo_list")
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = OrgaoExternoForm(instance=orgao, camara=request.camara)
    
    return render(request, "orgaos_externos/orgao_externo_form.html", {"form": form, "title": "Editar Órgão Externo"})


@login_required
def orgao_externo_delete(request, pk):
    """Exclui um órgão externo."""
    orgao = get_object_or_404(OrgaoExterno.objects.for_camara(request.camara), pk=pk)
    if request.method == "POST":
        nome_str = str(orgao)
        orgao.delete()
        messages.success(request, f"Órgão '{nome_str}' removido com sucesso!")
        return redirect("orgao_externo_list")
    
    return render(request, "orgaos_externos/orgao_externo_confirm_delete.html", {"orgao": orgao})
