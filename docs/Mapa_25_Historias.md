# Verificação das 25 histórias de usuário — Le Cupcake, versão 0.5

**Fonte de requisitos:** Projeto Integrador Transdisciplinar em Engenharia de Software I, loja virtual de cupcakes. O mapeamento abaixo avalia **o que o código executa**, não substitui uma avaliação final de todos os critérios de aceitação nem representa dispensa autorizada pela universidade.

**Legenda:** Implementada = fluxo básico funcional; Parcial = só parte dos critérios originais atendidos; Pendente = não construído.

| ID | História original resumida | Situação na v0.5 | Observação concreta |
|---|---|---|---|
| 1 | Visualizar cardápio com imagens e descrições | Parcial | Catálogo apresenta fotografias reais documentadas, mas critérios de desempenho ainda carecem de avaliação em hospedagem. |
| 2 | Filtrar cupcakes por sabor e categoria | Implementada | Busca por texto e filtros por categoria. |
| 3 | Adicionar cupcakes ao carrinho | Implementada | Adição, remoção e atualização com validação de estoque. |
| 4 | Ver total com frete incluso | Implementada | Frete, descontos e total recalculados no servidor no checkout. |
| 5 | Selecionar forma de recebimento | Parcial | Retirada ou entrega com taxas configuráveis; não há logística real. |
| 6 | Acompanhar status do pedido | Parcial | Link privado e pedidos vinculados à conta; sem notificação automática. |
| 7 | Criar conta para salvar pedidos | Implementada | Registro, autenticação por senha protegida e histórico de pedidos vinculados à conta. Ainda não há recuperação de senha. |
| 8 | Receber recomendações | Parcial | Recomendações por categoria na página do produto; não há recomendação por histórico. |
| 9 | Acessar promoções e cupons | Parcial | Cupom informado no checkout; ainda não há página pública listando promoções. |
| 10 | Deixar avaliações e comentários | Parcial | Avaliação autenticada de 1 a 5 estrelas, comentário e moderação; sem verificação de compra efetuada. |
| 11 | Receber notificações de andamento | Pendente | Não envia SMS nem e-mail; consulta de status é manual. |
| 12 | Escolher forma de pagamento | Pendente | A combinar; não há seleção de métodos nem cobrança. |
| 13 | Agendar entrega | Pendente | Sem calendário e reserva de datas. |
| 14 | Montar combos personalizados | Pendente | Ainda sem editor de combos. |
| 15 | Visualizar informações nutricionais | Parcial | Campo editável pelo administrador e exibição condicional; dados reais não foram fornecidos. |
| 16 | Cadastrar novos sabores | Implementada | Cadastro pelo painel, com fotografia da biblioteca documentada. |
| 17 | Editar ou remover cupcakes | Parcial | Editar/ocultar/reativar; não há exclusão definitiva. |
| 18 | Visualizar relatórios de vendas | Parcial | Resumo de pedidos, totais, descontos e produtos mais pedidos; **não mede receita recebida**. |
| 19 | Gerenciar pedidos em tempo real | Parcial | Listagem e avanço manual de status, não atualização automática/push. |
| 20 | Configurar promoções e cupons | Implementada | Criar, ativar/desativar, percentual/valor fixo, subtotal mínimo e limite de usos. |
| 21 | Receber notificações de novos pedidos | Pendente | Apenas consulta ao painel administrativo. |
| 22 | Gerenciar contas de clientes | Parcial | Listagem e bloqueio/reativação; ainda sem edição e recuperação de senha. |
| 23 | Responder avaliações de clientes | Implementada | Resposta via painel, após moderação; texto escapado na visualização. |
| 24 | Configurar opções de entrega e retirada | Parcial | Edita descrição, custo e disponibilidade das opções cadastradas; não define regiões nem horários. |
| 25 | Integrar sistemas de pagamento online | Pendente | Não há gateway, pagamento ou transação financeira real. |

## Testes e limitações

Os testes em `tests/` cobrem catálogo, carrinho, estoque, pedidos, registro, login, cupom, avaliações, moderação, administração, relatórios, segurança básica de formulários e limites de acesso. Executar `python -m pytest -q` para obter a quantidade atual de testes aprovados; **não confundir** testes automáticos com os cinco testes por pessoas reais exigidos pela universidade.

Antes da publicação pública, ainda são necessários revisão de segurança e privacidade, persistência confiável, recuperação de senha, tratamento de dados pessoais e licenciamento adequado das fotografias. Estas fotos mantêm suas referências no arquivo Word separado `docs/Referencias_Fotograficas_Simplificadas.docx`.
