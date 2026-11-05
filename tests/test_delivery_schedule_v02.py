"""Ciclo B1: frete local por CEP e agendamento demonstrativo, com autoridade do servidor."""
from datetime import date, timedelta
import re
import sqlite3

import pytest
from fastapi.testclient import TestClient
from app import create_app


def token(client, path='/'):
    r=client.get(path)
    assert r.status_code == 200, r.text[:250]
    m=re.search(r'name="_csrf" value="([^"]+)"',r.text)
    assert m, path
    return m.group(1)


@pytest.fixture
def state(tmp_path,monkeypatch):
    monkeypatch.setenv('ADMIN_EMAIL','admin@doce.test')
    monkeypatch.setenv('ADMIN_PASSWORD','SenhaUltraForte123!')
    path=tmp_path/'loja.db'
    app=create_app(path,testing=True)
    admin,buyer=TestClient(app),TestClient(app)
    assert admin.post('/entrar',data={'_csrf':token(admin,'/entrar'),
        'email':'admin@doce.test','senha':'SenhaUltraForte123!'},follow_redirects=False).status_code==303
    return admin,buyer,path


def region(admin,start='70000000',end='70009999',price='4,00'):
    return admin.post('/admin/entregas/regioes/criar',data={
        '_csrf':token(admin,'/admin/entregas'),'descricao':'Faixa de teste',
        'cep_inicio':start,'cep_fim':end,'adicional':price},follow_redirects=False)


def window(admin,method=2,capacity=1,start='09:00',end='11:00'):
    return admin.post('/admin/entregas/janelas/criar',data={
        '_csrf':token(admin,'/admin/entregas'),'opcao_entrega':str(method),
        'inicio':start,'fim':end,'capacidade':str(capacity)},follow_redirects=False)


def order(buyer,method=2,**extra):
    csrf=token(buyer,'/checkout')
    data={'_csrf':csrf,'nome':'Ana Maria','email':'ana@example.com',
          'telefone':'(65) 99999-9999','opcao_entrega':str(method),
          'endereco':'Avenida Teste, 123, Bairro Exemplo, Município Fictício'}
    data.update(extra)
    return buyer.post('/checkout',data=data,follow_redirects=False)


def add(buyer,product=1,qty=1):
    return buyer.post('/carrinho/adicionar',data={'_csrf':token(buyer),
        'produto_id':str(product),'quantidade':str(qty)},follow_redirects=False)


def test_admin_regions_and_server_quote(state):
    admin,buyer,_=state
    assert region(admin).status_code==303
    assert buyer.get('/api/frete?opcao_entrega=2&cep=70000-100').json()['frete_centavos']==1200
    assert buyer.get('/api/frete?opcao_entrega=1&cep=00000000').json()['frete_centavos']==0
    bad=buyer.get('/api/frete?opcao_entrega=2&cep=99000-000')
    assert bad.status_code==422 and 'fora das regiões' in bad.text
    assert buyer.get('/api/frete?opcao_entrega=2&cep=abc').status_code==422
    assert 'Regiões por CEP' in admin.get('/admin/entregas').text


def test_no_overlapping_active_regions_and_auth(state):
    admin,buyer,path=state
    assert buyer.post('/admin/entregas/regioes/criar',data={'_csrf':token(buyer)},follow_redirects=False).status_code==403
    assert region(admin).status_code==303
    assert region(admin,'70009000','70015000').status_code==422
    assert region(admin,'70010000','70019999').status_code==303
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT COUNT(*) FROM regioes_entrega').fetchone()[0]==2


def test_delivery_requires_cep_when_region_active_and_saves_server_quote(state):
    admin,buyer,path=state
    assert region(admin).status_code==303
    assert add(buyer).status_code==303
    r=order(buyer)
    assert r.status_code==422 and 'CEP válido' in r.text
    r=order(buyer,cep='70000-555')
    assert r.status_code==303, r.text[:200]
    with sqlite3.connect(path) as db:
        shipping,cep,reg,total=db.execute('SELECT frete_centavos,cep_entrega,regiao_entrega_id,total_centavos FROM pedidos').fetchone()
        assert shipping==1200 and cep=='70000555' and reg==1 and total==2450


