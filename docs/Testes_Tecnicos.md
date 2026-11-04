# Verificação técnica — versão 0.5

**Ambiente:** Python, FastAPI/Starlette TestClient, Pytest, HTTPX e SQLite; cada teste utiliza banco de dados isolado e temporário. A execução é local, não envolve serviço de pagamento, SMS, e-mail ou hospedagem pública.

**Comando:** `python -m pip install -r requirements-dev.txt` e, em seguida, `python -m pytest -q`.

**Resultado da execução desta versão:** **27 testes automatizados aprovados**, incluindo regressões das versões anteriores. Foram avaliados catálogo, imagens documentadas, busca, carrinho, proteção CSRF, checkout, estoque, pedido, cancelamento, conta de cliente, autenticação, histórico de pedidos, descontos percentuais e fixos, cupom inválido, limite de uso, avaliação moderada, resposta administrativa, proteção de HTML, relatório, modalidade de entrega e campo nutricional.

**O que esses testes não comprovam:** uso por cinco pessoas reais, desempenho em produção, recuperação de senha, auditoria de segurança, acessibilidade completa, integração de pagamento ou correspondência integral das 25 histórias de usuário. As avaliações humanas, correções documentadas e vídeos continuam pendentes e não foram inventados.
