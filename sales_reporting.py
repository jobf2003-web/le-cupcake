"""Relatórios demonstrativos: valores registrados não são receita recebida.

A fonte de produtos inclui cupcakes avulsos e componentes de combos. Quando
há filtro por categoria, o indicador financeiro é BRUTO de itens, antes de
cupom e frete, para não atribuir desconto/frete integral a uma categoria.
"""
from __future__ import annotations

import sqlite3

ITEMS_CTE = '''WITH itens AS (
    SELECT p.id pedido_id, substr(p.criado_em,1,7) periodo, c.categoria_id,
           pi.nome_snapshot nome, pi.quantidade unidades,
           pi.quantidade*pi.preco_unitario_centavos valor_bruto_centavos
    FROM pedidos p JOIN pedido_itens pi ON pi.pedido_id=p.id
    JOIN cupcakes c ON c.id=pi.cupcake_id
    WHERE p.status<>'cancelado' AND pi.cupcake_id IS NOT NULL
    UNION ALL
    SELECT p.id pedido_id, substr(p.criado_em,1,7) periodo, c.categoria_id,
           pc.nome_snapshot nome, pc.quantidade unidades,
           pc.quantidade*pc.preco_unitario_centavos valor_bruto_centavos
    FROM pedidos p JOIN pedido_itens pi ON pi.pedido_id=p.id
    JOIN pedido_combo_componentes pc ON pc.pedido_item_id=pi.id
    JOIN cupcakes c ON c.id=pc.cupcake_id
    WHERE p.status<>'cancelado'
)'''


def report_data(db: sqlite3.Connection, *, month: str='', category_id: int | None=None) -> dict:
    if category_id is not None:
        category = db.execute('SELECT id,nome FROM categorias WHERE id=?', (category_id,)).fetchone()
        if category is None:
            raise ValueError('Categoria não encontrada.')
    else:
        category = None
    categories = db.execute('SELECT id,nome FROM categorias ORDER BY nome').fetchall()
    conditions = []
    params: list = []
    if month:
        conditions.append('periodo=?')
        params.append(month)
    if category_id is not None:
        conditions.append('categoria_id=?')
        params.append(category_id)
    where = 'WHERE ' + ' AND '.join(conditions) if conditions else ''

    top = db.execute(ITEMS_CTE + ''' SELECT nome,SUM(unidades) unidades,
                  SUM(valor_bruto_centavos) valor_bruto_centavos
                  FROM itens '''+where+''' GROUP BY nome
                  ORDER BY unidades DESC,nome LIMIT 10''', params).fetchall()
    monthly = db.execute(ITEMS_CTE + ''' SELECT periodo,SUM(unidades) unidades,
                  SUM(valor_bruto_centavos) valor_bruto_centavos
                  FROM itens '''+where+''' GROUP BY periodo ORDER BY periodo DESC LIMIT 12''', params).fetchall()
    monthly = list(reversed(monthly))

    if category_id is None:
        clause = ' AND substr(p.criado_em,1,7)=?' if month else ''
        overview = db.execute('''SELECT COUNT(*) pedidos,
                   COALESCE(SUM(p.total_centavos),0) receita,
                   COALESCE(SUM(p.desconto_centavos),0) descontos
                   FROM pedidos p WHERE p.status<>'cancelado' '''+clause,
                   (month,) if month else ()).fetchone()
        total_label = 'Valor total dos pedidos (não é receita recebida)'
    else:
        overview = db.execute(ITEMS_CTE + ''' SELECT COUNT(DISTINCT pedido_id) pedidos,
                    COALESCE(SUM(valor_bruto_centavos),0) receita,
                    0 descontos FROM itens '''+where,params).fetchone()
        total_label = 'Valor bruto dos itens da categoria (sem frete e desconto)'
    by_status = db.execute('''SELECT status,COUNT(*) quantidade FROM pedidos
                             GROUP BY status ORDER BY quantidade DESC''').fetchall()
    points = [{'periodo':r['periodo'],'unidades':int(r['unidades']),
               'valor_centavos':int(r['valor_bruto_centavos'])} for r in monthly]
    return {'overview':overview,'top':top,'by_status':by_status,
            'categories':categories,'selected_category':category,
            'month':month,'total_label':total_label,'points':points,
            'max_units':max((p['unidades'] for p in points),default=0),
            'max_value':max((p['valor_centavos'] for p in points),default=0)}
