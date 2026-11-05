# Matriz de rastreabilidade — PIT I → PIT II | Le Cupcake

**Fonte primária:** arquivo original “Projeto - José Otávio Braga Fante (1).docx”, seção Resultado e discussão, imagens das histórias de usuário, mapa de afinidade, backlog e tarefas. Esta matriz é uma transcrição operacional RESUMIDA dos critérios, não substitui a leitura das imagens originais.

**Controle da entrega:** branch de desenvolvimento. A branch main e o site público NÃO são alterados por este documento. Não afirmar que uma história está concluída sem verificar todos os critérios de aceitação, regras de negócio e RNFs. Não confundir e-mails/SMS simulados, pagamento fictício ou teste sintético de carga com integração real comprovada.

**Backlog:** 25 histórias; soma da tabela original = **320 horas**; texto corrido original menciona **332 horas**. Divergência mantida para esclarecimento; não estimar horas de implementação a partir desses números sem replanejamento.

**Legenda da situação:** a situação registrada é o estado PRELIMINAR da versão pública 0.2, reavaliado diante dos critérios completos da PIT I. Não é atestado de conformidade.

| US | História | Prioridade original | Horas originais | Situação preliminar | Principal lacuna |
|---:|---|---:|---:|---|---|
| US-01 | Catálogo com imagens | 1 | 8 | Parcial | Conferir exibição de indisponíveis e desempenho real. |
| US-02 | Filtros combinados | 1 | 12 | Básica | Filtros no servidor não comprovam atualização dinâmica e desempenho. |
| US-03 | Carrinho persistente | 1 | 12 | Básica | Conferir atualização sem recarga e persistência entre navegações. |
| US-04 | Total com frete e descontos | 1 | 8 | Parcial | Hoje há taxa de entrega configurada, não frete efetivo por CEP. |
| US-05 | Forma de recebimento | 1 | 12 | Parcial | Implementar regras regionais e conferir alterações no checkout. |
| US-06 | Acompanhar status | 1 | 16 | Parcial | Faltam notificações e atualização automática; capacidade não comprovada. |
| US-07 | Conta e recuperação | 2 | 12 | Parcial perante a PIT I | Falta recuperação de senha; conferir privacidade e tempo de login. |
| US-08 | Recomendações históricas | 3 | 20 | Parcial | Sugestões por categoria não cumprem personalização histórica. |
| US-09 | Promoções e cupons | 2 | 8 | Parcial | Checkout possui cupons; conferir promoções públicas e desempenho. |
| US-10 | Avaliações e comentários | 2 | 8 | Parcial | Auditar todos os critérios, inclusive bloqueio de edição. |
| US-11 | Notificações de andamento | 3 | 16 | Ausente | Exige serviço externo real ou integração verificável; não contar simulação como envio. |
| US-12 | Forma de pagamento | 1 | 16 | Ausente | Requer gateway/ambiente de homologação, webhooks, idempotência e validação. |
| US-13 | Agendamento de entrega | 3 | 16 | Ausente | Criar calendário, janelas, capacidade e regras de produção. |
| US-14 | Combos personalizados | 3 | 16 | Ausente | Criar configuração, cálculo e movimentação de estoque por componente. |
| US-15 | Informações nutricionais | 4 | 8 | Parcial | Sem dados verificados ou alertas de alergênicos completos. |
| US-16 | Cadastrar sabores | 1 | 12 | Básica | Conferir validações de todos os campos e foto. |
| US-17 | Editar/remover cupcakes | 1 | 12 | Parcial | Ocultar não substitui exclusão condicionada; falta histórico de edição. |
| US-18 | Relatórios de vendas | 2 | 16 | Parcial | Relatórios atuais não demonstram filtros e gráficos completos. |
| US-19 | Pedidos em tempo real | 1 | 20 | Parcial | Faltam tempo estimado, atualização instantânea e prova de concorrência. |
| US-20 | Promoções administrativas | 2 | 12 | Parcial perante a PIT I | Cupom existe; faltam campanha pública e automatismos de expiração. |
| US-21 | Aviso de novos pedidos ao admin | 1 | 8 | Ausente | Implementar notificação efetiva, preferências e log. |
| US-22 | Gerenciar clientes | 3 | 12 | Parcial | Bloqueio existe; faltam edição e auditoria. |
| US-23 | Respostas a avaliações | 4 | 8 | Parcial perante a PIT I | Verificar autoria, data e moderação específica de respostas. |
| US-24 | Configurar entrega e retirada | 2 | 12 | Parcial | Faltam horários e regiões operacionais reais. |
| US-25 | Integrar pagamentos | 1 | 20 | Ausente | Exige pelo menos interfaces de provedores reais e homologação sem capturar dados de cartão. |

## Requisitos de referência por história

