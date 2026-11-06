# Evolução da modelagem e do banco de dados

A revisão dos requisitos da PIT I indicou mudanças na estrutura de dados da implementação inicial. O modelo relacional foi atualizado de maneira incremental, com migrações SQLite versionadas e preservação dos registros existentes.

## Principais alterações

| Área | Evolução da versão 0.2 |
|---|---|
| Produtos | Registro de arquivamento lógico, histórico administrativo e controle de estoque |
| Catálogo | Consultas combinadas por busca e categoria, com disponibilidade dos produtos |
| Entregas | Faixas de CEP, regiões, custos, horários de atendimento e bloqueios de agenda |
| Combos | Composição de produtos e detalhamento dos itens associados aos pedidos |
| Contas | Tokens temporários para redefinição de senha e controle de sessões |
| Informações de produto | Ingredientes e vínculo entre cupcakes e alergênicos |
| Pedidos | Histórico de eventos, acompanhamento e avisos internos |
| Pagamentos | Métodos demonstrativos, estados e histórico de decisões simuladas |

## Modelo físico consolidado

O esquema-base contém 23 tabelas. As migrações 1–7 acrescentaram as estruturas necessárias aos novos recursos, resultando em 27 tabelas, 173 colunas, 34 chaves estrangeiras e 20 índices nomeados no banco de referência.

O conjunto de diagramas apresenta casos de uso, classes, sequências, atividades, modelo conceitual e modelo lógico/físico. O dicionário de dados descreve os campos efetivos do SQLite migrado.

## Critérios de consistência

Os dados de carrinho são mantidos em sessão assinada durante o uso da aplicação, enquanto pedidos, pagamentos demonstrativos e eventos possuem registros no banco. Os campos monetários armazenam valores em centavos. As relações e índices apoiam as validações e a integridade referencial.

As modificações de dados correspondem aos recursos implementados nos ciclos A–E e documentados no Ciclo F.
