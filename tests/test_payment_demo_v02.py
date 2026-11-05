
"""Ciclo E — US-12 / US-25 demonstrativas: não há pagamento externo ou gateway real."""
import re
import sqlite3
import pytest
from fastapi.testclient import TestClient
from app import create_app
from migrations import MIGRATIONS
from payment_demo import PAYMENT_METHODS


def csrf(client, url='/'):
    page=client.get(url)
    assert page.status_code==200,page.text[:350]
    m=re.search(r'name="_csrf" value="([^"]+)"',page.text)
    assert m,url
    return m.group(1)

@pytest.fixture
def env(tmp_path,monkeypatch):
    monkeypatch.setenv('ADMIN_EMAIL','admin@doce.test')
    monkeypatch.setenv('ADMIN_PASSWORD','SenhaUltraForte123!')
    path=tmp_path/'payments.db'
    app=create_app(path,testing=True)
    buyer,admin,other=TestClient(app),TestClient(app),TestClient(app)
    assert admin.post('/entrar',data={'_csrf':csrf(admin,'/entrar'), 'email':'admin@doce.test',
        'senha':'SenhaUltraForte123!'},follow_redirects=False).status_code==303
    return buyer,admin,other,path


def add(client,product=1,qty=2):
    return client.post('/carrinho/adicionar',data={'_csrf':csrf(client),
        'produto_id':str(product),'quantidade':str(qty)},follow_redirects=False)


def checkout(client,method='pix_demo',**extra):
    data={'_csrf':csrf(client,'/checkout'),'nome':'Cliente Demonstração',
        'email':'cliente@demo.test','telefone':'(65) 99999-9999',
        'opcao_entrega':'1','metodo_pagamento':method}
    data.update(extra)
    return client.post('/checkout',data=data,follow_redirects=False)


def decide(client,link,decision,token=None):
    if token is None:
        token=csrf(client,'/')
    return client.post(link+'/simular-pagamento',data={'_csrf':token,'decisao':decision},follow_redirects=False)


def admin_status(client,action,order_id=1):
    return client.post(f'/admin/pedidos/{order_id}/status',
        data={'_csrf':csrf(client,'/admin/pedidos'),'status':action},follow_redirects=False)


def one(db,query,*params):
    with sqlite3.connect(db) as con:
        return con.execute(query,params).fetchone()[0]


def test_methods_are_explicitly_simulated_and_no_card_collection(env):
    buyer,_,_,_=env
    assert add(buyer).status_code==303
    page=buyer.get('/checkout').text
    for label in PAYMENT_METHODS.values(): assert label in page
    assert 'não há cobrança real' in page
    assert 'name="metodo_pagamento"' in page
    assert 'name="numero_cartao"' not in page
    assert 'name="cvv"' not in page


def test_invalid_payment_method_rejected_without_stock_change(env):
    buyer,_,_,db=env
    add(buyer)
    r=checkout(buyer,'gateway_inventado')
    assert r.status_code==422
    assert 'forma de pagamento válida' in r.text
    assert one(db,'SELECT COUNT(*) FROM pedidos')==0
    assert one(db,'SELECT estoque FROM cupcakes WHERE id=1')==30


def test_pix_demo_creates_pending_payment_and_blocks_confirmation(env):
    buyer,admin,_,db=env
    add(buyer)
    r=checkout(buyer,'pix_demo')
    assert r.status_code==303
    page=buyer.get(r.headers['location'])
    assert page.status_code==200
    assert 'Simular aprovação' in page.text
    assert 'sem cobrança' in page.text
    with sqlite3.connect(db) as con:
        assert con.execute('SELECT metodo,provedor,status FROM pagamentos').fetchone()==('pix_demo','simulador_local','pendente')
    assert admin_status(admin,'confirmado').status_code==422
    assert one(db,'SELECT status FROM pedidos')=='recebido'
    assert 'simulado' in admin.get('/admin/pedidos').text


