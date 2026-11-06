# Mapa das 25 histórias — versão 0.2 publicada

**Fonte:** documento original da PIT I, com 25 histórias. **Situação:** código dos Ciclos A–F integrado à `main` e publicado no Render, após as cinco avaliações e a revisão da PIT I.

**Importante:** nenhuma história foi declarada 100% homologada em todos os requisitos não funcionais. `Núcleo disponível` é fluxo central implementado/testado localmente; `demonstrativo` não é integração real; `parcial` possui requisitos faltantes; `não implementado` implica ausência de integração externa.

| História | Descrição | Situação e limites |
|---|---|---|
| US-01 | Catálogo, imagens e estoque | Núcleo disponível; desempenho externo não comprovado |
| US-02 | Filtros dinâmicos | Núcleo disponível; tempo de resposta no Render não medido |
| US-03 | Carrinho | Núcleo disponível; RNF não medido |
| US-04 | Frete e total | Demonstrativo, taxa por CEP; sem transportadora |
| US-05 | Recebimento | Demonstrativo, entrega e retirada; sem logística real |
| US-06 | Acompanhar pedido | Parcial, polling 15 s; não push |
| US-07 | Conta de cliente | Parcial, reset depende de SMTP externo |
| US-08 | Recomendações | Núcleo por histórico; RNF não medido |
| US-09 | Promoções e cupons | Núcleo disponível; RNF não medido |
| US-10 | Avaliações | Núcleo disponível; moderação com autenticação e testes HTTP |
| US-11 | Avisos a clientes | Parcial, só notificações internas |
| US-12 | Meios de pagamento | Apenas simulação interna, sem transações reais |
| US-13 | Agendamento | Demonstrativo, sem logística real |
| US-14 | Combos | Núcleo disponível, estoque validado localmente |
| US-15 | Nutrição/alergênicos | Parcial, dados reais não verificados |
| US-16 | Cadastrar produtos | Núcleo disponível; sem certificação formal de desempenho |
| US-17 | Editar e excluir produtos | Núcleo disponível, arquivamento lógico; sem certificação formal de desempenho |
| US-18 | Relatórios | Núcleo demonstrativo, pedidos não receita recebida |
| US-19 | Gestão em tempo real | Parcial, polling sem push nem carga comprovada |
| US-20 | Gerenciar promoções | Núcleo disponível; sem certificação formal de desempenho |
| US-21 | Avisos a administradores | Parcial, só notificações internas |
| US-22 | Contas de clientes no admin | Núcleo disponível; sem certificação formal de desempenho |
| US-23 | Respostas a avaliações | Núcleo disponível; resposta e moderação administrativa disponíveis |
| US-24 | Configurar entrega/retirada | Demonstrativo, sem logística real |
| US-25 | Gateway online | Não implementado externamente |

**Contexto:** o primeiro vídeo representa a 0.1; as cinco avaliações foram mantidas. A revisão das 25 histórias identificou requisitos adicionais posteriormente implementados na 0.2; não atribuir essas lacunas retroativamente aos avaliadores.

**Evidência local:** 93 testes aprovados; SQLite com 27 tabelas, 173 colunas, 34 FKs e migração v7. O Render confirmou a publicação da versão 0.2. O escopo dos 93 testes automatizados não inclui ensaios de carga, certificação em dispositivos físicos nem garantia de persistência em hospedagem gratuita.

**Restrições:** não existe pagamento real nem gateway (US-12/25), e-mail/SMS de pedido (US-11/21), logística contratada (US-04/05/13/24); a recuperação de senha depende de SMTP configurado (US-07). Consulta de pedidos é por polling 15 s (US-06/19), não push.

A referência técnica do desenvolvimento da versão 0.2 é a documentação do [Ciclo F](Ciclo_F_Auditoria_Consolidada_v02.md). Os arquivos oficiais de entrega refletem a versão 0.2, com 27 tabelas no banco migrado, 93 testes locais de referência e limites do protótipo declarados.
