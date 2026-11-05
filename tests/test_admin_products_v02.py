"""Ciclo A.2: aceite parcial das US-16/17 e auditoria de estoque sem perder pedidos."""
import json
import re
import sqlite3

import pytest
from fastapi.testclient import TestClient

from app import create_app


def token(client, url='/'):
    result = client.get(url)
    assert result.status_code == 200, result.text[:400]
    m = re.search(r'name="_csrf" value="([^"]+)"', result.text)
    assert m, result.text[:200]
    return m.group(1)


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setenv('ADMIN_EMAIL', 'admin@doce.test')
    monkeypatch.setenv('ADMIN_PASSWORD', 'SenhaUltraForte123!')
    path = tmp_path/'cupcakes.db'
    app = create_app(path, testing=True)
    adm, buyer = TestClient(app), TestClient(app)
    assert adm.post('/entrar', data={'_csrf': token(adm,'/entrar'),
        'email': 'admin@doce.test', 'senha':'SenhaUltraForte123!'}, follow_redirects=False).status_code == 303
    return adm, buyer, path


def submit_product(adm, **overrides):
    data = {'_csrf':token(adm,'/admin/produtos/novo'), 'categoria_id':'1',
            'nome':'Cupcake de Teste', 'descricao':'Cupcake para auditoria',
            'estoque':'6', 'preco':'18,90', 'imagem_id':'chocolate'}
    data.update(overrides)
    return adm.post('/admin/produtos/salvar', data=data, follow_redirects=False)


def make_order(buyer, product_id=1, qty=2):
    assert buyer.post('/carrinho/adicionar', data={'_csrf':token(buyer),
         'produto_id':str(product_id), 'quantidade':str(qty)}, follow_redirects=False).status_code == 303
    return buyer.post('/checkout', data={'_csrf':token(buyer, '/checkout'),
        'nome':'Ana Maria','email':'ana@example.test', 'telefone':'(65) 99999-9999',
        'opcao_entrega':'1','endereco':''},follow_redirects=False)


def test_admin_create_edit_snapshots_and_stock_movements(env):
    admin,_,db_path=env
    assert submit_product(admin).status_code==303
    with sqlite3.connect(db_path) as db:
        id=db.execute("SELECT id FROM cupcakes WHERE nome='Cupcake de Teste'").fetchone()[0]
        logs=db.execute("SELECT acao,descricao FROM auditoria WHERE entidade='cupcakes' AND entidade_id=?",(id,)).fetchall()
        assert len(logs)==1
        assert logs[0][0]=='criar produto'
        data=json.loads(logs[0][1])
        assert data['antes'] is None and data['depois']['estoque']==6
    assert submit_product(admin, id=str(id), nome='Cupcake Teste Atualizado', preco='20,00', estoque='9').status_code==303
    with sqlite3.connect(db_path) as db:
        log=db.execute("SELECT descricao FROM auditoria WHERE entidade='cupcakes' AND entidade_id=? ORDER BY id DESC LIMIT 1",(id,)).fetchone()[0]
        changes=json.loads(log)
        assert changes['antes']['preco_centavos']==1890 and changes['depois']['preco_centavos']==2000
        assert changes['antes']['estoque']==6 and changes['depois']['estoque']==9
        movements=db.execute('SELECT variacao,motivo FROM estoque_movimentos WHERE cupcake_id=?',(id,)).fetchall()
        assert movements==[(3,'Ajuste manual pelo administrador')]
    page=admin.get(f'/admin/produtos/{id}/historico')
    assert page.status_code==200
    assert 'editar produto' in page.text and 'criar produto' in page.text
    assert 'Estoque' in page.text or 'estoque' in page.text


def test_noop_edit_does_not_create_false_event_or_movement(env):
    admin,_,db_path=env
    assert submit_product(admin).status_code==303
    with sqlite3.connect(db_path) as db:
        id=db.execute("SELECT id FROM cupcakes WHERE nome='Cupcake de Teste'").fetchone()[0]
    assert submit_product(admin, id=str(id)).status_code==303
    with sqlite3.connect(db_path) as db:
        assert db.execute("SELECT COUNT(*) FROM auditoria WHERE entidade='cupcakes' AND entidade_id=?",(id,)).fetchone()[0]==1
        assert db.execute('SELECT COUNT(*) FROM estoque_movimentos WHERE cupcake_id=?',(id,)).fetchone()[0]==0


def test_exclusao_bloqueada_por_pedido_ativo_sem_alterar_auditoria(env):
    admin,buyer,path=env
    assert make_order(buyer).status_code==303
    with sqlite3.connect(path) as db:
        before=db.execute("SELECT COUNT(*) FROM auditoria WHERE entidade='cupcakes' AND entidade_id=1").fetchone()[0]
    response=admin.post('/admin/produtos/1/excluir',data={'_csrf':token(admin,'/admin')},follow_redirects=False)
    assert response.status_code==422
    assert 'pedido ativo' in response.text
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT ativo,excluido_em FROM cupcakes WHERE id=1').fetchone()==(1,None)
        assert db.execute("SELECT COUNT(*) FROM auditoria WHERE entidade='cupcakes' AND entidade_id=1").fetchone()[0]==before
    assert 'Chocolate da Casa' in buyer.get('/').text


