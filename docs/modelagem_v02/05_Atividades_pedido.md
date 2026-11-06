# Diagrama de atividades — pedido e pagamento demonstrativo

```mermaid
flowchart TD
 A([Pedido criado]) --> B{Forma de pagamento}
 B -->|PIX/cartão demo| C[Pendente sem cobrança real]
 B -->|A combinar| F[Pagamento não verificado]
 C --> D{Decisão do simulador}
 D -->|Recusa| E[Cancelar pedido; devolver estoque e cupom]
 D -->|Aprova apenas na demo| G[Registrar aprovação fictícia]
 G --> F2[Confirmar pedido no painel]
 F --> F2
 F2 --> H{Cancelar antes do preparo?}
 H -->|Sim| E
 H -->|Não| I[Entrar em preparo: não cancelar]
 I --> J[Pronto]
 J --> K[Entrega ou retirada demonstrativa]
 K --> L([Concluído])
 E --> M([Cancelado])
```

A decisão do simulador não prova autorização por um banco; a modalidade `a_combinar` não significa pagamento recebido. A regra do sistema bloqueia cancelamentos depois de entrar em preparo.
