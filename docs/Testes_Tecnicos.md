# Testes técnicos — versão 0.2 consolidada (pré-homologação)

**Ambiente de referência:** Python, FastAPI/Starlette TestClient, HTTPX, Pytest e SQLite local.

**Comandos:** `python -m pip install -r requirements-dev.txt`; `python -m pytest -q`.

**Resultado local do Ciclo E, novamente reproduzido no Ciclo F: 93 testes aprovados.** Incluem regressões dos ciclos anteriores e novos fluxos de catálogo, pedidos, combos, agendamento, estoque, autenticação, cupons, avaliações, administração, notificações internas e pagamento demonstrativo.

O banco de referência foi criado por `create_app(testing=True)`, com aplicação de `migrations.py`: `PRAGMA user_version=7`, **27 tabelas, 173 colunas, 34 FKs, 20 índices nomeados** e `PRAGMA foreign_key_check` sem violações.

**Limites importantes:** os testes automatizados não provam 100% dos 25 critérios de aceitação. Não medem metas de latência, 500/1.000 operações concorrentes, funcionamento visual em navegador real, persistência na hospedagem gratuita, cobrança/estorno financeiro, entrega logística ou SMS/e-mail externos. A coleta de cinco avaliações em PDF é uma obrigação separada; registros históricos existentes não foram reescritos.

**Versionamento:** 0.1 é a implementação anterior ao primeiro vídeo; 0.2 é a ampliação após avaliações e revisão das histórias. O site público permanece na revisão anterior até homologação da branch.

Documentação da auditoria atual: [Ciclo F](Ciclo_F_Auditoria_Consolidada_v02.md), [mapa](Mapa_25_Historias.md), [checklist](Checklist_Entrega_PIT_II.md).
