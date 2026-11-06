# Ciclo C — Contas, promoções e informações dos produtos

O Ciclo C deu continuidade à versão 0.2 com melhorias para clientes e informações de catálogo.

## Desenvolvimento

A recuperação de conta recebeu formulários próprios e tokens temporários de uso único, armazenados de forma protegida. A troca de senha invalida links anteriores e sessões antigas. O envio do link por e-mail depende da configuração de um servidor SMTP; os testes locais utilizaram um adaptador de simulação.

As recomendações passaram a considerar as categorias presentes no histórico de pedidos do cliente autenticado. Os cupons receberam regras de validade e exibição das promoções ativas. O cadastro de produtos passou a contemplar ingredientes e alergênicos, com alertas nas páginas de produto quando essas informações estiverem disponíveis.

A quinta migração criou `password_reset_tokens` e acrescentou campos de sessão e ingredientes. O esquema chegou a 26 tabelas.

## Verificação

Foram registrados **69 testes automatizados aprovados**, incluindo nove novos casos de autenticação, tokens, recomendações e promoções.

## Resultado na versão 0.2

Os recursos integram a versão publicada. As recomendações utilizam categorias de compras anteriores e não um serviço externo de personalização. Os dados nutricionais dependem das informações cadastradas, sem certificação alimentar. O envio de recuperação por e-mail requer a infraestrutura SMTP correspondente.
