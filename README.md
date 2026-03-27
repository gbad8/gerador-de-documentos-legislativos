# GDL - Gerador de Documentos Legislativos

O **GDL (Gerador de Documentos Legislativos)** é uma aplicação web desenvolvida para facilitar a criação, o gerenciamento e a emissão de documentos oficiais (como ofícios) em Câmaras Municipais e outros órgãos do Poder Legislativo. O sistema centraliza a produção de documentos, padroniza a formatação e automatiza a numeração, garantindo maior controle e eficiência administrativa.

<img width="2816" height="1504" alt="demo_gdl_desktop" src="https://github.com/user-attachments/assets/faf9dd46-7d52-4a8a-9989-cf56f751b776" />



## Funcionalidades Principais

*   **Gestão Completa de Ofícios**: Criação, formatação e acompanhamento do ciclo de vida dos documentos. O sistema gerencia automaticamente o status do ofício (RASCUNHO, FINALIZADO, MODIFICADO) com base no preenchimento de seus campos.
*   **Geração de PDF Automática**: Transformação instantânea de ofícios digitais em documentos PDF prontos para impressão ou envio oficial, com formatação padronizada e inclusão do cabeçalho da instituição (utilizando a biblioteca WeasyPrint).
*   **Controle Inteligente de Numeração**: Sistema de numeração automática e única, estruturada com base na Câmara, Órgão emissor, Autor do documento e Ano em curso (ex: Ofício n° 12/2026 — Ver. João).
*   **Gerenciamento de Órgãos Internos**: Cadastro e organização dos diversos órgãos e departamentos internos da Câmara Legislativa, permitindo segmentar e organizar a emissão de documentos por setor.
*   **Gerenciamento de Autores**: Cadastro de vereadores e demais autoridades com permissão para expedir documentos.
*   **Landing Page Institucional**: Página de apresentação do projeto voltada para a adesão de novas Câmaras, destacando as vantagens do sistema e oferecendo um formulário de contato/solicitação de acesso.
*   **Autenticação e Perfis**: Controle seguro de usuários, permissões e acesso aos dados de cada Câmara.

## Tecnologias Utilizadas

O projeto foi construído utilizando as melhores práticas do ecossistema Python moderno:

*   **Backend**: Python, [Django](https://www.djangoproject.com/) (versão 6+)
*   **Banco de Dados**: PostgreSQL (integrado via `psycopg`, compatível com instâncias na nuvem como o Supabase)
*   **Geração de Documentos (PDF)**: [WeasyPrint](https://doc.courtbouillon.org/weasyprint/en/latest/) 
*   **Frontend**: HTML, CSS, e [HTMX](https://htmx.org/) (para interatividade rápida em tempo real sem a necessidade de um framework JavaScript pesado / SPAs).
*   **Autenticação**: `django-allauth`
*   **Deploy**: Gunicorn, Whitenoise (para arquivos estáticos), preparados para hospedagem em plataformas como o Render.

## Como Executar o Projeto Localmente

### 1. Pré-requisitos
*   [Python 3.10+](https://www.python.org/downloads/)
*   [PostgreSQL](https://www.postgresql.org/) (ou um banco SQLite, se ajustado para desenvolvimento)
*   Bibliotecas do sistema operacional exigidas pelo *WeasyPrint* (como Pango, Cairo, etc.). Ver [documentação do WeasyPrint](https://doc.courtbouillon.org/weasyprint/en/latest/install.html).

### 2. Configurando o Ambiente

```bash
# Clone o repositório
git clone https://github.com/gbad8/gerador-de-documentos-legislativos.git
cd gerador-de-documentos-legislativos

# Crie e ative um ambiente virtual (venv)
python -m venv .venv

# No Linux/macOS
source .venv/bin/activate
# No Windows
# .venv\Scripts\activate

# Instale as dependências requeridas
pip install -r gdl_web/requirements.txt
```

### 3. Variáveis de Ambiente
Crie um arquivo `.env` na raiz ou dentro da pasta `gdl_web/` informando as credenciais necessárias:
```
SECRET_KEY=sua-secret-key-super-secreta-do-django
DEBUG=True
DATABASE_URL=postgres://usuario:senha@localhost:5432/nome_do_banco  # Caso utilize Postgres local ou remoto
```

### 4. Inicializando o Banco de Dados
Acesse a pasta `gdl_web/` onde fica o projeto Django e aplique as migrações:
```bash
cd gdl_web/
python manage.py migrate
```

Crie um usuário administrador para acessar o painel (`/admin`):
```bash
python manage.py createsuperuser
```

### 5. Rodando o Servidor
Com o banco configurado e atualizado, inicie o servidor de desenvolvimento do Django:
```bash
python manage.py runserver
```
Acesse `http://localhost:8000/` para visualizar a aplicação.

## Estrutura de Diretórios (Arquitetura)

Dentro de `gdl_web/`, o monólito Django está dividido nos seguintes apps (módulos):

*   **`core/`**: Configurações gerais, modelos base e views de infraestrutura compartilhada.
*   **`oficios/`**: Lógica de negócio, modelagem e fluxos principais para criação e emissão dos Ofícios e PDFs.
*   **`orgaos/`**: Gerenciamento das entidades/departamentos da Câmara legislativa e sua numeração.
*   **`autores/`**: Gerenciamento de vereadores e emissores dos documentos.
*   **`landing/`**: Views e templates públicos focados em apresentar a plataforma e captar novos clientes.
