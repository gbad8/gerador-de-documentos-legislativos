from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from core.models import Numeracao
from indicacoes.forms import IndicacaoForm
from indicacoes.models import Indicacao
from indicacoes.services import PdfService
from oficios.services import NumeracaoService


@login_required
def indicacao_list(request):
    qs = Indicacao.objects.for_camara(request.camara).select_related("autor", "orgao").order_by("-data", "-numero")
    
    paginator = Paginator(qs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "indicacoes/indicacao_list.html", {"page_obj": page_obj})


@login_required
def indicacao_create(request):
    if request.method == "POST":
        form = IndicacaoForm(request.POST, camara=request.camara)
        if form.is_valid():
            indicacao = form.save(commit=False)
            indicacao.camara = request.camara
            
            numero_manual = request.POST.get("numero_manual")
            tipo_numeracao = request.POST.get("tipo_numeracao")

            if tipo_numeracao == "manual":
                try:
                    indicacao.numero = NumeracaoService.registrar_numero_manual(
                        request.camara, indicacao.orgao, indicacao.autor, int(numero_manual), Numeracao.TipoDocumento.INDICACAO
                    )
                except ValueError as e:
                    form.add_error(None, str(e))
                    return render(request, "indicacoes/indicacao_form.html", {"form": form, "title": "Nova Indicação"})
            else:
                indicacao.numero = NumeracaoService.proximo_numero(
                    request.camara, indicacao.orgao, indicacao.autor, Numeracao.TipoDocumento.INDICACAO
                )

            indicacao.save()
            form.save_m2m()
            return redirect("indicacoes:preview", pk=indicacao.pk)
    else:
        form = IndicacaoForm(camara=request.camara)

    return render(request, "indicacoes/indicacao_form.html", {"form": form, "title": "Nova Indicação"})


@login_required
def indicacao_edit(request, pk):
    indicacao = get_object_or_404(
        Indicacao.objects.for_camara(request.camara), pk=pk
    )

    if request.method == "POST":
        form = IndicacaoForm(request.POST, instance=indicacao, camara=request.camara)
        if form.is_valid():
            indicacao = form.save(commit=False)
            indicacao.save()
            form.save_m2m()
            return redirect("indicacoes:preview", pk=indicacao.pk)
    else:
        form = IndicacaoForm(instance=indicacao, camara=request.camara)

    return render(request, "indicacoes/indicacao_form.html", {"form": form, "title": "Editar Indicação"})


@login_required
def indicacao_preview(request, pk):
    indicacao = get_object_or_404(
        Indicacao.objects.for_camara(request.camara).select_related("autor"), pk=pk
    )
    template = "indicacoes/_preview.html" if request.htmx else "indicacoes/indicacao_detail.html"
    return render(request, template, {"indicacao": indicacao})


@login_required
def indicacao_generate_pdf(request, pk):
    indicacao = get_object_or_404(
        Indicacao.objects.for_camara(request.camara).select_related("autor"), pk=pk
    )

    pdf = PdfService.gerar_indicacao(indicacao, request.camara)
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="indicacao_{indicacao.numero} - {indicacao.autor}.pdf"'
    return response


@login_required
def indicacao_search(request):
    q = request.GET.get("q", "")
    qs = Indicacao.objects.for_camara(request.camara).select_related("autor", "orgao").order_by("-data", "-numero")
    if q:
        qs = qs.filter(assunto__icontains=q)
        
    paginator = Paginator(qs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "indicacoes/_search_results.html", {"page_obj": page_obj})


@login_required
def indicacao_delete(request, pk):
    indicacao = get_object_or_404(Indicacao.objects.for_camara(request.camara), pk=pk)
    
    if request.method == "POST":
        numero = indicacao.numero
        indicacao.delete()
        messages.success(request, f"Indicação nº {numero} excluída com sucesso.")
        return redirect("indicacoes:list")
        
    return render(request, "indicacoes/indicacao_confirm_delete.html", {"indicacao": indicacao})
