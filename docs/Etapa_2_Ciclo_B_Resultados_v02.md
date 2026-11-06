# Le Cupcake — PIT II | Versão 0.2 | Etapa 2, Ciclo B

**Estado: implementado e testado em ambiente local, na branch `pit-ii-25-historias-completas`.**
O Ciclo B foi posteriormente integrado à `main` e publicado no Render como parte da versão 0.2. Não significa que as 25 histórias da PIT I estejam finalizadas.

## Evolução histórica — informações que não podem ser omitidas

- **0.1:** primeira versão demonstrada no primeiro vídeo, sem agendamento, frete por região/CEP ou montagem de combos.
- **Avaliações aprovadas pelo tutor:** permanecem registradas conforme recebidas, sem alterações retroativas nem alegação de que as pessoas testaram funções posteriormente criadas.
- **Revisão da PIT I:** as histórias US-04, US-05, US-13, US-14 e US-24 mostraram lacunas na implementação inicial, além das melhorias de usabilidade já identificadas.
- **0.2 em desenvolvimento:** o Ciclo B implementou os fluxos locais descritos abaixo. A evolução e seus limites demonstrativos estão apresentados no segundo vídeo da versão 0.2.

## O que foi implementado

1. **Entrega por CEP/região (US-04/05/24):** administrador cadastra faixas não sobrepostas de CEP e adicional em centavos; o sistema calcula frete como taxa-base + adicional regional. A API `/api/frete` ajuda a interface, mas o checkout **recalcula no servidor dentro da transação**. CEP inválido ou fora da cobertura é rejeitado. Sem regiões ativas, preserva-se a taxa fixa anterior como fallback explícito; não equivale a frete por CEP. Retirada mantém taxa de R$ 0,00 mesmo que alguém tente definir outra.
2. **Agendamento local (US-13/24):** administrador pode cadastrar janelas horárias por modalidade, definir capacidade diária e bloquear datas específicas. Quando existem janelas, cliente deve escolher data e hora. Servidor valida período de hoje a 15 dias, modalidade, data bloqueada e ocupação, incluindo concorrência via `BEGIN IMMEDIATE` durante o fechamento do pedido. Cancelamento permitido libera a vaga.
3. **Combos personalizados (US-14):** formulário para escolher 2 a 8 cupcakes, misturando sabores; até 10 combos distintos por carrinho. Interface calcula estimativa; servidor recalcula preço a partir de cada componente e soma o cupom global quando aplicável. Saldo de estoque é conferido para a soma de cupcakes avulsos e combos. O pedido registra snapshots dos componentes; o cancelamento permitido restaura exatamente as unidades utilizadas. Combos não possuem desconto automático: preço é a soma dos componentes, com eventual cupom aplicado no checkout.
4. **Migrações versionadas:** esquema físico de 23 tabelas da versão inicial mais as tabelas novas `agenda_bloqueios` e `pedido_combo_componentes`: **25 tabelas**; migrações SQLite `user_version=4`, sem sobrescrever pedidos e clientes existentes. Criados índices de CEP, data/hora e componentes.
5. **Interface:** menu para montar combo, composição do carrinho, resumo no checkout, data e CEP no comprovante, e administração de faixas de entrega, horários e bloqueios. A paleta, imagens e identidade da versão anterior foram preservadas.

## Evidência dos testes

Na pasta `tests/`, o comando local `python -m pytest -q` retornou **60 passed**: 44 anteriores + 8 testes de frete e agenda + 8 testes de combos. Foram conferidas regras de CEP, faixas sobrepostas, autorização, frete gratuito da retirada, capacidade e desbloqueio após cancelamento, datas fora do prazo, dados dos combos e integridade do estoque.

`node --check static/app.js` terminou sem erros sintáticos. **Não foi possível executar o teste visual com Chromium** porque o navegador não está instalado no ambiente de execução. Metas de latência e carga da PIT I **não foram comprovadas**. O código deste ciclo foi integrado posteriormente à versão 0.2 publicada.

## Limitações acadêmicas e do plano gratuito (expressas, não ocultas)

- **Sem frete real por transportadora.** Os intervalos de CEP e as taxas são configurados manualmente e simulam uma região atendida. O sistema não verifica a entrega real de mercadorias ou endereços.
- **Sem operação logística integrada.** A agenda reserva vagas de atendimento no banco local, mas não confirma disponibilidade real de funcionários/entregadores ou recorrência de dias fechados. O administrador precisa cadastrar janelas e bloqueios.
- **Sem pagamentos reais.** O checkout mantém `a combinar`, estado demonstrativo, sem gateway; a implementação das US-12/25 continuará em etapas posteriores, com critérios de sandbox/demonstração separados.
- **Sem envio real de SMS/e-mail**, metas de 500 ou 1.000 operações simultâneas ou garantia de persistência do SQLite no Render gratuito. Esses recursos de produção não integram o protótipo demonstrativo.
- **Integrações antigas e avaliações históricas não foram reescritas.** Os documentos oficiais, modelos UML e laudo foram consolidados no Ciclo F da versão 0.2.

## Continuidade e registro final

As funcionalidades do Ciclo B foram integradas ao desenvolvimento dos Ciclos C–F e à publicação da versão 0.2. A documentação final reúne 27 tabelas, 93 testes automatizados locais aprovados, as cinco avaliações preservadas e os dois vídeos. Frete, agenda e logística permanecem demonstrativos, sem alegar serviço externo contratado.

O primeiro vídeo registra a versão 0.1; o segundo apresenta a versão 0.2 em funcionamento.
