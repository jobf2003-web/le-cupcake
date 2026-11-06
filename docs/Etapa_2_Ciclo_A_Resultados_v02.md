# Le Cupcake — Etapa 2, ciclo A: implementação inicial da versão 0.2

**Estado:** ciclo implementado e testado localmente; posteriormente integrado à `main` como parte da versão 0.2 publicada. Este ciclo é a primeira parte da implementação da versão **0.2**, desenvolvida após as avaliações e a revisão do escopo da PIT I; não equivale à implementação completa das 25 histórias.

## 1. Contexto e evolução

A **versão 0.1** corresponde ao sistema apresentado no primeiro vídeo. Depois das cinco avaliações registradas e da revisão integral das 25 histórias do trabalho original da PIT I, foram identificadas melhorias de usabilidade e lacunas de implementação. A **versão 0.2** reunirá ambas as frentes. O primeiro vídeo e as avaliações existentes permanecem inalterados.

**Origem das mudanças deste ciclo:** o requisito de atualização dinâmica vem da revisão da **US-02** original; a restrição de cancelamento vem da regra de negócio da **US-19**; a migração versionada é uma decisão técnica para permitir evolução segura do banco. **Não atribuir automaticamente essas mudanças às opiniões dos avaliadores.**

## 2. Alterações implementadas

| Alteração | Arquivos | Evidência funcional | Situação |
|---|---|---|---|
| Migração de esquema sem apagar os dados existentes | `migrations.py`, `app.py` | `PRAGMA user_version`, savepoints, três índices adicionais, rejeição de banco com versão futura; testes de banco novo e legado | Implementado e testado localmente |
| Busca e filtros de categoria combinados sem recarregar a página | `app.py`, `templates/index.html`, `templates/catalogo_resultados.html`, `static/app.js`, `static/style.css` | Consulta compartilhada entre página completa e fragmento HTML; filtro JS progressivo e fallback por requisição GET; exclusão de esgotados em resultados filtrados | Código e testes HTTP implementados; demonstração final realizada no site publicado |
| Cancelamento somente antes do início do preparo | `app.py` | Remove transição para `cancelado` a partir de `preparo`, `pronto` e `em_entrega`; conserva transições válidas e restauração de estoque quando permitido | Implementado e testado |
| Identificação de cache compatível com a versão acadêmica 0.2 | `templates/base.html`, testes existentes | URLs de CSS e JavaScript usam `?v=0.2`, evitando reaproveitar código antigo do navegador | Implementado e testado |

**Banco:** continuam existindo **23 tabelas de aplicação**, além dos índices originais e três índices novos. O controle de migração usa o cabeçalho `PRAGMA user_version` do SQLite, sem introduzir tabela adicional. A revisão **1** é a versão do *esquema de migrações*, **não** uma nova versão do site.

**Migrações futuras:** deverão ser adicionadas sequencialmente em `MIGRATIONS`. Não manipular o banco de produção manualmente ou atualizar a `main` sem backup e ensaio de migração.

## 3. Testes executados

- Execução local: `python -m pytest -q`, a partir da pasta da aplicação.
- **Resultado:** 35 testes aprovados, sem falhas, incluindo cinco testes novos do ciclo A.
- Testes novos verificam: migração idempotente com preservação de dados; proteção contra abrir esquema futuro; endpoint de filtros combinados; exclusão de esgotados do filtro; impedimento de cancelamento depois do preparo, sem alteração indevida do estoque.
- Também foi verificada a sintaxe do JavaScript local com `node --check static/app.js`, sem erros.
- **Alcance do teste realizado neste ciclo:** os testes locais verificaram o fluxo HTTP e a existência do JavaScript dinâmico, sem uma bateria visual automatizada em navegador gráfico. O desenvolvimento desse ciclo integra a versão publicada da 0.2.
- **Não houve** teste de carga representativo ou homologação das 25 histórias.

## 4. Integração com os ciclos posteriores

O Ciclo A registrou a implantação das migrações iniciais, dos filtros e das regras de cancelamento. Os Ciclos A.2–E complementaram a gestão de produtos, agenda, combos, relacionamento, notificações e pagamentos demonstrativos; o Ciclo F consolidou a modelagem e os 93 testes locais. As metas de carga e as integrações comerciais externas não fazem parte da comprovação desta etapa.

## 5. Publicação

A versão 0.2 contendo os resultados deste ciclo foi integrada à `main` e publicada em https://le-cupcake.onrender.com/. O primeiro vídeo e as cinco avaliações permaneceram vinculados à implementação inicial 0.1.
