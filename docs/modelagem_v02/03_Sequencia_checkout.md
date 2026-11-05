# Diagrama de sequência — checkout da 0.2

```mermaid
sequenceDiagram
  autonumber
  actor Cliente
  participant Site as FastAPI / checkout
  participant DB as SQLite (transação)
  participant Demo as Simulador local
  Cliente->>Site: Enviar cesta, CEP, agendamento, cupom, método
  Site->>Site: CSRF, dados, estoque, capacidade e preço
  Site->>DB: Criar pedido/itens; reservar estoque; pagamento pendente
  DB-->>Site: Pedido e link privado
  Site-->>Cliente: Exibir pedido (nenhuma cobrança real)
  alt PIX ou cartão demonstrativo
    Cliente->>Site: Aprovar ou recusar simulação
    Site->>DB: Iniciar transação; validar pagamento e estado
    Site->>Demo: Decisão somente local
    alt Aprovado localmente
      Demo-->>Site: aprovado somente no simulador
      Site->>DB: Registrar evento demonstrativo
    else Recusado localmente
      Demo-->>Site: recusado somente no simulador
      Site->>DB: Cancelar pedido, devolver estoque e cupom uma vez
    end
    DB-->>Cliente: Novo estado no acompanhamento
  else A combinar
    Site-->>Cliente: Pagamento não verificado
  end
```

**Não há chamada a gateway, banco ou operadora**. Aprovar no simulador não significa receber dinheiro.
