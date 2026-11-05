# Checklist de homologação PIT II — versão 0.2 consolidada (pré-publicação)

Este checklist acompanha a evolução da versão 0.1 para a versão 0.2, após as cinco avaliações e a revisão das 25 histórias da PIT I. Não é autorização para publicar a branch.

## Evidências técnicas já verificadas localmente
- [x] Trabalho original PIT I recuperado e 25 histórias registradas com critérios e limitações.
- [x] Código evoluiu em branch isolada, sem alteração da `main`.
- [x] Modelo do banco: 23 tabelas iniciais + migrações 1–7 = **27 tabelas, 173 campos, 34 FKs**.
- [x] **93 testes automatizados** aprovados na cópia local do Ciclo E.
- [x] Fluxos internos de frete, agendamento, combos, recuperação por token, avisos internos e pagamentos simulados testados localmente.
- [x] Cinco avaliações históricas em PDF preservadas (orientação do tutor quanto ao uso informada pelo responsável).
- [x] Ciclo F: documentação, modelo conceitual, UML, esquemas físicos, dicionário e relatório de contradições preparados.

## Limitações que devem constar nas entregas
- [x] **US-12:** demonstração de pagamento, sem cobrança real.
- [x] **US-25:** nenhum gateway externo integrado — não considerar atendida.
- [x] **US-11/US-21:** notificações internas, não SMS/e-mail entregues.
- [x] **US-07:** SMTP não configurado/entrega externa não comprovada.
- [x] **US-06/US-19:** atualização por consulta de 15 s, sem push.
- [x] **US-04/05/13/24:** entrega/CEP/agendamento interno demonstrativo, sem logística contratada.
- [x] **US-15:** dados nutricionais reais não certificados; não inventar informações.
- [x] **RNFs:** tempos de resposta e concorrência ainda não medidos.

## Pendente antes de declarar a entrega final
- [ ] Testar a interface em navegador desktop e mobile, incluindo erros, formulários e acessibilidade.
- [ ] Verificar carga/latência conforme ambiente e critérios da PIT I, registrar metas não comprovadas.
- [ ] Homologar a persistência SQLite no Render e não expor dados pessoais reais.
- [ ] Conferir créditos/licenças das fotografias na página publicada.
- [ ] Aprovar ou registrar com tutor as limitações incontornáveis do plano gratuito.
- [ ] Substituir os arquivos oficiais desatualizados pelos documentos corrigidos da versão 0.2, mantendo as avaliações e o primeiro vídeo inalterados; após a publicação, atualizar links e evidências definitivas.
- [ ] Publicar a versão 0.2 consolidada na `main` e no Render **somente após aprovação de teste**.
- [ ] Gravar o segundo vídeo (até cinco minutos) demonstrando mudanças efetivas, mantendo o primeiro vídeo intacto.
- [ ] Verificar os dois links de vídeo e a entrega exigida no AVA.

## Instruções consultadas
**Situação 1:** revisão de escopo, UML, IHC, modelos conceitual/lógico/físico e dicionário. **Situação 2:** front-end/back-end, Git, testes, manual e apresentação narrada ≥5 minutos. **Situação 3:** cinco avaliações com nome/data/êxitos/falhas/não testados em PDF, laudo, evidências, correções e vídeo de atualização ≤5 minutos.

Não modificar retrospectivamente textos/datas dos avaliadores nem descrever a versão 0.2 como existente antes das avaliações e da revisão das 25 histórias.
