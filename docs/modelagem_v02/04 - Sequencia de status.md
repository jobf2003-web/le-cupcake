# Diagrama de sequência — status e notificação interna

```mermaid
sequenceDiagram
  autonumber
  actor Admin as Administrador
  participant API as FastAPI
  participant DB as SQLite
  actor Cliente
  Admin->>API: Solicita nova etapa com CSRF
  API->>DB: BEGIN IMMEDIATE; conferir transição e registrar evento
  DB->>DB: Criar notificação interna, canal=app
  DB-->>API: Status atualizado
  API-->>Admin: Confirmação da operação
  loop Cada 15 segundos
    Cliente->>API: GET /api/pedido/{token}/status
    API->>DB: Consultar estado e previsão
    DB-->>API: Status e previsão cadastrada
    API-->>Cliente: Exibir etapa atual
  end
  Cliente->>API: Ler notificações em Minha conta
  API-->>Cliente: Mensagens internas
```

Não representa comunicação push instantânea nem SMS/e-mail entregue externamente. Acompanhamento de pedidos por pessoas sem login é via token privado.
