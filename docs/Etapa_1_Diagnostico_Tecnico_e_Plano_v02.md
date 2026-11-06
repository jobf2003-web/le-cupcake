# Etapa 1 — Diagnóstico técnico e preparação da versão 0.2

**Projeto:** Le Cupcake — PIT II · **situação:** registro histórico do diagnóstico, usado no desenvolvimento concluído da versão 0.2.

## 1. Versões e registro histórico obrigatório

- **Versão 0.1:** implementação inicial apresentada no primeiro vídeo, preservada como registro histórico.
- **Avaliações:** os cinco registros já aprovados pelo tutor são mantidos como foram documentados. Suas observações são uma entrada para a melhoria; não serão reescritos para parecer que avaliaram funcionalidades que não existiam.
- **Revisão do escopo:** confronto do código com as 25 histórias originais da PIT I. A recuperação dos requisitos mostrou lacunas que não decorrem necessariamente das avaliações.
- **Versão 0.2 (evolução realizada nos Ciclos A–F):** deverá reunir as melhorias de usabilidade avaliadas e as implementações que atendam, na medida comprovada, às 25 histórias. O segundo vídeo apresentará esta evolução, com transparência sobre limitações gratuitas.

**Atenção:** a versão atualmente publicada e denominada 0.2 ainda é parcial. Não tomar sua numeração como prova de conclusão. O desenvolvimento ocorre nesta branch. Não alterar a `main` ou a aplicação pública sem validação e decisão de publicação.

## 2. Fontes e método da auditoria

1. Documento original **“Projeto - José Otávio Braga Fante (1).docx”**, seção *Resultado e discussão*, imagens das 25 histórias e tabela de tarefas. São fontes dos critérios CA, regras RN e requisitos RNF.
2. Matriz `docs/Matriz_Rastreabilidade_PIT_I_25_Historias.md`, na branch de desenvolvimento.
3. Código da branch principal consultado: `app.py` (SHA `cd680d223737437604b41c2ea5b9c5c52bf59ead`), `schema.sql` (SHA `12f4d7d6b7cd54fc6888f67a3ab6a1bcf88f6385`), templates HTML, JS e testes.
4. Uma cópia local de referência com `app.py` e `schema.sql` foi examinada com testes de regressão. Essa linha de base não constitui homologação das 25 histórias, das integrações externas nem da hospedagem; o registro final de testes da versão 0.2 consta da Etapa 2 e do Ciclo F.

**Estrutura inicial examinada:** 37 rotas GET/POST e 23 tabelas SQLite no esquema-base; o código era predominantemente centralizado em `app.py`, com templates Jinja2 e sessões assinadas. As quantidades finais da 0.2 são apresentadas no Ciclo F.

**Estimativas da PIT I:** o backlog soma 320 horas; o texto da PIT I informa 332 horas. A diferença permanece registrada, não corrigida arbitrariamente.

## 3. Diferenças técnicas verificadas

| Área / histórias | Evidência do código atual | Lacuna perante a PIT I |
|---|---|---|
| Catálogo e filtros (US-01/02) | `GET /` usa consulta e filtros de URL; catálogo HTML usa links e formulário GET | Filtros não são dinâmicos sem recarga; tempos de resposta não foram medidos. |
| Carrinho e frete (US-03/04/05) | Carrinho em sessão; modalidade de entrega com taxa fixa | Frete depende de modalidade, não de CEP/região; atualizações de valores dependem do fluxo atual; RNFs não comprovados. |
| Pedido e status (US-06/19) | `eventos_pedido` registra transições; cliente consulta pelo link; painel muda status | Na implementação 0.1 não havia atualização automática, aviso por mudança nem previsão de entrega. **O código permite cancelar pedidos em preparo/prontos**, contrariando a regra original de cancelar apenas antes da produção. |
| Conta (US-07) | Cadastro, login, hash de senha e histórico | Não existe fluxo de recuperação de senha. |
| Recomendações (US-08) | Produtos da mesma categoria na página do produto | Não utiliza histórico do cliente, nem garante as três sugestões na página inicial. |
| Promoção/avaliação (US-09/10/20/23) | Cupons com validação de servidor, moderação e resposta | Na implementação 0.1 ainda não havia divulgação de cupons na vitrine e a análise de desempenho não fazia parte daquela bateria. |
| Mensagens (US-11/21) | Tabela `notificacoes` presente | Não há envio real por e-mail/SMS, preferências nem fluxo de comunicação aos administradores. |
| Pagamentos (US-12/25) | Checkout mostra “a combinar”; registros em `pagamentos` como `demonstracao` e `pendente` | Sem escolha de meio de pagamento, confirmação por gateway ou múltiplos provedores; **não há pagamento real**. |
| Agendamento (US-13) | Tabela `janelas_entrega` presente | Sem calendário funcional, capacidade ou validação de até 15 dias e datas fechadas. |
| Combos (US-14) | Tabelas `combos` e `combo_itens` presentes | Não há interface ou fluxo de compra e controle de estoque de combos. |
| Informações nutricionais (US-15) | Campo `informacoes_nutricionais` em `cupcakes` | Alertas de alergênicos e verificação do conteúdo ainda carecem de implementação/validação. |
| Administração (US-16/17/18/22/24) | Inclusão/edição/ocultação de produto; relatórios resumidos, bloqueio de conta, custo de entrega | Na implementação 0.1 não havia os controles completos de arquivamento, auditoria, gráficos/filtros, edição de clientes e agenda por região que foram acrescentados nos ciclos posteriores. |
| Carga e desempenho (várias) | Testes Pytest de operações, sem carga representativa comprovada | Não foram comprovados os limites originais (1.000 pedidos, 500 transações, 1–8 segundos etc.). |

