# Ciclo F — Documentação e verificação da versão 0.2

O Ciclo F reuniu a documentação técnica produzida para a versão 0.2 da Le Cupcake. A sequência de desenvolvimento foi a implementação inicial 0.1, as cinco avaliações, a revisão das 25 histórias da PIT I e os ciclos A, A.2, B, C, D e E.

## Documentação consolidada

Foram revisados o mapeamento das histórias de usuário, os casos de uso, a modelagem de classes, os diagramas de sequência e atividades, os protótipos de interface e os modelos conceitual, lógico e físico do banco. O dicionário de dados registra o esquema SQLite após sete migrações, com **27 tabelas, 173 colunas, 34 relações de chave estrangeira e 20 índices nomeados**.

A documentação da versão 0.2 registra também os recursos disponibilizados no site, os resultados dos testes e as restrições dos serviços demonstrativos.

## Verificação

A execução local da suíte automatizada encerrou com **93 testes aprovados**. Foram abrangidos catálogo, carrinho, pedidos, estoque, cadastro, autenticação, administração, agenda, combos, avisos internos e pagamento demonstrativo. A suíte não é um ensaio formal de carga ou certificação de integrações externas.

## Publicação e evidências

O código dos ciclos foi integrado à branch `main` do repositório e publicado em https://le-cupcake.onrender.com/. O primeiro vídeo registra a versão 0.1. O segundo apresenta as alterações da versão 0.2: https://drive.google.com/file/d/1t3OihMjUK0ExYL8F4_LVbNIh55u8stNu/view?usp=sharing.

As cinco fichas de avaliação foram preservadas. As mudanças decorrentes da análise de usabilidade e as funcionalidades incluídas após a revisão dos requisitos foram descritas separadamente. Pagamentos bancários, logística comercial e notificações externas não fazem parte do funcionamento apresentado.
