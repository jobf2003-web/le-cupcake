-- LE CUPCAKE - PIT II | ESQUEMA-BASE DA VERSAO 0.2 CONSOLIDADA
-- Este arquivo cria 23 tabelas iniciais. O banco fisico efetivo exige migrations.py,
-- com PRAGMA user_version=7 e 27 tabelas apos as migracoes da versao 0.2.
-- Valores monetarios em centavos. Pagamentos locais sao SOMENTE demonstrativos;
-- nao ha gateway externo nem cobranca real. Nunca armazenar dados de cartao.
PRAGMA foreign_keys = ON;
CREATE TABLE usuarios (
 id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
 senha_hash TEXT NOT NULL, papel TEXT NOT NULL DEFAULT 'cliente' CHECK (papel IN ('cliente','admin')),
 ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0,1)), criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE enderecos (
 id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
 cep TEXT NOT NULL, logradouro TEXT NOT NULL, numero TEXT NOT NULL, complemento TEXT,
 bairro TEXT NOT NULL, cidade TEXT NOT NULL, uf TEXT NOT NULL, principal INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE categorias (
 id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL UNIQUE, ativa INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE cupcakes (
 id INTEGER PRIMARY KEY AUTOINCREMENT, categoria_id INTEGER NOT NULL REFERENCES categorias(id),
 nome TEXT NOT NULL, descricao TEXT NOT NULL DEFAULT '', preco_centavos INTEGER NOT NULL CHECK (preco_centavos >= 0),
 estoque INTEGER NOT NULL DEFAULT 0 CHECK (estoque >= 0), imagem_url TEXT, informacoes_nutricionais TEXT,
 ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0,1)), criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE alergenos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL UNIQUE);
