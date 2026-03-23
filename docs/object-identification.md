# Identificação de Objetos - Análise de Substantivos e Verbos

## Metodologia
Esta análise identifica candidatos a classes através da extração de **substantivos** (potenciais classes e atributos) e **verbos** (potenciais métodos e operações) dos documentos de requisitos e casos de uso.

---

## SUBSTANTIVOS IDENTIFICADOS

### **Entidades Principais do Domínio**

**📄 OFÍCIO**
- Documento principal do sistema
- Atributos identificados: número, autor, destinatário, assunto, corpo do texto, data, status (rascunho/finalizado)
- Operações: criar, editar, visualizar, gerar PDF, salvar, excluir, gerar numeração

**👤 USUÁRIO**
- Entidade que opera o sistema
- Tipos: Operador (Parlamentar, Secretário, Assessor Jurídico), Administrador
- Atributos: nome, tipo, cargo, câmara vinculada, credenciais
- Operações: autenticar, acessar, criar ofício, gerenciar histórico

**🏛️ CÂMARA**
- Órgão legislativo municipal
- Atributos: nome, estado, logomarca, endereço, e-mail, telefone, CNPJ
- Operações: configurar atributos, visualizar dados institucionais

**👥 AUTOR**
- Pessoa responsável pelo ofício
- Atributos: nome, cargo

**📬 DESTINATÁRIO** 
- Pessoa/órgão que receberá o ofício
- Atributos: nome, cargo, órgão, endereço, pronome de tratamento (se cabível)
- Operações: validar dados, formatar informações

### **Entidades de Controle e Interface**

**📋 FORMULÁRIO**
- Interface para entrada de dados
- Atributos: campos obrigatórios, campos opcionais, validações
- Operações: preencher, validar, limpar, salvar automaticamente

**🔧 TEMPLATE**
- Modelo de formatação do documento
- Atributos: estrutura, formatação, cabeçalho, rodapé
- Operações: aplicar formatação, configurar, ativar

**🏷️ TIMBRADO**
- Elementos visuais oficiais do documento
- Atributos: logomarca, nome do órgão, dados institucionais
- Operações: inserir, configurar, validar

**👁️ PRÉ-VISUALIZAÇÃO**
- Representação visual do documento final
- Atributos: layout, formatação aplicada
- Operações: gerar, exibir, atualizar

**📁 PDF**
- Formato final do documento
- Atributos: qualidade (300 DPI), proteção, nomenclatura automática
- Operações: converter, gerar, baixar, proteger

### **Entidades de Persistência e Controle**

**📚 HISTÓRICO**
- Registro de documentos criados
- Atributos: lista de ofícios, filtros de busca
- Operações: listar, filtrar, buscar, ordenar

**🔐 SESSÃO**
- Controle de acesso do usuário
- Atributos: usuário autenticado, tempo ativo, dados temporários
- Operações: iniciar, validar

**🔢 NUMERAÇÃO**
- Controle sequencial de ofícios
- Atributos: número atual, ano, autor
- Operações: gerar próximo número, validar unicidade

**💾 BACKUP**
- Cópia de segurança dos dados
- Atributos: dados salvos, horário, local armazenamento
- Operações: executar, validar, restaurar

**📝 LOG**
- Registro de atividades
- Atributos: ação executada, usuário, timestamp, IP
- Operações: registrar, consultar (só administrador)

### **Entidades de Validação e Configuração**

**✅ VALIDAÇÃO**
- Controle de qualidade dos dados
- Atributos: regras de validação, mensagens de erro
- Operações: validar campos, exibir alertas, impedir prosseguimento

**⚙️ CONFIGURAÇÃO**
- Definições do sistema
- Atributos: autores, dados institucionais
- Operações: alterar, salvar, aplicar

**📧 EMAIL**
- Sistema de envio de documentos
- Atributos: destinatário, assunto, anexo (PDF)
- Operações: enviar, validar endereço

---

## VERBOS IDENTIFICADOS

### **Verbos de Criação e Manipulação**
- **criar** → criar ofício, criar usuário, criar template
- **gerar** → gerar PDF, gerar numeração, gerar pré-visualização
- **aplicar** → aplicar formatação, aplicar template, aplicar timbrado
- **inserir** → inserir dados, inserir timbrado, inserir cabeçalho
- **salvar** → salvar documento, salvar configuração
- **editar** → editar ofício, editar template
- **configurar** → configurar câmara, configurar template

### **Verbos de Validação e Controle**
- **validar** → validar campos, validar dados, validar formato
- **verificar** → verificar completude, verificar integridade
- **impedir** → impedir geração, impedir acesso
- **bloquear** → bloquear edição
- **controlar** → controlar acesso, controlar versões

### **Verbos de Visualização e Consulta**
- **visualizar** → visualizar documento, visualizar histórico
- **exibir** → exibir formulário, exibir lista, exibir mensagem
- **apresentar** → apresentar dados, apresentar opções
- **listar** → listar documentos, listar usuários
- **buscar** → buscar por texto, buscar no histórico
- **filtrar** → filtrar por período, filtrar por status

### **Verbos de Acesso e Segurança**
- **autenticar** → autenticar usuário
- **acessar** → acessar sistema, acessar configurações
- **logar** → registrar atividade, fazer login
- **recuperar** → recuperar senha, recuperar sessão

### **Verbos de Transferência e Comunicação**
- **baixar** → baixar PDF, baixar documento
- **enviar** → enviar por email, enviar documento
- **transferir** → transferir backup
- **exportar** → exportar documento

### **Verbos de Manutenção e Suporte**
- **backup** → realizar backup, restaurar backup
- **monitorar** → monitorar sistema, monitorar performance
- **limpar** → limpar cache, limpar dados temporários
- **atualizar** → atualizar dados, atualizar template

---

## CANDIDATOS A CLASSES IDENTIFICADOS

### **Classes de Entidade (representam conceitos do mundo real)**
1. **Oficio** - documento principal do sistema
2. **Usuario** - operadores do sistema (funcionários da câmara)
3. **Camara** - órgão legislativo municipal
4. **Autor** - pessoa responsável pelo ofício
5. **Destinatario** - pessoa/órgão que receberá o ofício
6. **Template** - modelo de formatação do documento

### **Análise de Responsabilidades**

**OFICIO** - classe central
- Atributos: número, assunto, corpo do texto, data, status, autor, destinatário
- Métodos: criar(), editar(), gerar PDF(), validar(), salvar()

**USUARIO** - quem opera o sistema
- Atributos: nome, email, senha, tipo, cargo, câmara vinculada
- Métodos: autenticar(), criar ofício(), acessar histórico()

**CAMARA** - contexto institucional
- Atributos: nome, estado, endereço, telefone, CNPJ, logomarca
- Métodos: configurar dados(), gerar timbrado()

**AUTOR** - responsável pelo documento
- Atributos: nome, cargo
- Métodos: assinar(), formatar nome()

**DESTINATARIO** - receptor do ofício  
- Atributos: nome, cargo, órgão, endereço, tratamento
- Métodos: validar dados(), formatar endereço()

**TEMPLATE** - formatação padrão
- Atributos: estrutura, estilos, margens, fontes
- Métodos: aplicar formatação(), renderizar()

---

## PRÓXIMOS PASSOS
1. ✅ Classes básicas identificadas
2. ⏳ Definir atributos detalhados para cada classe
3. ⏳ Especificar métodos e operações
4. ⏳ Estabelecer relacionamentos entre classes
5. ⏳ Criar diagrama de classes UML
