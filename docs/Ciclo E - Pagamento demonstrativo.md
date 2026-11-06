# Ciclo E — Pagamento demonstrativo

O Ciclo E incorporou à versão 0.2 opções de pagamento simuladas, permitindo apresentar o fluxo do checkout sem realizar operações financeiras.

## Desenvolvimento

O checkout passou a oferecer PIX demonstrativo, cartão demonstrativo e a opção de pagamento a combinar. A aplicação registra os estados internos das tentativas, permitindo simular aprovação ou recusa. A recusa cancela o pedido e repõe o estoque quando cabível. As regras de idempotência evitam decisões repetidas ou contraditórias.

A interface deixa explícito que não há cobrança, transferência ou estorno de dinheiro. Nenhum dado de cartão é solicitado ou armazenado e não existe integração com provedores bancários.

A revisão 7 do esquema acrescentou a tabela `pagamento_eventos` e índices de apoio. Com todas as migrações aplicadas, o banco alcançou 27 tabelas.

## Verificação

A suíte do desenvolvimento chegou a **93 testes automatizados aprovados**, incluindo 14 novos casos de pagamento, proteção de formulários, transições de estado, estoques, cupons e compatibilidade com pedidos anteriores. A sintaxe do JavaScript foi conferida.

## Resultado na versão 0.2

O simulador integra a aplicação publicada, com suas restrições identificadas no checkout e na documentação. Os estados de pagamento são registros de demonstração, não comprovantes de transações financeiras.