def test_exclusao_sem_pedido_preserva_integridade_e_impede_reativar(env):
    admin,buyer,path=env
    r=admin.post('/admin/produtos/1/excluir',data={'_csrf':token(admin,'/admin')},follow_redirects=False)
    assert r.status_code==303
    assert 'Chocolate da Casa' not in buyer.get('/').text
    assert buyer.get('/produto/1').status_code==404
    assert 'Chocolate da Casa' not in admin.get('/admin').text.split('Produtos</h2>')[1].split('Produtos excluídos')[0]
    assert admin.get('/admin/produtos/1/editar').status_code==404
    assert admin.post('/admin/produtos/1/alternar',data={'_csrf':token(admin,'/admin')},follow_redirects=False).status_code==404
    assert admin.post('/admin/produtos/1/excluir',data={'_csrf':token(admin,'/admin')},follow_redirects=False).status_code==404
    with sqlite3.connect(path) as db:
        item=db.execute('SELECT ativo,excluido_em,estoque FROM cupcakes WHERE id=1').fetchone()
        assert item[0]==0 and item[1] is not None and item[2]==30
        audit=db.execute("SELECT descricao FROM auditoria WHERE entidade='cupcakes' AND acao='excluir produto' AND entidade_id=1").fetchone()[0]
        assert json.loads(audit)['antes']['ativo']==1
    assert admin.get('/admin/produtos/1/historico').status_code==200


def test_exclusao_pedido_concluido_preserva_historico_financeiro(env):
    admin,buyer,path=env
    assert make_order(buyer).status_code==303
    with sqlite3.connect(path) as db:
        db.execute("UPDATE pedidos SET status='concluido' WHERE id=1")
    assert admin.post('/admin/produtos/1/excluir',data={'_csrf':token(admin,'/admin')},follow_redirects=False).status_code==303
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT nome_snapshot, preco_unitario_centavos FROM pedido_itens WHERE cupcake_id=1').fetchone()==('Chocolate da Casa', 1250)
        assert db.execute('SELECT COUNT(*) FROM pedidos').fetchone()[0]==1
        assert db.execute('PRAGMA foreign_key_check').fetchall()==[]


def test_bloqueia_exclusao_em_combo_ativo(env):
    admin,_,path=env
    with sqlite3.connect(path) as db:
        combo=db.execute("INSERT INTO combos(nome, preco_centavos,ativo) VALUES('Caixa de teste',2500,1)").lastrowid
        db.execute('INSERT INTO combo_itens(combo_id,cupcake_id,quantidade) VALUES(?,?,?)',(combo,1,1))
    r=admin.post('/admin/produtos/1/excluir',data={'_csrf':token(admin,'/admin')},follow_redirects=False)
    assert r.status_code==422 and 'combo ativo' in r.text


def test_csrf_auth_and_input_validation_of_stock(env):
    admin,buyer,path=env
    assert buyer.get('/admin/produtos/1/historico').status_code==403
    assert buyer.post('/admin/produtos/1/excluir',data={'_csrf':token(buyer)},follow_redirects=False).status_code==403
    assert admin.post('/admin/produtos/1/excluir',data={},follow_redirects=False).status_code==403
    assert submit_product(admin,id='1',estoque='-1').status_code==422
    assert submit_product(admin,id='1',estoque='100001').status_code==422
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT estoque FROM cupcakes WHERE id=1').fetchone()[0]==30


def test_migration_v1_to_v2_preserves_legacy_rows(tmp_path,monkeypatch):
    path=tmp_path/'legacy.db'
    create_app(path,testing=True)
    with sqlite3.connect(path) as db:
        db.execute("UPDATE cupcakes SET nome='Cupcake Histórico' WHERE id=1")
        db.execute('DROP INDEX idx_cupcakes_arquivados')
        db.execute('ALTER TABLE cupcakes DROP COLUMN excluido_em')
        db.execute('PRAGMA user_version=1')
    create_app(path,testing=True)
    with sqlite3.connect(path) as db:
        assert db.execute('PRAGMA user_version').fetchone()[0]==6
        assert db.execute("SELECT nome,excluido_em FROM cupcakes WHERE id=1").fetchone()==('Cupcake Histórico',None)
        assert db.execute('PRAGMA foreign_key_check').fetchall()==[]
    create_app(path,testing=True)


def test_old_migration_with_reset_version_is_idempotent(tmp_path):
    path=tmp_path/'reset.db'
    create_app(path,testing=True)
    with sqlite3.connect(path) as db:
        db.execute('PRAGMA user_version = 0')
        db.execute('DROP INDEX idx_catalogo_ativo_estoque_categoria')
    create_app(path,testing=True)
    with sqlite3.connect(path) as db:
        assert db.execute('PRAGMA user_version').fetchone()[0]==6
        assert db.execute('SELECT COUNT(*) FROM cupcakes').fetchone()[0]==8
