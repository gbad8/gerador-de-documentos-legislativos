from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from oficios.forms import OficioForm, EncaminhamentoCriacaoForm
from oficios.models import Oficio, OficioEncaminhamento
from oficios.services import NumeracaoService, PdfService


@login_required
def oficio_list(request):
    oficios = Oficio.objects.for_camara(request.camara).select_related("autor", "orgao")
    return render(request, "oficios/oficio_list.html", {"oficios": oficios})


@login_required
def oficio_create(request):
    tipo = request.GET.get("tipo")
    if not tipo:
        return render(request, "oficios/tipo_select.html")

    if tipo == "encaminhamento":
        from autores.models import Autor
        presidente = Autor.objects.filter(camara=request.camara, cargo=Autor.Cargo.PRESIDENTE).first()
        if not presidente:
            messages.error(request, "Não há um Presidente cadastrado na câmara. Não é possível criar ofícios de encaminhamento. Volte nas configurações de Autores e cadastre o presidente.")
            return redirect("oficios:list")
            
        if request.method == "POST":
            form = EncaminhamentoCriacaoForm(request.POST, camara=request.camara)
            if form.is_valid():
                oficio = Oficio(
                    camara=request.camara,
                    tipo=Oficio.Tipo.ENCAMINHAMENTO,
                    autor=presidente,
                    orgao=form.cleaned_data["orgao"],
                    data=form.cleaned_data["data"],
                    destinatario_nome=form.cleaned_data["destinatario_nome"],
                    destinatario_cargo=form.cleaned_data["destinatario_cargo"],
                    destinatario_orgao=form.cleaned_data["destinatario_orgao"],
                    destinatario_endereco=form.cleaned_data["destinatario_endereco"],
                    destinatario_pronome=form.cleaned_data["destinatario_pronome"],
                    assunto=f"Encaminhamento do(a) {form.cleaned_data['proposicao']}, de autoria de {form.cleaned_data['autor_proposicao'].nome}"
                )
                
                numero_manual = form.cleaned_data.get("numero_manual")
                tipo_numeracao = form.cleaned_data.get("tipo_numeracao")
                if tipo_numeracao == "manual":
                    try:
                        oficio.numero = NumeracaoService.registrar_numero_manual(request.camara, oficio.orgao, oficio.autor, numero_manual)
                    except ValueError as e:
                        form.add_error("numero_manual", str(e))
                        return render(request, "oficios/oficio_encaminhamento_form.html", {"form": form})
                else:
                    oficio.numero = NumeracaoService.proximo_numero(request.camara, oficio.orgao, oficio.autor)
                oficio.save()
                
                enc = OficioEncaminhamento(
                    oficio=oficio,
                    sessao=form.cleaned_data["sessao"],
                    votacao=form.cleaned_data["votacao"],
                    proposicao=form.cleaned_data["proposicao"],
                    autor_proposicao=form.cleaned_data["autor_proposicao"],
                    data_aprovacao=form.cleaned_data["sessao"].data
                )
                enc.save()
                oficio.corpo = enc.get_corpo_gerado()
                oficio.save()
                return redirect("oficios:preview", pk=oficio.pk)
        else:
            form = EncaminhamentoCriacaoForm(camara=request.camara)
        return render(request, "oficios/oficio_encaminhamento_form.html", {"form": form, "title": "Novo Ofício de Encaminhamento"})

    # LIVRE (Default)
    if request.method == "POST":
        form = OficioForm(request.POST, camara=request.camara)
        if form.is_valid():
            oficio = form.save(commit=False)
            oficio.camara = request.camara
            oficio.tipo = Oficio.Tipo.LIVRE
            numero_manual = form.cleaned_data.get("numero_manual")
            tipo_numeracao = form.cleaned_data.get("tipo_numeracao")

            if tipo_numeracao == "manual":
                try:
                    oficio.numero = NumeracaoService.registrar_numero_manual(
                        request.camara, oficio.orgao, oficio.autor, numero_manual
                    )
                except ValueError as e:
                    form.add_error("numero_manual", str(e))
                    return render(request, "oficios/oficio_form.html", {"form": form, "title": "Novo Ofício Livre"})
            else:
                oficio.numero = NumeracaoService.proximo_numero(
                    request.camara, oficio.orgao, oficio.autor
                )

            oficio.save()
            form.save_m2m()
            return redirect("oficios:preview", pk=oficio.pk)
    else:
        form = OficioForm(camara=request.camara)

    return render(request, "oficios/oficio_form.html", {"form": form, "title": "Novo Ofício Livre"})


@login_required
def oficio_edit(request, pk):
    oficio = get_object_or_404(
        Oficio.objects.for_camara(request.camara), pk=pk
    )

    if oficio.tipo == Oficio.Tipo.ENCAMINHAMENTO:
        enc = oficio.encaminhamento
        initial = {
            "orgao": oficio.orgao,
            "data": oficio.data,
            "destinatario_nome": oficio.destinatario_nome,
            "destinatario_cargo": oficio.destinatario_cargo,
            "destinatario_orgao": oficio.destinatario_orgao,
            "destinatario_endereco": oficio.destinatario_endereco,
            "destinatario_pronome": oficio.destinatario_pronome,
            "sessao": enc.sessao,
            "votacao": enc.votacao,
            "proposicao": enc.proposicao,
            "autor_proposicao": enc.autor_proposicao,
        }
        if request.method == "POST":
            form = EncaminhamentoCriacaoForm(request.POST, camara=request.camara, is_edit=True)
            if form.is_valid():
                oficio.orgao = form.cleaned_data["orgao"]
                oficio.data = form.cleaned_data["data"]
                oficio.destinatario_nome = form.cleaned_data["destinatario_nome"]
                oficio.destinatario_cargo = form.cleaned_data["destinatario_cargo"]
                oficio.destinatario_orgao = form.cleaned_data["destinatario_orgao"]
                oficio.destinatario_endereco = form.cleaned_data["destinatario_endereco"]
                oficio.destinatario_pronome = form.cleaned_data["destinatario_pronome"]
                oficio.assunto = f"Encaminhamento do(a) {form.cleaned_data['proposicao']}, de autoria de {form.cleaned_data['autor_proposicao'].nome}"
                
                enc.sessao = form.cleaned_data["sessao"]
                enc.votacao = form.cleaned_data["votacao"]
                enc.proposicao = form.cleaned_data["proposicao"]
                enc.autor_proposicao = form.cleaned_data["autor_proposicao"]
                enc.data_aprovacao = form.cleaned_data["sessao"].data
                enc.save()
                
                oficio.corpo = enc.get_corpo_gerado()
                oficio.save()
                return redirect("oficios:preview", pk=oficio.pk)
        else:
            form = EncaminhamentoCriacaoForm(initial=initial, camara=request.camara, is_edit=True)
        return render(request, "oficios/oficio_encaminhamento_form.html", {"form": form, "title": "Editar Encaminhamento"})

    else:
        if request.method == "POST":
            form = OficioForm(request.POST, instance=oficio, camara=request.camara)
            if form.is_valid():
                form.save()
                return redirect("oficios:preview", pk=oficio.pk)
        else:
            form = OficioForm(instance=oficio, camara=request.camara)

        return render(request, "oficios/oficio_form.html", {"form": form, "title": "Editar Ofício Livre"})


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
