"""Montagem local de combos personalizados: não presume descontos inexistentes."""
from __future__ import annotations
from collections import Counter
import sqlite3

MAX_COMBOS = 10
MAX_PECAS = 8
MIN_PECAS = 2
COMBO_NOME = 'Combo personalizado'


def sanitize_combos(raw) -> list[dict[int, int]]:
    """Desconfia integralmente da sessão e limita volume para proteger cookie e consultas."""
    if not isinstance(raw, list):
        return []
    out = []
    for item in raw[:MAX_COMBOS]:
        if not isinstance(item, dict):
            continue
        cleaned = {}
        for k, v in item.items():
            try:
                product_id, amount = int(k), int(v)
            except (TypeError, ValueError):
                continue
            if product_id > 0 and 1 <= amount <= MAX_PECAS:
                cleaned[product_id] = amount
        if MIN_PECAS <= sum(cleaned.values()) <= MAX_PECAS:
            out.append(cleaned)
    return out


def build_bundle(db: sqlite3.Connection, cart: dict[int, int], combos: list[dict[int, int]]):
    """Preço sempre é recalculado pelo servidor; cestas sem estoque são barradas."""
    allocations = Counter(cart)
    ids = set(cart)
    for combo in combos:
        ids.update(combo)
        allocations.update(combo)
    products = {}
    if ids:
        qs = ','.join('?' for _ in ids)
        products = {r['id']:r for r in db.execute(
            f'SELECT id,nome,preco_centavos,estoque,ativo FROM cupcakes WHERE id IN ({qs})', sorted(ids))}
    enough = all(products.get(pid) is not None and products[pid]['ativo'] and
                 products[pid]['estoque'] >= qty for pid,qty in allocations.items())
    display = []
    for idx, combo in enumerate(combos):
        parts = []
        subtotal = 0
        for pid, qty in sorted(combo.items()):
            product = products.get(pid)
            if product is None:
                enough = False
                continue
            unit = int(product['preco_centavos'])
            subtotal += unit * qty
            parts.append({'id':pid,'nome':product['nome'],'qty':qty,'price':unit})
        display.append({'index':idx,'name':COMBO_NOME,'parts':parts,
                        'pieces':sum(combo.values()),'total':subtotal,'available':enough})
    return display, sum(x['total'] for x in display), dict(allocations), enough
