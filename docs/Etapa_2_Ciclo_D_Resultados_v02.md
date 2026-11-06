# Le Cupcake — Etapa 2, Ciclo D: operação e relacionamento (versão 0.2)

**Data:** 05/11/2026 · **Ambiente:** desenvolvimento local e branch `pit-ii-25-historias-completas`.

**Este documento não afirma que a versão 0.2 está concluída nem altera retroativamente a versão 0.1.**

## 1. Evolução histórica verídica

A versão **0.1** foi a implementação inicial apresentada no primeiro vídeo. Após as cinco avaliações registradas e a revisão do backlog de **25 histórias da PIT I**, constatamos que faltava implementar funções previstas originalmente. A nova **versão 0.2** agrega melhorias decorrentes das avaliações **e**, distintamente, corrige lacunas identificadas na comparação com o projeto inicial. O segundo vídeo apresenta essa evolução na versão 0.2 publicada. As fichas originais não são reescritas e não são atribuídas a elas solicitações que não constam nos registros.

Os testes e alterações deste ciclo foram desenvolvidos na branch isolada; não constituem publicação da aplicação final.

## 2. O que mudou no Ciclo D

| História | Versão inicial / estado anterior | Implementação deste ciclo | Limitação / status de aceite |
|---|---|---|---|
| US-06 — acompanhamento | Consulta manual do status por link/cadastro | API de status com token de alta entropia, histórico de eventos e atualização visual a cada 15 segundos enquanto a página estiver aberta; estimativa inserida pelo administrador | Consulta periódica, **não push em tempo real**. Requisito não funcional de 2 s e escala de 1.000 pedidos simultâneos **não comprovados**. |
| US-11 — avisos ao cliente | Tabela de notificações sem fluxo operacional | Notificações internas transacionais ao criar pedido e após mudanças de status, visíveis apenas ao titular da conta | **Não envia SMS ou e-mail**. Clientes convidados podem acompanhar pelo link do pedido; não recebem aviso interno associado a conta. Requisito de escolha de canal e entrega em até 1 minuto **não atendido**. |
| US-18 — relatórios | Resumo de pedidos e ranking sem filtro de categoria ou gráfico | Relatórios com filtro por mês/categoria, ranking de itens avulsos e componentes de combos, alternância entre unidades e valores em gráfico local | Valores **não são pagamentos recebidos**. Por categoria, somente valor bruto dos itens, sem atribuir frete/descontos; desempenho de 5 segundos e interação no navegador real ainda precisam de homologação. |
| US-19 — operação | Painel de pedidos com atualização manual; cancelamento após início da produção já corrigido no Ciclo A | Previsão opcional de entrega/retirada por pedido, consulta periódica ao status, registro de mudança e avisos internos ao cliente | Não é atualização por push; 500 pedidos simultâneos **não comprovados**; previsão é estimativa manual, não promessa logística. |
| US-21 — avisos ao administrador | Sem aviso de novo pedido | Registros internos para contas administrativas ativas, visíveis no painel, com opção de marcar como lidos | Sem canais externos configuráveis e sem SMS/e-mail. Testes de envio em massa e latência externa não executados. |
| US-22 — administração de contas | Listagem e bloqueio/reativação de clientes | Edição de nome/e-mail sob autenticação administrativa, validação de duplicidade e histórico de alterações com autor/data/antes/depois | A edição não substitui verificação de identidade externa; dados cadastrados são fictícios para fins acadêmicos. |

**Não foram alteradas nem substituídas as cinco avaliações existentes.** Melhorias não previstas nos formulários são atribuídas à revisão do escopo da PIT I, sem falsa causalidade.

## 3. Ajustes técnicos e rastreabilidade

- **Migração 6 do SQLite:** nova coluna `pedidos.previsao_entrega_em` e índices para notificação/eventos; preserva os registros anteriores, testada em base nova e em migração.
- **Notificações:** módulo `order_notifications.py` utiliza a tabela preexistente `notificacoes`; insert é realizado na mesma transação da criação do pedido ou da atualização do status. A marcação de leitura é restrita ao usuário autenticado e usa proteção CSRF.
- **Status:** `GET /api/pedido/{token}/status` expõe apenas situação, previsão e eventos, usa `Cache-Control: no-store` e requer token não previsível do pedido. Não divulga dados pessoais nesse endpoint.
- **Clientes:** rotas administrativas de edição e histórico, auditoria em `auditoria` e validação de e-mail duplicado. Acesso restrito ao administrador.
- **Relatórios:** módulo `sales_reporting.py` calcula com consultas SQL parametrizadas e agrega corretamente produtos avulsos e componentes de combos; pedidos cancelados são excluídos. O filtro por categoria mostra somente valor bruto de seus itens e não confunde isso com receita financeira recebida.
- **Interface:** alterações contidas em `templates/` e `static/` sem substituir as fotografias ou a identidade visual existente.

## 4. Testes realizados e limites

Executado localmente em uma cópia da branch, com Pytest/FastAPI TestClient e banco SQLite temporário:

- **79 testes passaram** (`69` de ciclos anteriores + `10` novos no arquivo `tests/test_cycle_d_v02.py`).
- Verificações: migração idempotente, preservação de pedidos, notificações de cliente/admin, leitura/autorização e CSRF, API privada de status e ausência de PII, previsão válida e inválida, edição de clientes e duplicidade, trilha de auditoria, filtros de relatórios e componentes de combos, exclusão de pedidos cancelados das métricas.
- Compilação Python e sintaxe do JavaScript foram verificadas. `PRAGMA foreign_key_check` não retornou violações na base de teste.

**Não realizados neste ciclo:** envio de e-mail ou SMS por provedor, teste de carga de 500/1.000 transações ou pedidos simultâneos, validação de latência do Render, teste completo de acessibilidade, verificação por dispositivo físico e testes de interface interativa em navegador gráfico.

## 5. Limitações do plano gratuito e do protótipo

- O projeto permanece **acadêmico e fictício**; não captura pagamentos reais.
- A comunicação de pedidos por e-mail/SMS não foi implementada neste ciclo. A tabela de notificações representa exclusivamente avisos **dentro do site**. Não usar a existência desses registros como prova de entrega de mensagens externas.
- A funcionalidade de previsão é informativa. Agendamento e frete por região são demonstrativos, sem contratação de entrega real.
- A hospedagem gratuita com SQLite pode não manter os dados após reinicialização, dependendo de configuração de armazenamento. Não alegar persistência em produção sem comprovação.
- O gráfico permite alternância acessível por controle JavaScript; comportamento visual real ainda requer verificação em navegador.

## 6. Continuidade e publicação

O Ciclo E integrou o pagamento demonstrativo e o Ciclo F consolidou a modelagem, os testes e a documentação da versão 0.2. Os ciclos A–F foram incorporados à `main`, com implantação ativa no Render. A suíte automatizada global concluiu 93 testes locais; a ausência de SMS/e-mail externo, gateway bancário e logística real está declarada como limitação do protótipo acadêmico.

As cinco fichas de avaliação e o primeiro vídeo permaneceram preservados; o segundo vídeo registra a solução 0.2.
