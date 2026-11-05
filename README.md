# Le Cupcake — loja virtual de cupcakes (PIT II)

**Versão:** 0.2 — protótipo acadêmico funcional ampliado. A marca e os produtos são **fictícios**. O sistema **não cobra pagamentos reais** nem envia e-mails/SMS.

O aplicativo dá continuidade ao planejamento da loja de cupcakes apresentado na disciplina **Projeto Integrador Transdisciplinar em Engenharia de Software I**. Não implementa as 25 histórias originais na íntegra; veja o mapeamento em [`docs/Mapa_25_Historias.md`](docs/Mapa_25_Historias.md).

## Melhorias de usabilidade — versão 0.2 (04/11/2026)

Após revisar as áreas não cobertas pelas fichas de verificação, foram incorporadas melhorias preventivas, sem alterar o visual principal: atalho de teclado para acessar o conteúdo, foco em mensagens de erro, orientação dinâmica entre entrega e retirada, valores estimados anunciados a tecnologias assistivas, tratamento de fotografias externas indisponíveis, pequenos ajustes para telas estreitas e respeito à preferência por movimento reduzido.

**Verificação técnica:** 30 testes técnicos aprovados (27 originais + 3 novos). Também foram conferidos os fluxos principais de checkout e as larguras de 390 px e 320 px em Chromium local com HTML renderizado pela aplicação; nesses cenários, não houve rolagem horizontal. As fotografias originais permanecem inalteradas quando carregam corretamente.

As alterações da versão 0.2 foram registradas como melhorias de usabilidade e verificadas por testes técnicos.

