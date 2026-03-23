from core.models import UsuarioPerfil


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.camara = None
        request.role = None

        if request.user.is_authenticated:
            try:
                perfil = UsuarioPerfil.objects.select_related("camara").get(
                    user=request.user
                )
                request.camara = perfil.camara
                request.role = perfil.role
            except UsuarioPerfil.DoesNotExist:
                pass

        return self.get_response(request)
