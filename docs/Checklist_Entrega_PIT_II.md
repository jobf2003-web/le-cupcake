# Checklist de entrega PIT II — versão 0.2

Este checklist acompanha a evolução da versão 0.1 para a versão 0.2, após as cinco avaliações e a revisão das 25 histórias da PIT I. A versão 0.2 foi integrada à `main` e sua implantação ativa foi confirmada no Render.

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
- [x] **RNFs:** testes formais de carga e latência não integram as 93 verificações locais.

## Registro de entrega e funcionamento

- [x] Código da versão 0.2 integrado à `main`, com preservação do histórico da versão 0.1.
- [x] Implantação ativa da versão 0.2 no serviço `le-cupcake` no Render.
- [x] Documentação UML, modelos de dados, dicionário e manual reunidos no repositório.
- [x] Cinco avaliações originais preservadas e laudo de qualidade preparado.
- [x] Primeiro vídeo vinculado à versão inicial 0.1; segundo vídeo da 0.2 disponibilizado em https://drive.google.com/file/d/1t3OihMjUK0ExYL8F4_LVbNIh55u8stNu/view?usp=sharing.
- [x] Suíte de regressão da versão 0.2: 93 testes automatizados locais aprovados.

Os critérios de desempenho em grande escala, persistência de armazenamento no plano gratuito, envio externo de notificações e pagamento bancário são limites declarados do protótipo, não serviços demonstrados como integrados.

## Instruções consultadas
**Situação 1:** revisão de escopo, UML, IHC, modelos conceitual/lógico/físico e dicionário. **Situação 2:** front-end/back-end, Git, testes, manual e apresentação narrada ≥5 minutos. **Situação 3:** cinco avaliações com nome/data/êxitos/falhas/não testados em PDF, laudo, evidências, correções e vídeo de atualização ≤5 minutos.

Não modificar retrospectivamente textos/datas dos avaliadores nem descrever a versão 0.2 como existente antes das avaliações e da revisão das 25 histórias.
