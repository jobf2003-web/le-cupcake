"""Ciclo D: US-06, US-11, US-18, US-19, US-21 e US-22.

Notificações são INTERNAS. Nenhum teste afirma envio real por SMS/e-mail.
"""
import json
import re
import sqlite3
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app import create_app


def csrf(client,url='/'):
    r=client.get(url)
    assert r.status_code==200,r.text[:250]
    m=re.search(r'name="_csrf" value="([^"]+)"',r.text)
    assert m,url
    return m.group(1)


@pytest.fixture
def clients(tmp_path,monkeypatch):
    monkeypatch.setenv('ADMIN_EMAIL','admin@doce.test')
    monkeypatch.setenv('ADMIN_PASSWORD','SenhaUltraForte123!')
    db=tmp_path/'le_cupcake.db'
    app=create_app(db,testing=True)
    admin,buyer,other=TestClient(app),TestClient(app),TestClient(app)
    assert admin.post('/entrar',data={'_csrf':csrf(admin,'/entrar'),
        'email':'admin@doce.test','senha':'SenhaUltraForte123!'},follow_redirects=False).status_code==303
    return admin,buyer,other,db


def register(client,email='cliente@doce.test',name='Cliente de Teste'):
    return client.post('/conta/cadastrar',data={'_csrf':csrf(client,'/conta/cadastrar'),
        'nome':name,'email':email,'senha':'SenhaUltraForte123!'},follow_redirects=False)


def add(client,product=1,qty=2):
    return client.post('/carrinho/adicionar',data={'_csrf':csrf(client),
        'produto_id':str(product),'quantidade':str(qty)},follow_redirects=False)


def checkout(client):
    return client.post('/checkout',data={'_csrf':csrf(client,'/checkout'),
        'nome':'Cliente de Teste','email':'cliente@doce.test','telefone':'(65) 99999-9999',
        'opcao_entrega':'1','endereco':''},follow_redirects=False)


def status(admin,order_id=1,next_status='confirmado',eta=''):
    data={'_csrf':csrf(admin,'/admin/pedidos'),'status':next_status}
    if eta:data['previsao_entrega']=eta
    return admin.post(f'/admin/pedidos/{order_id}/status',data=data,follow_redirects=False)


def test_schema_v6_is_idempotent_and_keeps_orders(clients):
    admin,buyer,_,db=clients
    add(buyer)
    assert checkout(buyer).status_code==303
    with sqlite3.connect(db) as con:
        assert con.execute('PRAGMA user_version').fetchone()[0]==6
        assert 'previsao_entrega_em' in {x[1] for x in con.execute('PRAGMA table_info(pedidos)')}
        before=con.execute('SELECT id,total_centavos FROM pedidos').fetchall()
    create_app(db,testing=True)
    with sqlite3.connect(db) as con:
        assert before==con.execute('SELECT id,total_centavos FROM pedidos').fetchall()
        assert con.execute('PRAGMA foreign_key_check').fetchall()==[]


def test_admin_receives_internal_new_order_alert_and_can_mark_read(clients):
    admin,buyer,_,db=clients
    assert add(buyer).status_code==303
    assert checkout(buyer).status_code==303
    page=admin.get('/admin/notificacoes').text
    assert 'Novo pedido #1' in page
    assert 'SMS/e-mail externo' in page
    with sqlite3.connect(db) as con:
        assert con.execute("SELECT canal,status FROM notificacoes").fetchall()==[('app','pendente')]
    assert admin.post('/admin/notificacoes/ler',data={'_csrf':csrf(admin,'/admin/notificacoes')},follow_redirects=False).status_code==303
    with sqlite3.connect(db) as con:
        assert con.execute('SELECT status FROM notificacoes').fetchone()[0]=='lida'
    assert 'Avisos internos (0)' in admin.get('/admin').text


