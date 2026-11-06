# Testes da versão 0.2

O conjunto de testes foi executado localmente com Python, FastAPI TestClient, HTTPX, Pytest e SQLite.

Para reproduzir a verificação:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

A suíte de regressão da versão 0.2 concluiu **93 testes automatizados aprovados**, abrangendo catálogo, carrinho, pedidos, estoque, clientes, autenticação, cupons, avaliações, administração, entrega, agendamento, combos, notificações internas e pagamento demonstrativo.

O banco de referência foi iniciado com as migrações 1–7. A inspeção identificou **27 tabelas, 173 colunas, 34 relações de chave estrangeira e 20 índices nomeados**, sem violações de integridade referencial no `PRAGMA foreign_key_check`.

A execução não corresponde a ensaio formal de carga, certificação de acessibilidade em dispositivos físicos ou prova de integração com serviços financeiros, logísticos e de comunicação externos. Essas restrições estão descritas na documentação técnica.

O código testado foi incorporado à `main` e publicado no Render como versão 0.2.
