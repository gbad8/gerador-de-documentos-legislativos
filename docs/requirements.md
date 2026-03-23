# Análise FURPS - GDL (Gerador de Documentos Legislativos)

## Visão Geral do Sistema
**Nome**: GDL - Gerador de Documentos Legislativos  
**Propósito**: Sistema web para geração automatizada de ofícios oficiais com timbrado de câmaras legislativas  
**Plataforma**: Aplicação Web (navegador)  

---

## Requisitos FURPS

### F - Funcionalidade (Functionality)

#### Requisitos Funcionais Principais (Core Features):

**RF01 - Capturar entrada de dados do usuário**
- Campos: Destinatário, assunto, corpo do texto, data, remetente
- Validação em tempo real dos dados inseridos
- Auto-save para prevenir perda de dados

**RF02 - Aplicar formatação oficial padrão aos documentos**
- Estrutura padrão: cabeçalho, corpo, fechamento
- Numeração automática de ofícios (exclusiva para o autor)
- Formatação de datas por extenso conforme padrão oficial
- Local para assinatura com nome do autor e cargo

**RF03 - Inserir timbrado da câmara legislativa automaticamente**
- Logomarca oficial da câmara no cabeçalho
- Nome "Poder Legislativo", nome do estado da câmara, e nome da câmara no cabeçalho
- Dados institucionais (endereço, telefone, CNPJ) no rodapé

**RF04 - Dados do documento ficam salvos em texto**
- Os inputs do usuário ficam salvos em formato texto
- Os dados em texto do documento são utilizados para a pré-visualização web
- Os dados em texto do documento são utilizados para gerar o PDF/A quando o usuário solicitar

**RF05 - Permitir visualização prévia do documento**
- O usuário pode solicitar a pré-visualização web do documento
- O programa gera uma visualização exata do layout final

**RF06 - Gerar documento final em formato PDF**
- Conversão automática para PDF/A (arquivo permanente)
- Qualidade mínima 300 DPI para impressão
- Proteção contra edição não autorizada

**RF07 - Salvar/exportar documento gerado**
- Nomenclatura automática: "Oficio_NNN_AAAA_Assunto"
- Download direto ou envio por email

#### Requisitos Funcionais Secundários (Enhanced Features):

**RF08 - Validar campos obrigatórios antes da geração**
- Verificação de campos obrigatórios
- Validação de formato de dados (CEP, telefone)
- Alertas visuais para campos pendentes
- Impedimento de geração com campos obrigatórios em branco ou com dados em formato errados

**RF09 - Permitir configuração de diferentes camaras**
- Suporte a múltiplas câmaras municipais
- Cada câmara terá seus próprios dados, logotipo, legislaturas, sessões ordinárias, e numeração
- Configuração de templates por órgão
- Troca rápida entre diferentes timbrados
- Gestão centralizada de templates

**RF10 - Manter histórico de documentos gerados**
- Lista cronológica de ofícios criados
- Busca por autor, destinatário, assunto ou data
- Status: rascunho, finalizado
- Backup automático do histórico

**RF11 - Permitir edição de documentos salvos**
- Reabrir ofícios para modificação
- Controle de versões dos documentos
- Comparação entre versões
- Bloqueio de edição em documentos enviados

#### Requisitos de Segurança:

**RF12 - Autenticação de usuários do sistema**
- Cada usuário está ligado a uma câmara municipal especificamente
- Cada usuário tem um tipo, como secretário, assessor jurídico, etc
- Login com usuário e senha
- Recuperação de senha via email
- Tentativas limitadas de login (3x)

**RF13 - Controle de acesso por perfis de usuário**
- Perfis: Administrador, Operador
- Permissões diferenciadas por funcionalidade

**RF14 - Log de atividades do sistema**
- Acesso a logs somente para o usuário administrador
- Registro de todas as ações dos usuários
- Timestamp e IP de cada operação

---

### U - Usabilidade (Usability)

#### Facilidade de Uso:

