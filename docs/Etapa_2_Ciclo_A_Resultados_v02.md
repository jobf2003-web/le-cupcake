# Ciclo A — Catálogo, migrações e cancelamento

O Ciclo A iniciou as alterações da versão 0.2 após as avaliações da versão 0.1 e a revisão dos requisitos da PIT I. O trabalho concentrou-se no catálogo, na atualização do banco de dados e nas regras de cancelamento de pedidos.

## Desenvolvimento

A busca por texto e os filtros por categoria passaram a funcionar de forma combinada. Na interface com JavaScript, os resultados do catálogo são atualizados sem recarregar toda a página; quando o navegador não executa o script, a consulta tradicional por endereço continua disponível. Produtos sem estoque são tratados segundo as condições dos filtros.

Foi incorporado o controle de versões do esquema SQLite com `PRAGMA user_version` e migrações sequenciais. A primeira migração preservou as 23 tabelas do esquema inicial. O cancelamento de pedidos passou a ser bloqueado depois do início do preparo, mantendo a consistência das alterações de estoque.

## Verificação

O ciclo encerrou com **35 testes automatizados aprovados**. Foram verificados o funcionamento das migrações, os filtros do catálogo, o cancelamento em situações permitidas e os bloqueios de transições indevidas. A sintaxe do JavaScript também foi conferida.

## Resultado na versão 0.2

As alterações foram incorporadas aos ciclos seguintes e integram o site publicado. O desenvolvimento posterior acrescentou gestão de produtos, agendamento, combos, funcionalidades de relacionamento e pagamentos demonstrativos. A versão final reúne 93 testes automatizados aprovados em ambiente local.
