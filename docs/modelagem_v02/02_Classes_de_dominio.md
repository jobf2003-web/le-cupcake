# Classes de domínio — versão 0.2

O diagrama é uma abstração do domínio; as colunas exatas estão no banco físico. O carrinho é guardado em **sessão**, embora tabelas não utilizadas de carrinho também existam no SQL inicial.

```mermaid
classDiagram
direction LR
class Usuario {
  +int id
  +str email
  +str papel
  +bool ativo
}
class Cupcake {
  +int id
  +int categoria_id
  +int preco_centavos
  +int estoque
}
class CarrinhoSessao {
  +map itens_por_id
}
class Pedido {
  +int id
  +int usuario_id
  +str status
  +int total_centavos
  +date agendado_para
}
class ItemPedido {
  +int id
  +int pedido_id
  +int quantidade
  +int preco_unitario_centavos
}
class ComboComponente {
  +int pedido_item_id
  +int cupcake_id
  +int quantidade
}
class Pagamento {
  +int pedido_id
  +str metodo
  +str provedor
  +str status
}
class EventoPagamento {
  +str status_anterior
  +str status_novo
}
class NotificacaoInterna {
  +int usuario_id
  +str canal_app
  +str status
}
class Avaliacao {
  +int cupcake_id
  +int nota
  +str status
}
Usuario "1" --> "0..*" Pedido
Pedido "1" --> "1..*" ItemPedido
ItemPedido "1" --> "0..*" ComboComponente
ComboComponente "0..*" --> "1" Cupcake
ItemPedido "0..*" --> "0..1" Cupcake
Pedido "1" --> "0..*" Pagamento
Pagamento "1" --> "0..*" EventoPagamento
Usuario "1" --> "0..*" NotificacaoInterna
Usuario "1" --> "0..*" Avaliacao
CarrinhoSessao ..> Cupcake : IDs e quantidades
```

**Não há classe de gateway de pagamento conectado em produção.** `Pagamento` registra tentativa demonstrativa em `simulador_local`.
