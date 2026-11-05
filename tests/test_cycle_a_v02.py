"""Etapa 2 ciclo A: migração compatível, catálogo dinâmico e cancelamento antes da produção."""
import re
import sqlite3
from fastapi.testclient import TestClient
from app import create_app


def csrf(client, url='/'):
    r = client.get(url)
    assert r.status_code == 200, r.text[:500]
    m = re.search(r'name="_csrf" value="([^"]+)"', r.text)
    assert m
    return m.group(1)


def test_migracao_preserva_banco_ja_existente(tmp_path, monkeypatch):
    monkeypatch.setenv('ADMIN_EMAIL', 'admin@teste.local')
    monkeypatch.setenv('ADMIN_PASSWORD', 'SenhaSegura123456')
    database = tmp_path / 'legado.db'
    create_app(database, testing=True)
    with sqlite3.connect(database) as db:
        assert db.execute('PRAGMA user_version').fetchone()[0] == 7
        assert db.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchone()[0] == 27
        db.execute("UPDATE cupcakes SET estoque=7 WHERE id=1")
        db.execute('PRAGMA user_version = 0')
        db.execute('DROP INDEX idx_catalogo_ativo_estoque_categoria')
    create_app(database, testing=True)
    with sqlite3.connect(database) as db:
        assert db.execute('PRAGMA user_version').fetchone()[0] == 7
        assert db.execute('SELECT estoque FROM cupcakes WHERE id=1').fetchone()[0] == 7
        assert db.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchone()[0] == 27
        assert db.execute("SELECT 1 FROM sqlite_master WHERE name='idx_catalogo_ativo_estoque_categoria'").fetchone()
    create_app(database, testing=True)


def test_rejeita_schema_futuro_sem_modificar_dados(tmp_path):
    from pytest import raises
    database = tmp_path / 'futuro.db'
    create_app(database, testing=True)
    with sqlite3.connect(database) as db:
        db.execute('PRAGMA user_version = 100')
    with raises(RuntimeError, match='esquema futuro'):
        create_app(database, testing=True)
    with sqlite3.connect(database) as db:
        assert db.execute('PRAGMA user_version').fetchone()[0] == 100
        assert db.execute('SELECT COUNT(*) FROM cupcakes').fetchone()[0] == 8


def test_catalogo_sem_recarga_e_filtros_combinados(tmp_path):
    c = TestClient(create_app(tmp_path/'catalogo.db', testing=True))
    home = c.get('/')
    assert home.status_code == 200
    assert 'id="catalogo-resultados"' in home.text
    assert 'id="catalogo-filtro"' in home.text
    assert 'id="catalogo-categorias"' in home.text
    js = c.get('/static/app.js').text
    assert 'fetch(url' in js and 'history.replaceState' in js
    result = c.get('/catalogo/resultados', params={'busca':'limão','categoria':'Frutados'})
    assert result.status_code == 200
    assert result.headers['x-total-results'] == '1'
    assert 'Limão Fresquinho' in result.text
    assert 'Chocolate da Casa' not in result.text
    assert '<html' not in result.text.lower()
    assert '_csrf' in result.text
    assert c.get('/?busca=limão&categoria=Frutados').status_code == 200
    assert 'Limão Fresquinho' in c.get('/?busca=limão&categoria=Frutados').text


def test_filtro_exclui_esgotado_mas_vitrine_geral_sinaliza(tmp_path):
    db_path = tmp_path/'estoque.db'
    c = TestClient(create_app(db_path, testing=True))
    with sqlite3.connect(db_path) as db:
        db.execute('UPDATE cupcakes SET estoque=0 WHERE id=1')
    assert 'Chocolate da Casa' in c.get('/').text
    assert 'Esgotado' in c.get('/').text
    assert 'Chocolate da Casa' not in c.get('/catalogo/resultados?busca=Chocolate').text
    assert 'Chocolate da Casa' not in c.get('/?categoria=Clássicos').text
    assert 'Baunilha Encantada' in c.get('/?categoria=Clássicos').text


def test_cancelamento_so_antes_da_producao(tmp_path, monkeypatch):
    monkeypatch.setenv('ADMIN_EMAIL','admin@doce.test')
    monkeypatch.setenv('ADMIN_PASSWORD','SenhaUltraForte123!')
    db_path = tmp_path/'pedidos.db'
    c = TestClient(create_app(db_path, testing=True))
    t = csrf(c)
    assert c.post('/carrinho/adicionar',data={'_csrf':t,'produto_id':'1','quantidade':'2'},follow_redirects=False).status_code == 303
    t = csrf(c,'/checkout')
    data={'_csrf':t,'nome':'Ana Maria','email':'ana@example.com','telefone':'(65) 99999-9999','opcao_entrega':'1','endereco':''}
    assert c.post('/checkout',data=data,follow_redirects=False).status_code == 303
    t = csrf(c,'/entrar')
    assert c.post('/entrar',data={'_csrf':t,'email':'admin@doce.test','senha':'SenhaUltraForte123!'},follow_redirects=False).status_code == 303
    for old in ['preparo', 'pronto', 'em_entrega']:
        with sqlite3.connect(db_path) as db:
            db.execute('UPDATE pedidos SET status=? WHERE id=1',(old,))
        t = csrf(c,'/admin/pedidos')
        response = c.post('/admin/pedidos/1/status',data={'_csrf':t,'status':'cancelado'},follow_redirects=False)
        assert response.status_code == 422
        with sqlite3.connect(db_path) as db:
            assert db.execute('SELECT status FROM pedidos WHERE id=1').fetchone()[0] == old
            assert db.execute('SELECT estoque FROM cupcakes WHERE id=1').fetchone()[0] == 28
            assert db.execute('SELECT COUNT(*) FROM estoque_movimentos WHERE motivo="Pedido cancelado"').fetchone()[0] == 0
    with sqlite3.connect(db_path) as db:
        db.execute("UPDATE pedidos SET status='confirmado' WHERE id=1")
    t = csrf(c,'/admin/pedidos')
    assert c.post('/admin/pedidos/1/status',data={'_csrf':t,'status':'cancelado'},follow_redirects=False).status_code == 303
    with sqlite3.connect(db_path) as db:
        assert db.execute('SELECT estoque FROM cupcakes WHERE id=1').fetchone()[0] == 30
        assert db.execute('SELECT COUNT(*) FROM estoque_movimentos WHERE motivo="Pedido cancelado"').fetchone()[0] == 1
