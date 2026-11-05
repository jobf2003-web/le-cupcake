# Etapa 2 — Ciclo A.2: gestão de produtos, exclusão condicionada e auditoria

**Le Cupcake / PIT II · versão-alvo 0.2 · branch `pit-ii-25-historias-completas`**

**Estado:** implementado e verificado localmente; **não implantado em produção**. Esta entrega é parte da evolução iniciada com a versão 0.1 e registrada após as cinco avaliações e a revisão das 25 histórias originais da PIT I. **Não modifica** o conteúdo histórico das avaliações nem o primeiro vídeo.

## Escopo efetivamente alterado

| Tema | Estado do site anterior | Mudança desenvolvida neste ciclo |
|---|---|---|
| US-16 — Cadastro de produto | Já havia cadastro administrativo com validação de campos, preço, estoque e foto da biblioteca | Mantido, com registro estruturado de **criação** em `auditoria`. |
| US-17 — Edição e remoção de produto | Administrador podia editar ou ocultar; não havia exclusão condicionada | Incluída ação **Excluir** com bloqueio se existir pedido ativo ou combo ativo. A remoção é **lógica**: o produto sai da vitrine e das opções de edição/reativação, mas seus dados e o histórico de pedidos permanecem preservados. |
| US-17 — Histórico | Havia mensagens genéricas de auditoria | Cada edição registra os valores **antes/depois**, ator e data. Há tela de histórico por produto, inclusive arquivado. A tela mostra os campos alterados. |
| Estoque | Alteração de estoque administrativo não gravava a diferença no livro de movimentos | Mudanças manuais agora criam movimentos com variação positiva/negativa, dentro da mesma transação do produto. Edição sem alteração não gera evento artificial. |
| Persistência/migração | Migração SQLite interna até `user_version=1` | Criada migração interna para `user_version=2`, com `cupcakes.excluido_em` e índice. **Não confundir** a versão interna do esquema com a versão **0.2** da aplicação. |
| Proteção | Administração e CSRF já existentes | Novas rotas exigem sessão de administrador e validação CSRF; exclusão é POST e não permite exclusão repetida. |

**Nota sobre a exclusão:** `excluido_em` e `ativo=0` deixam o produto indisponível. Optou-se por **arquivamento lógico**, não `DELETE` físico, para proteger integridade referencial, auditoria, avaliações e itens históricos dos pedidos. Mesmo quando não há pedidos, o registro é arquivado para preservar rastreabilidade. Produtos ligados a pedidos **recebidos, confirmados, em preparo, prontos ou em entrega** não podem ser excluídos. Também não podem ser excluídos se estiverem associados a combo ativo. Pedidos **concluídos ou cancelados** não bloqueiam arquivamento, pois seus registros são conservados.

## Testes executados

**Resultado local:** `python -m pytest -q` → **44 testes aprovados** (35 anteriores + 9 novos), em cópia do código da branch com os arquivos deste ciclo.

Os nove testes adicionais cobrem:

1. criação/edição e comparação dos valores antes/depois, inclusive ajuste de estoque;
2. inexistência de registros de alteração artificiais em edição sem mudanças;
3. impedimento de excluir produto com pedido ativo;
4. exclusão lógica, ocultação e impossibilidade de reativação;
5. preservação de itens históricos e chaves estrangeiras após pedido concluído;
6. impedimento de excluir produto pertencente a combo ativo;
7. autenticação administrativa, CSRF e validação de limites de estoque;
8. atualização de banco legado da migração v1 para a v2 com preservação de dados;
9. repetição idempotente quando o `PRAGMA user_version` foi reiniciado.

Foram também mantidos os testes de regressão da primeira parte do ciclo: filtros dinâmicos, preservação de estoque e cancelamento somente antes da produção.

**Limites da comprovação:** não houve ensaio de carga, testes completos no navegador com automação de interface, validação do site Render após publicação ou testes de todas as 25 histórias. **Não afirmar** que US-16 ou US-17 estão definitivamente aceitas sem todos os critérios originais, inclusive seus requisitos não funcionais.

## Alteração no modelo de dados e necessidade de atualizar diagramas

- **`cupcakes`**: adicionada coluna `excluido_em TEXT`, nula enquanto o produto não foi arquivado.
- **`auditoria`**: reaproveitada tabela existente para registro em JSON de snapshots de produto (campos antes/depois), vínculo com administrador e timestamp. Registros antigos de texto continuam legíveis.
- **`estoque_movimentos`**: reaproveitada tabela existente para variações de estoque efetuadas administrativamente.
- **`pedidos` + `pedido_itens`**: usadas para bloquear exclusões quando houver pedido ativo; não foram migradas nesta etapa.
- **`combo_itens` + `combos`**: impedimento antecipado de arquivar ingrediente em combo ativo; o editor de combos ainda NÃO está implementado.
- **23 tabelas preservadas**. A nova estrutura modifica uma tabela e cria um índice, sem mudar o número de tabelas.

No modelo final 0.2, refletir a nova coluna, as relações de auditoria e estoque, e o fluxo de exclusão condicionada. Em todos os diagramas, diferenciar o que existia na 0.1 daquilo que foi acrescentado após avaliações e revisão da PIT I.

## Pontos pendentes (não apresentar como concluídos)

- Completar critérios e RNFs de US-16/US-17 (incluindo prova de tempos de resposta de cadastro/edição/exclusão).
- Criar fluxos reais de combos, horários, CEP/região, agendamento, avisos e demais histórias da PIT I.
- Atualizar integralmente casos de uso, classes, sequência, atividades, modelo lógico/físico e dicionário após estabilização do esquema.
- Publicar somente quando os testes e a avaliação da branch estiverem aprovados.
- Integrar pagamentos reais e e-mail/SMS **apenas se houver serviço externo configurável**; caso contrário, declarar modo demonstrativo, dependências e critérios não comprovados no laudo e no segundo vídeo.

**Publicação:** não houve merge na `main` ou atualização do site `https://le-cupcake.onrender.com/` neste ciclo.
