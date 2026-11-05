"""Migrações versionadas para bancos SQLite já existentes da Le Cupcake.

Usa PRAGMA user_version para não criar uma tabela nova apenas de controle.
Cada revisão é aplicada numa transação/salvamento, sem apagar registros anteriores.
"""
from __future__ import annotations
import sqlite3

MIGRATIONS: dict[int, tuple[str, ...]] = {
    1: (
        'CREATE INDEX IF NOT EXISTS idx_catalogo_ativo_estoque_categoria ON cupcakes(ativo, estoque, categoria_id)',
        'CREATE INDEX IF NOT EXISTS idx_pedidos_criacao_status ON pedidos(criado_em, status)',
        'CREATE INDEX IF NOT EXISTS idx_auditoria_entidade_data ON auditoria(entidade, entidade_id, criado_em)',
    ),
    2: (
        'ALTER TABLE cupcakes ADD COLUMN excluido_em TEXT',
        'CREATE INDEX IF NOT EXISTS idx_cupcakes_arquivados ON cupcakes(excluido_em, ativo)',
    ),
    3: (
        'ALTER TABLE pedidos ADD COLUMN cep_entrega TEXT',
        'ALTER TABLE pedidos ADD COLUMN regiao_entrega_id INTEGER REFERENCES regioes_entrega(id)',
        'ALTER TABLE pedidos ADD COLUMN agendado_para TEXT',
        '''CREATE TABLE IF NOT EXISTS agenda_bloqueios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opcao_entrega_id INTEGER NOT NULL REFERENCES opcoes_entrega(id),
            data TEXT NOT NULL, motivo TEXT NOT NULL DEFAULT 'Fechado',
            UNIQUE(opcao_entrega_id,data))''',
        'CREATE INDEX IF NOT EXISTS idx_pedidos_agendados ON pedidos(janela_entrega_id,agendado_para,status)',
        'CREATE INDEX IF NOT EXISTS idx_regioes_cep ON regioes_entrega(ativa,cep_inicio,cep_fim)',
    ),
    4: (
        """CREATE TABLE IF NOT EXISTS pedido_combo_componentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_item_id INTEGER NOT NULL REFERENCES pedido_itens(id) ON DELETE CASCADE,
            cupcake_id INTEGER NOT NULL REFERENCES cupcakes(id),
            quantidade INTEGER NOT NULL CHECK(quantidade>0),
            nome_snapshot TEXT NOT NULL,
            preco_unitario_centavos INTEGER NOT NULL CHECK(preco_unitario_centavos>=0)
        )""",
        'CREATE INDEX IF NOT EXISTS idx_combo_componentes_item ON pedido_combo_componentes(pedido_item_id)',
    ),
    5: (
        'ALTER TABLE usuarios ADD COLUMN sessao_versao INTEGER NOT NULL DEFAULT 0',
        'ALTER TABLE cupcakes ADD COLUMN ingredientes TEXT',
        """CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
            token_digest TEXT NOT NULL UNIQUE,
            expiracao_em TEXT NOT NULL,
            usado_em TEXT,
            criado_em TEXT NOT NULL
        )""",
        'CREATE INDEX IF NOT EXISTS idx_reset_user_created ON password_reset_tokens(usuario_id,criado_em)',
    ),
    6: (
        'ALTER TABLE pedidos ADD COLUMN previsao_entrega_em TEXT',
        'CREATE INDEX IF NOT EXISTS idx_notificacoes_fila_app ON notificacoes(usuario_id,canal,status,id)',
        'CREATE INDEX IF NOT EXISTS idx_eventos_pedido_id ON eventos_pedido(pedido_id,id)',
    ),
}


def apply_migrations(db: sqlite3.Connection) -> None:
    """Atualiza índices/esquema in-place e falha sem aceitar bases de versões futuras."""
    version = int(db.execute('PRAGMA user_version').fetchone()[0])
    highest = max(MIGRATIONS, default=0)
    if version > highest:
        raise RuntimeError(f'O banco utiliza esquema futuro {version}; aplicação suporta até {highest}.')
    for next_version in range(version + 1, highest + 1):
        db.execute('SAVEPOINT schema_migration')
        try:
            for statement in MIGRATIONS[next_version]:
                # Um banco legado pode possuir colunas da migração quando
                # user_version foi reiniciado por uma ferramenta externa.
                if statement.startswith('ALTER TABLE ') and ' ADD COLUMN ' in statement:
                    table = statement.split(' ')[2]
                    column = statement.split(' ADD COLUMN ')[1].split(' ')[0]
                    present = {col[1] for col in db.execute(f'PRAGMA table_info({table})')}
                    if column in present:
                        continue
                db.execute(statement)
            db.execute(f'PRAGMA user_version = {next_version}')
            db.execute('RELEASE SAVEPOINT schema_migration')
        except Exception:
            db.execute('ROLLBACK TO SAVEPOINT schema_migration')
            db.execute('RELEASE SAVEPOINT schema_migration')
            raise
