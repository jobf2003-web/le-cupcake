# Le Cupcake — Projeto Integrador em Engenharia de Software II

A Le Cupcake é uma loja virtual acadêmica de cupcakes, desenvolvida como continuidade do planejamento realizado na PIT I. A versão inicial 0.1 foi apresentada no primeiro vídeo. Após a etapa de avaliações e a revisão das 25 histórias de usuário, o projeto evoluiu para a versão 0.2.

A aplicação está disponível em **https://le-cupcake.onrender.com/**, e o código-fonte está publicado na branch `main` deste repositório.

## Funcionalidades

O catálogo apresenta cupcakes com pesquisa, filtros de categoria, preços e disponibilidade. O cliente pode selecionar produtos avulsos ou montar combos, alterar o carrinho, aplicar cupons e registrar pedidos demonstrativos.

O checkout oferece entrega ou retirada, cálculo local de taxas por região, horários de agendamento e opções de pagamento simuladas. Clientes cadastrados podem consultar pedidos e avaliações; a área administrativa permite gerenciar produtos, estoque, pedidos, cupons, entregas, contas e relatórios.

O acompanhamento de pedidos é atualizado por consultas periódicas. Os avisos de andamento são exibidos dentro da aplicação.

## Tecnologias

O sistema utiliza Python 3.11+, FastAPI, Jinja2, HTML, CSS e JavaScript, com banco SQLite. A estrutura-base contém 23 tabelas e sete migrações elevam o modelo final a 27 tabelas, com 173 colunas, 34 chaves estrangeiras e 20 índices nomeados.

## Execução local

1. Instale Python 3.11 ou superior.
2. Instale as dependências com `python -m pip install -r requirements.txt`.
3. Execute `python iniciar.py` (ou `INICIAR_WINDOWS.bat` no Windows).
4. Abra `http://127.0.0.1:8000`.

As credenciais administrativas são configuradas pelas variáveis `ADMIN_EMAIL` e `ADMIN_PASSWORD`. Não inclua senhas, arquivos `.env` ou dados pessoais reais no repositório.

## Testes

A suíte de referência foi executada em ambiente local por meio de `python -m pytest -q`, com **93 testes automatizados aprovados**. Os casos incluem catálogo, cadastro, pedidos, estoque, combos, agendamento, notificações internas e pagamento demonstrativo.

A suíte não representa certificação de desempenho sob alto volume de acessos nem validação de serviços externos. O projeto não processa cobranças bancárias, não contrata entregas físicas e não envia SMS/e-mail de acompanhamento. A persistência do SQLite na hospedagem gratuita não é garantida após reinicializações.

## Documentação e apresentação

A pasta `docs` reúne a documentação do projeto, a modelagem UML, o dicionário de dados, a rastreabilidade das histórias, os resultados dos ciclos de desenvolvimento, o laudo de qualidade e o formulário da PIT II. As cinco fichas de avaliação e o primeiro vídeo foram preservados como registros da versão inicial.

O segundo vídeo apresenta a versão 0.2: https://drive.google.com/file/d/1t3OihMjUK0ExYL8F4_LVbNIh55u8stNu/view?usp=sharing.
