# Modelagem da versão 0.2 — Le Cupcake

Modelos de **pré-homologação**, extraídos do código e do esquema SQLite migrado. Eles **não representam a versão 0.1 inicial** e não devem ser associados retroativamente ao primeiro vídeo.

1. [Casos de uso e fronteira demonstrativa](01_Casos_de_uso.md)
2. [Classes de domínio](02_Classes_de_dominio.md)
3. [Sequência do checkout e simulador](03_Sequencia_checkout.md)
4. [Sequência da atualização de status e avisos internos](04_Sequencia_status.md)
5. [Atividades do pedido](05_Atividades_pedido.md)
6. [Modelo conceitual](06_Modelo_conceitual.md)
7. [Modelo físico/lógico, 27 tabelas](07_Modelo_logico_fisico.md)
8. [IHC/protótipos esquemáticos](08_Prototipos_IHC.md)

Os diagramas são mantidos como **texto-fonte Mermaid editável** e renderizados pelo GitHub. Há PNG e fontes DOT adicionais no pacote acadêmico do Ciclo F. Os 173 campos, 34 FKs, índices e tipos reais devem ser lidos no dicionário extraído do banco, disponível junto da documentação consolidada. `schema.sql` define 23 tabelas-base; `migrations.py` leva à versão física 7, total de 27.

**Limites explícitos:** pagamentos são simulações locais; mensagens de pedidos são internas (`canal=app`); a atualização do status usa polling de 15 segundos; logística é fictícia; recuperação por e-mail depende de SMTP. O código não possui gateway real integrado.
