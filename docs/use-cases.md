# Casos de Uso - GDL (Gerador de Documentos Legislativos)

## Visão Geral
Este documento apresenta os casos de uso do sistema GDL, organizados por atores e funcionalidades principais.

---

## Atores do Sistema

### 👤 **Usuário Operador**
- Funcionário da câmara legislativa responsável pela criação de ofícios
- Acesso às funcionalidades principais de criação e edição
- Não possui permissões administrativas
- Pode ser de diferentes tipos: Parlamentar, secretário, Assessor jurídico ou Parlamentar etc.

### 👥 **Administrador**
- Usuário com privilégios elevados
- Gerencia configurações de templates e timbrados
- Controla acessos e monitora o sistema

---

## Casos de Uso Principais

### **UC01 - Criar Novo Ofício**

**Ator Principal**: Usuário Operador  
**Objetivo**: Criar um novo ofício oficial da câmara legislativa  
**Pré-condições**: 
- Usuário autenticado no sistema
- Template padrão configurado

**Fluxo Principal**:
1. Usuário acessa o sistema e seleciona o botão de criar novo ofício
2. Sistema apresenta formulário com campos obrigatórios:
   - Autor
   - Destinatário (nome, cargo, órgão, endereço)
   - Assunto do ofício
   - Corpo do texto
   - Data (preenchida automaticamente ou manualmente)
3. Usuário preenche os dados necessários
4. Sistema valida campos em tempo real
5. Usuário finaliza preenchimento
6. Sistema gera numeração automática do ofício baseado no autor escolhido
7. Sistema salva dados em texto
8. Caso de uso encerra com sucesso

**Fluxos Alternativos**:
- **A1 - Campo obrigatório não preenchido**: Sistema destaca campo em vermelho e impede prosseguimento
- **A2 - Falha de conexão**: Sistema mantém dados localmente até reconexão

**Pós-condições**: 
- Ofício criado e salvo como rascunho
- Dados disponíveis para pré-visualização e para geração de PDF

---

### **UC02 - Pré-visualização do Documento**

**Ator Principal**: Usuário Operador  
**Objetivo**: Verificar formatação e layout antes da geração de PDF  
**Pré-condições**: 
- Ofício criado (UC01) ou editado (UC03)
- Dados mínimos preenchidos

**Fluxo Principal**:
1. Usuário solicita pré-visualização
2. Sistema valida se dados mínimos estão preenchidos
3. Sistema aplica template padrão aos dados
4. Sistema insere timbrado da câmara automaticamente
5. Sistema gera visualização web exata do layout final
6. Sistema apresenta documento formatado na tela
7. Usuário analisa resultado
8. Caso de uso encerra com sucesso

**Fluxos Alternativos**:
- **A1 - Dados insuficientes**: Sistema exibe mensagem informativa sobre campos pendentes
- **A2 - Falha na renderização**: Sistema oferece opção de gerar PDF direto

**Pós-condições**: 
- Documento visualizado conforme será impresso
- Usuário pode prosseguir para geração de PDF ou retornar para edição

---

### **UC03 - Editar Ofício Existente**

**Ator Principal**: Usuário Operador  
**Objetivo**: Modificar ofício salvo anteriormente  
**Pré-condições**: 
- Usuário autenticado
- Ofício existente

**Fluxo Principal**:
1. Usuário acessa lista de ofícios salvos
2. Sistema apresenta histórico de documentos do usuário
3. Usuário seleciona ofício para editar
4. Sistema carrega dados salvos no formulário
5. Usuário modifica campos desejados
6. Sistema valida alterações em tempo real
7. Sistema aplica auto-save das modificações
8. Usuário confirma alterações
9. Sistema atualiza dados salvos
10. Caso de uso encerra com sucesso

**Fluxos Alternativos**:
- **A3 - Perda de dados durante edição**: Sistema restaura última versão 

**Pós-condições**: 
- Ofício atualizado com novas informações
- Versão anterior mantida no histórico

---

### **UC04 - Gerar PDF Final**

**Ator Principal**: Usuário Operador  
**Objetivo**: Produzir documento oficial em formato PDF para envio/impressão  
**Pré-condições**: 
- Ofício existente

**Fluxo Principal**:
1. Usuário solicita geração de PDF (botão "Gerar PDF")
2. Sistema valida completude de todos os campos obrigatórios
3. Sistema aplica formatação oficial padrão
4. Sistema insere timbrado da câmara e informações no cabeçalho
5. Sistema adiciona dados institucionais no rodapé
6. Sistema adiciona local para assinatura com nome do autor
7. Sistema gera PDF/A com qualidade 300 DPI
8. Sistema aplica nome automático ao arquivo
9. Sistema oferece opções de download ou envio por email
10. Usuário baixa ou envia documento
11. Caso de uso encerra com sucesso

**Fluxos Alternativos**:
- **A1 - Validação falha**: Sistema destaca campos pendentes e impede geração
- **A2 - Falha de download**: Sistema mantém arquivo disponível por 24h para nova tentativa

**Pós-condições**: 
- PDF oficial gerado e disponibilizado
- Log de geração registrado no sistema

---

### **UC05 - Gerenciar Histórico de Documentos**

**Ator Principal**: Usuário Operador
**Objetivo**: Consultar e organizar ofícios criados anteriormente
**Pré-condições**: 
- Usuário autenticado

**Fluxo Principal**:
1. Usuário acessa seção de histórico
2. Sistema apresenta lista cronológica de documentos do usuário
3. Sistema exibe para cada item: número, destinatário, assunto, data, status
4. Usuário pode filtrar por: autor, destinatário, período, status
5. Usuário pode buscar por texto no assunto
6. Sistema apresenta resultados filtrados
7. Usuário seleciona ação: visualizar, editar, baixar, excluir
8. Sistema executa ação selecionada
9. Caso de uso encerra conforme ação escolhida