### US-01 — Catálogo com imagens

CA: exibir sabores inclusive indisponíveis; foto com qualidade; produto sem estoque sinalizado. RN: atualizar após cadastro; bloquear compra sem estoque; categorias. RNF: imagem em até 3 s.

**Situação anterior:** Parcial. **Trabalho pendente:** Conferir exibição de indisponíveis e desempenho real.

### US-02 — Filtros combinados

CA: filtros em tempo real; múltiplos filtros combinados; atualizar sem recarregar. RN: apenas produtos disponíveis; categorias administrativas. RNF: resposta em até 1 s.

**Situação anterior:** Básica. **Trabalho pendente:** Filtros no servidor não comprovam atualização dinâmica e desempenho.

### US-03 — Carrinho persistente

CA: quantidade e subtotal atualizados em tempo real; remover itens. RN: respeitar estoque e indisponibilidade. RNF: persistência durante a utilização.

**Situação anterior:** Básica. **Trabalho pendente:** Conferir atualização sem recarga e persistência entre navegações.

### US-04 — Total com frete e descontos

CA: cálculo imediato e detalhamento. RN: frete por CEP; cupom correto. RNF: cálculo até 1 s; compatível com mobile.

**Situação anterior:** Parcial. **Trabalho pendente:** Hoje há taxa de entrega configurada, não frete efetivo por CEP.

### US-05 — Forma de recebimento

CA: opções entrega/retirada e custo adicional; alterar antes da finalização. RN: retirada gratuita; entrega por região. RNF: interface intuitiva e mobile.

**Situação anterior:** Parcial. **Trabalho pendente:** Implementar regras regionais e conferir alterações no checkout.

### US-06 — Acompanhar status

CA: status em tempo real, notificação a cada mudança, visibilidade na conta e histórico. RN: só admin muda status; fluxo lógico. RNF: atualização até 2 s; até 1.000 pedidos simultâneos.

**Situação anterior:** Parcial. **Trabalho pendente:** Faltam notificações e atualização automática; capacidade não comprovada.

### US-07 — Conta e recuperação

CA: nome, e-mail e senha; histórico após login; recuperação de senha. RN: proteção dos dados; só cadastrados avaliam. RNF: login até 5 s.

**Situação anterior:** Parcial perante a PIT I. **Trabalho pendente:** Falta recuperação de senha; conferir privacidade e tempo de login.

### US-08 — Recomendações históricas

CA: recomendações pelo histórico, ao menos 3 opções na página inicial, atualizadas a cada pedido. RN: histórico de compras; não recomendar sem estoque. RNF: até 3 s.

**Situação anterior:** Parcial. **Trabalho pendente:** Sugestões por categoria não cumprem personalização histórica.

### US-09 — Promoções e cupons

CA: aplicar cupom no checkout; mostrar desconto; validade; erro para inválidos. RN: regras por cupom e máximo 1 por pedido. RNF: aplicação até 2 s.

**Situação anterior:** Parcial. **Trabalho pendente:** Checkout possui cupons; conferir promoções públicas e desempenho.

### US-10 — Avaliações e comentários

CA: nota; comentário opcional; avaliação visível no produto; só logados. RN: não editar após envio; moderação admin. RNF: registro até 3 s.

**Situação anterior:** Parcial. **Trabalho pendente:** Auditar todos os critérios, inclusive bloqueio de edição.

### US-11 — Notificações de andamento

CA: e-mail/SMS em cada status; número do pedido; cliente escolhe canal. RN: só cadastrados; RNF: entrega em até 1 min; suporte a envio em massa.

**Situação anterior:** Ausente. **Trabalho pendente:** Exige serviço externo real ou integração verificável; não contar simulação como envio.

### US-12 — Forma de pagamento

CA: opções no checkout; transação segura; confirmação; mensagem em falha. RN: integração gateway; só confirmar após aprovação. RNF: transação em até 5 s.

**Situação anterior:** Ausente. **Trabalho pendente:** Requer gateway/ambiente de homologação, webhooks, idempotência e validação.

### US-13 — Agendamento de entrega

CA: calendário; disponibilidade; entrada em produção na data prevista. RN: até 15 dias; sem dias de fechamento. RNF: interface intuitiva, resposta até 2 s.

**Situação anterior:** Ausente. **Trabalho pendente:** Criar calendário, janelas, capacidade e regras de produção.

### US-14 — Combos personalizados

CA: selecionar quantidade e sabores; preço automático; resumo pré-compra. RN: estoque; regras de descontos. RNF: interface responsiva.

**Situação anterior:** Ausente. **Trabalho pendente:** Criar configuração, cálculo e movimentação de estoque por componente.

### US-15 — Informações nutricionais

