# Copilot Instructions for GDL (Gerador de Documentos Legislativos)

## Project Overview

GDL is a Django web application for legislative document management in municipal chambers. It provides a multi-tenant system where each chamber manages its own documents (ofícios/official letters), with automatic PDF generation, numbering, and user role-based access control.

**Key Tech Stack:**
- Backend: Django 6.0+ with PostgreSQL
- Frontend: HTMX + HTML/CSS (no heavy JavaScript frameworks)
- PDF Generation: WeasyPrint
- Testing: pytest + pytest-django
- Auth: django-allauth

## Build, Test & Lint Commands

All commands run from the `gdl_web/` directory unless noted otherwise.

### Installation & Setup
```bash
# Install dependencies
pip install -r gdl_web/requirements.txt

# Create .env file (if not exists)
# DATABASE_URL=postgres://user:password@localhost:5432/gdl
# SECRET_KEY=your-secret-key
# DEBUG=True

# Apply migrations
cd gdl_web/
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
```

### Running the Development Server
```bash
python manage.py runserver
# Accessible at http://localhost:8000/
```

### Testing
```bash
# Run all tests with coverage
pytest --cov=. --cov-report=term

# Run tests for specific app
pytest oficios/tests/

# Run specific test file
pytest oficios/tests/test_models.py

# Run specific test class or function
pytest oficios/tests/test_models.py::TestOficio::test_str

# Run tests with verbose output
pytest -v

# Run with specific test marker
pytest -m "not slow"
```

**Current Test Coverage:** 84% (92 passing tests)

### Database
```bash
# Create migrations for model changes
python manage.py makemigrations

# Apply pending migrations
python manage.py migrate

# Reset database (careful!)
python manage.py flush

# Create test database
pytest --create-db
```

## High-Level Architecture

### Multi-Tenant Design
- **TenantMiddleware** (`core/middleware.py`) injects `request.camara` (Chamber object) and `request.role` into every request
- All models use `objects = TenantManager()` with custom `for_camara()` queryset filter to ensure data isolation
- Users access the system via their `UsuarioPerfil` which links them to a specific chamber

### Django App Structure

| App | Purpose |
|-----|---------|
| **core** | Base models (Camara, UsuarioPerfil, Numeracao), tenant middleware, abstract base models, mixins, managers |
| **oficios** | Main business logic: Oficio and OficioEncaminhamento models, form handling, PDF generation via services |
| **autores** | Author management (Vereadores, Presidents, etc.) with cargo hierarchy |
| **orgaos** | Internal departments/organs of the chamber |
| **orgaos_externos** | External entity catalog (destinations for official letters) |
| **indicacoes** | Related legislation documents (similar structure to oficios) |
| **legislaturas** | Legislative term management |
| **sessoes** | Legislative session tracking |
| **landing** | Public landing page and marketing views |

### Key Design Patterns

**Model Inheritance:**
- `DocumentoLegislativoBase` (in core/models.py) provides shared fields for all legislative documents (camara, autor, numero, data, status, criado_em, atualizado_em)
- All document models inherit from this base class
- `CoautoriaMixin` handles co-authored documents with author ordering by cargo hierarchy
- `DestinatarioMixin` provides recipient/destination fields (destinatario_nome, cargo, orgao, endereco, pronome)

**Services Layer:**
- `NumeracaoService` handles automatic & manual document numbering with transaction safety (select_for_update)
- `PdfService` generates WeasyPrint-based PDFs with custom styling
- `PronomeService` conjugates pronouns based on gender and treatment level (Brazilian Portuguese)

**Status Management:**
- Documents have a `DocumentoStatus` enum: RASCUNHO (draft) → FINALIZADO (finalized) → MODIFICADO (modified)
- Status is calculated automatically based on `_campos_completos()` and `calcular_status()` method
- `CAMPOS_OBRIGATORIOS` list defines which fields are required for finalization

### Request Context
- Every authenticated request has `request.camara` set by TenantMiddleware
- Views use `@login_required` decorator and filter querysets via `Model.objects.for_camara(request.camara)`
- Unauthenticated users cannot access `/painel/*` routes

## Key Conventions

### Testing Conventions
- **Location**: Tests live in `{app}/tests/` directory (e.g., `oficios/tests/test_models.py`)
- **Structure**: Use pytest fixtures from shared `conftest.py`; each test class inherits test data fixtures
- **Database**: Use `@pytest.fixture` decorator; fixtures with `db` parameter need database access
- **Common Fixtures**: `camara`, `outra_camara` (for tenant isolation tests), `autor`, `usuario`, `usuario_perfil` are pre-defined in conftest.py
- **Naming**: Test classes use `Test*` naming; test functions use `test_*` naming (enforced by pytest.ini)
- **Forms**: When testing forms, include all required fields including `selecao_destino` for document recipient selection

