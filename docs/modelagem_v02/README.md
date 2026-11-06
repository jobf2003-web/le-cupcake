# Modelagem da versão 0.2 — Le Cupcake

Estes modelos descrevem as estruturas e os fluxos da versão 0.2 publicada. O primeiro vídeo registra a implementação inicial 0.1.

1. [Casos de uso e fronteira demonstrativa](01%20-%20Casos%20de%20uso.md)
2. [Classes de domínio](02%20-%20Classes%20de%20dominio.md)
3. [Sequência do checkout e simulador](03%20-%20Sequencia%20do%20checkout.md)
4. [Sequência da atualização de status e avisos internos](04%20-%20Sequencia%20de%20status.md)
5. [Atividades do pedido](05%20-%20Atividades%20do%20pedido.md)
6. [Modelo conceitual](06%20-%20Modelo%20conceitual.md)
7. [Modelo físico/lógico, 27 tabelas](07%20-%20Modelo%20logico%20e%20fisico.md)
8. [IHC/protótipos esquemáticos](08%20-%20Prototipos%20de%20interface.md)

Os diagramas são mantidos como **texto-fonte Mermaid editável** e renderizados pelo GitHub. Há PNG e fontes DOT adicionais no pacote acadêmico do Ciclo F. O dicionário de dados complementa os diagramas com os tipos, atributos e relações do banco SQLite migrado. `schema.sql` define 23 tabelas-base; `migrations.py` leva à versão física 7, total de 27.

**Escopo do protótipo:** pagamentos demonstrativos, mensagens internas (`canal=app`), atualização de status por consultas periódicas, logística simulada e recuperação por e-mail condicionada à configuração de SMTP.