def test_order_state_notification_private_and_after_status_change(clients):
    admin,buyer,other,db=clients
    assert register(buyer).status_code==303
    assert add(buyer).status_code==303
    order=checkout(buyer)
    assert order.status_code==303
    path=order.headers['location']
    assert 'Avisos sobre seus pedidos' in buyer.get('/minha-conta').text
    assert 'Pedido #1 registrado' in buyer.get('/minha-conta').text
    assert other.get('/minha-conta').status_code==403
    assert other.get('/admin/notificacoes').status_code==403
    assert status(admin).status_code==303
    own=buyer.get('/minha-conta').text
    assert 'Pedido #1: Confirmado.' in own
    assert 'Pedido #1: Confirmado.' not in other.get('/').text
    assert buyer.post('/minha-conta/notificacoes/ler',data={},follow_redirects=False).status_code==403
    with sqlite3.connect(db) as con:
        assert con.execute("SELECT COUNT(*) FROM notificacoes WHERE canal='email' OR canal='sms'").fetchone()[0]==0
        assert con.execute("SELECT COUNT(*) FROM notificacoes WHERE usuario_id=2").fetchone()[0]==2
    assert buyer.post('/minha-conta/notificacoes/ler',data={'_csrf':csrf(buyer,'/minha-conta')},follow_redirects=False).status_code==303
    assert 'Novo' not in buyer.get('/minha-conta').text.split('Avisos sobre seus pedidos')[1].split('</section>')[0]
    assert buyer.get(path).status_code==200


def test_status_api_token_privacy_and_polling_markup(clients):
    admin,buyer,other,db=clients
    add(buyer)
    response=checkout(buyer)
    assert response.status_code==303
    path=response.headers['location']
    secret=path.rsplit('/',1)[-1]
    html=buyer.get(path).text
    assert 'pedido-acompanhamento' in html and 'pedido-eventos' in html
    api=other.get(f'/api/pedido/{secret}/status')
    assert api.status_code==200
    assert api.headers['cache-control']=='no-store'
    assert api.json()['status']=='recebido'
    assert 'contato_email' not in api.text and 'contato_telefone' not in api.text
    assert other.get('/api/pedido/naoexiste12345/status').status_code==404
    assert other.get('/api/pedido/!invalid/status').status_code==404
    assert 'setInterval(refreshOrder, 15000)' in buyer.get('/static/app.js').text


