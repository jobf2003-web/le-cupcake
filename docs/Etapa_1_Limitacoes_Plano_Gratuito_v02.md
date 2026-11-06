# Características e limitações do protótipo acadêmico

A Le Cupcake foi desenvolvida como aplicação demonstrativa utilizando recursos compatíveis com a atividade acadêmica e a hospedagem gratuita. O objetivo é apresentar o funcionamento das principais regras de negócio sem simular integrações comerciais como se fossem serviços contratados.

## Pagamentos

O checkout oferece PIX e cartão em modo demonstrativo e a opção de pagamento a combinar. Aprovação e recusa são eventos locais de teste: não há cobrança, transferência, gateway, webhooks bancários ou coleta de dados de cartão.

## Notificações e contas

Os avisos de pedidos são exibidos dentro da aplicação. Não há entrega de SMS ou e-mail de andamento. O fluxo de recuperação de senha utiliza tokens temporários, mas o envio de mensagens depende da configuração externa de SMTP e endereço público HTTPS.

## Entregas e agendamento

As faixas de CEP, taxas, modalidades e horários são configurados no painel administrativo. O resultado é uma demonstração do cálculo e da reserva de capacidade, sem vínculo com transportadora ou disponibilidade logística comercial.

## Dados e desempenho

O banco SQLite da aplicação pode não manter os registros após reinicializações na hospedagem gratuita. Por isso, o projeto é apresentado com dados demonstrativos. Os 93 testes automatizados locais verificam regras funcionais e controles de acesso; não constituem certificação de desempenho ou concorrência em escala de produção.

## Fotografias e informações nutricionais

A aplicação utiliza fotografias externas com referências documentadas. Sua exibição depende da disponibilidade das fontes. As informações nutricionais e de alergênicos são exibidas conforme cadastro administrativo e não representam certificação de receitas reais.

Estas características delimitam o alcance da versão 0.2 publicada em https://le-cupcake.onrender.com/.
