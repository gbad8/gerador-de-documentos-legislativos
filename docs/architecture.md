# Arquitetura — GDL (Gerador de Documentos Legislativos)

## Stack Tecnológica

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| Linguagem | Python | 3.12+ |
| Framework | Django | 6.x |
| Views | Django Templates (.html) | — |
| Interatividade | HTMX + django-htmx | 2.x |
| ORM | Django ORM | — |
| Banco de Dados | PostgreSQL | 16+ |
| CSS | Bootstrap | 5.x |
| Autenticação | Django Auth nativo | — |
| Auth Integration | `django.contrib.auth` | — |
| Geração de PDF | WeasyPrint | — |
| Validação | Django Forms / ModelForms | — |
| Testes | pytest + pytest-django | — |
| Deploy | Docker / Render | — |

---

## Infraestrutura (Free Tier)

Todo o MVP roda em free tier — custo zero.

| Serviço | Plano | Limites | Uso no GDL |
|---------|-------|---------|-----------|
| **Supabase PostgreSQL** | Free | 500MB storage, 2 projetos gratuitos | Banco de dados do sistema |
| **Render** | Free | 750h/mês de runtime, domínio custom + SSL grátis | Deploy do web service |
| **UptimeRobot** | Free | 50 monitores, ping a cada 5min | Mantém o app acordado em horário comercial |

### Quando escalar (sinais de que saiu do free tier)

| Sinal | Ação |
|-------|------|
| Storage PostgreSQL > 400MB | Upgrade para Supabase Pro (~$25/mês) ou limpar histórico antigo |
| Precisa de mais de 1 web service | Upgrade para Render Individual ($7/mês por serviço) |
| App dorme fora do horário comercial | Aceitável — ou configurar ping 24/7 (750h cobre 1 serviço 24/7) |
| Precisa de background workers | Adicionar segundo serviço no Render |

### docker-compose.yml (ambiente local)

```yaml
services:
  gdl-web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgres://gdl:gdl@postgres:5432/gdl
    depends_on:
      - postgres

  postgres:
    image: postgres:16
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=gdl
      - POSTGRES_USER=gdl
      - POSTGRES_PASSWORD=gdl
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
```

Local usa PostgreSQL em container. Em produção, a connection string aponta para o Supabase e o deploy é feito via **Render** (diretamente do repositório GitHub, sem necessidade de Dockerfile).

### Deploy no Render

Render detecta o projeto Python automaticamente. A configuração mínima:

| Configuração | Valor |
|---|---|
| **Build Command** | `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate` |
| **Start Command** | `gunicorn gdl_web.wsgi:application` |
| **Variáveis de Ambiente** | `DATABASE_URL`, `SECRET_KEY`, `DJANGO_SETTINGS_MODULE`, `ALLOWED_HOSTS` |

---

## Tipo de Arquitetura

**Monólito modular** — projeto único, deployável como container Docker.

Não usamos microserviços, Celery ou message queues. O volume do sistema (50 usuários simultâneos, ~1000 docs/dia) não justifica essa complexidade.

---

## Estrutura do Projeto (Django Apps)

Cada app Django agrupa um módulo do domínio: models, forms, views, URLs e templates. Código compartilhado (tenant, serviços transversais) fica no app `core`.

```
gdl/
├── gdl/                              # App de configuração do projeto
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── core/                             # App: domínio compartilhado
│   ├── models.py                     # Camara, UsuarioPerfil
│   ├── admin.py                      # Admin para Camara
│   ├── middleware.py                  # TenantMiddleware (injeta camara no request)
│   └── managers.py                   # TenantManager (filtro automático por camara)
│
├── oficios/                          # App: ofícios
│   ├── models.py                     # Oficio, Numeracao
│   ├── forms.py                      # OficioForm (substitui VMs + Validators)
│   ├── views.py                      # create, edit, list, preview, generate_pdf
│   ├── urls.py
│   ├── services.py                   # NumeracaoService, PdfService (WeasyPrint)
│   ├── templates/oficios/
│   │   ├── oficio_list.html           # lista + busca HTMX
│   │   ├── oficio_form.html           # criar/editar (compartilhado)
│   │   ├── oficio_detail.html         # preview completo
│   │   ├── _preview.html              # partial HTMX
│   │   ├── _search_results.html       # partial HTMX (resultados da busca)
│   │   └── oficio_pdf.html            # template HTML do timbrado (WeasyPrint)
│   └── tests/
│       ├── test_models.py
│       ├── test_forms.py
│       ├── test_views.py
│       └── test_pdf.py
│
├── autores/                          # App: autores
│   ├── models.py                     # Autor
│   ├── admin.py                      # Admin para Autor (Django Admin nativo)
│   └── tests/
│       └── test_models.py
│
├── templates/                        # Templates globais
│   ├── base.html                     # Layout base (Bootstrap 5 CDN + HTMX)
│   ├── home.html                     # Página inicial
│   └── registration/
│       └── login.html                # Login (standalone, sem navbar)
│
├── static/
│   ├── css/
│   │   └── gdl.css                   # Estilos customizados
│   └── images/
│       ├── logo.png
│       └── logo_cc.png
│
├── docs/
├── manage.py
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── pytest.ini
```