def test_pickup_has_no_freight_even_if_admin_attempts_to_charge(state):
    admin,buyer,path=state
    csrf=token(admin,'/admin/entregas')
    r=admin.post('/admin/entregas/1/salvar',data={'_csrf':csrf,'descricao':'Retirada local','custo':'99,00','ativo':'1'},follow_redirects=False)
    assert r.status_code==303
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT custo_base_centavos FROM opcoes_entrega WHERE id=1').fetchone()[0]==0
    assert add(buyer).status_code==303
    r=order(buyer,method=1,endereco='')
    assert r.status_code==303
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT frete_centavos FROM pedidos').fetchone()[0]==0


def test_scheduled_pickup_capacity_and_cancel_reopens_slot(state):
    admin,buyer,path=state
    assert window(admin,method=1,capacity=1).status_code==303
    scheduled=(date.today()+timedelta(days=2)).isoformat()
    assert add(buyer).status_code==303
    assert order(buyer,method=1,endereco='').status_code==422
    r=order(buyer,method=1,endereco='',data_agendada=scheduled,janela_entrega='1')
    assert r.status_code==303
    assert scheduled in buyer.get(r.headers['location']).text
    other=TestClient(buyer.app)
    assert add(other,2).status_code==303
    bad=order(other,method=1,endereco='',data_agendada=scheduled,janela_entrega='1')
    assert bad.status_code==422 and 'esgotou' in bad.text
    csrf=token(admin,'/admin/pedidos')
    assert admin.post('/admin/pedidos/1/status',data={'_csrf':csrf,'status':'cancelado'},follow_redirects=False).status_code==303
    good=order(other,method=1,endereco='',data_agendada=scheduled,janela_entrega='1')
    assert good.status_code==303
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT COUNT(*) FROM pedidos WHERE agendado_para=?',(scheduled,)).fetchone()[0]==2


def test_schedule_rejects_wrong_option_or_dates(state):
    admin,buyer,_=state
    assert window(admin,method=2,capacity=2).status_code==303
    assert add(buyer).status_code==303
    today=date.today()
    for dt in [today-timedelta(days=1),today+timedelta(days=16)]:
        r=order(buyer,method=2, data_agendada=dt.isoformat(),janela_entrega='1')
        assert r.status_code==422 and '15 dias' in r.text
    r=order(buyer,method=1,endereco='',data_agendada=(today+timedelta(days=1)).isoformat(),janela_entrega='1')
    assert r.status_code==422


def test_blackout_blocks_checkout_and_can_be_removed(state):
    admin,buyer,_=state
    assert window(admin,method=1).status_code==303
    scheduled=(date.today()+timedelta(days=2)).isoformat()
    r=admin.post('/admin/entregas/bloqueios/criar',data={
        '_csrf':token(admin,'/admin/entregas'),'opcao_entrega':'1','data':scheduled,'motivo':'Loja fechada'},follow_redirects=False)
    assert r.status_code==303
    assert add(buyer).status_code==303
    bad=order(buyer,method=1,endereco='',data_agendada=scheduled,janela_entrega='1')
    assert bad.status_code==422 and 'não há atendimento' in bad.text.lower()
    r=admin.post('/admin/entregas/bloqueios/1/remover',data={
        '_csrf':token(admin,'/admin/entregas')},follow_redirects=False)
    assert r.status_code==303
    assert order(buyer,method=1,endereco='',data_agendada=scheduled,janela_entrega='1').status_code==303


def test_api_quote_and_calendar_do_not_modify_orders(state):
    admin,buyer,path=state
    region(admin)
    window(admin)
    for _ in range(3):
        buyer.get('/api/frete?opcao_entrega=2&cep=70000-000')
        buyer.get('/checkout')
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT COUNT(*) FROM pedidos').fetchone()[0]==0
        assert db.execute('PRAGMA user_version').fetchone()[0]==6
        assert db.execute('PRAGMA foreign_key_check').fetchall()==[]
