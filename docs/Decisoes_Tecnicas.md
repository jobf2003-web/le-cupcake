# Tecnologias e decisões de implementação

A Le Cupcake utiliza Python e FastAPI no servidor; Jinja2, HTML, CSS e JavaScript nas páginas; e SQLite para persistência dos dados. A estrutura do código foi ampliada por módulos conforme as necessidades dos ciclos.

O esquema inicial contém 23 tabelas. Sete migrações versionadas compõem a estrutura final de 27 tabelas, 173 colunas, 34 relações de chave estrangeira e 20 índices nomeados.

A aplicação utiliza sessões assinadas e proteção de formulários por CSRF. As regras de preço, estoque, autorização e pagamento demonstrativo são verificadas pelo servidor. Os valores monetários são representados em centavos.

O carrinho operacional é armazenado na sessão. Pedidos, eventos de acompanhamento, avisos e pagamentos simulados ficam registrados no banco. O acompanhamento consulta periodicamente os estados dos pedidos, em vez de utilizar comunicação instantânea por push.

O escopo é acadêmico: não existe gateway bancário integrado, contratação de transportadora ou envio externo de SMS/e-mail de andamento. O envio de recuperação de senha requer serviço SMTP configurado. A persistência do SQLite na hospedagem gratuita não é garantida após reinicializações.

Os ciclos A–F foram integrados à `main`, preservando o histórico da versão 0.1. A versão 0.2 está publicada no Render. A suíte de referência concluiu 93 testes automatizados locais aprovados, sem representar ensaio de carga ou certificação de segurança de produção.
