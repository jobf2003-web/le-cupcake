# Le Cupcake — Projeto Integrador em Engenharia de Software II

A Le Cupcake é uma aplicação acadêmica de loja virtual de cupcakes. O projeto dá continuidade ao planejamento da PIT I, com 25 histórias de usuário. A versão 0.1 foi apresentada no primeiro vídeo e acompanhada pela etapa de avaliações; a revisão dos requisitos e das avaliações orientou a versão 0.2.

**Aplicação publicada:** https://le-cupcake.onrender.com/

## Funcionalidades

O catálogo possui busca, filtros por categoria, preços e informações de disponibilidade. O cliente pode montar um carrinho com produtos avulsos ou combos, utilizar cupons e registrar pedidos demonstrativos.

No checkout, a aplicação apresenta modalidades de entrega ou retirada, taxas por região, opções de agendamento e pagamentos simulados. O cliente cadastrado pode consultar seu histórico e avaliações. A administração permite gerenciar produtos, pedidos, estoque, clientes, promoções, entregas e relatórios.

## Tecnologias e testes

O projeto utiliza Python 3.11+, FastAPI, Jinja2, HTML, CSS, JavaScript e SQLite. Após sete migrações, o banco possui 27 tabelas. A suíte automatizada de referência concluiu **93 testes locais aprovados**.

As operações de pagamento são exclusivamente demonstrativas. O protótipo não realiza entregas físicas nem envia notificações de acompanhamento por SMS ou e-mail, e a hospedagem gratuita não oferece garantia de persistência dos dados SQLite após reinicializações.

## Executar no computador

1. Instale Python 3.11 ou superior.
2. Execute `python -m pip install -r requirements.txt`.
3. Inicie com `python iniciar.py` ou `INICIAR_WINDOWS.bat` no Windows.
4. Abra `http://127.0.0.1:8000`.

O acesso administrativo utiliza as variáveis de ambiente `ADMIN_EMAIL` e `ADMIN_PASSWORD`. Não coloque senhas ou informações reais de clientes no repositório.

## Documentos da entrega

- [Documentação técnica em Word](docs/Documentacao%20do%20projeto.docx)
- [Documentação técnica em PDF](docs/Documentacao%20do%20projeto.pdf)
- [Diagramas e protótipos](docs/Diagramas%20do%20sistema.md)
- [Dicionário de dados](docs/Dicionario%20de%20dados.docx)
- [Laudo de qualidade](docs/Laudo%20de%20qualidade.pdf)
- [Avaliações dos participantes](docs/Avaliacoes%20dos%20participantes.pdf)
- [Formulário da PIT II](docs/Atividade%20PIT%20II%20preenchida.docx)
- [Referências das fotografias](docs/Referencias%20fotograficas.docx)

O primeiro vídeo registra a versão 0.1. O segundo apresenta as mudanças da versão 0.2: https://drive.google.com/file/d/1t3OihMjUK0ExYL8F4_LVbNIh55u8stNu/view?usp=sharing.
