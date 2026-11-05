# Manual de utilização — Le Cupcake, versão 0.2

## Iniciar no Windows

Extraia o ZIP, abra a pasta e execute `INICIAR_WINDOWS.bat`. Na primeira execução, tenha internet para instalar as bibliotecas. Acesse `http://127.0.0.1:8000`. Configure `ADMIN_EMAIL` e `ADMIN_PASSWORD` em `.env`, interrompa o servidor e inicie novamente para habilitar o painel.

## Cliente

1. Escolha cupcakes no cardápio ou nos filtros. O produto contém descrição, preço, fotografia real e estoque.
2. Na página do produto, veja outras sugestões da mesma categoria. Caso tenha conta, você pode enviar uma avaliação (sujeita à moderação).
3. Adicione itens ao carrinho e edite as quantidades.
4. Opcionalmente, abra **Entrar / Cadastrar**, crie uma conta com senha de 12 ou mais caracteres e faça login. Seus pedidos posteriores aparecerão em **Minha conta**.
5. No checkout, informe nome, e-mail, telefone e modalidade de recebimento. Ao selecionar **entrega**, o sistema orienta a preencher o endereço completo; na **retirada**, esse campo deixa de ser obrigatório. Insira o cupom (se tiver) no campo próprio.
6. Confirme o pedido, confira o desconto e o valor final e guarde o link de acompanhamento. Você também poderá abrir os pedidos vinculados a sua conta em **Minha conta**.

**Importante:** não há processamento de pagamentos ou entregas reais. Não insira dados verdadeiros de cartões, nomes ou endereços ao testar o protótipo.

## Administrador

1. Entre em **Área administrativa** com as credenciais do arquivo `.env`.
2. No painel, gerencie produtos, fotos reais da biblioteca documentada, preços, estoque e informações nutricionais verificadas. Use **Pedidos** para avançar o status; cancelamentos devolvem estoque e liberam o uso de eventual cupom.
3. Acesse **Cupons** para criar códigos percentuais/fixos, definir mínimo e limite de usos ou desativá-los.
4. Acesse **Avaliações** para publicar, ocultar e responder comentários recebidos.
5. Em **Relatórios**, consulte o total de pedidos (não cancelados), seus valores e produtos mais pedidos. Os valores **não** indicam pagamentos recebidos.
6. Em **Entregas**, ajuste as duas modalidades e seus custos. Ao menos uma deve permanecer ativa.
7. Em **Clientes**, consulte as contas e bloqueie ou reative seu acesso.
8. Use **Sair** para encerrar a sessão de administrador.

## Limitações e publicação

Ainda não há recuperação de senha, autenticação/verificação por e-mail, mensagens automáticas, gateway de pagamento, agendamento ou combos. Antes de receber usuários reais, revisar privacidade, segurança e persistência dos dados. As fotos são reais e suas fontes/licenças constam somente do arquivo `Referencias_Fotograficas_Simplificadas.docx`.