CA: calorias e ingredientes; página do produto; dados legíveis; alerta de alergênicos. RN: conteúdo informado pelo admin; atualizar junto ao produto. RNF: até 2 s.

**Situação anterior:** Parcial. **Trabalho pendente:** Sem dados verificados ou alertas de alergênicos completos.

### US-16 — Cadastrar sabores

CA: nome, descrição e foto; preço e estoque; catálogo imediato; obrigatórios validados. RN: ID único; estoque não negativo. RNF: até 3 s.

**Situação anterior:** Básica. **Trabalho pendente:** Conferir validações de todos os campos e foto.

### US-17 — Editar/remover cupcakes

CA: editar nome, descrição, foto e preço; refletir de imediato; impedir exclusão com pedidos ativos. RN: trilha de alterações; só admin. RNF: até 2 s.

**Situação anterior:** Parcial. **Trabalho pendente:** Ocultar não substitui exclusão condicionada; falta histórico de edição.

### US-18 — Relatórios de vendas

CA: vendas por período; ranking sabores; filtro categoria. RN: atualizar diariamente; só admin. RNF: gerar em até 5 s; gráficos interativos.

**Situação anterior:** Parcial. **Trabalho pendente:** Relatórios atuais não demonstram filtros e gráficos completos.

### US-19 — Pedidos em tempo real

CA: pedidos ativos; alterar status; estimativa de entrega; cancelar. RN: fluxo lógico; cancelar somente antes da produção. RNF: tempo real; 500 pedidos simultâneos.

**Situação anterior:** Parcial. **Trabalho pendente:** Faltam tempo estimado, atualização instantânea e prova de concorrência.

### US-20 — Promoções administrativas

CA: criar cupons com validade; mostrar promoções; desativar expiradas; validar existentes. RN: código único; não retroativo. RNF: aplicar até 2 s; administração amigável.

**Situação anterior:** Parcial perante a PIT I. **Trabalho pendente:** Cupom existe; faltam campanha pública e automatismos de expiração.

### US-21 — Aviso de novos pedidos ao admin

CA: notificação com número do pedido imediatamente; canal configurável. RN: somente administradores; registro em log. RNF: até 1 min; envio em massa.

**Situação anterior:** Ausente. **Trabalho pendente:** Implementar notificação efetiva, preferências e log.

### US-22 — Gerenciar clientes

CA: alterar dados; bloquear contas; refletir imediatamente; histórico de alterações. RN: somente admin. RNF: até 2 s.

**Situação anterior:** Parcial. **Trabalho pendente:** Bloqueio existe; faltam edição e auditoria.

### US-23 — Respostas a avaliações

CA: resposta junto à avaliação; só admin; data/autor. RN: impedir linguagem ofensiva; sem autorresposta. RNF: até 2 s; interface intuitiva.

**Situação anterior:** Parcial perante a PIT I. **Trabalho pendente:** Verificar autoria, data e moderação específica de respostas.

### US-24 — Configurar entrega e retirada

CA: horários retirada; taxa entrega; refletir no checkout; validar região. RN: frete correto por região; retirada grátis. RNF: até 2 s; interface responsiva.

**Situação anterior:** Parcial. **Trabalho pendente:** Faltam horários e regiões operacionais reais.

### US-25 — Integrar pagamentos

CA: múltiplos gateways; transações seguras/confirmadas; validar cliente. RN: confirmar pedido só após aprovação. RNF: até 8 s; 500 transações simultâneas.

**Situação anterior:** Ausente. **Trabalho pendente:** Exige pelo menos interfaces de provedores reais e homologação sem capturar dados de cartão.

## Condições para encerrar as histórias

1. Implementação real e consistente com as regras do sistema e com as demais histórias.
2. Evidência de teste de sucesso e falha para cada critério de aceitação.
3. Evidência de controle de acesso, persistência, consistência de estoque/pedidos e proteção de dados para operações relevantes.
4. Critérios de desempenho verificados em ambiente definido, não apenas assumidos. Se não for possível comprovar throughput/latência, registrar explicitamente como **não comprovado**.
5. Modelagem UML (casos de uso, classes, sequência, atividades) + modelos conceitual/lógico/físico e dicionário de dados revisados a partir do código final.
6. Não iniciar nova gravação do segundo vídeo nem atualizar o formulário/laudo para “100% concluído” antes da homologação final.
7. Integrações reais com pagamentos e envio externo dependem de ambiente e credenciais apropriadas; armazenar segredos fora do GitHub. Em modo de demonstração, declarar claramente qualquer operação simulada.

**Primeiro vídeo:** permanece como evidência da versão inicial 0.1, conforme definido pelo responsável pelo projeto. **Segundo vídeo:** deverá mostrar o sistema final após implementação e testes, sem mudar a numeração acordada 0.1 → 0.2.
