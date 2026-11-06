# Etapa 1 — Limitações de plano gratuito, integrações e transparência (versão 0.2)

## Princípio

A Le Cupcake é um projeto acadêmico demonstrativo, sem comercialização real. Recursos externos podem depender de conta, cobrança, credenciais, aprovação comercial ou infraestrutura persistente. **Uma tela que simula uma operação não é a execução real dessa operação.** Sempre distinguir “implementado e testado”, “demonstrativo” e “não disponível/não validado”.

Este registro integra a documentação da evolução **0.1 → avaliações + revisão das 25 histórias → 0.2**. As limitações precisam constar também da documentação acadêmica, da matriz, do laudo, do formulário oficial (quando finalizado) e do segundo vídeo, conforme relevância.

## Matriz de dependência externa

| Recurso / histórias | O que é possível desenvolver sem serviço pago | O que depende de serviço externo, acesso ou infraestrutura | Como documentar |
|---|---|---|---|
| **Pagamento** — US-12/25 | Tela de escolha de método; contrato/adaptadores de pagamento; validação; estados pendente/aprovado/recusado em **modo de demonstração**; testes com provedores **sandbox** quando disponíveis | Cobranças reais, conta de recebedor, gateway, homologação, webhooks de produção, antifraude, 2 ou mais provedores efetivamente integrados | “Não processa pagamentos reais”; especificar se há apenas simulação ou sandbox real. Não afirmar que CA de integração produtiva foi cumprido. Não coletar cartão. |
| **Notificação e-mail/SMS** — US-11/21 | Notificações internas no sistema, preferências e fila/registro de eventos, visualização e testes de mensagens; e-mail de testes quando houver provedor habilitado | Entrega externa real, API/SMTP/SMS, quotas, verificação de remetente, custo por SMS | Identificar canais realmente entregues. Registro na base não prova recebimento. Marcar CA de envio como pendente se não houver prova. |
| **Recuperação de senha** — US-07 | Tokens de uso único, expiração, formulários e visualização de link **somente para ambiente de desenvolvimento** | Enviar link com segurança ao destinatário depende de e-mail configurado | Nunca exibir tokens de recuperação para qualquer visitante em produção; se envio não existir, identificar a limitação e não marcar funcionalidade completa. |
| **Frete por CEP/região** — US-04/05/24 | Tabela administrativa de faixas CEP, cálculo local validado no servidor, custo da região e retirada gratuita | Consulta de CEP externa ou frete de transportadora, rastreamento/roteirização reais | “Simulador de valores por região configurada; sem contrato com transportadora”, se aplicável. Não declarar logística real. |
| **Agenda de entrega** — US-13 | Calendário e janelas internas, datas de operação, reserva de capacidade, limites de até 15 dias | Compromisso operacional com confeitaria/entregadores e disponibilidade real | “Agendamento demonstrativo; sem serviço real de entregas”, se aplicável. |
| **Desempenho/concorrência** — RNFs de várias US | Testes locais de tempo de resposta, carga com limites realistas e ambiente documentado | Demonstração sustentada de 500 transações/1.000 pedidos simultâneos em hospedagem gratuita pode ser incompatível com limites reais | Registrar números medidos e infraestrutura. Se não ensaiado, escrever **“não comprovado”** e não alegar conformidade. |
| **Persistência e segurança** — transversal | SQLite local e cenários de migração; proteção de sessão e CSRF; dados de teste | No plano gratuito, disco persistente/serviço de banco gerenciado e backups podem não estar disponíveis | Informar que persistência após reinicialização da hospedagem não está garantida até teste/configuração. Usar apenas informações fictícias. |
| **Fotografias** — catálogo | Catálogo usa fotos de fontes documentadas | Licenças CC BY/CC BY-SA exigem atribuição apropriada; disponibilidade externa variável | Conservar crédito/licença no documento e verificar atendimento dos termos na publicação. |

## Linguagem obrigatória nos artefatos finais

- **Implementado e testado:** há evidência de fluxo real e a regra funciona no ambiente declarado.
- **Demonstrativo/simulado:** há interface e lógica local, mas não há transmissão/cobrança/entrega externa efetiva. Identificar o limite explicitamente.
- **Pendente por custo/credenciais/serviço:** não completou a integração, com motivação e consequência para cada CA.
- **Não comprovado:** meta de latência ou concorrência ainda sem teste representativo.

**Não ocultar limitações e não reduzir o escopo documental às partes já construídas.** O objetivo é demonstrar a evolução da 0.1 para a 0.2 com a máxima implementação tecnicamente viável, documentando com exatidão o que não pode ser realizado sob restrições da hospedagem gratuita.

## Condições antes da publicação da 0.2

1. Confirmar quais recursos gratuitos e credenciais de teste são efetivamente disponíveis.
2. Testar cada integração no nível correspondente (local, sandbox, produção), com evidência e sem segredos no GitHub.
3. Revisar documentação e modelagem antes do segundo vídeo. O primeiro vídeo permanece como registro histórico da versão 0.1.
4. Preservar os textos e datas das cinco avaliações aprovadas pelo tutor. Não atribuir retroativamente às avaliações funcionalidades que não existiam naquele momento.