### Regra de organização

| O que é | Onde fica |
|---------|----------|
| Model, form, view, URL de um módulo | `{app}/` |
| Templates específicos de um app | `{app}/templates/{app}/` |
| Entidades de domínio compartilhadas (Camara, UsuarioPerfil) | `core/models.py` |
| Serviço usado por mais de um app | `core/services.py` |
| Layout base e partials globais | `templates/` |
| Admin de CRUD simples (Camara, Autor) | `{app}/admin.py` (Django Admin nativo) |

---

## Multi-Tenancy

`Camara` funciona como tenant. Toda entidade principal tem `ForeignKey` para `Camara`.

O isolamento é garantido via um **custom Manager** e um **middleware**:

```python
# core/managers.py
class TenantManager(models.Manager):
    def for_camara(self, camara):
        return self.filter(camara=camara)
```

```python
# core/middleware.py
class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            perfil = request.user.usuarioperfil
            request.camara = perfil.camara
            request.role = perfil.role
        return self.get_response(request)
```

Nas views, o acesso é sempre filtrado:

```python
def oficio_list(request):
    oficios = Oficio.objects.for_camara(request.camara).order_by("-criado_em")
    return render(request, "oficios/oficio_list.html", {"oficios": oficios})
```

O `request.camara` é resolvido a partir do `UsuarioPerfil` do usuário autenticado.

---

## Modelo de Dados (PostgreSQL)

PostgreSQL é relacional. Cada entidade é uma tabela. Dados que no MongoDB seriam embutidos (Destinatário) viram **campos diretos na tabela do Ofício** — sem tabela separada, porque o destinatário não tem vida própria.

### Tabelas

| Tabela | Estratégia | Justificativa |
|--------|-----------|---------------|
| `core_camara` | Tabela raiz | Tenant — dados institucionais, logomarca em `BinaryField` |
| `core_usuarioperfil` | Tabela raiz | Vínculo User Django → Câmara + role |
| `autores_autor` | Tabela raiz | Referenciado por ofícios e numeração |
| `oficios_oficio` | Tabela raiz, **destinatário como campos diretos** | Destinatário não existe sem ofício |
| `oficios_numeracao` | Tabela raiz | Controle de sequência por autor + ano |

### Models Django

```python
# core/models.py
class Camara(models.Model):
    nome = models.CharField(max_length=200)
    estado = models.CharField(max_length=2)
    cnpj = models.CharField(max_length=18)
    endereco = models.TextField()
    telefone = models.CharField(max_length=20)
    logomarca = models.BinaryField(blank=True, null=True)

class UsuarioPerfil(models.Model):
    class Role(models.TextChoices):
        ADMIN = "Admin"
        OPERADOR = "Operador"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    camara = models.ForeignKey(Camara, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.OPERADOR)
    nome = models.CharField(max_length=200)
    cargo = models.CharField(max_length=200)
```

```python
# autores/models.py
class Autor(models.Model):
    camara = models.ForeignKey(Camara, on_delete=models.CASCADE)
    nome = models.CharField(max_length=200)
    cargo = models.CharField(max_length=200)

    objects = TenantManager()
```

```python
# oficios/models.py
class Oficio(models.Model):
    class Status(models.TextChoices):
        RASCUNHO = "rascunho"
        FINALIZADO = "finalizado"

    camara = models.ForeignKey(Camara, on_delete=models.CASCADE)
    autor = models.ForeignKey(Autor, on_delete=models.PROTECT)
    numero = models.CharField(max_length=20)
    assunto = models.CharField(max_length=500)
    corpo = models.TextField()
    data = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RASCUNHO)

    # Destinatário (campos diretos — não tem vida própria)
    destinatario_nome = models.CharField(max_length=200)
    destinatario_cargo = models.CharField(max_length=200)
    destinatario_orgao = models.CharField(max_length=200)
    destinatario_endereco = models.TextField()
    destinatario_pronome = models.CharField(max_length=50)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    objects = TenantManager()

class Numeracao(models.Model):
    camara = models.ForeignKey(Camara, on_delete=models.CASCADE)
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE)
    ano = models.IntegerField()
    ultimo_numero = models.IntegerField(default=0)

    objects = TenantManager()

    class Meta:
        unique_together = ("camara", "autor", "ano")
```