**RU01 - Interface intuitiva para entrada de dados**
- Layout de formulário familiar e simples (caixas de input)
- Campos claramente rotulados e organizados logicamente
- Ícones universais para ações comuns (salvar, imprimir, etc.)
- Navegação simples com no máximo 2 níveis de profundidade

**RU02 - Formulário simplificado com campos claros**
- Agrupamento lógico: Dados do Autor, Destinatário, Conteúdo, Configurações
- Placeholder text explicativo em cada campo
- Validação visual imediata (verde/vermelho)
- Tooltips contextuais para esclarecimentos

**RU03 - Feedback visual durante o processamento**
- Loading spinner durante geração de PDF
- Barra de progresso para uploads de timbrados
- Notificações toast para ações concluídas
- Indicadores de status em tempo real

#### Eficiência:

**RU04 - Geração de documento em menos de 2 segundos**
- Processamento assíncrono em background
- Os dados em texto do documento selecionado são inseridos pelo sistema no template de PDF/A

**RU05 - Máximo 3 cliques para gerar um ofício completo**
- Fluxo direto: Preencher → Preview → Gerar
- Valores padrão inteligentes baseados no usuário

#### Satisfação do Usuário:

**RU06 - Design responsivo para diferentes tamanhos de tela**
- Adaptação automática para tablets e smartphones
- Layout stack em mobile para consulta
- Zoom touch-friendly em dispositivos móveis
- Fonte legível em todas as resoluções

**RU07 - Mensagens de erro claras e orientativas**
- Linguagem não-técnica e específica ao contexto
- Sugestões de correção quando possível
- Links para ajuda contextual
- Evitar códigos de erro numéricos

**RU08 - Help/tutorial integrado ao sistema**
- Tour guiado para novos usuários
- Central de ajuda com busca
- Vídeos tutoriais de 2-3 minutos
- FAQ com problemas mais comuns

---

### R - Confiabilidade (Reliability)

#### Disponibilidade:

**RR01 - Sistema disponível 99% do tempo durante horário comercial**
- Uptime de 99% entre 7h-18h (horário de funcionamento das câmaras)

**RR02 - Tempo de recuperação máximo de 2 horas em caso de falha**
- RTO (Recovery Time Objective): 2 horas máximo
- RPO (Recovery Point Objective): perda máxima de 15 minutos de dados
- Procedimentos documentados de recuperação

**RR03 - Backup automático de dados**
- Backup completo diário às 2h da madrugada
- Retenção: 7 dias locais + 30 dias na nuvem

#### Tolerância a Falhas:

**RR04 - Sistema continua funcionando com falhas não-críticas**
- Degradação gradual: se preview falhar, sistema continua gerando PDFs
- Fallback para templates básicos se personalizados falharem
- Cache local para funcionar offline por tempo limitado
- Mensagens informativas sobre funcionalidades indisponíveis

**RR05 - Validação de entrada para prevenir erros**
- Sanitização de dados de entrada (prevenção XSS)
- Validação de formato de arquivos de timbrado
- Limite de tamanho para uploads (5MB máximo)
- Verificação de integridade de templates

#### Precisão:

**RR06 - 100% de precisão na formatação dos documentos**
- Testes automatizados de formatação
- Controle de qualidade manual mensal

**RR07 - Garantia de integridade dos dados inseridos**
- Encoding UTF-8 para caracteres especiais
- Preservação de formatação original do usuário
- Validação de caracteres não imprimíveis

**RR08 - Validação de formato de documentos antes da geração**
- Verificação de estrutura mínima obrigatória
- Validação de tamanho de campos (ex: assunto até 100 caracteres)
- Checagem de formato de datas e números
- Prevenção de documentos malformados

---

### P - Performance

#### Velocidade:

**RP01 - Tempo de carregamento inicial < 3 segundos**
- Primeira renderização da página em até 3s (3G connection)
- Lazy loading de componentes não-críticos

**RP02 - Tempo de geração de documento < 2 segundos**
- Processamento de PDF em até 2s para documentos padrão
- Otimização de renderização de templates
- Pool de workers para processamento paralelo