def test_approval_requires_csrf_is_idempotent_and_allows_admin_confirmation(env):
    buyer,admin,_,db=env
    add(buyer)
    link=checkout(buyer,'cartao_demo').headers['location']
    assert buyer.post(link+'/simular-pagamento',data={'decisao':'aprovar'},follow_redirects=False).status_code==403
    bad=buyer.post(link+'/simular-pagamento',data={'_csrf':'falso','decisao':'aprovar'},follow_redirects=False)
    assert bad.status_code==403
    assert decide(buyer,link,'aprovar').status_code==303
    assert decide(buyer,link,'aprovar').status_code==303
    with sqlite3.connect(db) as con:
        assert con.execute('SELECT status FROM pagamentos').fetchone()[0]=='aprovado'
        assert con.execute('SELECT COUNT(*) FROM pagamento_eventos').fetchone()[0]==1
        assert con.execute('SELECT estoque FROM cupcakes WHERE id=1').fetchone()[0]==28
    assert 'Aprovado apenas na simulação' in buyer.get(link).text
    assert admin_status(admin,'confirmado').status_code==303
    assert one(db,'SELECT status FROM pedidos')=='confirmado'
    assert decide(buyer,link,'recusar').status_code==422
    assert one(db,'SELECT status FROM pagamentos')=='aprovado'


def test_decline_cancels_and_restores_stock_exactly_once(env):
    buyer,admin,_,db=env
    add(buyer,1,3)
    link=checkout(buyer,'pix_demo').headers['location']
    assert one(db,'SELECT estoque FROM cupcakes WHERE id=1')==27
    assert decide(buyer,link,'recusar').status_code==303
    assert decide(buyer,link,'recusar').status_code==303
    with sqlite3.connect(db) as con:
        assert con.execute('SELECT status FROM pedidos').fetchone()[0]=='cancelado'
        assert con.execute('SELECT status FROM pagamentos').fetchone()[0]=='recusado'
        assert con.execute('SELECT estoque FROM cupcakes WHERE id=1').fetchone()[0]==30
        assert con.execute('SELECT COUNT(*) FROM pagamento_eventos').fetchone()[0]==1
        assert con.execute("SELECT COUNT(*) FROM eventos_pedido WHERE status='cancelado'").fetchone()[0]==1
    assert admin_status(admin,'cancelado').status_code==422
    assert decide(buyer,link,'aprovar').status_code==422
    assert one(db,'SELECT estoque FROM cupcakes WHERE id=1')==30


def test_cancel_after_simulated_approval_records_demo_reversal(env):
    buyer,admin,_,db=env
    add(buyer)
    link=checkout(buyer).headers['location']
    decide(buyer,link,'aprovar')
    assert admin_status(admin,'cancelado').status_code==303
    assert one(db,'SELECT status FROM pagamentos')=='estornado'
    assert one(db,'SELECT estoque FROM cupcakes WHERE id=1')==30
    with sqlite3.connect(db) as con:
        assert con.execute('SELECT status_anterior,status_novo FROM pagamento_eventos ORDER BY id').fetchall()==[
          ('pendente','aprovado'),('aprovado','estornado')]
    assert admin_status(admin,'cancelado').status_code==422


def test_decline_combo_and_simple_item_restores_all_stock(env):
    buyer,_,_,db=env
    add(buyer,1,1)
    assert buyer.post('/combos/adicionar',data={'_csrf':csrf(buyer,'/combos'),
        'q_1':'2','q_2':'1'},follow_redirects=False).status_code==303
    link=checkout(buyer,'cartao_demo').headers['location']
    assert one(db,'SELECT estoque FROM cupcakes WHERE id=1')==27
    assert one(db,'SELECT estoque FROM cupcakes WHERE id=2')==24
    assert decide(buyer,link,'recusar').status_code==303
    assert one(db,'SELECT estoque FROM cupcakes WHERE id=1')==30
    assert one(db,'SELECT estoque FROM cupcakes WHERE id=2')==25


def test_a_combinar_remains_unverified_and_not_simulatable(env):
    buyer,admin,_,db=env
    add(buyer)
    link=checkout(buyer,'a_combinar').headers['location']
    assert 'A combinar' in buyer.get(link).text
    assert 'Simular aprovação' not in buyer.get(link).text
    assert decide(buyer,link,'aprovar').status_code==422
    assert one(db,'SELECT status FROM pagamentos')=='pendente'
    # Pedido recebido no sistema não equivale a pagamento; confirma apenas processamento.
    assert admin_status(admin,'confirmado').status_code==303
    assert one(db,'SELECT status FROM pagamentos')=='pendente'


