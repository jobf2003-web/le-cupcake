# Protótipos esquemáticos da interface — versão 0.2

**Não são capturas de tela testadas em navegador.** Estas são estruturas e fluxos para conferência de IHC; a identidade visual existente (verde-sálvia, terracota e creme) deve ser preservada.

```mermaid
flowchart TD
  A[Catálogo: busca, filtros dinâmicos, fotos, preço, estoque e promoções]
  B[Montagem: cupcake avulso ou combo personalizado]
  C[Carrinho: quantidade, subtotal e cupom]
  D[Checkout: CEP, região, modalidade e agenda]
  E[Pagamento: PIX demo, cartão demo ou a combinar]
  F[Pedido: token privado, status consultado a cada 15 s]
  G[Minha conta: histórico, recomendações e notificações internas]
  H[Administração: produtos, clientes, cupons, entrega e relatórios]
  A --> B --> C --> D --> E --> F --> G
  H -. configura dados internos .-> A
  H -. configura taxas/agenda .-> D
```

**Mensagens exigidas pela IHC:** estoque insuficiente, CEP não atendido, horário indisponível, cupom inválido, bloqueio de cancelamento em preparo, link de redefinição indisponível sem SMTP, pagamento sem cobrança real.

**Limitação:** não houve homologação visual de todas as telas em navegador real neste ciclo. As fotos/licenças também devem ser conferidas na versão publicada.
