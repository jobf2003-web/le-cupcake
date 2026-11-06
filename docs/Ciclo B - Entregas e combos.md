# Ciclo B — Entrega, agendamento e combos

O Ciclo B ampliou o fluxo de compra da versão 0.2 com recursos de entrega e composição de produtos. As regras são demonstrativas, adequadas à finalidade acadêmica da loja.

## Desenvolvimento

O administrador passou a configurar modalidades de recebimento, faixas de CEP, taxas por região, janelas de horário e bloqueios de agenda. O checkout calcula o valor conforme a modalidade escolhida; na retirada, não exige endereço de entrega. O agendamento observa disponibilidade e capacidade cadastradas.

Também foi criada a montagem de combos personalizados. O cliente escolhe os sabores e as quantidades, e o servidor calcula o preço com base nos componentes, conferindo o estoque disponível. O carrinho e o registro do pedido mantêm a composição escolhida.

As migrações SQLite das revisões 3 e 4 acrescentaram as tabelas de bloqueios de agenda e componentes de pedidos em combos. Ao término desta etapa, o banco possuía 25 tabelas.

## Verificação

A suíte atingiu **60 testes automatizados aprovados**. Os casos contemplaram CEP, faixas sobrepostas, regras de retirada, capacidade da agenda, datas fora do intervalo, composição de combos, preços e preservação de estoque.

## Resultado na versão 0.2

Os recursos estão disponíveis na versão publicada. As taxas e os horários representam uma simulação administrativa: não há contratação de transportadora, confirmação logística externa ou processamento de encomendas comerciais reais.
