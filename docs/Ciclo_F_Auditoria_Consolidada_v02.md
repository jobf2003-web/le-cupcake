# Ciclo F — auditoria, modelagem e consolidação da Le Cupcake 0.2

**Situação: DOCUMENTAÇÃO DA VERSÃO 0.2 PUBLICADA.** Os Ciclos A–F foram integrados à `main`, com implantação confirmada no Render. O primeiro vídeo e as cinco avaliações são registros da versão inicial 0.1; o segundo vídeo apresenta a 0.2.

## Histórico e causalidade

A PIT I definiu **25 histórias**. A PIT II exige revisar escopo, UML, IHC, modelos conceitual/lógico/físico, dicionário, codificação, testes, cinco avaliações em PDF, laudo com evidências e dois vídeos.

A sequência factual adotada é **0.1 (implementação inicial e primeiro vídeo) → cinco avaliações preservadas → revisão dos requisitos originais → Ciclos A–E da versão 0.2 → Ciclo F → integração à `main` e publicação no Render**. A revisão de requisitos identificou lacunas não necessariamente apontadas nas avaliações. O primeiro vídeo permanecerá como registro histórico. A versão 0.2 é a evolução documentada diretamente a partir da implementação inicial 0.1, após as avaliações e a revisão dos requisitos da PIT I.

## Fontes efetivamente verificadas

- Documento original da PIT I: 25 histórias, regras, critérios, RNFs, backlog e tarefas. A tabela original soma **320 horas**, enquanto o texto menciona **332 horas**; divergência documental preservada.
- Material didático da PIT II: situações 1, 2 e 3; modelo oficial `PIT_atividade.docx`.
- Código-fonte da branch, módulos e `tests/`; documentação de ciclos A–E.
- Cópia local do código do Ciclo E, novamente testada com `python -m pytest -q`: **93 testes aprovados**.
- SQLite criado de `schema.sql` + `migrations.py`: **PRAGMA user_version=7, 27 tabelas, 173 campos, 34 relações FK, 20 índices nomeados, 61 rotas FastAPI**. Sem violações no `PRAGMA foreign_key_check` da base de teste.

`schema.sql` sozinho contém **23 tabelas-base**. A modelagem física da 0.2 deve sempre contar as quatro adicionais criadas nas migrações. O carrinho ativo é de **sessão assinada**, não das tabelas projetadas `carrinhos` e `carrinho_itens`.

## Matriz das 25 histórias

Consultar [Mapa_25_Historias.md](Mapa_25_Historias.md). O fato de uma função central existir não comprova todos os critérios não funcionais. A versão atual contém recursos centrais implementados e **recursos demonstrativos/parciais**, não uma afirmação de 25 histórias integralmente homologadas.

**Limitações declaradas do protótipo:**
- **US-12:** meios PIX/cartão demonstrativos sem cobrança; **US-25: nenhum gateway externo integrado**.
- **US-11/21:** avisos dentro do aplicativo, não SMS/e-mail para mudanças de pedidos.
- **US-07:** recuperação por token depende de SMTP/HTTPS configurado para envio real.
- **US-06/19:** status consultado por polling de 15 s, não push instantâneo.
- **US-04/05/13/24:** CEP, taxa, retirada e agenda demonstrativos; sem operador logístico.
- **US-15:** valores nutricionais não são certificados; não inventar dados.
- Requisitos de tempo/carga (incluindo 500/1.000 operações simultâneas) **não comprovados**, assim como uso em dispositivos físicos.
- Fotos externas e atribuições CC BY/CC BY-SA precisam de verificação na aplicação publicada.
- Persistência do SQLite no plano gratuito do Render **não está garantida** sem configuração adequada.

## Modelagem (fonte versionada e arquivos visuais)

[Índice de modelos](modelagem_v02/README.md): casos de uso, classes de domínio, dois diagramas de sequência, atividades, modelo conceitual e visões lógicas. **Pagamento no diagrama é simulador local, sem conexão a PSP**. **Notificação no diagrama é canal app, sem envio externo**. Diagramas e dicionário físicos foram extraídos do banco de teste migrado; os campos e FKs não foram inferidos de diagramas de planejamento.

Os modelos representam a implementação 0.2 integrada à `main`. Os documentos de interface são protótipos esquemáticos, não capturas de testes.

## Controle de consistência dos documentos da versão 0.2

Os registros de avaliação e o primeiro vídeo pertencem à versão 0.1 e permanecem inalterados. A revisão dos requisitos do PIT I e os Ciclos A–F produziram a versão 0.2 descrita neste documento.

- **Banco efetivo:** 23 tabelas no esquema-base e 27 tabelas após as migrações 1–7; o dicionário oficial deve refletir as 27.
- **Testes atuais:** 93 casos automatizados aprovados em ambiente local, sem equivaler a testes visuais ou de produção.
- **Pagamentos:** métodos demonstrativos; nenhuma transação financeira ou gateway real.
- **Comunicação:** notificações internas; SMTP e SMS externos não homologados.
- **Relatórios:** valores de pedidos registrados, não receita financeira recebida.
- **Evidências:** prints locais da 0.2 identificados como locais; o serviço publicado foi confirmado no Render em implantação ativa.
- **Entrega acadêmica:** formulário, laudo e documentação principal devem relatar somente 0.1 → avaliações → revisão da PIT I → 0.2 e guardar as limitações verificadas.

## Correspondência com a atividade PIT II

| Situação | Evidência de entrega |
|---|---|
| 1 — escopo, UML, IHC e dados | Matriz das 25 histórias, diagramas, modelos conceitual/lógico/físico, dicionário de dados e protótipos |
| 2 — código, Git, testes, manual e vídeo inicial | Código da versão 0.2 publicado na `main`, site ativo no Render, 93 testes locais e manual; primeiro vídeo documenta a 0.1 |
| 3 — cinco avaliações, melhorias, laudo e vídeo de atualização | Cinco fichas preservadas, melhorias de interface e funcionalidades registradas, laudo com evidências comparativas e segundo vídeo da 0.2 |

As limitações de pagamentos, notificações externas, logística e certificação de carga pertencem ao escopo do protótipo acadêmico e são declaradas nos documentos. Os registros das avaliações não foram alterados.

## Registro de publicação

A evolução do projeto segue a sequência **versão 0.1 → avaliações e revisão da PIT I → desenvolvimento da versão 0.2**. A publicação da 0.2 na `main` e no serviço https://le-cupcake.onrender.com/ foi confirmada no Render. O segundo vídeo está disponível em https://drive.google.com/file/d/1t3OihMjUK0ExYL8F4_LVbNIh55u8stNu/view?usp=sharing. A documentação e as evidências preservam a distinção entre testes automatizados, capturas locais e demonstração do sistema publicado.
