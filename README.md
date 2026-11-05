# Le Cupcake — Projeto Integrador Transdisciplinar em Engenharia de Software II

**Versão 0.2 em desenvolvimento, ainda não publicada no Render.** O repositório `main` e o primeiro vídeo mostram a implementação anterior. A branch `pit-ii-25-historias-completas` contém a evolução posterior às cinco avaliações e à revisão integral das 25 histórias da PIT I.

O projeto é uma **loja virtual fictícia**, sem processamento de pagamentos reais, entregas físicas, serviço de SMS/e-mail para andamento de pedidos ou garantias de persistência em hospedagem gratuita. Não use dados pessoais verdadeiros no protótipo.

## Evolução verificável

1. **0.1 — primeiro vídeo:** implementação inicial da loja, antes da ampliação.
2. **Cinco avaliações e revisão do backlog da PIT I:** foram preservadas as avaliações históricas; as lacunas descobertas na revisão dos requisitos não são apresentadas como sugestões que os avaliadores teriam feito.
3. **0.2 — Ciclos A–E:** atualização incremental do site com filtros dinâmicos, migrações, gestão de produtos, CEP e agenda demonstrativos, combos, relacionamento, mensagens internas e pagamentos simulados.
4. **Ciclo F:** consolidação da documentação, dicionário de dados, diagramas e auditoria; **homologação pública e vídeo final ainda pendentes**.

## Funções disponíveis no código da branch 0.2

- **Vitrine:** catálogo com disponibilidade, busca e filtros dinâmicos, produtos e promoções.
- **Compra:** carrinho, combos com controle de estoque, cupom, cálculo local de taxa por faixas de CEP, entrega/retirada e agendamento demonstrativo em até 15 dias.
- **Pagamento:** escolha entre `PIX demonstrativo`, `cartão demonstrativo` e `a combinar`. Aprovação/recusa são fictícias e idempotentes; **não são cobranças nem estornos reais**.
- **Cliente:** cadastro, login, pedidos e recuperação por token com envio apenas se SMTP/HTTPS estiver realmente configurado; recomendações por categorias do histórico; avaliações moderadas; notificações **internas**.
- **Administração:** produtos, arquivamento e auditoria, pedidos e estados, cupons, horários e regiões, contas de clientes e relatórios. Os valores exibidos são valores de pedidos, **não receita financeira recebida**.
- **Acompanhamento:** status consultado automaticamente a cada 15 segundos, **não** push em tempo real.

**Ressalvas da PIT I:** nem todos os critérios de aceitação e metas não funcionais foram comprovados. US-11 e US-21 não enviam SMS/e-mail; US-12 é demonstrativa; **US-25 não possui gateway real integrado**. Consultar o [mapa atualizado de 25 histórias](docs/Mapa_25_Historias.md) e o [relatório do Ciclo F](docs/Ciclo_F_Auditoria_Consolidada_v02.md).

## Tecnologias e arquitetura

Python 3.11+, FastAPI, Jinja2, HTML, CSS, JavaScript, SQLite, Pytest/HTTPX. A organização atual é incremental por serviços; **não é MVC formal completo**. `schema.sql` define **23 tabelas-base**; `migrations.py` aplica versões 1–7, totalizando **27 tabelas, 173 colunas e 34 chaves estrangeiras** no banco migrado. O carrinho operacional é guardado em **sessão assinada**; as tabelas projetadas `carrinhos`/`carrinho_itens` não equivalem a um carrinho persistente em uso.

## Executar localmente

1. Instale Python 3.11 ou mais recente.
2. Instale as dependências: `python -m pip install -r requirements.txt`.
3. Inicie: `python iniciar.py` ou `INICIAR_WINDOWS.bat` no Windows.
4. Acesse `http://127.0.0.1:8000`.
5. Para criar administrador, configure `ADMIN_EMAIL` e `ADMIN_PASSWORD` (12+ caracteres), sem incluir credenciais no GitHub.

Banco local de teste em `instance/cupcakes.db`; nunca publique esse banco, `.env`, `.local_secret` ou dados de clientes. No Render gratuito, a persistência do SQLite **não está garantida** sem volume persistente configurado.

## Testes e verificações

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

A cópia local do Ciclo E passou em **93 testes automatizados**; a checagem de estrutura do Ciclo F encontrou `PRAGMA user_version=7`, 27 tabelas, 173 campos e 34 FKs sem violações na base de teste. Os testes **não** substituem inspeção visual em navegadores reais, ensaios de desempenho/carga, homologação do site publicado, entrega efetiva de SMS/e-mail ou gateway de pagamento.

## Documentação e entrega

- [Matriz original das 25 histórias](docs/Matriz_Rastreabilidade_PIT_I_25_Historias.md).
- [Mapa atualizado, com limites explícitos](docs/Mapa_25_Historias.md).
- [Auditoria e modelagem — Ciclo F](docs/Ciclo_F_Auditoria_Consolidada_v02.md).
- [Manual atualizado](docs/Manual_de_Uso.md).
- [Testes técnicos](docs/Testes_Tecnicos.md).
- [Checklist real de homologação](docs/Checklist_Entrega_PIT_II.md).
- [Cinco avaliações históricas em PDF](docs/Cinco_Fichas_Avaliacao_ABNT.pdf), mantidas sem alteração.
- **Laudo de qualidade da versão 0.2:** preparar o documento atualizado a partir da implementação e dos testes da branch, incluindo as evidências locais e os limites reais. A publicação do DOCX/PDF definitivo no repositório ainda está pendente.
- **Formulário oficial da PIT II:** atualizar os campos técnicos para a versão 0.2, manter as cinco avaliações intactas e inserir o segundo vídeo após a sua gravação.
- [Fontes das fotografias](docs/Referencias_Fotograficas_Simplificadas.docx). A publicação deve observar atribuições CC BY/CC BY-SA.

**Link atual do site público (versão anterior):** https://le-cupcake.onrender.com/. **Não confundir com a branch de desenvolvimento.**

**Primeiro vídeo:** mantido como demonstração inicial, sem regravação. **Segundo vídeo:** deverá representar a versão 0.2 após publicação e testes, com limites do plano gratuito explicitados. Não afirmar que os registros de avaliações foram alterados.

## Segurança e alcance

O projeto é acadêmico; não processa pagamentos ou cartões, não provê logística real e não garante persistência após reinício na hospedagem gratuita. Os testes de carga de 500/1.000 operações concorrentes e as metas de latência da PIT I **não foram comprovados**. A declaração de atendimento integral depende da aceitação acadêmica dos limites, dos testes manuais e da homologação final.
