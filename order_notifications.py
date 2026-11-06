"""Notificações *internas* da Le Cupcake, sem fingir SMS/e-mail externo.

Os registros são feitos na mesma transação que o pedido ou a troca de status.
A interface de cada usuário mostra somente suas próprias notificações.
"""
from __future__ import annotations

from collections.abc import Iterable
import sqlite3

STATUS_LABELS = {
    'recebido': 'Recebido', 'confirmado': 'Confirmado',
    'preparo': 'Em preparo', 'pronto': 'Pronto',
    'em_entrega': 'Em entrega', 'concluido': 'Concluído',
    'cancelado': 'Cancelado',
}


def create_app_notification(db: sqlite3.Connection, user_id: int, order_id: int, message: str) -> None:
    if not user_id or not message:
        return
    db.execute('''INSERT INTO notificacoes(usuario_id,pedido_id,canal,conteudo,status)
                  VALUES (?,?,'app',?,'pendente')''', (user_id, order_id, message))


def notify_new_order(db: sqlite3.Connection, order_id: int, customer_id: int | None) -> None:
    if customer_id:
        create_app_notification(db, customer_id, order_id,
                                f'Pedido #{order_id} registrado. Acompanhe o andamento no site.')
    administrators = db.execute("SELECT id FROM usuarios WHERE papel='admin' AND ativo=1").fetchall()
    for admin in administrators:
        create_app_notification(db, admin[0], order_id,
                                f'Novo pedido #{order_id} recebido. Consulte o painel de pedidos.')


def notify_status_change(db: sqlite3.Connection, order_id: int,
                         customer_id: int | None, status: str) -> None:
    if customer_id:
        create_app_notification(db, customer_id, order_id,
                                f'Pedido #{order_id}: {STATUS_LABELS.get(status,status)}.')


def user_notifications(db: sqlite3.Connection, user_id: int, *, limit: int = 30):
    return db.execute('''SELECT id, pedido_id, conteudo, status, criado_em
                         FROM notificacoes
                         WHERE usuario_id=? AND canal='app'
                         ORDER BY id DESC LIMIT ?''', (user_id, max(1, min(limit, 100)))).fetchall()


def mark_user_notifications_read(db: sqlite3.Connection, user_id: int) -> int:
    cur = db.execute('''UPDATE notificacoes SET status='lida' WHERE usuario_id=?
                        AND canal='app' AND status='pendente' ''', (user_id,))
    return cur.rowcount
