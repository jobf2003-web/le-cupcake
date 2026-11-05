"""US-14: montagem personalizada, estoque agregado, snapshots e cancelamento."""
import re
import sqlite3
import pytest
from fastapi.testclient import TestClient
from app import create_app


def csrf(c,url='/'):
    r=c.get(url)
    assert r.status_code==200,r.text[:400]
    m=re.search(r'name="_csrf" value="([^"]+)"',r.text)
    assert m
    return m.group(1)


@pytest.fixture
def ctx(tmp_path,monkeypatch):
    monkeypatch.setenv('ADMIN_EMAIL','admin@doce.test')
    monkeypatch.setenv('ADMIN_PASSWORD','SenhaUltraForte123!')
    db_path=tmp_path/'cupcakes.db'
    app=create_app(db_path,testing=True)
    buyer,admin=TestClient(app),TestClient(app)
    assert admin.post('/entrar',data={'_csrf':csrf(admin,'/entrar'),
        'email':'admin@doce.test','senha':'SenhaUltraForte123!'},follow_redirects=False).status_code==303
    return buyer,admin,db_path


def combo(buyer,**parts):
    d={'_csrf':csrf(buyer,'/combos')}
    d.update({'q_'+str(k):str(v) for k,v in parts.items()})
    return buyer.post('/combos/adicionar',data=d,follow_redirects=False)


def buy(buyer,**changes):
    data={'_csrf':csrf(buyer,'/checkout'),'nome':'Ana Maria',
          'email':'ana@example.com','telefone':'(65) 99999-9999',
          'opcao_entrega':'1','endereco':''}
    data.update(changes)
    return buyer.post('/checkout',data=data,follow_redirects=False)


def single(buyer,pid,qty):
    return buyer.post('/carrinho/adicionar',data={'_csrf':csrf(buyer),
        'produto_id':str(pid),'quantidade':str(qty)},follow_redirects=False)


def test_custom_combo_only_cart_and_order_components(ctx):
    buyer,_,path=ctx
    assert 'Monte seu combo' in buyer.get('/combos').text
    r=combo(buyer,**{'1':2,'2':1})
    assert r.status_code==303
    cart=buyer.get('/carrinho')
    assert cart.status_code==200
    assert 'Combo personalizado' in cart.text and 'R$ 36,50' in cart.text
    r=buy(buyer)
    assert r.status_code==303
    order=buyer.get(r.headers['location'])
    assert order.status_code==200 and '2× Chocolate da Casa' in order.text
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT subtotal_centavos FROM pedidos').fetchone()[0]==3650
        row=db.execute('SELECT cupcake_id,combo_id,quantidade FROM pedido_itens').fetchone()
        assert row[0] is None and row[1] is not None and row[2]==1
        comps=db.execute('SELECT cupcake_id,quantidade FROM pedido_combo_componentes ORDER BY cupcake_id').fetchall()
        assert comps==[(1,2),(2,1)]
        assert db.execute('SELECT estoque FROM cupcakes WHERE id=1').fetchone()[0]==28
        assert db.execute('SELECT estoque FROM cupcakes WHERE id=2').fetchone()[0]==24
    assert 'Seu carrinho está vazio' in buyer.get('/carrinho').text


def test_aggregate_stock_combo_and_single(ctx):
    buyer,_,path=ctx
    assert single(buyer,1,29).status_code==303
    r=combo(buyer,**{'1':2})
    assert r.status_code==422
    assert 'Estoque insuficiente' in r.text
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT COUNT(*) FROM pedidos').fetchone()[0]==0


def test_remove_combo_without_affecting_standard_cart(ctx):
    buyer,_,_=ctx
    assert single(buyer,1,1).status_code==303
    assert combo(buyer,**{'2':2}).status_code==303
    assert 'Combo personalizado' in buyer.get('/carrinho').text
    r=buyer.post('/combos/remover',data={'_csrf':csrf(buyer,'/carrinho'),'indice':'0'},follow_redirects=False)
    assert r.status_code==303
    cart=buyer.get('/carrinho').text
    assert 'Combo personalizado' not in cart
    assert 'Chocolate da Casa' in cart


def test_cancel_restores_every_combo_component_once(ctx):
    buyer,admin,path=ctx
    combo(buyer,**{'1':2,'3':1})
    r=buy(buyer)
    assert r.status_code==303
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT estoque FROM cupcakes WHERE id=1').fetchone()[0]==28
        assert db.execute('SELECT estoque FROM cupcakes WHERE id=3').fetchone()[0]==19
    r=admin.post('/admin/pedidos/1/status',data={'_csrf':csrf(admin,'/admin/pedidos'),
        'status':'cancelado'},follow_redirects=False)
    assert r.status_code==303
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT estoque FROM cupcakes WHERE id=1').fetchone()[0]==30
        assert db.execute('SELECT estoque FROM cupcakes WHERE id=3').fetchone()[0]==20
        assert db.execute('SELECT COUNT(*) FROM estoque_movimentos WHERE motivo="Combo cancelado"').fetchone()[0]==2
    r=admin.post('/admin/pedidos/1/status',data={'_csrf':csrf(admin,'/admin/pedidos'),
        'status':'cancelado'},follow_redirects=False)
    assert r.status_code==422
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT estoque FROM cupcakes WHERE id=1').fetchone()[0]==30


def test_invalid_qty_and_missing_csrf_rejected(ctx):
    buyer,_,path=ctx
    assert buyer.post('/combos/adicionar',data={'q_1':'3'},follow_redirects=False).status_code==403
    assert combo(buyer,**{'1':1}).status_code==422
    assert combo(buyer,**{'1':9}).status_code==422
    assert combo(buyer,**{'999':2}).status_code==422
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT COUNT(*) FROM pedidos').fetchone()[0]==0


def test_combo_price_reflects_current_product_price(ctx):
    buyer,_,path=ctx
    assert combo(buyer,**{'1':2}).status_code==303
    with sqlite3.connect(path) as db:
        db.execute('UPDATE cupcakes SET preco_centavos=2000 WHERE id=1')
    assert 'R$ 40,00' in buyer.get('/carrinho').text
    assert buy(buyer).status_code==303
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT subtotal_centavos FROM pedidos').fetchone()[0]==4000
        assert db.execute('SELECT preco_unitario_centavos FROM pedido_combo_componentes').fetchone()[0]==2000


def test_combo_v4_schema_and_no_duplicate_seed(ctx):
    _,_,path=ctx
    with sqlite3.connect(path) as db:
        assert db.execute('PRAGMA user_version').fetchone()[0]==4
        assert db.execute('SELECT COUNT(*) FROM combos WHERE nome="Combo personalizado"').fetchone()[0]==1
        assert db.execute('PRAGMA foreign_key_check').fetchall()==[]
    create_app(path,testing=True)
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT COUNT(*) FROM combos WHERE nome="Combo personalizado"').fetchone()[0]==1


def test_single_plus_combo_checkout_and_stock(ctx):
    buyer,_,path=ctx
    assert single(buyer,1,1).status_code==303
    assert combo(buyer,**{'1':2,'2':2}).status_code==303
    assert 'R$ 60,50' in buyer.get('/carrinho').text
    assert buy(buyer).status_code==303
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT estoque FROM cupcakes WHERE id=1').fetchone()[0]==27
        assert db.execute('SELECT estoque FROM cupcakes WHERE id=2').fetchone()[0]==23
        assert db.execute('SELECT COUNT(*) FROM pedido_itens').fetchone()[0]==2
        assert db.execute('SELECT subtotal_centavos FROM pedidos').fetchone()[0]==6050