CREATE TABLE cupcake_alergenos (
 cupcake_id INTEGER NOT NULL REFERENCES cupcakes(id), alergeno_id INTEGER NOT NULL REFERENCES alergenos(id),
 PRIMARY KEY(cupcake_id,alergeno_id)
);
CREATE TABLE carrinhos (
 id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER REFERENCES usuarios(id),
 sessao_anonima TEXT, atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 CHECK (usuario_id IS NOT NULL OR sessao_anonima IS NOT NULL)
);
CREATE TABLE carrinho_itens (
 id INTEGER PRIMARY KEY AUTOINCREMENT, carrinho_id INTEGER NOT NULL REFERENCES carrinhos(id) ON DELETE CASCADE,
 cupcake_id INTEGER NOT NULL REFERENCES cupcakes(id), quantidade INTEGER NOT NULL CHECK (quantidade > 0),
 UNIQUE(carrinho_id,cupcake_id)
);
CREATE TABLE combos (
 id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, descricao TEXT,
 preco_centavos INTEGER NOT NULL CHECK (preco_centavos >= 0), ativo INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE combo_itens (
 combo_id INTEGER NOT NULL REFERENCES combos(id) ON DELETE CASCADE,
 cupcake_id INTEGER NOT NULL REFERENCES cupcakes(id), quantidade INTEGER NOT NULL CHECK (quantidade > 0),
 PRIMARY KEY(combo_id,cupcake_id)
);
CREATE TABLE opcoes_entrega (
 id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT NOT NULL CHECK (tipo IN ('entrega','retirada')),
 descricao TEXT NOT NULL, custo_base_centavos INTEGER NOT NULL DEFAULT 0 CHECK(custo_base_centavos >= 0),
 ativa INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE regioes_entrega (
 id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT NOT NULL, cep_inicio TEXT NOT NULL,
 cep_fim TEXT NOT NULL, taxa_adicional_centavos INTEGER NOT NULL DEFAULT 0 CHECK(taxa_adicional_centavos >= 0),
 ativa INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE janelas_entrega (
 id INTEGER PRIMARY KEY AUTOINCREMENT, opcao_entrega_id INTEGER NOT NULL REFERENCES opcoes_entrega(id),
 inicio TEXT NOT NULL, fim TEXT NOT NULL, capacidade INTEGER NOT NULL DEFAULT 1 CHECK (capacidade >= 0),
 CHECK(fim > inicio)
);
CREATE TABLE cupons (
 id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT NOT NULL UNIQUE, tipo TEXT NOT NULL CHECK(tipo IN ('percentual','fixo')),
 valor INTEGER NOT NULL CHECK (valor >= 0), valor_minimo_centavos INTEGER NOT NULL DEFAULT 0,
 valido_de TEXT, valido_ate TEXT, limite_uso INTEGER CHECK (limite_uso IS NULL OR limite_uso > 0),
 ativo INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE pedidos (
 id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER REFERENCES usuarios(id),
 endereco_id INTEGER REFERENCES enderecos(id), opcao_entrega_id INTEGER NOT NULL REFERENCES opcoes_entrega(id),
 janela_entrega_id INTEGER REFERENCES janelas_entrega(id),
 contato_nome TEXT NOT NULL, contato_email TEXT NOT NULL, contato_telefone TEXT NOT NULL,
 endereco_entrega TEXT, token_acesso TEXT NOT NULL UNIQUE,
 status TEXT NOT NULL DEFAULT 'recebido'
 CHECK(status IN ('recebido','confirmado','preparo','pronto','em_entrega','concluido','cancelado')),
 subtotal_centavos INTEGER NOT NULL CHECK(subtotal_centavos >= 0),
 frete_centavos INTEGER NOT NULL DEFAULT 0 CHECK(frete_centavos >= 0),
 desconto_centavos INTEGER NOT NULL DEFAULT 0 CHECK(desconto_centavos >= 0),
 total_centavos INTEGER NOT NULL CHECK(total_centavos >= 0),
 criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE pedido_itens (
 id INTEGER PRIMARY KEY AUTOINCREMENT, pedido_id INTEGER NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
 cupcake_id INTEGER REFERENCES cupcakes(id), combo_id INTEGER REFERENCES combos(id),
 nome_snapshot TEXT NOT NULL, quantidade INTEGER NOT NULL CHECK (quantidade > 0),
 preco_unitario_centavos INTEGER NOT NULL CHECK(preco_unitario_centavos >= 0),
 CHECK ((cupcake_id IS NULL) != (combo_id IS NULL))
);
CREATE TABLE cupom_utilizacoes (
 id INTEGER PRIMARY KEY AUTOINCREMENT, cupom_id INTEGER NOT NULL REFERENCES cupons(id),
 pedido_id INTEGER NOT NULL UNIQUE REFERENCES pedidos(id), utilizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE pagamentos (
 id INTEGER PRIMARY KEY AUTOINCREMENT, pedido_id INTEGER NOT NULL REFERENCES pedidos(id),
 metodo TEXT NOT NULL, provedor TEXT, referencia_externa TEXT UNIQUE,
 status TEXT NOT NULL DEFAULT 'pendente' CHECK(status IN ('pendente','aprovado','recusado','estornado')),
 valor_centavos INTEGER NOT NULL CHECK(valor_centavos >= 0), atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE eventos_pedido (
 id INTEGER PRIMARY KEY AUTOINCREMENT, pedido_id INTEGER NOT NULL REFERENCES pedidos(id),
 status TEXT NOT NULL, observacao TEXT, ocorrido_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE notificacoes (
 id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER REFERENCES usuarios(id),
 pedido_id INTEGER REFERENCES pedidos(id), canal TEXT NOT NULL CHECK(canal IN ('app','email','sms')),
 conteudo TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pendente', criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE avaliacoes (
 id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
 cupcake_id INTEGER NOT NULL REFERENCES cupcakes(id), nota INTEGER NOT NULL CHECK(nota BETWEEN 1 AND 5),
 comentario TEXT, status TEXT NOT NULL DEFAULT 'pendente' CHECK(status IN ('pendente','publicada','oculta')),
 resposta_admin TEXT, respondida_em TEXT, criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE estoque_movimentos (
 id INTEGER PRIMARY KEY AUTOINCREMENT, cupcake_id INTEGER NOT NULL REFERENCES cupcakes(id),
 pedido_id INTEGER REFERENCES pedidos(id), variacao INTEGER NOT NULL,
 motivo TEXT NOT NULL, criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE auditoria (
 id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER REFERENCES usuarios(id),
 entidade TEXT NOT NULL, entidade_id INTEGER, acao TEXT NOT NULL,
 descricao TEXT, criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_cupcakes_categoria ON cupcakes(categoria_id,ativo);
CREATE INDEX idx_pedidos_usuario_data ON pedidos(usuario_id,criado_em);
CREATE INDEX idx_pedidos_status ON pedidos(status);
CREATE INDEX idx_itens_pedido ON pedido_itens(pedido_id);
CREATE INDEX idx_eventos_pedido ON eventos_pedido(pedido_id,ocorrido_em);
CREATE INDEX idx_notificacoes_usuario ON notificacoes(usuario_id,status);
CREATE INDEX idx_avaliacoes_cupcake ON avaliacoes(cupcake_id,status);
