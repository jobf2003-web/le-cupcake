# Modelo conceitual — Le Cupcake 0.2

```mermaid
erDiagram
  USUARIO ||--o{ PEDIDO : registra
  PEDIDO ||--|{ ITEM_PEDIDO : contem
  CUPCAKE ||--o{ ITEM_PEDIDO : participa
  ITEM_PEDIDO ||--o{ COMPONENTE_COMBO : desdobra
  CUPCAKE ||--o{ COMPONENTE_COMBO : compoe
  PEDIDO ||--o{ PAGAMENTO_DEMO : registra
  PAGAMENTO_DEMO ||--o{ EVENTO_PAGAMENTO : historiza
  PEDIDO ||--o{ NOTIFICACAO_INTERNA : gera
  USUARIO ||--o{ NOTIFICACAO_INTERNA : recebe
  USUARIO ||--o{ AVALIACAO : publica
  CUPCAKE ||--o{ AVALIACAO : possui
  PEDIDO }o--o| REGIAO_ENTREGA : usa
  PEDIDO }o--o| JANELA_ENTREGA : agenda
  PEDIDO }o--o| CUPOM : aplica
```

As cardinalidades ilustram o domínio. O físico completo contém 27 tabelas, algumas de apoio e outras de estrutura projetada que não são utilizadas por todos os fluxos.
