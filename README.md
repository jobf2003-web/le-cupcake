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

## Manual de uso

### Navegação e pedidos

1. Abra o [site da Le Cupcake](https://le-cupcake.onrender.com/) e consulte o **Cardápio**. Use o campo de busca ou os filtros por categoria para encontrar um cupcake.
2. Selecione um produto para conferir seus detalhes e adicioná-lo ao carrinho. Para combinar sabores, abra **Monte seu combo**, escolha os itens e adicione o conjunto ao carrinho.
3. Acesse **Carrinho** para conferir os produtos e valores. É possível atualizar quantidades ou remover itens antes de continuar.
4. Avance para **Finalizar pedido**. Informe nome, e-mail e telefone; escolha **entrega** ou **retirada**. Para entrega, preencha o endereço e, quando solicitado, o CEP. A taxa é calculada conforme a região cadastrada.
5. Se houver horários configurados, selecione a data e o intervalo disponível. Informe um cupom, caso tenha, e confira o resumo e o valor final.
6. Escolha uma das opções de pagamento apresentadas e confirme o pedido. As opções de PIX e cartão funcionam apenas como **demonstração**; não há cobrança bancária. A opção **A combinar** não significa pagamento concluído.
7. Na página do pedido, acompanhe o status e o histórico de movimentações pelo link individual. Para pagamentos demonstrativos, a própria página oferece opções de simular aprovação ou recusa; a recusa cancela o pedido. Guarde o endereço da página para consultas posteriores.

### Conta do cliente

Para criar uma conta, selecione **Entrar / Cadastrar** no menu e preencha o formulário. Depois de entrar, acesse **Minha conta** para consultar seus pedidos e avisos internos. Os avisos podem ser marcados como lidos.

Para avaliar um cupcake, abra a página do produto com a conta autenticada, selecione uma nota de 1 a 5 estrelas e escreva um comentário. A avaliação passa pela moderação da loja antes de aparecer publicamente. O menu também permite encerrar a sessão.

### Área administrativa

1. Clique em **Área administrativa** e entre com as credenciais definidas para o sistema.
2. No **Painel de gestão**, consulte os indicadores, os pedidos recentes e a lista de produtos. Utilize **Novo cupcake** para cadastrar um produto, **Editar** para alterar seus dados e **Ocultar/Ativar** para controlar sua exibição. **Excluir** arquiva o produto, preservando o histórico aplicável.
3. Em **Pedidos**, consulte as compras registradas, altere o status conforme as etapas permitidas e informe uma previsão quando necessário. Para pagamentos demonstrativos, a confirmação do pedido requer que a aprovação correspondente tenha sido registrada.
4. Em **Cupons**, cadastre códigos promocionais, configure regras de uso, valores e validade ou desative cupons existentes.
5. Em **Avaliações**, examine as avaliações recebidas, defina sua situação de publicação e registre uma resposta da loja quando pertinente.
6. Em **Entregas**, ajuste modalidades e taxas, regiões por CEP, horários disponíveis, capacidade e datas sem atendimento.
7. Em **Clientes**, consulte e atualize cadastros e seus históricos. Em **Relatórios**, filtre informações por mês e categoria. Em **Avisos internos**, consulte e marque as notificações administrativas como lidas.

As alterações feitas no painel são registradas na própria aplicação. O projeto utiliza pedidos e pagamentos de demonstração e não realiza entregas físicas.

## Documentos da entrega

- [Documentação técnica em Word](docs/Documentacao%20do%20projeto.docx)
- [Documentação técnica em PDF](docs/Documentacao%20do%20projeto.pdf)
- [Diagramas e protótipos](docs/Diagramas%20do%20sistema.md)
- [Dicionário de dados](docs/Dicionario%20de%20dados.docx)
- [Laudo de qualidade](docs/Laudo%20de%20qualidade.pdf)
- [Avaliações dos participantes](docs/Avaliacoes%20dos%20participantes.pdf)
- [Referências das fotografias](docs/Referencias%20fotograficas.docx)

O primeiro vídeo registra a versão 0.1: [assistir ao primeiro vídeo](https://drive.google.com/file/d/1jj2vhp1Bgc8iYXeqt2CTQA2VwP723w0I/view?usp=drive_link). O segundo apresenta as mudanças da versão 0.2: [assistir ao segundo vídeo](https://drive.google.com/file/d/1t3OihMjUK0ExYL8F4_LVbNIh55u8stNu/view?usp=sharing).
