from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from oficios.forms import OficioForm
from oficios.models import Oficio
from oficios.services import NumeracaoService, PdfService


@login_required
def oficio_list(request):
    oficios = Oficio.objects.for_camara(request.camara).select_related("autor", "orgao")
    return render(request, "oficios/oficio_list.html", {"oficios": oficios})


@login_required
def oficio_create(request):
    if request.method == "POST":
        form = OficioForm(request.POST, camara=request.camara)
        if form.is_valid():
            oficio = form.save(commit=False)
            oficio.camara = request.camara
            numero_manual = form.cleaned_data.get("numero_manual")
            tipo_numeracao = form.cleaned_data.get("tipo_numeracao")

            if tipo_numeracao == "manual":
                try:
                    oficio.numero = NumeracaoService.registrar_numero_manual(
                        request.camara, oficio.orgao, oficio.autor, numero_manual
                    )
                except ValueError as e:
                    form.add_error("numero_manual", str(e))
                    return render(request, "oficios/oficio_form.html", {"form": form})
            else:
                oficio.numero = NumeracaoService.proximo_numero(
                    request.camara, oficio.orgao, oficio.autor
                )

            oficio.save()
            return redirect("oficios:preview", pk=oficio.pk)
    else:
        form = OficioForm(camara=request.camara)

    return render(request, "oficios/oficio_form.html", {"form": form})


@login_required
def oficio_edit(request, pk):
    oficio = get_object_or_404(
        Oficio.objects.for_camara(request.camara), pk=pk
    )

    if request.method == "POST":
        form = OficioForm(request.POST, instance=oficio, camara=request.camara)
        if form.is_valid():
            form.save()
            return redirect("oficios:preview", pk=oficio.pk)
    else:
        form = OficioForm(instance=oficio, camara=request.camara)

    return render(request, "oficios/oficio_form.html", {"form": form})


@login_required
def oficio_preview(request, pk):
    oficio = get_object_or_404(
        Oficio.objects.for_camara(request.camara).select_related("autor"), pk=pk
    )
    template = "oficios/_preview.html" if request.htmx else "oficios/oficio_detail.html"
    return render(request, template, {"oficio": oficio})


@login_required
def oficio_generate_pdf(request, pk):
    oficio = get_object_or_404(
        Oficio.objects.for_camara(request.camara).select_related("autor"), pk=pk
    )

    pdf = PdfService.gerar_oficio(oficio, request.camara)
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="oficio_{oficio.numero} - {oficio.autor}.pdf"'
    return response


@login_required
def oficio_search(request):
    q = request.GET.get("q", "")
    oficios = Oficio.objects.for_camara(request.camara).select_related("autor", "orgao")
    if q:
        oficios = oficios.filter(assunto__icontains=q)
    return render(request, "oficios/_search_results.html", {"oficios": oficios})


@login_required
def oficio_delete(request, pk):
    oficio = get_object_or_404(Oficio.objects.for_camara(request.camara), pk=pk)
    
    if request.method == "POST":
        numero = oficio.numero
        oficio.delete()
        messages.success(request, f"Ofício nº {numero} excluído com sucesso.")
        return redirect("oficios:list")
        
    return render(request, "oficios/oficio_confirm_delete.html", {"oficio": oficio})
