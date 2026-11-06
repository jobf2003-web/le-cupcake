# Etapa 1 — Mapa de impacto na modelagem e no banco de dados (v0.1 → v0.2)

**Situação:** registro de planejamento de dados da Etapa 1. A versão 0.2 final foi implementada e publicada; a modelagem física efetiva consta do dicionário de 27 tabelas e dos diagramas do Ciclo F.

## 1. Estado inicial validado

O arquivo `schema.sql` contém **23 tabelas**. Parte dos relacionamentos físicos foi criada antecipadamente, mas o `app.py` só implementa alguns fluxos. Uma tabela existente não prova o funcionamento da história correspondente.

**Evolução das migrações:** o esquema-base foi mantido e a versão 0.2 passou a aplicar sete migrações SQLite sequenciais e idempotentes, com preservação da estrutura de bancos anteriores.

## 2. Modelagem de dados — mudanças a desenhar e validar antes da migração

| Entidades atuais | Relação com a PIT I | Mudança proposta (não executada) | Testes que precedem a publicação |
|---|---|---|---|
| `usuarios`, `enderecos` | US-07/22 | Tokens de recuperação com hash/expiração/uso único, histórico de alterações do perfil, preferências de canal, endereço validado e vínculo seguro do cliente | Login sem regressão; bloqueio; renovação segura; migração de contas existentes. |
| `cupcakes`, `categorias`, `alergenos`, `cupcake_alergenos` | US-01/02/15/16/17 | Regras de desativação/exclusão com pedidos ativos, histórico de edições e associação efetiva de alergênicos | Alergia exibida somente se cadastrada; índices e paginação; estoque não negativo. |
| `carrinhos`, `carrinho_itens`, `combos`, `combo_itens`, `pedido_itens` | US-03/14 | Projetar persistência de carrinho e composição de combos, preço histórico e consumo de estoque em cada componente | Carrinho legado mantido; soma e desconto corretos; operações atômicas; cancelamento restaura ingredientes. |
| `opcoes_entrega`, `regioes_entrega`, `janelas_entrega`, `pedidos` | US-04/05/13/24 | CEP estruturado, horário e dia de operação, datas de pedido, reserva por janela e taxa por região. Avaliar tabela de reservas para capacidade por **data + janela** | Impedir datas fora do limite, regiões não atendidas e sobre-reserva; retirada gratuita. |
| `pedidos`, `eventos_pedido`, `estoque_movimentos` | US-06/19 | Estado coerente com o início da produção; eventos imutáveis e estimativa de horário; outbox transacional para disparos | Garantir cancelamento só antes da produção, consistência de estoque, eventos únicos e concorrência. |
| `cupons`, `cupom_utilizacoes` | US-09/20 | Validade administrável, publicação de promoções e regras de ativação automática | Cupom único, limites por uso, expiração, não retroatividade. |
| `notificacoes` | US-11/21 | Destinatário/canal/preferência, tentativa, erro, provedor e estado de entrega, log e retentativa idempotente | Prova de notificação **interna** e, separadamente, de entrega externa quando houver conta de provedor. |
| `pagamentos` | US-12/25 | Métodos/seleção, tentativa, chave idempotente, identificador externo, eventos de gateway e estados de autorização | Nunca aprovar pedido por simulação sem rotular; sandbox real só com provedor configurado. Nunca armazenar cartão. |
| `avaliacoes`, `auditoria` | US-10/23/22 | Identificar administrador que respondeu, publicar data/autor, trilha para alteração de clientes e moderação | Proibir usuário comum de responder, entrada maliciosa sanitizada e autoria verificável. |

**Integração do modelo com o código:** contratos de serviço e migrações serão acordados antes de acrescentar colunas/tabelas. Preservar chaves estrangeiras, índices e dados já existentes. Não presumir que `janelas_entrega` atual reserva a capacidade por dia: contém início/fim/capacidade, mas nenhuma data de reserva.

## 3. Diagramas obrigatórios no processo de atualização

| Artefato | Representação da versão 0.2 a produzir | Evolução que deve ser explicitada |
|---|---|---|
| Casos de uso | Atores cliente, visitante, administrador, provedores externos e fronteiras da demonstração | Novos casos de senha, combos, agenda, notificações e pagamento. |
| Classes / domínio | Entidades acima e serviços de preço, entrega, pedidos e identidade, com cardinalidades e restrições | Mostrar tabelas antes apenas previstas e agora utilizadas. |
| Sequência | Checkout com combo, estoque, cupom, entrega, tentativa de pagamento (real/sandbox/demo explicitado) e evento | De “pedido a combinar” para o fluxo com aprovação ou limitação registrada. |
| Sequência | Criação de pedido, mudança de status, aviso a cliente/admin, falha e retentativa | Separar evento interno de entrega por e-mail/SMS. |
| Atividades | Fluxo pedido → produção → entrega/retirada; alternativas, cancelamento antes do preparo | Regras de status da PIT I e controles de estoque. |
| Atividades | Agendamento (data, horário, região, capacidade) e opção de retirada | Restrições de 15 dias, dia de funcionamento e regiões. |
| Conceitual | Cliente, Produto, Cupom, Pedido, Item, Combo, Entrega, Pagamento, Avaliação, Notificação | Rastreabilidade às 25 US. |
| Lógico | Tabelas, PK/FK, cardinalidade, campos obrigatórios e normalização | Tratar adaptações das 23 tabelas existentes. |
| Físico / dicionário | SQL SQLite efetivamente migrado, índices, domínio de valores e campos | Atualizar `Dicionario_de_Dados_v02.docx` **depois** de confirmar DDL final. |
| Wireframes/telas | Catálogo, conta, calendário, combo, checkout, pedido e administração, sem redesenhar desnecessariamente | Preservar a identidade visual da 0.1; mostrar apenas recursos que o código suporta. |

## 4. Registro histórico das mudanças

Para cada história implementada, adicionar uma linha ao registro de alterações com:

`US | comportamento disponível na 0.1 | constatação da avaliação (quando existir) | diferença identificada na revisão da PIT I | mudança na 0.2 | modelo alterado | teste/evidência | limitação restante`.

**A ordem causal importa.** Não afirmar que a avaliação sugeriu uma função que, na verdade, foi incluída porque sua ausência foi descoberta na revisão das histórias originais.

## 5. Gatilhos para congelar o modelo

O esquema, os diagramas finais e o formulário oficial só serão considerados estabilizados quando:

- todas as migrações forem testadas tanto em banco novo quanto em banco legado;
- o código implementado corresponder a cada diagrama;
- testes de aceitação e de regressão passarem;
- a matriz diferenciar requisito atendido, demonstrativo e não comprovado;
- custos/limitações de gateways, notificações e infraestrutura estiverem claramente descritos.

**Esta Etapa 1 não modifica o esquema, o código, a modelagem antiga ou a aplicação publicada.**
