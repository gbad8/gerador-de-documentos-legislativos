from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SolicitacaoAcessoForm

def landing_page(request):
    if request.user.is_authenticated:
        # User is already logged in, show a different button in template
        pass

    if request.method == "POST":
        form = SolicitacaoAcessoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, 
                "Solicitação enviada com sucesso! Nossa equipe entrará em contato em breve para realizar o setup gratuito da sua Câmara."
            )
            return redirect("landing:index")
    else:
        form = SolicitacaoAcessoForm()

    return render(request, "landing/index.html", {"form": form})