def test_api_exposes_only_demo_status_and_invalid_secret_fails(env):
    buyer,_,other,db=env
    add(buyer)
    link=checkout(buyer).headers['location']
    token=link.rsplit('/',1)[-1]
    data=other.get('/api/pedido/'+token+'/status').json()
    assert data['pagamento']=={'tipo':'pix_demo','status':'pendente','demonstrativo':True}
    assert 'contato_email' not in str(data)
    assert other.post('/pedido/!invalid/simular-pagamento',data={'decisao':'aprovar'}).status_code==403
    assert other.post('/pedido/'+token+'/simular-pagamento',data={'_csrf':'outro','decisao':'aprovar'}).status_code==403
    assert one(db,'SELECT status FROM pagamentos')=='pendente'


def test_migration_from_version6_preserves_existing_order(env):
    buyer,_,_,db=env
    add(buyer)
    checkout(buyer,'a_combinar')
    with sqlite3.connect(db) as con:
        expected=con.execute('SELECT id,total_centavos FROM pedidos').fetchall()
        con.execute('DROP TABLE pagamento_eventos')
        con.execute('DROP INDEX idx_pagamento_eventos_pagamento') if False else None
        con.execute('PRAGMA user_version=6')
    create_app(db,testing=True)
    create_app(db,testing=True)
    with sqlite3.connect(db) as con:
        assert con.execute('PRAGMA user_version').fetchone()[0]==max(MIGRATIONS)
        assert con.execute('SELECT id,total_centavos FROM pedidos').fetchall()==expected
        assert con.execute('PRAGMA foreign_key_check').fetchall()==[]
        assert con.execute("SELECT name FROM sqlite_master WHERE name='pagamento_eventos'").fetchone()


def test_payment_is_never_a_real_gateway_even_if_approved(env):
    buyer,_,_,db=env
    add(buyer)
    link=checkout(buyer).headers['location']
    decide(buyer,link,'aprovar')
    with sqlite3.connect(db) as con:
        pay=con.execute('SELECT provedor,referencia_externa,status FROM pagamentos').fetchone()
        assert pay==('simulador_local',None,'aprovado')
        assert con.execute("SELECT COUNT(*) FROM notificacoes WHERE canal IN ('sms','email')").fetchone()[0]==0
    assert 'Nenhum gateway de pagamento está conectado' in buyer.get(link).text


def test_decline_releases_coupon_and_does_not_use_limited_code(env):
    buyer,admin,_,db=env
    r=admin.post('/admin/cupons/criar',data={
        '_csrf':csrf(admin,'/admin/cupons'),'codigo':'REUSAVEL10',
        'tipo':'percentual','valor':'10','minimo':'0','limite':'1'},follow_redirects=False)
    assert r.status_code==303
    add(buyer)
    link=checkout(buyer,cupom='REUSAVEL10').headers['location']
    assert one(db,'SELECT COUNT(*) FROM cupom_utilizacoes')==1
    assert decide(buyer,link,'recusar').status_code==303
    assert one(db,'SELECT COUNT(*) FROM cupom_utilizacoes')==0
    # Um novo pedido pode reutilizar o cupom após a recusa simulada.
    add(buyer)
    second=checkout(buyer,cupom='REUSAVEL10')
    assert second.status_code==303
    assert one(db,'SELECT COUNT(*) FROM cupom_utilizacoes')==1


def test_concurrent_duplicate_approval_is_serialized(env):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    buyer,_,other,db=env
    add(buyer)
    link=checkout(buyer).headers['location']
    token1=csrf(buyer,'/')
    token2=csrf(other,'/')
    sync=Barrier(2)
    def worker(client,csrf_token):
        sync.wait()
        return client.post(link+'/simular-pagamento',data={
            '_csrf':csrf_token,'decisao':'aprovar'},follow_redirects=False).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        f1=pool.submit(worker,buyer,token1)
        f2=pool.submit(worker,other,token2)
        assert sorted([f1.result(),f2.result()])==[303,303]
    assert one(db,'SELECT COUNT(*) FROM pagamento_eventos')==1
    assert one(db,'SELECT status FROM pagamentos')=='aprovado'


def test_invalid_decision_and_cancelled_payment_are_rejected(env):
    buyer,admin,_,db=env
    add(buyer)
    link=checkout(buyer).headers['location']
    assert decide(buyer,link,'fraude').status_code==422
    assert one(db,'SELECT status FROM pagamentos')=='pendente'
    # Cancelamento administrativo antes da decisão não permite aprovação posterior.
    assert admin_status(admin,'cancelado').status_code==303
    assert decide(buyer,link,'aprovar').status_code==422
    assert one(db,'SELECT estoque FROM cupcakes WHERE id=1')==30
    assert one(db,'SELECT status FROM pagamentos')=='pendente'
