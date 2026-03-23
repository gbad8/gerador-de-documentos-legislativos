# CRC Cards - Sistema de Ofícios

## O que são CRC Cards?
**C**lasse - **R**esponsabilidades - **C**olaboradores

Cartões simples que ajudam a identificar o que cada classe faz e com quem ela trabalha.

---

## 📄 OFÍCIO

| **Classe: Oficio**                                                  |
|:--------------------------------------------------------------------|
| **Responsabilidades**                                               | **Colaboradores** |
| Armazenar dados do documento (número, assunto, corpo, data, status) | |
| Criar novo ofício                                                   | |
| Editar conteúdo                                                     | |
| Gerar PDF do documento                                              | |
| Validar campos obrigatórios                                         | |
| Salvar/recuperar documento                                          | |
| Solicitar número ao criar                                           | |

---

## 👤 PERFIL DE USUÁRIO

| **Classe: UsuarioPerfil** |
|:---|
| **Responsabilidades** | **Colaboradores** |
| Vincular identidade Entra ID ao domínio (entraIdObjectId) | Camara |
| Armazenar role no sistema (Admin/Operador) | |
| Armazenar nome e cargo | |
| Resolver câmara do usuário autenticado | |

---

## 🏛️ CÂMARA

| **Classe: Camara** |
|:---|
| **Responsabilidades** | **Colaboradores** |
| Armazenar dados institucionais (nome, estado, CNPJ, endereço, telefone) | UsuarioPerfil |
| Gerenciar logomarca | |
| Configurar dados para timbrado | |
| Fornecer informações para cabeçalho | |

---

## 👥 AUTOR

| **Classe: Autor** |
|:---|
| **Responsabilidades** | **Colaboradores** |
| Armazenar dados (nome, cargo) | |
| Formatar nome para assinatura | |
| Assinar documento | |

---

## 📬 DESTINATÁRIO (embutido em Ofício)

| **Classe: Destinatario** |
|:---|
| **Responsabilidades** | **Colaboradores** |
| Armazenar dados (nome, cargo, órgão, endereço) | — (parte do Oficio) |
| Definir pronome de tratamento | |
| Validar dados obrigatórios | |
| Formatar endereço completo | |

---

## 🔢 NUMERAÇÃO

| **Classe: Numeracao** |
|:---|
| **Responsabilidades** | **Colaboradores** |
| Controlar sequência numérica por autor | Autor |
| Gerar próximo número disponível | Oficio |
| Registrar número utilizado | |
| Reiniciar contagem (anual, se necessário) | |
| Garantir unicidade do número por autor | |
| Consultar último número gerado | |

---

## 📊 Resumo das Relações

```
                    ┌──────────────────┐
                    │  Microsoft       │
                    │  Entra ID        │  ◀── autenticação gerenciada
                    └────────┬─────────┘
                             │ entraIdObjectId
                             ▼
┌──────────────┐    ┌──────────────────┐
│    Camara     │◀───│  UsuarioPerfil   │  (vínculo Entra ID → Câmara + Role)
│   (tenant)   │    └──────────────────┘
└──────┬───────┘
       │ camaraId
       ├──────────────────────────────────────┐
       │                                      │
       ▼                                      ▼
┌──────────────┐                     ┌──────────────┐
│    Autor      │                     │    Oficio     │
└──────┬───────┘                     │              │
       │ autorId                     │ ┌──────────┐ │
       ├─────────────────────────────│▶│Destinat. │ │ ◀── embutido
       │                             │ └──────────┘ │
       │                             └──────────────┘
       │                                    ▲
       ▼                                    │ gera número
┌──────────────┐                            │
│  Numeracao    │───────────────────────────┘
│  (seq/ano)   │
└──────────────┘
```

### Cardinalidades

| Relação | Tipo |
|---------|------|
| Câmara → UsuarioPerfis | 1:N |
| Câmara → Autores | 1:N |
| Câmara → Ofícios | 1:N |
| Autor → Ofícios | 1:N |
| Autor → Numeração | 1:N (uma por ano) |
| Ofício → Destinatário | 1:1 (embutido) |

---

## 📝 Notas

- **6 classes no domínio**: Oficio, UsuarioPerfil, Camara, Autor, Destinatario (embutido), Numeracao
- **Autenticação delegada**: Entra ID cuida de login/senha/MFA; UsuarioPerfil só mapeia para o domínio
- **Destinatário embutido**: Não tem vida própria — é um subdocumento dentro de Ofício (MongoDB)
- **Numeração separada**: Regra de negócio importante (sequência por autor + ano) justifica classe própria