### Diagrama de Relações

```
┌──────────────┐
│    Camara     │ (tenant)
└──────┬───────┘
       │ FK camara
       ├──────────────────────────────────────┐
       │                                      │
       ▼                                      ▼
┌──────────────┐                     ┌──────────────┐
│UsuarioPerfil │                     │    Autor      │
│              │                     └──────┬───────┘
│ user (1:1) ──┤── auth_user                │ FK autor
└──────────────┘                            │
                              ┌─────────────┼─────────────┐
                              ▼             │             ▼
                       ┌──────────────┐     │      ┌──────────────┐
                       │  Numeracao    │     │      │    Oficio     │
                       │  (seq/ano)   │     │      │              │
                       │              │     │      │ destinatario_│
                       │  unique:     │     │      │ nome, cargo, │
                       │  (camara,    │     │      │ orgao, ...   │
                       │   autor,ano) │     │      └──────────────┘
                       └──────────────┘     │             │
                                            └─────────────┘
```

### Índices

```python
# Definidos via Meta.indexes nos models
class Oficio(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=["camara", "-criado_em"]),    # listagem por câmara
            models.Index(fields=["camara", "autor"]),          # filtro por autor
            models.Index(fields=["camara", "status"]),         # filtro por status
        ]

class Numeracao(models.Model):
    class Meta:
        unique_together = ("camara", "autor", "ano")           # garante uma seq por autor/ano

class Autor(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=["camara"]),                   # listagem por câmara
        ]
```

---

## HTMX — Uso no Projeto

HTMX é usado para interações que se beneficiam de não recarregar a página inteira. A integração é feita via `django-htmx`, que adiciona `request.htmx` para detectar requisições HTMX. Exemplos concretos:

**Preview do ofício** (carrega parcial sem reload):
```html
<button hx-get="{% url 'oficios:preview' oficio.pk %}"
        hx-target="#preview-container"
        hx-swap="innerHTML">
    Pré-visualizar
</button>
<div id="preview-container"></div>
```

**Validação de campo em tempo real**:
```html
<input name="destinatario_email"
       hx-post="{% url 'oficios:validate_field' %}"
       hx-trigger="blur"
       hx-target="#email-feedback" />
<span id="email-feedback"></span>
```

**Busca na lista de ofícios com filtro**:
```html
<input type="search"
       hx-get="{% url 'oficios:search' %}"
       hx-trigger="keyup changed delay:300ms"
       hx-target="#results-table" />
```

As views retornam template parcial para requisições HTMX e template completo para navegação normal:

```python
def oficio_preview(request, pk):
    oficio = Oficio.objects.for_camara(request.camara).get(pk=pk)
    template = "_preview.html" if request.htmx else "oficio_detail.html"
    return render(request, f"oficios/{template}", {"oficio": oficio})
```

---

## Geração de PDF

Usamos **WeasyPrint** para gerar PDF a partir de templates HTML+CSS. O timbrado é um template Django renderizado e convertido para PDF:

```python
# oficios/services.py
from weasyprint import HTML
from django.template.loader import render_to_string

class PdfService:
    def gerar_oficio(self, oficio, camara):
        html_string = render_to_string("oficios/oficio_pdf.html", {
            "oficio": oficio,
            "camara": camara,
        })
        return HTML(string=html_string).write_pdf()
```

O layout do timbrado (cabeçalho com logo, nome da câmara, rodapé com CNPJ/endereço) é definido em HTML+CSS no template `oficio_pdf.html` — sem dependência de ferramentas externas.

```html
<!-- oficios/templates/oficios/oficio_pdf.html -->
<!DOCTYPE html>
<html>
<head>
  <style>
    @page {
      margin: 2cm;
      @top-center { content: element(header); }
      @bottom-center { content: element(footer); }
    }
    .header { position: running(header); }
    .footer { position: running(footer); }
  </style>
</head>
<body>
  <div class="header">
    <img src="data:image/png;base64,{{ camara.logomarca_base64 }}" />
    <h1>{{ camara.nome }}</h1>
  </div>
  <div class="content">
    <p>Ofício nº {{ oficio.numero }}</p>
    <p>{{ oficio.corpo }}</p>
  </div>
  <div class="footer">
    {{ camara.endereco }} — CNPJ: {{ camara.cnpj }}
  </div>
</body>
</html>
```

---

## Autenticação e Autorização

**Django Auth** cuida de toda a autenticação (login, sessão).

O vínculo entre o usuário e o domínio do GDL é feito pelo model `UsuarioPerfil`:

```python
# core/models.py
class UsuarioPerfil(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    camara = models.ForeignKey(Camara, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=Role.choices)
    nome = models.CharField(max_length=200)
    cargo = models.CharField(max_length=200)
```

