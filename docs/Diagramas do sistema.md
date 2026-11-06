# Diagramas e protótipos da Le Cupcake

Os diagramas representam a estrutura e o funcionamento da versão 0.2 da aplicação. A descrição dos requisitos, das regras e dos testes consta na [documentação técnica](Documentacao%20do%20projeto.docx) e no [dicionário de dados](Dicionario%20de%20dados.docx).

## Casos de uso

![Diagrama de casos de uso](diagramas/Casos%20de%20uso.png)

## Classes do domínio

![Diagrama de classes](diagramas/Classes.png)

## Sequência do checkout

![Sequência de finalização do pedido](diagramas/Sequencia%20do%20checkout.svg)

O checkout registra o pedido e reserva o estoque. As operações de pagamento demonstrativo ocorrem dentro da aplicação, sem comunicação com bancos ou gateways.

## Sequência de acompanhamento

![Sequência de acompanhamento de pedidos](diagramas/Sequencia%20de%20acompanhamento.svg)

O administrador registra a mudança de status. O cliente consulta o estado do pedido periodicamente e recebe avisos internos no sistema.

## Atividades do pedido

![Atividades de pedidos e pagamento demonstrativo](diagramas/Atividades%20do%20pedido.svg)

O cancelamento é permitido somente antes do início do preparo. Pagamentos simulados não representam transferência financeira.

## Modelo conceitual e relacionamentos

![Diagrama de relacionamentos](diagramas/Relacionamentos.png)

O esquema SQLite possui 23 tabelas na estrutura inicial e 27 tabelas após as sete migrações. A descrição de atributos e relações está no dicionário de dados.

## Protótipos de interface

### Catálogo

![Protótipo do catálogo](diagramas/Prototipo%20do%20catalogo.png)

### Carrinho

![Protótipo do carrinho](diagramas/Prototipo%20do%20carrinho.png)

### Administração

![Protótipo da área administrativa](diagramas/Prototipo%20da%20administracao.png)

Os protótipos são representações esquemáticas da interface. As comparações das versões 0.1 e 0.2 estão no [laudo de qualidade](Laudo%20de%20qualidade.pdf).
