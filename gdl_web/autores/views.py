from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AutorForm
from .models import Autor


@login_required
def autor_list(request):
    """Lista os autores da câmara do usuário."""
    # Usando o manager customizado para filtrar pela câmara atual
    autores_qs = Autor.objects.for_camara(request.camara).order_by('nome')
    paginator = Paginator(autores_qs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "autores/autor_list.html", {"page_obj": page_obj})


@login_required
def autor_create(request):
    """Cria um novo autor para a câmara do usuário."""
    if request.method == "POST":
        form = AutorForm(request.POST, camara=request.camara)
        if form.is_valid():
            autor = form.save(commit=False)
            autor.camara = request.camara
            autor.save()
            messages.success(request, "Autor adicionado com sucesso!")
            return redirect("autor_list")
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = AutorForm(camara=request.camara)
    
    return render(request, "autores/autor_form.html", {"form": form, "title": "Novo Autor"})


@login_required
def autor_edit(request, pk):
    """Edita um autor existente."""
    # Filtragem garantida pelo manager para segurança multi-tenant
    autor = get_object_or_404(Autor.objects.for_camara(request.camara), pk=pk)
    if request.method == "POST":
        form = AutorForm(request.POST, instance=autor, camara=request.camara)
        if form.is_valid():
            form.save()
            messages.success(request, "Dados do autor atualizados com sucesso!")
            return redirect("autor_list")
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = AutorForm(instance=autor, camara=request.camara)
    
    return render(request, "autores/autor_form.html", {"form": form, "title": "Editar Autor"})


@login_required
def autor_delete(request, pk):
    """Exclui um autor."""
    # Filtragem garantida pelo manager para segurança multi-tenant
    autor = get_object_or_404(Autor.objects.for_camara(request.camara), pk=pk)
    if request.method == "POST":
        nome = autor.nome
        autor.delete()
        messages.success(request, f"Autor '{nome}' removido com sucesso!")
        return redirect("autor_list")
    
    return render(request, "autores/autor_confirm_delete.html", {"autor": autor})
