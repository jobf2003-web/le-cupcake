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
                db.execute(statement)
            db.execute(f'PRAGMA user_version = {next_version}')
            db.execute('RELEASE SAVEPOINT schema_migration')
        except Exception:
            db.execute('ROLLBACK TO SAVEPOINT schema_migration')
            db.execute('RELEASE SAVEPOINT schema_migration')
            raise