**Aplicação hospedada:** [https://le-cupcake.onrender.com/](https://le-cupcake.onrender.com/)

## Como executar no Windows (caminho mais fácil)

1. Descompacte o ZIP em uma pasta do computador. Não execute diretamente dentro do ZIP.
2. Instale **Python 3.11 ou mais recente** de [python.org](https://www.python.org/downloads/) e marque a opção de adicionar Python ao PATH, se aparecer.
3. Dê dois cliques em **`INICIAR_WINDOWS.bat`**. Na primeira execução, será necessário ter internet para instalar as bibliotecas.
4. Abra o navegador e acesse **http://127.0.0.1:8000**.
5. Para habilitar o painel administrativo, interrompa o servidor (`Ctrl+C`), abra o arquivo `.env` (será criado no primeiro início) e preencha `ADMIN_EMAIL` e `ADMIN_PASSWORD` com uma senha exclusiva de **pelo menos 12 caracteres**. Inicie o programa novamente e use **Área administrativa**.

> Se o Windows não encontrar `py`, abra o Prompt de Comando na pasta, execute `python -m venv .venv` e depois `.venv\Scripts\python -m pip install -r requirements.txt`. Por fim, use `.venv\Scripts\python iniciar.py`.

## Execução manual (Windows, macOS ou Linux)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
python -m pip install -r requirements.txt
python iniciar.py
```

O aplicativo armazena os registros em **`instance/cupcakes.db`** e inicia com oito cupcakes de exemplo. O banco é criado automaticamente na primeira execução. **Não envie seu banco com dados pessoais para repositórios públicos.**

### Área administrativa

Para criar o primeiro usuário administrador, configure no `.env`:

```text
ADMIN_EMAIL=seu-email-de-teste@exemplo.com
ADMIN_PASSWORD=uma-senha-exclusiva-com-12-ou-mais-caracteres
```

O usuário é criado automaticamente quando o aplicativo inicia. Por segurança, o projeto **não tem senha padrão**. Se um administrador já tiver sido criado, alterar a variável `ADMIN_PASSWORD` não redefine sua senha anterior.

## O que funciona nesta versão

- Catálogo público com oito produtos fictícios e categorias;
- busca por produto/descrição e filtro por categoria;
- página de detalhes, carrinho, alteração de quantidade e remoção;
- retirada ou entrega fictícia com taxa fixa e endereço obrigatório;
- cadastro de pedido com cálculo no servidor, número de pedido, link privado aleatório e redução automática do estoque;
- painel administrativo com autenticação, cadastro/edição/ocultação de cupcakes;
- consulta e atualização do status de pedidos e restauração do estoque após cancelamento;
- páginas responsivas, validações no servidor e tokens CSRF nos formulários.

**Novidades da 0.5:** cadastro e login de clientes (senha protegida), página de pedidos da conta, avaliações com moderação e respostas do administrador, cupons de desconto com regras e desconto calculado no servidor, relatório de pedidos, configuração administrativa de entrega e campo opcional de informações nutricionais verificadas. A página do produto também mostra sugestões da mesma categoria.

**Não funciona ainda:** pagamentos on-line, recuperação de senha por e-mail, disparo de e-mails/SMS, combos personalizados, agendamento de entregas, análise de receita recebida, avaliações verificadas por compra e recomendações personalizadas pelo histórico. Recursos parciais e pendentes estão no mapa das 25 histórias. Os dados de entrega exibidos são exemplos, não uma oferta real de logística.

## Tecnologias

- **Python + FastAPI** para a aplicação web e as regras do servidor;
- **Jinja2, HTML, CSS e JavaScript** para as telas;
- **SQLite** para armazenamento inicial, com o esquema de 23 tabelas proposto no planejamento (nem todas utilizadas nesta versão);
- **Pytest + HTTPX** para os testes técnicos.

O material da disciplina sugere MVC e linguagens como Python, Java ou PHP. Nesta implementação, as funções são separadas logicamente por responsabilidades e a interface fica isolada em templates; uma migração futura para uma organização completa em camadas é recomendável antes da versão final.

## Testes técnicos

Instale também o arquivo de dependências de desenvolvimento e execute:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Os testes técnicos incluem as verificações anteriores e também os novos cenários de acessibilidade, navegação e orientação de entrega da versão 0.2. Isso **não substitui** os **cinco testes com pessoas reais** exigidos pela universidade. Há um modelo para os registros humanos em `docs/Modelo_Avaliacao_5_Usuarios.md`.

## Publicação no GitHub e hospedagem

1. Crie um repositório para o projeto e envie **os arquivos da pasta**; não envie `instance/cupcakes.db`, `.env`, senhas ou dados reais.
2. O GitHub publica código, mas **não executa este back-end Python automaticamente**. A loja precisa de um serviço de hospedagem Python para funcionar num link público.
3. No provedor escolhido, instale `requirements.txt`, configure `SECRET_KEY`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` e `COOKIE_SECURE=1` com HTTPS; comando de início: `uvicorn app:app --host 0.0.0.0 --port $PORT` (quando o provedor definir `PORT`).
4. **Atenção ao SQLite:** ambientes de hospedagem com armazenamento efêmero podem apagar os pedidos ao reiniciar; use armazenamento persistente ou migre para PostgreSQL antes da avaliação real.
5. Nunca insira dados verdadeiros de cartão neste protótipo. Para teste público, use nomes e endereços fictícios, pois esta versão ainda não passou por uma revisão formal de segurança e privacidade de produção.

**Repositório do projeto:** [https://github.com/jobf2003-web/le-cupcake](https://github.com/jobf2003-web/le-cupcake)

**Link da aplicação:** [https://le-cupcake.onrender.com/](https://le-cupcake.onrender.com/)

Na entrega, conferir o acesso do tutor ao repositório (atualmente privado), os links das gravações e o funcionamento público da aplicação.

## Materiais da universidade ainda pendentes

A aplicação está hospedada; os dois vídeos foram gravados e estão armazenados externamente, aguardando a inserção de seus links. As cinco fichas e o laudo de qualidade foram preparados em documentos separados. Antes da entrega, atualizar o modelo oficial `PIT_atividade.docx`, anexar ou indicar os documentos finais, conferir as permissões de acesso e revisar o conteúdo acadêmico.

A documentação ABNT preliminar está em `docs/Documentacao_ABNT.docx`. O relatório simplificado, também em padrão ABNT, está em `docs/Relatorio_Atualizacao_Sistema_ABNT.docx`. Nenhum deles substitui o formulário oficial preenchido após os testes reais. Os diagramas e wireframes de planejamento também ficam em `docs/diagramas`.

## Estrutura

```text
app.py                    # Regras da aplicação e endpoints
schema.sql                # Modelo relacional de 23 tabelas
iniciar.py                # Inicializador local e leitura do .env
INICIAR_WINDOWS.bat       # Inicialização guiada no Windows
templates/                 # Páginas HTML com Jinja2
static/                    # Estilo e JS da interface
tests/                     # Testes técnicos
docs/                      # Documentação acadêmica, modelos e relatórios
instance/                  # Banco local (não publicar)
```


## Fotografias reais e referências

- As fotografias exibidas no catálogo, nas páginas de produtos e na administração são **fotografias reais de terceiros**, com fontes e licenças identificadas no documento de referências.
- Fonte: **Wikimedia Commons**, com autor, página de origem e licença verificados individualmente.
- As referências estão **somente no Word** [`docs/Referencias_Fotograficas_Simplificadas.docx`](docs/Referencias_Fotograficas_Simplificadas.docx); a página `/creditos` e os links de créditos foram removidos do site.
- As imagens são **ilustrativas** e representam cupcakes semelhantes; não são fotos de cupcakes que a loja fictícia produziu ou vende de verdade.
- Os arquivos são carregados da Wikimedia Commons via Internet e, portanto, **não estarão visíveis sem acesso à rede**. Caso a origem remova um arquivo, será necessário substituí-lo por outra fotografia verificada.
- O formulário administrativo permite selecionar somente fotografias da biblioteca documentada; outros endereços não são aceitos.
- O recorte visual (enquadramento do navegador) é realizado via CSS, sem alterar os arquivos originais.

**Licenciamento das fotografias:** algumas fotos têm licenças CC BY ou CC BY-SA que exigem atribuição em usos públicos. O arquivo Word reúne os créditos e links, mas, antes de publicar a loja abertamente, verifique como disponibilizar esses créditos de forma compatível com as licenças. Uma alternativa é usar exclusivamente fotografias em domínio público ou CC0.


## Identidade visual preservada na versão 0.2

A paleta foi revisada e conferida em todas as páginas: verde-sálvia `#3D634D`,
terracota `#B45C3C`, creme `#FFF8EC` e verde-claro `#DDE9D7`.
A faixa acadêmica superior continua marrom (`#5A4143`).
O endereço dos arquivos estáticos utiliza identificadores de atualização para evitar que o navegador
exiba estilos antigos guardados em cache.

**Importante ao atualizar:** feche o servidor anterior e abra o
`INICIAR_WINDOWS.bat` **dentro da nova pasta extraída**. Se a aparência
continuar antiga, pressione `Ctrl + F5` no navegador.


## Recursos funcionais da versão 0.1 preservados na versão 0.2

- **Cliente:** clique em **Entrar / Cadastrar** no cabeçalho. Crie uma conta com senha de pelo menos 12 caracteres. O carrinho permanece ao entrar, e os pedidos criados com a sessão autenticada aparecem em **Minha conta**. Pedidos anteriores feitos como visitante não são associados automaticamente.
- **Cupom:** o administrador faz login em **Área administrativa → Cupons** e cria o código (percentual ou valor fixo, mínimo e limite de usos). O cliente informa o código no checkout. O valor final é verificado no servidor e aparece no resumo do pedido concluído. Cupom de pedido cancelado não consome o limite.
- **Avaliações:** clientes registrados avaliam o cupcake na página de detalhes. O comentário permanece oculto até **Administração → Avaliações → Publicar**. A equipe pode responder ou ocultar comentários. Uma avaliação por cliente e produto.
- **Relatórios:** consulte **Administração → Relatórios**. Os totais indicam o valor dos pedidos não cancelados; **não representam pagamentos realizados**.
- **Entrega:** o administrador altera custos e descrições em **Administração → Entregas**. Ao menos uma modalidade deve permanecer ativa.
- **Informações nutricionais:** são preenchidas na edição do cupcake e só aparecem na página do produto se houver dados informados e verificados. Nenhum valor nutricional foi inventado.

**Segurança e privacidade:** este continua sendo um protótipo. Use contas e dados de teste ao apresentar em público. A recuperação de senha, a verificação de e-mails, o tratamento formal da LGPD e uma avaliação de segurança para hospedagem aberta ainda não foram feitos. Não utilize nomes, endereços ou telefones reais de clientes neste protótipo público.

## Manutenção do repositório

O projeto está versionado no GitHub e hospedado no Render. Nunca envie `.env`, `instance/cupcakes.db`, credenciais nem dados pessoais ao repositório. Antes de liberar o acesso público, confirme a atribuição das fotografias e a persistência do banco de dados.
