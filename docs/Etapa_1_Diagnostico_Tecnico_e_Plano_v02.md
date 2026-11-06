# Revisão técnica do projeto — PIT II

## Histórico

A PIT I definiu o planejamento de uma loja virtual de cupcakes e um conjunto de 25 histórias de usuário. Na PIT II, a primeira implementação, identificada como versão 0.1, foi apresentada em vídeo e submetida à etapa de avaliação. A análise dos registros e a revisão dos requisitos originais orientaram as melhorias e a ampliação da versão 0.2.

## Situação da implementação inicial

A versão 0.1 já possuía catálogo, pesquisa, carrinho, cadastro de clientes, pedidos demonstrativos, estoque, cupons, moderação de avaliações e funções administrativas. Os requisitos da PIT I, porém, abrangiam fluxos adicionais: filtros dinâmicos, cancelamento condicionado ao preparo, histórico de alterações de produtos, configuração de regiões e horários de entrega, combos, recuperação de conta, recomendações, notificações e opções de pagamento.

Os ajustes foram distribuídos em ciclos incrementais para permitir testes de regressão e evolução controlada do banco de dados. A arquitetura utiliza Python com FastAPI, páginas Jinja2, HTML, CSS e JavaScript e armazenamento SQLite.

## Organização do desenvolvimento

Os ciclos A e A.2 trataram de catálogo, migrações, estoque e auditoria administrativa. O Ciclo B acrescentou entrega demonstrativa, agendamento e combos. O Ciclo C ampliou contas, promoções e informações de produtos. O Ciclo D desenvolveu recursos de acompanhamento e gestão. O Ciclo E incorporou pagamento demonstrativo. O Ciclo F reuniu a modelagem e os documentos.

A sequência de migrações SQLite preservou o esquema-base e ampliou a estrutura de 23 para 27 tabelas. Ao término do desenvolvimento, a suíte local atingiu 93 testes automatizados aprovados.

## Limites do protótipo

Por se tratar de uma aplicação acadêmica, pagamentos não realizam operações bancárias; avisos por SMS/e-mail e logística externa não fazem parte do sistema; e a hospedagem gratuita não oferece garantia documental de persistência do arquivo SQLite após reinicializações. As verificações automatizadas não representam certificação de desempenho para grande volume de acessos.

A versão 0.2 foi integrada à branch `main` e publicada em https://le-cupcake.onrender.com/.