**Fluxos Alternativos**:
- **A1 - Nenhum documento encontrado**: lista aparece vazia
- **A2 - Erro ao carregar histórico**: Sistema exibe mensagem e tenta recarregar
- **A3 - Tentativa de exclusão de documento finalizado**: Sistema solicita confirmação adicional

**Pós-condições**: 
- Usuário visualiza e gerencia seus documentos
- Ações executadas conforme seleção

---

## Casos de Uso Administrativos

### **UC06 - Gerenciar Informações Institucionais**

**Ator Principal**: Administrador  
**Objetivo**: Configurar logomarcas e dados institucionais  
**Pré-condições**: 
- Usuário administrador autenticado

**Fluxo Principal**:
1. Administrador acessa "Configurações > Informações Institucionais"
2. Sistema apresenta formulário de configuração:
   - Upload de logomarca
   - Nome da câmara
   - Dados institucionais (endereço, telefone, CNPJ)
3. Administrador preenche/atualiza informações
4. Sistema valida arquivos e dados inseridos
5. Administrador confirma configuração
6. Sistema salva e insere as informações no template
7. Caso de uso encerra com sucesso

**Fluxos Alternativos**:
- **A1 - Arquivo inválido**: Sistema rejeita upload e solicita formato correto
- **A2 - Dados incompletos**: Sistema destaca campos obrigatórios
- **A3 - Logomarca muito grande**: Sistema oferece redimensionamento automático

**Pós-condições**: 
- Template configurado e disponível para uso

---

### UC07 - Gerenciar Autores ###
**Ator Principal**: Administrador  
**Objetivo**: Adicionar ou remover autores (parlamentares)
**Pré-condições**: 
- Usuário administrador autenticado

**Fluxo Principal**:
1. Administrador acessa "Configurações > Informações Institucionais"
2. Sistema apresenta lista de parlamentares (autores) cadastrados
3. Administrador pode remover, adicionar ou modificar parlamentares e seus dados
4. Sistema valida dados inseridos
5. Administrador confirma configuração
6. Sistema salva informações
7. Caso de uso encerra com sucesso

FLuxos Alternativos:
- **A1 - Dados incompletos na adição ou modificação:** Sistema destaca campos obrigatórios
- **A2 - Remoção mal sucedida:** Sistema informa ao usuário e pede que tente novamente

### UC08 - Gerenciar Órgãos ###
**Ator Principal**: Administrador  
**Objetivo**: Adicionar ou remover órgãos internos
**Pré-condições**: 
- Usuário administrador autenticado

**Fluxo Principal**:
1. Administrador acessa "Configurações > Informações Institucionais"
2. Sistema apresenta lista de órgãos internos cadastrados
3. Administrador pode remover, adicionar ou modificar órgãos e seus dados
4. Sistema valida dados inseridos
5. Administrador confirma configuração
6. Sistema salva informações
7. Caso de uso encerra com sucesso

FLuxos Alternativos:
- **A1 - Dados incompletos na adição ou modificação:** Sistema destaca campos obrigatórios
- **A2 - Remoção mal sucedida:** Sistema informa ao usuário e pede que tente novamente

---

## Casos de Uso do Sistema

### **UC09 - Realizar Backup Automático**

**Ator Principal**: Sistema
**Objetivo**: Garantir segurança dos dados através de backups regulares
**Pré-condições**: 
- Sistema em operação
- Horário de backup programado

**Fluxo Principal**:
1. Sistema identifica horário de backup (diário às 2h)
2. Sistema verifica espaço disponível para backup
3. Sistema coleta dados a serem salvos:
   - Documentos criados/modificados nas últimas 24h
   - Configurações alteradas
   - Logs do sistema
4. Sistema compacta dados coletados
5. Sistema transfere backup para storage seguro
6. Sistema valida integridade do backup criado
7. Sistema atualiza registro de backups realizados
8. Sistema remove backups antigos conforme política de retenção
9. Caso de uso encerra com backup completo

**Fluxos Alternativos**:
- **A1 - Espaço insuficiente**: Sistema envia alerta para administrador e tenta limpar arquivos antigos
- **A2 - Falha na transferência**: Sistema tenta novamente em 1 hora
- **A3 - Backup corrompido**: Sistema gera novo backup e alerta administradores

**Pós-condições**: 
- Dados protegidos por backup válido
- Sistema pronto para recuperação se necessário

---

### **UC10 - Gerar Numeração Automática**

**Ator Principal**: Sistema
**Objetivo**: Atribuir numeração única e sequencial aos ofícios
**Pré-condições**: 
- Ofício sendo finalizado
- Sistema de numeração configurado

**Fluxo Principal**:
1. Sistema recebe solicitação de numeração para novo ofício
2. Sistema identifica ano corrente e o autor solicitado
3. Sistema consulta último número usado no ano para o autor
4. Sistema incrementa sequência (ex: 01/2024, 02/2024)
5. Sistema verifica se número não está em uso
6. Sistema reserva número para o documento
7. Sistema atualiza contador de sequência
8. Sistema retorna número gerado
9. Caso de uso encerra com número atribuído

**Fluxos Alternativos**:
- **A1 - Conflito de numeração**: Sistema tenta próximo número disponível
- **A2 - Mudança de ano**: Sistema reinicia sequência em 001 para o novo ano
- **A3 - Erro de sistema**: Sistema usa numeração temporal e corrige posteriormente

**Pós-condições**: 
- Ofício possui numeração única e oficial
- Contador atualizado para próximas numerações
