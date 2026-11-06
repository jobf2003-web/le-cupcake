# Checklist de entrega PIT II — versão 0.2

Este checklist acompanha a evolução da versão 0.1 para a versão 0.2, após as cinco avaliações e a revisão das 25 histórias da PIT I. A integração do código à `main` foi concluída; a confirmação da atualização do serviço no Render é etapa independente.

## Evidências técnicas já verificadas localmente
- [x] Trabalho original PIT I recuperado e 25 histórias registradas com critérios e limitações.
- [x] Código desenvolvido em branch isolada e integrado à `main`, com preservação do histórico da 0.1.
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
- [x] Formulário oficial sincronizado e relatório de atualização do sistema corrigido na `main`, com 93 testes de referência e histórico preservado.
- [ ] Inserir o link real do segundo vídeo e reunir evidências da aplicação publicada depois da confirmação do Render.
- [x] Integrar a versão 0.2 consolidada à `main` após os testes locais.
- [ ] Verificar se o Render implantou o commit atual da `main`, testando as rotas públicas sem expor dados pessoais.
- [ ] Gravar o segundo vídeo (até cinco minutos) demonstrando mudanças efetivas, mantendo o primeiro vídeo intacto.
- [ ] Verificar os dois links de vídeo e a entrega exigida no AVA.

## Instruções consultadas
**Situação 1:** revisão de escopo, UML, IHC, modelos conceitual/lógico/físico e dicionário. **Situação 2:** front-end/back-end, Git, testes, manual e apresentação narrada ≥5 minutos. **Situação 3:** cinco avaliações com nome/data/êxitos/falhas/não testados em PDF, laudo, evidências, correções e vídeo de atualização ≤5 minutos.

Não modificar retrospectivamente textos/datas dos avaliadores nem descrever a versão 0.2 como existente antes das avaliações e da revisão das 25 histórias.