**RP03 - Tempo de resposta < 1 segundo para ações básicas**
- Validação de campos: < 200ms
- Auto-save: < 500ms
- Busca no histórico: < 1s
- Mudança de template: < 800ms

#### Escalabilidade:

**RP04 - Suporte a pelo menos 50 usuários simultâneos**
- Arquitetura horizontal escalável
- Load balancer para distribuir carga
- Testes de carga para validar limites
- Monitoramento de recursos em tempo real

**RP05 - Capacidade de processar 1000 documentos por dia**
- Queue system para processamento em lote
- Otimização de banco de dados para writes
- Cleanup automático de arquivos temporários
- Métricas diárias de volume processado

**RP06 - Crescimento horizontal conforme demanda**
- Containerização para fácil scaling
- Auto-scaling baseado em CPU/Memória
- Database clustering para alta carga
- Monitoramento proativo de performance

#### Recursos:

**RP07 - Uso eficiente de memória (< 512MB por usuário)**
- Gestão adequada de recursos do navegador
- Limpeza de cache periodicamente
- Otimização de imagens e assets
- Garbage collection eficiente no backend

**RP08 - Otimização para conexões de internet padrão**
- Funciona adequadamente com 1Mbps
- Compressão de dados transmitidos

**RP09 - Cache inteligente para melhorar performance**
- Cache de documentos gerados por 1 dia
- Invalidação automática quando necessário

---

### S - Suportabilidade (Supportability)

#### Manutenibilidade:

**RS01 - Código modularizado e bem documentado**
- Arquitetura em camadas bem definidas
- Comentários inline para lógica complexa
- Documentação de API completa e atualizada
- Padrões de código consistentes

**RS02 - Logs detalhados para debug e monitoramento**
- Logs estruturados em JSON para facilitar análise
- Níveis: ERROR, WARN, INFO, DEBUG
- Correlação ID para rastrear requisições
- Dashboards de monitoramento em tempo real

**RS03 - Configuração centralizada e flexível**
- Arquivo de configuração único por ambiente
- Variáveis de ambiente para dados sensíveis
- Hot reload para mudanças não-críticas
- Versionamento de configurações

#### Testabilidade:

**RS04 - Cobertura de testes automatizados > 80%**
- Testes unitários para lógica de negócio
- Testes de integração para APIs
- Testes end-to-end para fluxos críticos
- Relatórios de cobertura automáticos no CI

**RS05 - Ambiente de teste isolado**
- Dados de teste separados da produção
- Reset automático do ambiente a cada ciclo
- Simulação de diferentes cenários de falha
- Testes de performance regulares

**RS06 - Testes de integração para funcionalidades críticas**
- Teste completo do fluxo de geração de PDF
- Integração com serviços de autenticação
- Validação de templates e timbrados
- Testes de stress para pontos críticos

#### Configurabilidade:

**RS07 - Configuração de templates de documento via interface**
- Editor visual para templates não-técnicos
- Preview em tempo real das alterações
- Versionamento de templates com rollback

**RS08 - Personalização de timbrados por órgão**
- Upload de logomarcas via interface web
- Configuração de dados institucionais
- Preview de como ficará no documento
- Backup automático de configurações

**RS09 - Configuração de campos obrigatórios/opcionais**
- Interface para administradores configurarem campos
- Diferentes configurações por tipo de usuário
- Validação dinâmica baseada na configuração
- Histórico de mudanças nas configurações

#### Instalação/Deploy:

**RS10 - Deploy automatizado via CI/CD**
- Pipeline CI/GitHub Actions
- Deploy em staging automático para todas as branches
- Rollback automático em caso de falha

**RS11 - Containerização para facilitar implantação**
- Docker containers para todos os serviços
- Docker Compose para ambiente local

**RS12 - Documentação completa de instalação e configuração**
- Guia passo-a-passo para instalação
- Documentação de troubleshooting
- Diagramas de arquitetura atualizados
- Runbooks para operações comuns