def test_status_eta_validation_commit_and_no_changes_on_failure(clients):
    admin,buyer,_,db=clients
    add(buyer)
    p=checkout(buyer)
    assert p.status_code==303
    assert status(admin,next_status='confirmado',eta='data inválida').status_code==422
    with sqlite3.connect(db) as con:
        assert con.execute('SELECT status,previsao_entrega_em FROM pedidos').fetchone()==('recebido',None)
    eta=(datetime.now()+timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
    assert status(admin,next_status='confirmado',eta=eta).status_code==303
    with sqlite3.connect(db) as con:
        assert con.execute('SELECT status,previsao_entrega_em FROM pedidos').fetchone()==('confirmado',eta)
    token=p.headers['location'].split('/')[-1]
    assert buyer.get('/api/pedido/'+token+'/status').json()['previsao_entrega_em']==eta
    assert eta in buyer.get(p.headers['location']).text
    assert status(admin,next_status='confirmado').status_code==422
    with sqlite3.connect(db) as con:
        assert con.execute("SELECT COUNT(*) FROM eventos_pedido WHERE status='confirmado'").fetchone()[0]==1


def test_customer_admin_edit_with_audit_and_duplicate_rejection(clients):
    admin,buyer,other,db=clients
    register(buyer,email='primeira@doce.test')
    register(other,email='segunda@doce.test')
    assert 'Editar' in admin.get('/admin/clientes').text
    assert buyer.get('/admin/clientes/2/editar').status_code==403
    assert admin.get('/admin/clientes/2/editar').status_code==200
    token=csrf(admin,'/admin/clientes/2/editar')
    dup=admin.post('/admin/clientes/2/salvar',data={
        '_csrf':token,'nome':'Outro Nome Teste','email':'segunda@doce.test'},follow_redirects=False)
    assert dup.status_code==422
    assert admin.post('/admin/clientes/2/salvar',data={
        '_csrf':token,'nome':'Cliente Atualizado','email':'novo@doce.test'},follow_redirects=False).status_code==303
    assert 'Cliente Atualizado' in buyer.get('/minha-conta').text
    history=admin.get('/admin/clientes/2/historico')
    assert history.status_code==200 and 'editar cadastro' in history.text
    assert 'novo@doce.test' in history.text
    with sqlite3.connect(db) as con:
        desc=con.execute("SELECT descricao FROM auditoria WHERE entidade='usuarios' AND acao='editar cadastro'").fetchone()[0]
        data=json.loads(desc)
        assert data['antes']['email']=='primeira@doce.test'
        assert data['depois']['email']=='novo@doce.test'


def test_admin_customer_blocking_is_audited(clients):
    admin,buyer,_,db=clients
    register(buyer)
    r=admin.post('/admin/clientes/2/alternar',data={'_csrf':csrf(admin,'/admin/clientes')},follow_redirects=False)
    assert r.status_code==303
    assert buyer.get('/minha-conta').status_code==403
    assert 'alternar acesso' in admin.get('/admin/clientes/2/historico').text
    with sqlite3.connect(db) as con:
        assert con.execute("SELECT ativo FROM usuarios WHERE id=2").fetchone()[0]==0
        assert '1 -> 0' in con.execute("SELECT descricao FROM auditoria WHERE acao='alternar acesso'").fetchone()[0]


def test_reports_category_month_filter_security_and_chart(clients):
    admin,buyer,_,db=clients
    add(buyer,1,2)
    assert checkout(buyer).status_code==303
    html=admin.get('/admin/relatorios').text
    assert 'R$ 25,00' in html
    assert 'Chocolate da Casa' in html
    assert 'report-show-value' in html and 'report-bars' in html
    assert buyer.get('/admin/relatorios').status_code==403
    assert admin.get('/admin/relatorios?categoria=999').status_code==422
    assert admin.get('/admin/relatorios?categoria=abc').status_code==422
    assert admin.get('/admin/relatorios?mes=2026-99').status_code==422
    html=admin.get('/admin/relatorios?categoria=1').text
    assert 'Clássicos' in html and 'R$ 25,00' in html
    assert 'Chocolate da Casa' in html
    assert 'componentes dos combos' in html
    html=admin.get('/admin/relatorios?categoria=2').text
    assert 'Frutados' in html
    assert 'Nenhuma venda demonstrativa' in html
    with sqlite3.connect(db) as con:
        month=con.execute('SELECT substr(criado_em,1,7) FROM pedidos').fetchone()[0]
    assert 'Chocolate da Casa' in admin.get('/admin/relatorios?mes='+month).text
    assert 'Sem dados para os filtros' in admin.get('/admin/relatorios?mes=2099-01').text


def test_report_counts_combo_components_and_excludes_cancelled(clients):
    admin,buyer,_,db=clients
    r=buyer.post('/combos/adicionar',data={'_csrf':csrf(buyer,'/combos'),
        'q_1':'2','q_3':'1'},follow_redirects=False)
    assert r.status_code==303
    assert checkout(buyer).status_code==303
    classic=admin.get('/admin/relatorios?categoria=1').text
    fruity=admin.get('/admin/relatorios?categoria=2').text
    assert 'Chocolate da Casa' in classic and '2</td>' in classic
    assert 'Morango dos Sonhos' in fruity and '1</td>' in fruity
    assert 'R$ 25,00' in classic
    assert 'R$ 14,00' in fruity
    assert status(admin,next_status='cancelado').status_code==303
    assert 'Chocolate da Casa' not in admin.get('/admin/relatorios?categoria=1').text
    assert 'Morango dos Sonhos' not in admin.get('/admin/relatorios?categoria=2').text


def test_guest_order_admin_notice_not_wrong_customer(clients):
    admin,buyer,_,db=clients
    assert add(buyer).status_code==303
    assert checkout(buyer).status_code==303
    with sqlite3.connect(db) as con:
        assert con.execute('SELECT usuario_id,canal FROM notificacoes').fetchall()==[(1,'app')]
    assert 'Novo pedido #1' in admin.get('/admin/notificacoes').text