### Model Conventions
- All document models implement `objects = TenantManager()` with custom `for_camara()` filter
- `__str__` methods return human-readable output including document number/name (e.g., `"Ofício n° 001/2026 — João da Silva"`)
- Use Django's `TextChoices` for enums (e.g., `Status`, `Cargo`, `Tipo`)
- Foreign keys to authors/recipients use `.related_name` with app label template: `"%(app_label)s_%(class)s_fieldname"` to avoid clashes
- `CAMPOS_OBRIGATORIOS` list defines required fields; implement `_campos_completos()` helper method for status checks
- Call parent `save()` to ensure status is calculated via `calcular_status()`

### View Conventions
- Use function-based views with `@login_required` decorator
- Use `Model.objects.for_camara(request.camara)` to filter all querysets
- Use `select_related()` to reduce N+1 queries where models have many ForeignKey relationships
- Use `django.contrib.messages` for user feedback (success/error messages)
- Use `get_object_or_404()` to safely retrieve single objects
- Redirect to list view after POST (success) or re-render form on validation errors
- Implement pagination using Django's `Paginator` class
- Return `page_obj` in context when paginating

### Form Conventions
- Forms must accept `camara` parameter in `__init__` to filter choices by chamber
- Include `selecao_destino` field for document recipient selection (manual vs. catalog)
- Use conditional `clean()` method to validate based on recipient selection mode
- Use `ModelChoiceField` with `queryset=None` in `__init__` to filter dynamically

### Template Conventions
- Templates use HTMX for dynamic interactions; no Vue/React components
- Use `{{ request.camara.nome }}` to display chamber name in shared header templates
- HTMX attributes (hx-get, hx-post, hx-swap) trigger server-side view fragments
- Use Django template tags for form rendering and conditional blocks
- List views should use pagination with `page_obj.object_list` in context

### Service Layer Conventions
- Services are stateless, single-responsibility classes with @staticmethod methods
- Use `@transaction.atomic()` and `.select_for_update()` for operations requiring consistent state (e.g., numbering)
- Generate business logic output (e.g., rendered body text) as return values, not by modifying models directly

### URL Conventions
- Admin app at `/admin/`
- Public routes at `/` (landing.urls)
- Authenticated dashboard at `/painel/`
- Feature-specific routes under `/painel/{feature}/` (e.g., `/painel/oficios/`, `/painel/configuracoes/`)
- Each Django app has its own urls.py file and is included in the main urlpatterns
- Use `name` parameter for URL reversing

### Environment Configuration
- Use `.env` file for sensitive settings (DATABASE_URL, SECRET_KEY, etc.)
- `.env` is loaded by `python-dotenv` in settings.py
- For development: `DEBUG=True`, PostgreSQL local or cloud
- For production: `DEBUG=False`, PostgreSQL on cloud (e.g., Supabase), WhiteNoise for static files

### Migration Conventions
- When moving models between apps, use `SeparateDatabaseAndState` to decouple state and database operations
- Always add proper dependencies between migrations to ensure correct execution order
- For robustness with new databases, check if tables/columns exist before altering them
- Include both `state_operations` and `database_operations` as needed for consistency
- Test migrations with `pytest` to ensure they work on fresh databases

## Common Workflows

### Adding a New Document Type
1. Create model inheriting from `DocumentoLegislativoBase`, `CoautoriaMixin`, `DestinatarioMixin`
2. Define `CAMPOS_OBRIGATORIOS` and `_campos_completos()` method in model
3. Create ModelForm in forms.py that accepts `camara` parameter
4. Create views (list, create, detail) with `@login_required` and `.for_camara()` filter
5. Implement pagination using `Paginator` if list is large
6. Add tests in `tests/test_models.py`, `tests/test_forms.py`, `tests/test_views.py`
7. Add URL pattern in app's urls.py and include in main urlpatterns
8. Use `NumeracaoService` and `PdfService` if document needs numbering/PDF generation
9. Run tests to ensure coverage is above 80%

### Adding a New Configuration Page
1. Create model in relevant app (e.g., `orgaos/models.py`)
2. Register in Django admin for superuser management
3. Create list/create/update views protected with `@login_required`
4. Filter by `request.camara` to ensure tenant isolation
5. Add to `/painel/configuracoes/` URL hierarchy
6. Add template with HTMX interactions if needed
7. Include `selecao_destino` or similar choice fields if applicable

### Handling Migration Issues with Multi-Tenant Moves
When moving models between apps (especially with multi-tenant architecture):
1. Use `SeparateDatabaseAndState` to separate state changes from database changes
2. Add explicit dependencies between migrations to control execution order
3. Make SQL operations robust by checking for table/column existence
4. Test migrations on both fresh databases and existing schemas
5. Run full test suite to ensure no data integrity issues

### Running Tests Before Commit
```bash
cd gdl_web/
pytest --cov=. -v
```
Aim for high coverage; new models/views should have 80%+ coverage.

**Recent Changes:**
- ✅ Fixed migration conflicts from moving `Numeracao` model to core app
- ✅ All 92 tests passing (84% coverage)
- ✅ Multi-tenant design fully working with tenant isolation
