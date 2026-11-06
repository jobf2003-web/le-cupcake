# Etapa 1 — Limitações de plano gratuito, integrações e transparência (versão 0.2)

## Princípio

A Le Cupcake é um projeto acadêmico demonstrativo, sem comercialização real. Recursos externos podem depender de conta, cobrança, credenciais, aprovação comercial ou infraestrutura persistente. **Uma tela que simula uma operação não é a execução real dessa operação.** Sempre distinguir “implementado e testado”, “demonstrativo” e “não disponível/não validado”.

Este registro integra a documentação da evolução **0.1 → avaliações + revisão das 25 histórias → 0.2**. As limitações de recursos gratuitos são declaradas no relatório técnico, no laudo e na apresentação final da versão publicada.

## Matriz de dependência externa

| Recurso / histórias | O que é possível desenvolver sem serviço pago | O que depende de serviço externo, acesso ou infraestrutura | Como documentar |
|---|---|---|---|
| **Pagamento** — US-12/25 | Tela de escolha de método; contrato/adaptadores de pagamento; validação; estados pendente/aprovado/recusado em **modo de demonstração**; testes com provedores **sandbox** quando disponíveis | Cobranças reais, conta de recebedor, gateway, homologação, webhooks de produção, antifraude, 2 ou mais provedores efetivamente integrados | “Não processa pagamentos reais”; especificar se há apenas simulação ou sandbox real. Não afirmar que CA de integração produtiva foi cumprido. Não coletar cartão. |
| **Notificação e-mail/SMS** — US-11/21 | Notificações internas no sistema, preferências e fila/registro de eventos, visualização e testes de mensagens; e-mail de testes quando houver provedor habilitado | Entrega externa real, API/SMTP/SMS, quotas, verificação de remetente, custo por SMS | Identificar canais realmente entregues. Registro na base não prova recebimento. Descrever o limite de não haver envio externo e não apresentar notificações internas como SMS/e-mail entregues. |
| **Recuperação de senha** — US-07 | Tokens de uso único, expiração, formulários e visualização de link **somente para ambiente de desenvolvimento** | Enviar link com segurança ao destinatário depende de e-mail configurado | Nunca exibir tokens de recuperação para qualquer visitante em produção; se envio não existir, identificar a limitação e não marcar funcionalidade completa. |
| **Frete por CEP/região** — US-04/05/24 | Tabela administrativa de faixas CEP, cálculo local validado no servidor, custo da região e retirada gratuita | Consulta de CEP externa ou frete de transportadora, rastreamento/roteirização reais | “Simulador de valores por região configurada; sem contrato com transportadora”, se aplicável. Não declarar logística real. |
| **Agenda de entrega** — US-13 | Calendário e janelas internas, datas de operação, reserva de capacidade, limites de até 15 dias | Compromisso operacional com confeitaria/entregadores e disponibilidade real | “Agendamento demonstrativo; sem serviço real de entregas”, se aplicável. |
| **Desempenho/concorrência** — RNFs de várias US | Testes locais de tempo de resposta, carga com limites realistas e ambiente documentado | Demonstração sustentada de 500 transações/1.000 pedidos simultâneos em hospedagem gratuita pode ser incompatível com limites reais | Registrar números medidos e infraestrutura. Se não ensaiado, escrever **“não comprovado”** e não alegar conformidade. |
| **Persistência e segurança** — transversal | SQLite local e cenários de migração; proteção de sessão e CSRF; dados de teste | No plano gratuito, disco persistente/serviço de banco gerenciado e backups podem não estar disponíveis | Informar que persistência após reinicialização da hospedagem não está garantida até teste/configuração. Usar apenas informações fictícias. |
| **Fotografias** — catálogo | Catálogo usa fotos de fontes documentadas | Licenças CC BY/CC BY-SA exigem atribuição apropriada; disponibilidade externa variável | Conservar crédito/licença no documento e verificar atendimento dos termos na publicação. |

## Linguagem obrigatória nos artefatos finais

- **Implementado e testado:** há evidência de fluxo real e a regra funciona no ambiente declarado.
- **Demonstrativo/simulado:** há interface e lógica local, mas não há transmissão/cobrança/entrega externa efetiva. Identificar o limite explicitamente.
- **Integração não incluída no protótipo gratuito:** explicar a dependência de custo, credencial ou serviço externo e o efeito nos critérios de aceitação.
- **Não comprovado:** meta de latência ou concorrência ainda sem teste representativo.

**Não ocultar limitações e não reduzir o escopo documental às partes já construídas.** O objetivo é demonstrar a evolução da 0.1 para a 0.2 com a máxima implementação tecnicamente viável, documentando com exatidão o que não pode ser realizado sob restrições da hospedagem gratuita.

## Registro de publicação e escopo

A versão 0.2 foi integrada à `main` e publicada no Render. O trabalho preservou as cinco avaliações e o primeiro vídeo, e o segundo vídeo apresenta a atualização. A aplicação mantém pagamentos internos demonstrativos, notificações somente no aplicativo e frete/agendamento sem operadores logísticos externos. São escolhas e limites documentados do protótipo acadêmico.
