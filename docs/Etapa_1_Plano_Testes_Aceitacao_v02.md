# Etapa 1 — Plano de testes de aceitação das 25 histórias (antes da implementação)

**Fonte:** PIT I original: critérios de aceitação (CA), regras de negócio (RN) e requisitos não funcionais (RNF). **Estado deste plano:** TODOS os testes abaixo são **a executar**. Os 30 testes técnicos preexistentes não são prova suficiente da conformidade completa das histórias.

## Roteiros e provas esperadas

| História | Cenários obrigatórios para o aceite | Estado |
|---|---|---|
| US-01 — Catálogo | Listar ativos com estoque e zerados; os zerados aparecem como indisponíveis, sem botão para adicionar; validar foto/categoria; medir carregamento de imagem até 3 s. | Não executado nesta etapa |
| US-02 — Filtro dinâmico | Combinar busca/sabor/categoria; atualizar lista sem reload; limitar resultados aos disponíveis na visão filtrada; medir até 1 s. | Não executado nesta etapa |
| US-03 — Carrinho | Adicionar, alterar quantidade, subtotal e remover; proibir indisponíveis e excesso de estoque; preservar carrinho ao navegar, validar persistência durante uso. | Não executado nesta etapa |
| US-04 — Frete | Informar CEP, obter região/taxa, recalcular total e cupom corretamente; detalhar valores; medir cálculo até 1 s; exercitar celular. | Não executado nesta etapa |
| US-05 — Recebimento | Alternar retirada/entrega antes do fim; retirada gratuita; taxa por região; validar campos e apresentação móvel. | Não executado nesta etapa |
| US-06 — Acompanhamento | Atualizar status em tempo real; respeitar sequência; gravar histórico; mostrar na conta; notificar por alteração; medir até 2 s e planejar carga até 1000 pedidos. | Não executado nesta etapa |
| US-07 — Conta | Cadastro nome/e-mail/senha, autenticação e histórico; recuperação de senha com token expirável, uso único e não revelação da existência da conta; medir login até 5 s. | Não executado nesta etapa |
| US-08 — Recomendações | Registrar histórico real de pedidos; mostrar 3 sugestões relacionadas na página inicial; atualizar após nova compra; excluir estoque zerado; medir até 3 s. | Não executado nesta etapa |
| US-09 — Cupom cliente | Aplicar apenas um cupom por pedido; validar validade, regras e código inválido; exibir desconto e mensagens; medir aplicação até 2 s. | Não executado nesta etapa |
| US-10 — Avaliação | Somente login; exigir nota, comentário opcional; publicar no produto após moderação; impedir edição após envio; testar escape e resposta até 3 s. | Não executado nesta etapa |
| US-11 — Notificação cliente | Escolher e-mail ou SMS; ao mudar status, gerar mensagem com número do pedido; prova de entrega externa em até 1 min ou registrar simulação SEM comprovar esse CA. | Não executado nesta etapa |
| US-12 — Pagamento cliente | Mostrar métodos; tentar aprovação e recusa por gateway de testes; validar segurança e confirmação apenas após aprovação; medir 5 s no cenário testado. | Não executado nesta etapa |
| US-13 — Agendamento | Calendário e datas até 15 dias; bloquear datas sem operação/capacidade; associar janela à produção; medir 2 s. | Não executado nesta etapa |
| US-14 — Combos | Selecionar produtos/quantidades; atualizar preço; resumo; respeitar desconto e estoque de cada ingrediente; interface móvel. | Não executado nesta etapa |
| US-15 — Nutrição | Mostrar calorias e ingredientes somente quando verificados; alerta de alergênicos; edição só no admin; legibilidade e até 2 s. | Não executado nesta etapa |
| US-16 — Cadastro de sabores | Somente administrador; nome/descrição/foto/preço/estoque e campos obrigatórios; ID único; nunca estoque negativo; vitrine imediata; medir 3 s. | Não executado nesta etapa |
| US-17 — Edição/exclusão | Atualizar produto e catálogo; registrar histórico; proibir exclusão de produto com pedido ativo; autorizar só admin; medir 2 s. | Não executado nesta etapa |
| US-18 — Relatórios | Selecionar período e categoria; ranking; atualização diária; dados apenas para administrador; gráficos interativos; medir geração em até 5 s. | Não executado nesta etapa |
| US-19 — Gestão de pedidos | Listar pedidos ativos, alterar status em sequência, mostrar prazo estimado; permitir cancelamento SOMENTE antes de entrar em produção; atualização instantânea; ensaio de 500 pedidos simultâneos. | Não executado nesta etapa |
| US-20 — Promoção admin | Criar código único/validade/regras; expor promoções ativas no site e desativar expiradas; não aplicar retroativamente; medir até 2 s. | Não executado nesta etapa |
| US-21 — Notificação admin | Avisar ao criar pedido com número; canal configurável e somente admins; log de envio; até 1 min e envio em massa, ou marcar integração não comprovada. | Não executado nesta etapa |
| US-22 — Contas admin | Editar dados e bloquear conta; efeito imediato e histórico/auditoria; acesso restrito; medir 2 s. | Não executado nesta etapa |
| US-23 — Resposta admin | Exibir resposta junto à avaliação, com data e autor; impedir autorresposta e conteúdo ofensivo; somente admin; até 2 s. | Não executado nesta etapa |
| US-24 — Configuração de entregas | Definir horários de retirada, taxas e regiões por CEP; refletir no checkout; retirada sempre gratuita; medir 2 s e testar mobile. | Não executado nesta etapa |
| US-25 — Gateways | Provar suporte a múltiplos adaptadores, processamento homologado, aprovação/rejeição e validação de dados; pagamento só confirmado após aprovação; 8 s/500 transações são metas não comprovadas sem medição. | Não executado nesta etapa |

## Tipos de evidência para cada história

- **Teste automático de sucesso** e **teste automático de falha** em banco temporário; sempre verificar estado da base, não só código HTTP.
- **Teste de autorização:** papel cliente/visitante/administrador; CSRF e proteção contra ações alheias nos fluxos relevantes.
- **Teste de integração:** entidades do SQLite e fluxos encadeados (estoque → pedido → pagamento/status → notificação).
- **Teste de interface:** navegação desktop/móvel, acessibilidade básica, mensagens e estados sem estoque.
- **Teste de desempenho:** cronometrar RNFs com ambiente, quantidade de amostras, concorrência e resultados; não confundir teste de unidade com teste de carga.
- **Teste de provedores externos:** se houver credencial de sandbox ou conta configurada, realizar requisições reais ao sandbox e registrar resposta; nunca inserir credenciais em commits. Se faltar serviço, demonstrar o fluxo local e registrar **limitação**, não “teste aprovado de envio/cobrança real”.

## Caso de aceite e rastreabilidade

Cada caso de teste implementado nas próximas etapas deverá usar marcador `USxx-CAnn` (critério), `USxx-RNnn` (regra) ou `USxx-RNFnn` (não funcional), de acordo com a numeração do documento original. Exemplo: `US19-RN02` verifica que não é possível cancelar após a entrada em produção.

**Condição de conclusão de uma história:** implementar todos os critérios viáveis, demonstrar testes de sucesso/erro, registrar desempenho e identificar cada exceção não verificada por falta de recursos. A numeração “0.2” não garante, por si, conformidade.
