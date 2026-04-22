from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LegislaturaForm
from .models import Legislatura


@login_required
def legislatura_list(request):
    """Lista as legislaturas da câmara do usuário."""
    legislaturas = Legislatura.objects.for_camara(request.camara)
    return render(request, "legislaturas/legislatura_list.html", {"legislaturas": legislaturas})


@login_required
def legislatura_create(request):
    """Cria uma nova legislatura para a câmara do usuário."""
    if request.method == "POST":
        form = LegislaturaForm(request.POST, camara=request.camara)
        if form.is_valid():
            legislatura = form.save(commit=False)
            legislatura.camara = request.camara
            legislatura.save()
            messages.success(request, "Legislatura adicionada com sucesso!")
            return redirect("legislatura_list")
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = LegislaturaForm(camara=request.camara)
    
    return render(request, "legislaturas/legislatura_form.html", {"form": form, "title": "Nova Legislatura"})


@login_required
def legislatura_edit(request, pk):
    """Edita uma legislatura existente."""
    legislatura = get_object_or_404(Legislatura.objects.for_camara(request.camara), pk=pk)
    if request.method == "POST":
        form = LegislaturaForm(request.POST, instance=legislatura, camara=request.camara)
        if form.is_valid():
            form.save()
            messages.success(request, "Dados da legislatura atualizados com sucesso!")
            return redirect("legislatura_list")
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = LegislaturaForm(instance=legislatura, camara=request.camara)
    
    return render(request, "legislaturas/legislatura_form.html", {"form": form, "title": "Editar Legislatura"})


@login_required
def legislatura_delete(request, pk):
    """Exclui uma legislatura."""
    legislatura = get_object_or_404(Legislatura.objects.for_camara(request.camara), pk=pk)
    if request.method == "POST":
        nome_str = str(legislatura)
        legislatura.delete()
        messages.success(request, f"Legislatura '{nome_str}' removida com sucesso!")
        return redirect("legislatura_list")
    
    return render(request, "legislaturas/legislatura_confirm_delete.html", {"legislatura": legislatura})
