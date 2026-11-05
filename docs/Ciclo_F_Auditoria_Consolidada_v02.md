# Ciclo F — auditoria, modelagem e consolidação da Le Cupcake 0.2

**Situação: PRÉ-HOMOLOGAÇÃO.** Este relatório é a referência técnica da branch `pit-ii-25-historias-completas`. O site público e a branch `main` ainda representam a versão anterior; nenhum vídeo foi regravado.

## Histórico e causalidade

A PIT I definiu **25 histórias**. A PIT II exige revisar escopo, UML, IHC, modelos conceitual/lógico/físico, dicionário, codificação, testes, cinco avaliações em PDF, laudo com evidências e dois vídeos.

A sequência factual adotada é **0.1 (implementação inicial e primeiro vídeo) → cinco avaliações preservadas → revisão dos requisitos originais → Ciclos A–E da versão 0.2 → Ciclo F → futura homologação/publicação**. A revisão de requisitos identificou lacunas não necessariamente apontadas nas avaliações. O primeiro vídeo permanecerá como registro histórico. A versão 0.2 consolidada substituirá a edição intermediária rotulada 0.2; não será criada 0.3.

## Fontes efetivamente verificadas

- Documento original da PIT I: 25 histórias, regras, critérios, RNFs, backlog e tarefas. A tabela original soma **320 horas**, enquanto o texto menciona **332 horas**; divergência documental preservada.
- Material didático da PIT II: situações 1, 2 e 3; modelo oficial `PIT_atividade.docx`.
- Código-fonte da branch, módulos e `tests/`; documentação de ciclos A–E.
- Cópia local do código do Ciclo E, novamente testada com `python -m pytest -q`: **93 testes aprovados**.
- SQLite criado de `schema.sql` + `migrations.py`: **PRAGMA user_version=7, 27 tabelas, 173 campos, 34 relações FK, 20 índices nomeados, 61 rotas FastAPI**. Sem violações no `PRAGMA foreign_key_check` da base de teste.

`schema.sql` sozinho contém **23 tabelas-base**. A modelagem física da 0.2 deve sempre contar as quatro adicionais criadas nas migrações. O carrinho ativo é de **sessão assinada**, não das tabelas projetadas `carrinhos` e `carrinho_itens`.

## Matriz das 25 histórias

Consultar [Mapa_25_Historias.md](Mapa_25_Historias.md). O fato de uma função central existir não comprova todos os critérios não funcionais. A versão atual contém recursos centrais implementados e **recursos demonstrativos/parciais**, não uma afirmação de 25 histórias integralmente homologadas.

**Limitações incontornáveis ou pendentes:**
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

A modelagem final deverá ser reconferida com o código publicado. Documentos de interface são protótipos esquemáticos, não capturas de teste.

## Registro de contradições corrigidas neste ciclo

| Contradição anterior | Tratamento |
|---|---|
| README e manual referiam 0.5/0.6 como versão acadêmica atual | Referências atuais unificadas como **0.2 em desenvolvimento**; revisões anteriores preservadas no histórico Git |
| Mapa antigo declarava US-13/14 como não implementadas | Atualizado: agenda e combos existentes em nível demonstrativo/local |
| Alguns textos afirmavam “23 tabelas” | **23 no esquema-base; 27 depois das migrações v1–7** |
| Laudo e textos antigos usavam “27” ou “30 testes” | Números históricos; referência atual: **93 testes locais** |
| “Relatórios de vendas” poderiam soar como recebimento financeiro | Documentado: **valores de pedidos, sem comprovação de receita recebida** |
| Pagamento e notificações simuladas poderiam parecer integração externa | Diagramas, manual e documentos especificam explicitamente as fronteiras |
| Formulário oficial e laudo antigos pareceriam entrega final | Marcados como **artefatos históricos**, sujeitos a nova revisão após publicação |
| “Todas as histórias cumpridas” não seria sustentado por RNFs | Situações detalhadas por história e **aceitação integral não declarada** |

## Instruções PIT II: evidências e pendências

| Situação | Evidências atuais | Pendência |
|---|---|---|
| 1 — escopo, UML, IHC, dados | Matriz, modelos, dicionário e protótipos produzidos | Conferência final com telas/rotas do site publicado |
| 2 — código, Git, testes, manual, vídeo ≥5 minutos | Branch, teste local, manual atualizado e primeiro vídeo histórico | Homologação da branch, persistência pública, teste em navegador e eventual exigência do tutor sobre limites |
| 3 — cinco opiniões, correções, laudo e vídeo ≤5 minutos | Cinco registros em PDF preservados; melhorias e ciclos documentados | Novas evidências após publicação, laudo/formulário final e segundo vídeo compatível com a edição publicada |

**Não alterar os nomes, datas ou pareceres das cinco avaliações retroativamente.** Distinguir sempre melhoria motivada por avaliação de requisito faltante identificado pela revisão da PIT I.

## Critério para liberar publicação e entrega

- [ ] Verificar 25 histórias no site publicado, incluindo erros, permissões, estoque, agenda e pagamento demonstrativo.
- [ ] Inspecionar visualmente em navegador desktop e mobile.
- [ ] Medir ou declarar não comprovadas metas de latência e concorrência da PIT I.
- [ ] Verificar dados após reinício/redeploy no Render e licenças das fotos.
- [ ] Atualizar os DOCX/PDF definitivos, o formulário oficial, laudo, links dos vídeos e segundo vídeo.
- [ ] Não mesclar à `main` antes da homologação.

**Conclusão do Ciclo F:** documentação/modelagem de pré-homologação consolidada, com limitações evidentes. A entrega acadêmica final e o deploy público continuam pendentes; nenhum resultado não testado foi descrito como concluído.
