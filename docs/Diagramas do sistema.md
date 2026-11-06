# Diagramas do sistema

Os diagramas abaixo foram atualizados para refletir corretamente as relações do domínio e do banco de dados da versão 0.2 da Le Cupcake. Eles são simplificados, mas seguem a estrutura representada em `schema.sql` e nas migrações do projeto.

## Casos de uso

![Casos de uso corrigidos](diagramas/Casos%20de%20uso%20corrigido.svg)

O diagrama separa os fluxos do **cliente** e do **administrador**. Os pagamentos continuam demonstrativos, sem integração real com bancos ou gateways.

## Classes de domínio

![Classes de domínio corrigidas](diagramas/Classes%20de%20dominio%20corrigido.svg)

As associações principais agora correspondem às entidades do sistema. Em especial:

- **Categoria** se relaciona com **Cupcake**;
- **Pedido** se relaciona com **ItemPedido** e **Pagamento**;
- **Avaliação** depende de **Usuário** e **Cupcake**;
- **ItemPedido** referencia **Cupcake** ou **Combo**, e não ambos ao mesmo tempo.

## Relacionamentos principais do banco

![Relacionamentos corrigidos](diagramas/Relacionamentos%20corrigidos.svg)

Este diagrama resume as tabelas centrais do banco SQLite. Ele evita associações inexistentes, como ligações diretas entre **Cupcake** e **Pagamento** ou entre **Categoria** e **Pedido**.

## Diagramas já válidos

### Sequência do checkout

![Sequência de finalização do pedido](diagramas/Sequencia%20do%20checkout.svg)

### Sequência de acompanhamento

![Sequência de acompanhamento de pedidos](diagramas/Sequencia%20de%20acompanhamento.svg)

### Atividades do pedido

![Atividades de pedidos e pagamento demonstrativo](diagramas/Atividades%20do%20pedido.svg)

## Protótipos de interface

### Catálogo

![Protótipo do catálogo](diagramas/Prototipo%20do%20catalogo.png)

### Carrinho

![Protótipo do carrinho](diagramas/Prototipo%20do%20carrinho.png)

### Administração

![Protótipo da área administrativa](diagramas/Prototipo%20da%20administracao.png)
