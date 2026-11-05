# Manual de uso — Le Cupcake 0.2 (branch em desenvolvimento)

Este manual descreve o código da branch `pit-ii-25-historias-completas`. **A versão pública no Render ainda não foi substituída**. Use apenas dados fictícios.

## Preparação local

Instale Python 3.11+, execute `python -m pip install -r requirements.txt` e `python iniciar.py` (ou `INICIAR_WINDOWS.bat` no Windows). Abra `http://127.0.0.1:8000`. Configure `ADMIN_EMAIL` e `ADMIN_PASSWORD` com senha forte para acesso administrativo; não comite `.env`.

## Cliente e visitante

1. No **catálogo**, busque por texto, combine categorias e observe os produtos sem estoque. Na área do cliente autenticado podem aparecer sugestões conforme o histórico de compras.
2. No **carrinho**, adicione cupcakes, ajuste quantidades e exclua itens. Em **Combos**, selecione sabores e quantidades; o servidor calcula preços e disponibilidade dos componentes.
3. No **checkout**, escolha entrega ou retirada. Para entrega, informe CEP/região atendida e agendamento habilitado. A taxa é **demonstrativa**, definida pelo administrador, sem transportadora.
4. Escolha `PIX demonstrativo`, `cartão demonstrativo` ou `a combinar`. Nas duas primeiras modalidades, a decisão de aprovar/recusar é apenas uma **simulação interna**; não ocorre transferência financeira nem coleta de cartão.
5. Anote o link privado do pedido e acompanhe o status; a tela consulta a API a cada 15 segundos, e notificações internas aparecem em **Minha conta** para clientes cadastrados.
6. Crie conta ou faça login para consultar o histórico e avaliar produtos. O fluxo de recuperação de senha usa token com validade; o e-mail só é enviado se o administrador configurou SMTP com URL pública HTTPS. Sem serviço externo, a recuperação por e-mail não está disponível.

## Administrador

1. Acesse **Área administrativa** usando credenciais próprias, sem senha padrão.
2. Em **Produtos**, crie/edite cupcakes, preço, estoque, foto documentada, ingredientes e alergênicos. O arquivamento lógico é bloqueado em produtos com pedidos ativos; o histórico administrativo registra alterações.
3. Em **Entregas**, configure modalidades, regiões/faixas CEP, taxas, janelas, capacidade e datas bloqueadas. O agendamento é interno e não confirma transporte real.
4. Em **Pedidos**, atualize status conforme as transições permitidas. Não é permitido cancelar após iniciar o preparo. Pagamentos fictícios pendentes não podem ser tratados como aprovados; `a combinar` permanece não verificado.
5. Em **Cupons**, cadastre descontos/validade; em **Avaliações**, modere e responda; em **Clientes**, edite e bloqueie cadastros com trilha.
6. Em **Relatórios**, filtre dados de pedidos por mês/categoria; os valores são **pedidos registrados, não recebimentos bancários**. Em **Notificações**, veja avisos internos e marque-os como lidos.

## Limitações e testes

- **Não realiza pagamentos reais**, PIX, estornos bancários ou integração com gateways.
- **Não envia SMS/e-mail de andamento de pedidos**; mensagens são internas no sistema.
- Recomendações e conteúdo nutricional são demonstrativos e dependem de dados cadastrados.
- O SQLite pode ser apagado quando a instância gratuita for reiniciada; não use clientes/endereços reais.
- Testes: `python -m pip install -r requirements-dev.txt && python -m pytest -q`. Resultado local de referência: **93 aprovados**. Faltam medições de carga, inspeção visual em navegador real e confirmação da publicação final.
- Fotografias externas e licenças devem ser conferidas antes do uso público.

O primeiro vídeo e as cinco avaliações pertencem ao histórico da versão anterior. A nova apresentação será gravada apenas após a validação e publicação da edição 0.2 consolidada.
