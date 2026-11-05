# Le Cupcake — PIT II · Etapa 2, Ciclo E · versão 0.2 em desenvolvimento

**Situação do ciclo:** implementado e testado localmente; ainda não publicado no site. **Não é homologação integral da US-12 ou US-25.**

## 1. Registro da evolução real do projeto

- **PIT I:** especificou 25 histórias. A US-12 solicita seleção de pagamento e confirmação segura; a US-25 solicita integração a gateways online, com aprovação confirmada e metas de desempenho/concorrência.
- **Versão 0.1:** implementação inicial apresentada no primeiro vídeo, com pedidos cadastrados e pagamento “a combinar”, sem cobrança.
- **Avaliações:** foram realizadas e registradas nas fichas já aprovadas pelo tutor; mantidas como material histórico, sem alterações retrospectivas.
- **Revisão das histórias após as avaliações:** mostrou que US-12 e US-25 não estavam atendidas. A correção decorre da revisão do escopo da PIT I; **não atribuir a existência de pagamentos simulados a recomendações específicas dos avaliadores se isso não constar das fichas**.
- **Versão 0.2 em desenvolvimento, Ciclo E:** introduz métodos demonstrativos selecionáveis, transições e auditoria locais, com limitação explícita de serviço gratuito.

## 2. Implementação verificada neste ciclo

| Recurso | Implementação e observação |
|---|---|
| Escolha de pagamento | Checkout oferece **PIX demonstrativo**, **cartão demonstrativo (sem capturar cartão)** e **a combinar**. Valores finais continuam calculados no servidor. |
| Simulador de aprovação/recusa | Em pedido com método demonstrativo, o visitante que possui o link privado pode escolher aprovar ou recusar **somente na simulação**; a aprovação não representa dinheiro recebido. |
| Estado do pedido | Pagamento demonstrativo **pendente** bloqueia confirmação administrativa do pedido. Aprovação permite avançar o fluxo de preparação; recusa cancela o pedido. |
| Estoque e cupons | Ao recusar, o estoque de cupcakes e componentes de combos é restituído e a utilização do cupom é desfeita. Um cancelamento administrativo válido também restaura estoque e, se havia aprovação simulada, registra reversão **simulada**, não estorno bancário. |
| Idempotência | Repetir a mesma decisão não duplica eventos, devoluções ou alterações de pagamento. Decisão contrária depois da primeira é rejeitada. Transições usam `BEGIN IMMEDIATE` do SQLite. |
| Histórico técnico | Nova migração SQLite **versão 7**, com tabela `pagamento_eventos` e índices. Registra estado anterior, novo estado e origem; sem salvar número do cartão ou credencial de provedor. |
| Interface administrativa | O painel exibe método/estado do pagamento, identifica os demonstrativos e não oferece confirmar um pedido demonstrativo ainda pendente; o servidor também proíbe esse avanço. |
| API do pedido | Expõe apenas método, estado e indicador de demonstração junto ao status, sem informações financeiras sensíveis e sem dados pessoais novos. |
| Controle de acesso | A ação de simular exige o link privado do pedido e token CSRF válido. Esse link é uma credencial de consulta e de demonstração e não deve ser compartilhado. |

**Compatibilidade:** pedidos antigos com método `a_combinar` permanecem registrados como `pendente` e podem seguir o fluxo operacional já existente. **Confirmar preparo não equivale a afirmar pagamento recebido.**

## 3. Testes e evidências

Ambiente local Python/FastAPI/Jinja2/SQLite, execução `python -m pytest -q` em cópia do projeto na revisão deste ciclo: **93 testes aprovados** (79 de ciclos anteriores e **14 novos** do Ciclo E). `node --check static/app.js` também passou.

Os novos testes cobrem: opções e avisos na interface, rejeição de método inválido, pendência inicial, CSRF, aprovação, recusa, idempotência e impossibilidade de decisão contraditória, cancelamento administrativo, reposição de estoque de produto isolado e combo, reutilização de cupom, duplicidade concorrente, consulta por token, ausência de dados de cartão/integração externa e migração a partir do esquema v6 preservando pedidos. Há testes de regressão nos fluxos anteriores, incluindo pedidos antigos.

**Atenção:** os testes de API/HTML não substituem a inspeção visual manual em navegador real nem medição de carga e latência. Não foi executada compra real nem homologação em ambiente sandbox de um PSP.

## 4. Restrições econômicas e de infraestrutura (obrigatório nos documentos finais)

**O projeto usa hospedagem gratuita e não possui conta de cobrança nem gateways configurados. Portanto:**

1. **Não recebe pagamentos reais**, não gera QR Code PIX cobravel, não cria cobranças, não faz transferência financeira e não executa estornos bancários.
2. As palavras **“aprovado”, “recusado” e “estornado”**, quando o provedor é `simulador_local`, descrevem exclusivamente um **fluxo fictício de demonstração**.
3. Não há cartão capturado, CVV, tokens de cartão, conta bancária ou API financeira de terceiros no sistema.
4. A US-12 está **implementada de forma demonstrativa**, com métodos e validações locais, mas a confirmação por gateway real continua **não atendida**.
5. A US-25 permanece **não integrada a gateways reais**; ter mais de um método demonstrativo NÃO corresponde a “integração com múltiplos gateways”.
6. Requisitos não funcionais de 5/8 segundos e 500 transações simultâneas permanecem **não comprovados**; as execuções locais não constituem ensaio formal de carga.
7. Persistência na hospedagem gratuita pode não ser garantida, como já registrado nos ciclos anteriores; não apresentar pedidos como reservas ou encomendas comerciais.

Esta informação deverá permanecer no laudo, na matriz de rastreabilidade, na documentação geral da versão 0.2, nos diagramas (com a fronteira do **simulador local**, sem ator gateway externo realmente conectado) e no segundo vídeo.

## 5. Diagramação/modelagem a atualizar na consolidação da 0.2

- **Casos de uso:** selecionar método; confirmar/recusar **em simulador local**; consultar resultado. Um gateway real deve ser mostrado apenas como **dependência não implementada**.
- **Atividades:** `recebido → pagamento demonstrativo pendente → aprovar/recusar → confirmado/cancelado`, evidenciando que a confirmação final de compra real não existe.
- **Sequência:** cliente → checkout → SQLite/pagamentos → simulador local → evento de pagamento/pedido → estoque; sem chamada a PSP.
- **Classes/modelo lógico:** `pedidos (1:N) pagamentos (1:N) pagamento_eventos`; preservação de pedidos antigos; estados e auditoria.
- **Modelo físico/dicionário de dados:** incorporar `pagamento_eventos` (v7) e os índices; nenhuma coluna de cartão/segredo.
- **Evolução 0.1→0.2:** preservar fidelidade histórica e separar motivação das avaliações da correção decorrente da revisão das 25 histórias.

## 6. Publicação e conclusão

Todos os arquivos deste ciclo pertencem à branch isolada `pit-ii-25-historias-completas`. **Não mesclar à `main`, não substituir o site do Render e não atualizar a documentação oficial como “concluída” até a homologação final das 25 histórias e as limitações identificadas.** O primeiro vídeo permanece inalterado.

**Próxima fase:** consolidação da modelagem UML, dados e documentação da versão 0.2, com auditoria final das 25 histórias e testes de navegação e desempenho dentro das condições do plano gratuito.