**Persistência no diagnóstico inicial:** o esquema-base possuía tabelas previstas para o domínio. O projeto incorporou posteriormente as migrações sequenciais 1–7, preservando dados existentes no processo de atualização.

## 4. Decisões técnicas para a execução

- **Padrão de entrega:** manter FastAPI/Jinja2/SQLite no desenvolvimento, preservar a identidade visual e acrescentar módulos conforme necessário. Evitar reescrita completa sem justificativa.
- **Migrações:** utilizar revisões versionadas de esquema com `PRAGMA user_version` do SQLite, savepoints e rollback; a estratégia foi aplicada e verificada localmente antes da integração ao ramo principal. A implementação inicial desta estratégia está em `migrations.py` (Etapa 2, ciclo A).
- **Contratos de domínio:** separar serviços para catálogo, carrinho/combos, pedidos, logística/agendamento, cupons, notificações, pagamento, identidade e auditoria. A divisão foi desenvolvida de forma incremental e verificada por testes.
- **Pedidos/estoque:** garantir transações atômicas, estoque de combo por componente, regras de mudança de status, cancelamento antes da produção e proteção contra processamento duplicado.
- **Segurança:** CSRF, autorização, sessão segura, não armazenar dados de cartão, proteção de tokens, auditoria, dados fictícios na demonstração e segredos apenas em ambiente seguro.
- **Dados no serviço gratuito:** não presumir persistência do SQLite no Render. Testar/recomendar armazenamento persistente antes de demonstrar continuidade dos pedidos.
- **Integrações externas:** desenvolver fluxos de demonstração quando não houver serviço gratuito; rotular explicitamente como simulação. **Nunca marcar um CA que exige entrega externa ou autorização de pagamento como integralmente validado por simulação.**
- **RNFs:** verificar latência e carga separadamente, documentando ambiente e evidência. Não declarar metas cumpridas apenas porque um teste unitário passou.
- **Documentação/modelagem:** os diagramas finais representarão a versão 0.2 realmente implementada; uma seção de evolução registrará as diferenças em relação à 0.1, separando resultados das avaliações de correções de requisitos descobertos na revisão.

## 5. Ordem de implementação e dependências

| Ciclo previsto na etapa inicial | Escopo | Histórias envolvidas | Critério de saída |
|---|---|---|---|
| A — Base e consistência | Migrações, auditoria, catálogo dinâmico, carrinho, validações, regras de exclusão e status | US-01/02/03/06/16/17/19 | Testes novos + regressão, sem alterações que destruam dados. |
| B — Recebimento e compra | CEP/regiões, taxas, retirada/horário, calendário e combos | US-04/05/13/14/24 | Checkout, preço e estoque consistente em todos os caminhos. |
| C — Cliente e relacionamento | Recuperação de senha, recomendações históricas, nutrição/alergênicos, avaliações e promoções | US-07/08/09/10/15/20/23 | Controles e regras de domínio validados. |
| D — Operação e informação | Administração de clientes, gráficos e filtros de vendas, tempo estimado e comunicação | US-06/11/18/19/21/22 | Logs, permissões, eventos e entrega verificável ou limitação declarada. |
| E — Pagamento e homologação | Métodos de pagamento, adaptadores para gateways, aprovação, erros, segurança e requisitos de carga | US-12/25 e RNFs transversais | Homologação apenas no modo realmente disponível; marcar separadamente simulado e externo. |
| F — Modelagem e entrega | Modelos UML, conceitual/lógico/físico, dicionário, testes integrados, laudo e segundo vídeo | Todas | Matriz de aceite revisada item a item; site antigo preservado até aprovação. |

**Nota:** a modelagem de dados e dos fluxos começa junto com cada ciclo; o ciclo F é a consolidação e revisão final, não a primeira vez que os diagramas serão pensados.

## 6. Portões de qualidade (não pular)

1. **Preparado:** história, critérios originais, regras, dependências e casos de teste especificados.
2. **Implementado:** código, migração quando necessária, interface, casos de sucesso e falha.
3. **Verificado:** teste automatizado + roteiro manual pertinente, sem regressões no conjunto anterior.
4. **Validado/limitado:** indicar separadamente cada CA atendido, simulado, dependente de provedor ou não atendido; RNFs com medição ou “não comprovado”.
5. **Documentado:** modelo, dicionário, changelog 0.1→0.2, laudo e evidência atualizados.
6. **Publicado:** somente após revisão da branch de trabalho; não sobrescrever a versão pública antes do aceite final.

**Entrega da Etapa 1:** este diagnóstico, a matriz das 25 histórias, o plano de testes de aceitação e o registro de limitações técnicas/econômicas. **Nenhuma história adicional é declarada implementada neste marco.**
