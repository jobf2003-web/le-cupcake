# Ciclo D — Acompanhamento de pedidos e administração

O Ciclo D acrescentou funções de acompanhamento e gestão à versão 0.2 da Le Cupcake.

## Desenvolvimento

O histórico de pedidos passou a registrar eventos de mudança de status e previsão de atendimento. A página de acompanhamento consulta periodicamente essas informações enquanto está aberta. Os avisos ao cliente e ao administrador são apresentados dentro do sistema, sem envio por SMS ou e-mail.

A área administrativa recebeu recursos de edição e bloqueio de clientes, consulta do histórico de alterações e relatórios com filtros por período e categoria. Os indicadores reúnem pedidos e produtos registrados, inclusive componentes de combos, distinguindo valores demonstrativos de receitas financeiras efetivamente recebidas.

A atualização do banco incluiu estruturas para eventos e avisos, preservando a compatibilidade com as migrações anteriores.

## Verificação

A suíte alcançou **79 testes automatizados aprovados**, com dez novos casos relativos a notificações internas, autorização, consulta de status, previsão, edição de clientes e relatórios.

## Resultado na versão 0.2

As funcionalidades foram incorporadas ao site publicado. A atualização do acompanhamento é feita por consultas periódicas, e os avisos permanecem internos à aplicação. Os testes locais não equivalem a uma medição de capacidade de atendimento sob grande volume de acessos.
