# Le Cupcake — PIT II · Etapa 2 · Ciclo C: cliente, promoções e dados de produtos

**Status:** implementado e aprovado nos testes automáticos locais; **não publicado** no site público. Este trabalho complementa os Ciclos A e B na branch `pit-ii-25-historias-completas`, prosseguindo com a **implementação da versão 0.2**, de acordo com a sequência histórica pactuada: **versão inicial 0.1 → cinco avaliações + revisão da PIT I → desenvolvimento da versão 0.2**. Os registros dos avaliadores não foram alterados. As funcionalidades listadas abaixo não existiam integralmente na versão inicial e não devem ser apresentadas retroativamente como existentes na 0.1.

## Implementações verificadas

| História | Implementação neste ciclo | Evidência e limites |
|---|---|---|
| US-07 — recuperação de senha | Interface de solicitação, token aleatório de uso único armazenado somente como SHA-256, prazo de 30 minutos, limite de três solicitações por conta em 15 minutos, troca de senha com PBKDF2, invalidação de outros links e de sessões anteriores à troca. Sem revelar se e-mail existe. | Testes de uso único, expiração, CSRF, acesso antigo revogado e resposta indistinguível. **E-mail real exige SMTP configurado**, com `PUBLIC_BASE_URL` HTTPS, `SMTP_HOST` e `SMTP_FROM`; nenhum envio real foi executado no plano gratuito. Sem configuração, a interface informa a indisponibilidade e o servidor devolve 503. Teste SMTP usa adaptador simulado, não comprova entrega externa. |
| US-08 — recomendações por histórico | Na página inicial, após pedidos de usuário autenticado, sugestões ordenadas pelas categorias dos itens comprados, inclusive componentes de combos. Exclui produtos indisponíveis e tenta mostrar três opções quando houver estoque. | Testes com pedidos comuns, compras de combos e estoque zerado. Sem compras, não afirma ter personalização nem exibe sugestão falsamente personalizada. Técnica é preferência por categoria, **não recomendação avançada**. |
| US-09/20 — promoções | Administrador define datas de validade dos novos cupons; vitrine mostra os cupons realmente válidos, ativos e com saldo de usos. O checkout já validava limites e desconto do lado do servidor. | Teste de período válido, expirado e datas invertidas. Expiração é efetiva na consulta (filtragem); a flag `ativo` não precisa ser modificada automaticamente para excluir o cupom vencido. Sem integração externa de marketing. |
| US-15 — ingredientes e alergênicos | Administrador informa ingredientes, texto nutricional e marca alergênicos da receita em relação específica; o cliente vê alerta quando há alergênicos cadastrados. Sem dados confirmados, a página informa explicitamente que as informações **não foram verificadas**. | Teste de tela, gravação relacional, auditoria, IDs inválidos e preservação em migração. **Não foram inventadas informações sobre receitas, calorias ou segurança alimentar**. A verificação dos dados reais continua pendente. |

## Banco e rastreabilidade

A migração SQLite nº **5**, aplicada após as migrações anteriores e preservando pedidos e usuários, cria `password_reset_tokens`, adiciona `usuarios.sessao_versao` e `cupcakes.ingredientes`. As tabelas de alergênicos e seus relacionamentos já existiam, mas agora possuem telas e fluxos de cadastro. Há **26 tabelas de aplicação** após a migração. O código registra alterações de alergênicos na auditoria administrativa.

As novas entidades/atributos deverão ser refletidos nos diagramas de classes, sequência de redefinição, casos de uso de cliente e modelo físico/dicionário de dados da documentação final da **0.2**. Não foram alterados os diagramas históricos neste ciclo.

## Resultado dos testes

- Suíte total: **69 testes automatizados aprovados** em ambiente local (60 do ciclo anterior + nove novos testes sobre relacionamento/segurança e promoções).
- Executado com `python -m pytest -q`; sem servidor SMTP real, teste de carga, navegador físico ou garantia da persistência do banco no Render.
- Testes de e-mail apenas com adaptador simulado e garantias locais de proteção de tokens; **não representam envio de e-mail externo comprovado**.

## Próximos itens e ressalvas

1. Registrar testes reais de envio por e-mail se um serviço SMTP viável estiver disponível; caso contrário, US-07 continuará **parcial na integração externa**.
2. Validar interface em navegadores reais, acessibilidade, latências e comportamento com base de dados persistente.
3. Reavaliar US-08 contra critérios completos da PIT I (frequência/atualização e desempenho); US-15 depende de conteúdo nutricional confiável.
4. Prosseguir com notificações ao cliente e administração, relatórios, contas administrativas e, por último, fluxos de pagamento demonstrativos/sandbox, todos com as limitações corretamente identificadas.
5. Reunir a modelagem final e o laudo **após** implementar os demais ciclos, mantendo claro o histórico de evolução da 0.1 para a 0.2.

**Integridade:** o primeiro vídeo, as avaliações já entregues, a `main` e a aplicação pública não são modificados neste ciclo.
