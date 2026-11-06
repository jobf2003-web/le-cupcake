# Ciclo A.2 — Produtos, estoque e histórico de alterações

Este ciclo ampliou os recursos administrativos desenvolvidos para a versão 0.2, mantendo os dados e as regras comerciais da implementação anterior.

## Desenvolvimento

O cadastro e a edição de produtos receberam validações adicionais de preço e estoque. A exclusão passou a utilizar arquivamento lógico, com registro da data da operação, para preservar o histórico de pedidos e evitar a remoção indevida de produtos vinculados a encomendas em andamento.

As alterações administrativas são registradas na tabela de auditoria, incluindo os dados anteriores e posteriores. O histórico de movimentações do estoque também foi incorporado aos controles de gestão. A migração do esquema foi atualizada para a revisão 2, com a coluna `cupcakes.excluido_em` e índices de apoio. O banco manteve 23 tabelas nesta etapa.

## Verificação

A suíte chegou a **44 testes automatizados aprovados**, com nove casos adicionais sobre edição, auditoria, arquivamento, estoque e controle de acesso. As restrições de exclusão foram testadas em situações com pedidos ativos.

## Resultado na versão 0.2

Os recursos administrativos deste ciclo integram a aplicação publicada. A montagem de combos, desenvolvida no Ciclo B, passou a observar também a disponibilidade dos produtos utilizados como componentes. O funcionamento demonstrativo e os limites de desempenho estão descritos na documentação da versão final.