### Fluxo

1. Usuário acessa o GDL → redirecionado para `/login/`
2. Usuário faz login com username/password no Django
3. `TenantMiddleware` consulta `UsuarioPerfil` pelo `user` → injeta `camara` e `role` no `request`
4. `request.camara` é usado como filtro de tenant em todas as queries

### O que fica em cada lado

| Responsabilidade | Django Auth | PostgreSQL (UsuarioPerfil) |
|-----------------|-------------|----------------------------|
| Login/senha | ✅ | — |
| Vínculo com Câmara | — | ✅ |
| Role no domínio (Admin/Operador) | — | ✅ |
| Nome/cargo para assinatura | — | ✅ |

---

## Decisões Arquiteturais

| Decisão | Justificativa |
|---------|--------------|
| Django sobre ASP.NET | Ecossistema Python, ORM maduro, admin embutido, comunidade grande |
| Monólito | Volume do sistema não justifica microserviços |
| Django Templates sobre SPA | App baseado em formulários; server-side rendering é mais direto |
| HTMX sobre JS/SPA | Interatividade sem framework JavaScript separado |
| WeasyPrint sobre ReportLab | Template HTML+CSS é mais fácil de manter que API programática |
| PostgreSQL sobre MongoDB | ORM nativo do Django, migrations, admin, relações — tudo funciona out-of-the-box |
| Destinatário como campos diretos | Não tem vida própria fora do Ofício — evita tabela separada e JOIN desnecessário |
| Django Forms | Validação integrada nos forms, sem biblioteca extra |
| Django Admin para CRUD admin | Camara e Autores são CRUD simples — admin nativo poupa trabalho |
| Bootstrap 5 | Componentes prontos, prototipagem rápida, sem build step |
| Supabase PostgreSQL | Free tier de 500MB |
| Render | Deploy automático do GitHub, SSL + domínio custom grátis, sem config de container |

---

## Estratégia de Testes

Não seguimos TDD estrito (test-first). A regra é: **criou uma funcionalidade importante → cria o teste logo em seguida**, antes de passar para a próxima.

### O que testar e quando

| Criou... | Testa imediatamente | Tipo de teste |
|----------|---------------------|---------------|
| Model (ex: `Oficio`) | Regras de construção, validações, `__str__`, constraints | Unitário |
| Form (ex: `OficioForm`) | Campos obrigatórios, dados inválidos, limites, `clean()` | Unitário |
| Service (ex: `NumeracaoService`) | Lógica de sequência, virada de ano, unicidade | Unitário (com mock) |
| Service com I/O (ex: `PdfService`) | Gera PDF sem erro, contém dados esperados | Integração |
| View | Retorna status correto, redireciona, retorna template parcial | Integração (com `Client()`) |
| Fluxo completo (ex: criar ofício → gerar PDF) | Caminho feliz ponta a ponta | E2E (eventual) |

### Estrutura dos testes (dentro de cada app)

```
oficios/
└── tests/
    ├── test_models.py
    ├── test_forms.py
    ├── test_views.py
    └── test_pdf.py

core/
└── tests/
    ├── test_models.py
    └── test_numeracao_service.py

autores/
└── tests/
    └── test_models.py
```

### Stack de testes

| Ferramenta | Uso |
|-----------|-----|
| **pytest** | Framework de testes |
| **pytest-django** | Integração com Django (fixtures, client, DB de teste) |
| **unittest.mock** | Mocks (stdlib do Python, sem dependência extra) |
| **factory_boy** | Factories para criar objetos de teste (opcional) |

### Exemplo prático do fluxo

```
1. Crio Oficio em oficios/models.py
   → Escrevo test_models.py (construção, status default, campos obrigatórios, __str__)

2. Crio OficioForm em oficios/forms.py
   → Escrevo test_forms.py (assunto vazio, corpo vazio, destinatário incompleto)

3. Crio NumeracaoService em core/services.py
   → Escrevo test_numeracao_service.py (próximo número, virada de ano, autor diferente)

4. Crio views em oficios/views.py
   → Escrevo test_views.py (POST válido redireciona, POST inválido retorna form com erros)
```

### O que NÃO testar

- Templates (.html) — validados visualmente
- Configuração (`settings.py`) — validada pelo startup
- Models sem lógica custom — o ORM do Django já é testado pelo framework

---

## Roadmap (futuras implementações)

| Feature | Descrição | Prioridade |
|---------|-----------|------------|
| Assistente de IA | Geração de texto do corpo do ofício a partir de um tópico, usando LLM | Média |
| Novos modelos de documento | Indicações, portarias, e outros documentos legislativos | Baixa |
