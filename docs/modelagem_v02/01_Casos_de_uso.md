# Casos de uso — versão 0.2 (fronteiras reais)

Atores: visitante, cliente cadastrado e administrador. Os serviços externos NÃO estão integrados.

```mermaid
flowchart LR
  V([Visitante])
  C([Cliente cadastrado])
  A([Administrador])
  subgraph SITE["Le Cupcake 0.2"]
    U1([Consultar catálogo e filtros])
    U2([Montar carrinho e combos])
    U3([Calcular frete e agenda demonstrativos])
    U4([Selecionar pagamento e simular aprovação/recusa])
    U5([Consultar status e pedido])
    U6([Conta, recuperação e avaliação])
    U7([Ler avisos internos])
    U8([Gerenciar produtos e clientes])
    U9([Gerenciar pedidos, logística interna e relatórios])
  end
  V --- U1 & U2 & U3 & U4 & U5
  C --- U2 & U5 & U6 & U7
  A --- U7 & U8 & U9
  OUT["Fora da implementação: cobrança bancária; SMS/e-mail de pedidos; transporte real"]
  U4 -.-> OUT
```

A ligação pontilhada indica **ausência de integração**. Esta representação complementa os diagramas formais de domínio e não declara atendimento integral dos requisitos de desempenho.
