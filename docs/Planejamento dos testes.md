# Planejamento dos testes de aceitação

O planejamento de testes foi elaborado a partir dos critérios de aceitação, das regras de negócio e dos requisitos não funcionais das 25 histórias da PIT I. Os casos abaixo serviram de referência para os ciclos de desenvolvimento da versão 0.2. A suíte final concluiu 93 testes automatizados locais aprovados.

## Cenários de teste

| História | Cenários previstos no planejamento |
|---|---|
| US-01 — Catálogo | Listar ativos com estoque e zerados; os zerados aparecem como indisponíveis, sem botão para adicionar; validar foto/categoria; medir carregamento de imagem até 3 s. |
| US-02 — Filtro dinâmico | Combinar busca/sabor/categoria; atualizar lista sem reload; limitar resultados aos disponíveis na visão filtrada; medir até 1 s. |
| US-03 — Carrinho | Adicionar, alterar quantidade, subtotal e remover; proibir indisponíveis e excesso de estoque; preservar carrinho ao navegar, validar persistência durante uso. |
| US-04 — Frete | Informar CEP, obter região/taxa, recalcular total e cupom corretamente; detalhar valores; medir cálculo até 1 s; exercitar celular. |
| US-05 — Recebimento | Alternar retirada/entrega antes do fim; retirada gratuita; taxa por região; validar campos e apresentação móvel. |
| US-06 — Acompanhamento | Atualizar status em tempo real; respeitar sequência; gravar histórico; mostrar na conta; notificar por alteração; medir até 2 s e planejar carga até 1000 pedidos. |
| US-07 — Conta | Cadastro nome/e-mail/senha, autenticação e histórico; recuperação de senha com token expirável, uso único e não revelação da existência da conta; medir login até 5 s. |
| US-08 — Recomendações | Registrar histórico real de pedidos; mostrar 3 sugestões relacionadas na página inicial; atualizar após nova compra; excluir estoque zerado; medir até 3 s. |
| US-09 — Cupom cliente | Aplicar apenas um cupom por pedido; validar validade, regras e código inválido; exibir desconto e mensagens; medir aplicação até 2 s. |
| US-10 — Avaliação | Somente login; exigir nota, comentário opcional; publicar no produto após moderação; impedir edição após envio; testar escape e resposta até 3 s. |
| US-11 — Notificação cliente | Escolher e-mail ou SMS; ao mudar status, gerar mensagem com número do pedido; prova de entrega externa em até 1 min ou registrar simulação SEM comprovar esse CA. |
| US-12 — Pagamento cliente | Mostrar métodos; tentar aprovação e recusa por gateway de testes; validar segurança e confirmação apenas após aprovação; medir 5 s no cenário testado. |
| US-13 — Agendamento | Calendário e datas até 15 dias; bloquear datas sem operação/capacidade; associar janela à produção; medir 2 s. |
| US-14 — Combos | Selecionar produtos/quantidades; atualizar preço; resumo; respeitar desconto e estoque de cada ingrediente; interface móvel. |
| US-15 — Nutrição | Mostrar calorias e ingredientes somente quando verificados; alerta de alergênicos; edição só no admin; legibilidade e até 2 s. |
| US-16 — Cadastro de sabores | Somente administrador; nome/descrição/foto/preço/estoque e campos obrigatórios; ID único; nunca estoque negativo; vitrine imediata; medir 3 s. |
| US-17 — Edição/exclusão | Atualizar produto e catálogo; registrar histórico; proibir exclusão de produto com pedido ativo; autorizar só admin; medir 2 s. |
| US-18 — Relatórios | Selecionar período e categoria; ranking; atualização diária; dados apenas para administrador; gráficos interativos; medir geração em até 5 s. |
| US-19 — Gestão de pedidos | Listar pedidos ativos, alterar status em sequência, mostrar prazo estimado; permitir cancelamento SOMENTE antes de entrar em produção; atualização instantânea; ensaio de 500 pedidos simultâneos. |
| US-20 — Promoção admin | Criar código único/validade/regras; expor promoções ativas no site e desativar expiradas; não aplicar retroativamente; medir até 2 s. |
| US-21 — Notificação admin | Avisar ao criar pedido com número; canal configurável e somente admins; log de envio; até 1 min e envio em massa, ou marcar integração não comprovada. |
| US-22 — Contas admin | Editar dados e bloquear conta; efeito imediato e histórico/auditoria; acesso restrito; medir 2 s. |
| US-23 — Resposta admin | Exibir resposta junto à avaliação, com data e autor; impedir autorresposta e conteúdo ofensivo; somente admin; até 2 s. |
| US-24 — Configuração de entregas | Definir horários de retirada, taxas e regiões por CEP; refletir no checkout; retirada sempre gratuita; medir 2 s e testar mobile. |
| US-25 — Gateways | Provar suporte a múltiplos adaptadores, processamento homologado, aprovação/rejeição e validação de dados; pagamento só confirmado após aprovação; 8 s/500 transações são metas não comprovadas sem medição. |

## Metodologia utilizada

O planejamento combinou testes funcionais de sucesso e falha, validações de autenticação, integridade dos dados e regras de pedidos, estoque e pagamentos demonstrativos. Os testes de regressão foram executados com base SQLite isolada.

As integrações comerciais externas e os requisitos de desempenho em grande escala não foram incluídos na certificação de testes locais. O registro final das verificações está no documento de testes da versão 0.2.

## Rastreabilidade

Os casos podem ser associados aos identificadores das histórias e critérios originais, como `US19-RN02`, relativo à proibição de cancelamento após o início do preparo. A matriz de rastreabilidade e o mapa das 25 histórias apresentam a correspondência entre o projeto planejado e a implementação final.
