# Decisões técnicas — Le Cupcake 0.2

## Histórico da implementação
A PIT I definiu 25 histórias de usuário. Na PIT II foi apresentada a versão inicial **0.1** no primeiro vídeo, seguida das cinco avaliações preservadas. Após a revisão dos requisitos originais, os Ciclos A, A.2, B, C, D, E e F deram origem à versão **0.2**, ainda não publicada. Atribuir cada mudança à revisão dos requisitos ou às avaliações apenas quando sustentado pelo registro.

## Arquitetura e persistência
- Python/FastAPI, HTML, CSS, JavaScript, templates Jinja2, SQLite e testes Pytest.
- Organização por serviços incremental, sem declaração de MVC formal.
- `schema.sql`: 23 tabelas-base; migrações 1–7: **27 tabelas, 173 colunas, 34 relações FK e 20 índices nomeados**.
- O carrinho em uso é mantido em sessão assinada; as tabelas SQL projetadas para carrinhos não são sua persistência operacional.
- Pedidos, cupons, produtos, combos e estoque possuem validações no servidor e operações transacionais.

## Limitações
- PIX e cartão são exclusivamente demonstrativos: não há gateway de pagamento ou transferência real.
- Avisos de pedidos ocorrem dentro da aplicação; SMS/e-mail externos não estão homologados.
- Recuperação de senha depende de SMTP e HTTPS configurados.
- Taxa por CEP, horários e agendamento não equivalem a logística física contratada.
- Status de pedidos é consultado a cada 15 segundos, e não via push instantâneo.
- Persistência do SQLite no Render gratuito, desempenho sob carga e navegação mobile real não foram comprovados.

## Qualidade, evidências e publicação
O código do Ciclo E passou por **93 testes automatizados locais**; isso não prova todos os critérios de aceitação e requisitos não funcionais. Os documentos oficiais devem refletir os resultados locais, sem fingir homologação no Render. As cinco avaliações e o primeiro vídeo são registros da 0.1 e não devem ser alterados. A branch `pit-ii-25-historias-completas` é a fonte do desenvolvimento da 0.2; a `main` permanece preservada até aprovação e autorização expressa.
