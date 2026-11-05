'''Simulador LOCAL de pagamento para PIT II — não integra gateways nem cobra valores.

Nunca solicitar números de cartões. Estados aprovados neste módulo não representam
recebimento financeiro real. Transições são atômicas e idempotentes no banco SQLite.
'''
from __future__ import annotations

import sqlite3

PAYMENT_METHODS = {
    'a_combinar': 'A combinar (sem pagamento verificado)',
    'pix_demo': 'PIX demonstrativo (sem transferência)',
    'cartao_demo': 'Cartão demonstrativo (sem dados de cartão)',
}
DEMO_METHODS = frozenset({'pix_demo', 'cartao_demo'})
PAYMENT_STATUSES = {
    'pendente': 'Pendente — nenhuma cobrança realizada',
    'aprovado': 'Aprovado apenas na simulação — sem cobrança',
    'recusado': 'Recusado na simulação — sem cobrança',
    'estornado': 'Revertido na simulação — sem operação financeira',
}


def validate_payment_method(value: str) -> str:
    if value not in PAYMENT_METHODS:
        raise ValueError('Escolha uma forma de pagamento válida.')
    return value


def payment_label(method: str, status: str) -> str:
    title = PAYMENT_METHODS.get(method, 'Método não especificado')
    label = PAYMENT_STATUSES.get(status, 'Não verificado')
    return f'{title} — {label}'


def restore_order_stock(db: sqlite3.Connection, order_id: int) -> None:
    '''Devolve componentes de produtos/combos uma vez na transição de cancelamento.

    Chamador deve segurar transação BEGIN IMMEDIATE e verificar estado != cancelado.
    '''
    db.execute('DELETE FROM cupom_utilizacoes WHERE pedido_id=?', (order_id,))
    items = db.execute('''SELECT cupcake_id, quantidade FROM pedido_itens
                          WHERE pedido_id=? AND cupcake_id IS NOT NULL''', (order_id,)).fetchall()
    for cupcake_id, qty in items:
        db.execute('UPDATE cupcakes SET estoque=estoque+? WHERE id=?', (qty, cupcake_id))
        db.execute('''INSERT INTO estoque_movimentos(cupcake_id,pedido_id,variacao,motivo)
                      VALUES (?,?,?,?)''', (cupcake_id, order_id, qty, 'Pedido cancelado'))
    components = db.execute('''SELECT pc.cupcake_id,pc.quantidade
                     FROM pedido_combo_componentes pc JOIN pedido_itens pi ON pi.id=pc.pedido_item_id
                     WHERE pi.pedido_id=?''', (order_id,)).fetchall()
    for cupcake_id, qty in components:
        db.execute('UPDATE cupcakes SET estoque=estoque+? WHERE id=?', (qty, cupcake_id))
        db.execute('''INSERT INTO estoque_movimentos(cupcake_id,pedido_id,variacao,motivo)
                      VALUES (?,?,?,?)''', (cupcake_id, order_id, qty, 'Combo cancelado'))


def log_payment_event(db: sqlite3.Connection, payment_id: int, previous: str,
                      current: str, origin: str) -> None:
    db.execute('''INSERT INTO pagamento_eventos(pagamento_id,status_anterior,status_novo,origem)
                  VALUES (?,?,?,?)''', (payment_id, previous, current, origin))


def simulate_decision(db: sqlite3.Connection, *, order_id: int, decision: str) -> tuple[str, bool]:
    '''Executar APENAS dentro da transação de escrita BEGIN IMMEDIATE.

    Repetição da mesma decisão é operação sem efeito; decisões divergentes falham.
    '''
    if decision not in ('aprovar', 'recusar'):
        raise ValueError('Decisão de pagamento inválida.')
    order = db.execute('SELECT id,status,usuario_id FROM pedidos WHERE id=?', (order_id,)).fetchone()
    pay = db.execute('''SELECT * FROM pagamentos WHERE pedido_id=? ORDER BY id DESC LIMIT 1''',
                     (order_id,)).fetchone()
    if order is None or pay is None or pay['metodo'] not in DEMO_METHODS or pay['provedor'] != 'simulador_local':
        raise ValueError('Este pedido não possui pagamento demonstrativo disponível.')
    target = 'aprovado' if decision == 'aprovar' else 'recusado'
    if pay['status'] == target:
        return target, False
    if pay['status'] != 'pendente':
        raise ValueError('O pagamento demonstrativo já foi finalizado e não pode ser alterado.')
    if order['status'] != 'recebido':
        raise ValueError('O pedido não permite mais decisões de pagamento.')
    db.execute('UPDATE pagamentos SET status=?,atualizado_em=CURRENT_TIMESTAMP WHERE id=?',
               (target, pay['id']))
    log_payment_event(db, pay['id'], 'pendente', target, 'simulacao_local_cliente')
    if target == 'recusado':
        restore_order_stock(db, order_id)
        db.execute("UPDATE pedidos SET status='cancelado' WHERE id=?", (order_id,))
        db.execute('''INSERT INTO eventos_pedido(pedido_id,status,observacao)
                      VALUES (?,'cancelado','Pagamento recusado na demonstração — sem cobrança')''', (order_id,))
    return target, True
