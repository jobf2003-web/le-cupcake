"""Testes automatizados dos fluxos mais importantes da loja acadêmica."""
import re
import sqlite3
from urllib.parse import urlparse

import pytest
from fastapi.testclient import TestClient

from app import create_app, parse_brl, reais


def token(client, path='/'):
    page = client.get(path)
    assert page.status_code == 200, page.text[:500]
    match = re.search(r'name="_csrf" value="([^"]+)"', page.text)
    assert match, f'Sem token CSRF em {path}'
    return match.group(1)


@pytest.fixture
def setup(tmp_path, monkeypatch):
    monkeypatch.setenv('ADMIN_EMAIL', 'admin@doce.test')
    monkeypatch.setenv('ADMIN_PASSWORD', 'SenhaUltraForte123!')
    db_path = tmp_path / 'loja.db'
    app = create_app(db_path, testing=True)
    client = TestClient(app)
    return client, db_path


def add(client, product_id=1, quantity=1):
    csrf = token(client)
    return client.post('/carrinho/adicionar', data={
        '_csrf': csrf, 'produto_id': str(product_id), 'quantidade': str(quantity)
    }, follow_redirects=False)


def order(client, *, shipping=1, **overrides):
    csrf = token(client, '/checkout')
    data = {'_csrf': csrf, 'nome':'Ana Maria', 'email':'ana@example.com',
            'telefone':'(65) 99999-9999', 'opcao_entrega':str(shipping), 'endereco':''}
    data.update(overrides)
    return client.post('/checkout', data=data, follow_redirects=False)


def login(client):
    csrf = token(client, '/entrar')
    return client.post('/entrar', data={'_csrf': csrf, 'email':'admin@doce.test',
                          'senha':'SenhaUltraForte123!'}, follow_redirects=False)


def test_catalog_has_eight_products(setup):
    client, db_path = setup
    result = client.get('/')
    assert result.status_code == 200
    assert 'Chocolate da Casa' in result.text
    assert 'Red Velvet' in result.text
    with sqlite3.connect(db_path) as db:
        assert db.execute('SELECT COUNT(*) FROM cupcakes').fetchone()[0] == 8
        assert db.execute('SELECT COUNT(*) FROM sqlite_master WHERE type="table" AND name NOT LIKE "sqlite_%"').fetchone()[0] == 23


def test_filter_and_search_parameterized(setup):
    client, _ = setup
    assert 'Limão Fresquinho' in client.get('/?categoria=Frutados').text
    assert 'Chocolate da Casa' not in client.get('/?categoria=Frutados').text
    assert 'Red Velvet' in client.get('/?busca=velvet').text
    assert 'Nenhum cupcake encontrado' in client.get('/?busca=xxxxno').text
    assert client.get('/?busca=%27%20OR%201%3D1--').status_code == 200


def test_product_details(setup):
    client, _ = setup
    assert 'Chocolate da Casa' in client.get('/produto/1').text
    assert client.get('/produto/9000').status_code == 404


def test_cart_add_update_remove(setup):
    client, _ = setup
    assert add(client, 1, 2).status_code == 303
    assert 'R$ 25,00' in client.get('/carrinho').text
    csrf = token(client, '/carrinho')
    result = client.post('/carrinho/atualizar', data={'_csrf':csrf, 'produto_id':'1', 'quantidade':'3'}, follow_redirects=False)
    assert result.status_code == 303
    assert 'R$ 37,50' in client.get('/carrinho').text
    csrf = token(client, '/carrinho')
    result = client.post('/carrinho/remover', data={'_csrf':csrf, 'produto_id':'1'}, follow_redirects=False)
    assert result.status_code == 303
    assert 'Seu carrinho está vazio' in client.get('/carrinho').text


def test_cannot_add_beyond_stock(setup):
    client, _ = setup
    r = add(client, 1, 40)
    assert r.status_code == 303
    assert 'Estoque insuficiente' in client.get('/carrinho').text
    assert 'Seu carrinho está vazio' in client.get('/carrinho').text


def test_order_pickup_persists_and_reduces_inventory(setup):
    client, db_path = setup
    add(client, 1, 2)
    result = order(client)
    assert result.status_code == 303, result.text[:300]
    link = result.headers['location']
    assert link.startswith('/pedido/')
    page = client.get(link)
    assert page.status_code == 200
    assert 'Ana Maria' in page.text
    assert 'R$ 25,00' in page.text
    assert 'Seu pedido foi registrado com sucesso.' in page.text
    assert 'Seu carrinho está vazio' in client.get('/carrinho').text
    with sqlite3.connect(db_path) as db:
        assert db.execute('SELECT estoque FROM cupcakes WHERE id=1').fetchone()[0] == 28
        assert db.execute('SELECT COUNT(*) FROM pedidos').fetchone()[0] == 1
        assert db.execute('SELECT quantidade FROM pedido_itens').fetchone()[0] == 2
        assert db.execute('SELECT status FROM pagamentos').fetchone()[0] == 'pendente'


def test_delivery_address_required_and_fee(setup):
    client, db_path = setup
    add(client, 2, 1)
    bad = order(client, shipping=2)
    assert bad.status_code == 422
    assert 'Informe o endereço completo' in bad.text
    good = order(client, shipping=2, endereco='Rua das Flores, 123, Centro, Nova Xavantina - MT')
    assert good.status_code == 303
    with sqlite3.connect(db_path) as db:
        row = db.execute('SELECT frete_centavos,total_centavos,endereco_entrega FROM pedidos').fetchone()
        assert row[0] == 800
        assert row[1] == 1950
        assert 'Rua das Flores' in row[2]


def test_invalid_data_does_not_create_order(setup):
    client, db_path = setup
    add(client, 1)
    bad = order(client, nome='X', email='sememail', telefone='000')
    assert bad.status_code == 422
    with sqlite3.connect(db_path) as db:
        assert db.execute('SELECT COUNT(*) FROM pedidos').fetchone()[0] == 0


def test_order_link_is_random_and_not_guessable(setup):
    client, _ = setup
    add(client)
    response = order(client)
    location = response.headers['location']
    assert len(location.rsplit('/', 1)[-1]) >= 30
    assert client.get('/pedido/1').status_code == 404
    assert client.get(location).status_code == 200


def test_cross_site_request_forgery_protection(setup):
    client, _ = setup
    assert client.post('/carrinho/adicionar', data={'produto_id':'1', 'quantidade':'1'}).status_code == 403
    token(client)
    assert client.post('/carrinho/adicionar', data={'_csrf':'fake', 'produto_id':'1', 'quantidade':'1'}).status_code == 403


def test_admin_requires_authentication(setup):
    client, _ = setup
    assert client.get('/admin').status_code == 403
    assert client.get('/admin/pedidos').status_code == 403
    csrf = token(client, '/entrar')
    invalid = client.post('/entrar', data={'_csrf': csrf, 'email':'admin@doce.test', 'senha':'errada'})
    assert invalid.status_code == 401
    assert client.get('/admin').status_code == 403


def test_admin_login_create_edit_hide_product(setup):
    client, db_path = setup
    assert login(client).status_code == 303
    assert client.get('/admin').status_code == 200
    csrf = token(client, '/admin/produtos/novo')
    response = client.post('/admin/produtos/salvar', data={
        '_csrf':csrf, 'categoria_id':'1', 'nome':'Cupcake Teste', 'descricao':'Delícia experimental',
        'preco':'18,90', 'estoque':'7', 'imagem_url':'🧁'
    }, follow_redirects=False)
    assert response.status_code == 303, response.text[:500]
    with sqlite3.connect(db_path) as db:
        row = db.execute("SELECT id,preco_centavos,ativo FROM cupcakes WHERE nome='Cupcake Teste'").fetchone()
        assert row[1] == 1890
        product_id = row[0]
    assert 'Cupcake Teste' in client.get('/').text
    csrf = token(client, '/admin')
    hidden = client.post(f'/admin/produtos/{product_id}/alternar', data={'_csrf': csrf},follow_redirects=False)
    assert hidden.status_code == 303
    assert 'Cupcake Teste' not in client.get('/').text


def test_cancel_order_restocks_and_avoids_double_cancellation(setup):
    client, db_path = setup
    add(client, 1, 3)
    response = order(client)
    assert response.status_code == 303
    assert login(client).status_code == 303
    csrf = token(client, '/admin/pedidos')
    cancelled = client.post('/admin/pedidos/1/status', data={'_csrf':csrf, 'status':'cancelado'},follow_redirects=False)
    assert cancelled.status_code == 303
    with sqlite3.connect(db_path) as db:
        assert db.execute('SELECT estoque FROM cupcakes WHERE id=1').fetchone()[0] == 30
        assert db.execute('SELECT status FROM pedidos WHERE id=1').fetchone()[0] == 'cancelado'
    csrf = token(client, '/admin/pedidos')
    repeated = client.post('/admin/pedidos/1/status', data={'_csrf':csrf, 'status':'cancelado'},follow_redirects=False)
    assert repeated.status_code == 422
    with sqlite3.connect(db_path) as db:
        assert db.execute('SELECT estoque FROM cupcakes WHERE id=1').fetchone()[0] == 30


def test_order_stock_race_safely_rolled_back(setup):
    client, db_path = setup
    another = TestClient(client.app)
    add(client, 1, 20)
    add(another, 1, 20)
    assert order(client).status_code == 303
    outdated = order(another)
    assert outdated.status_code == 422
    assert 'itens indisponíveis' in outdated.text
    with sqlite3.connect(db_path) as db:
        assert db.execute('SELECT COUNT(*) FROM pedidos').fetchone()[0] == 1
        assert db.execute('SELECT estoque FROM cupcakes WHERE id=1').fetchone()[0] == 10


def test_money_parse_and_display():
    assert parse_brl('12,50') == 1250
    assert parse_brl('12.50') == 1250
    assert reais(1250) == 'R$ 12,50'
    with pytest.raises(ValueError):
        parse_brl('-12,5')
    with pytest.raises(ValueError):
        parse_brl('12,999')


def test_brand_photos_only_in_word_and_one_banner(setup):
    from photo_sources import PHOTOS
    from pathlib import Path
    client, db_path = setup
    html = client.get('/').text
    assert 'Le <strong>Cupcake</strong>' in html
    assert 'hero-photo' in html
    assert html.count('PROJETO ACADÊMICO') == 1
    assert '/creditos' not in html
    assert html.lower().count('loja fictícia') == 1  # Apenas faixa superior
    with sqlite3.connect(db_path) as db:
        saved = db.execute('SELECT nome,imagem_url FROM cupcakes ORDER BY id').fetchall()
    assert len(saved) == 8
    assert set(url for _, url in saved) == {p['imagem_url'] for key,p in PHOTOS.items() if key!='destaque'}
    assert client.get('/creditos').status_code == 404
    assert (Path(__file__).resolve().parent.parent / 'docs' / 'Referencias_Fotograficas_Simplificadas.docx').exists()


def test_clean_site_pages_and_new_palette(setup):
    client,_ = setup
    urls = ('/', '/produto/1', '/carrinho', '/entrar')
    for url in urls:
        html = client.get(url).text
        assert html.count('PROJETO ACADÊMICO') == 1
        assert '/creditos' not in html
        assert 'demonstração acadêmica' not in html.lower()
        assert 'fictício' not in html.lower().replace('LOJA FICTÍCIA'.lower(), '')
    add(client,1)
    for url in ('/carrinho', '/checkout'):
        html = client.get(url).text
        assert html.count('PROJETO ACADÊMICO') == 1
        assert '/creditos' not in html
        assert 'pedido demonstrativo' not in html.lower()
    css = client.get('/static/style.css').text
    assert '--rose:#3D634D' in css
    assert '.hero {background:linear-gradient(113deg' in css
    assert '#3D634D' in css
    assert '#e75b78' not in css.lower()


def test_admin_cannot_add_uncredited_photo(setup):
    client,_=setup
    assert login(client).status_code == 303
    csrf=token(client,'/admin/produtos/novo')
    data={'_csrf':csrf,'nome':'Cupcake Novo','descricao':'Teste de biblioteca autorizada',
          'categoria_id':'1','preco':'12,00','estoque':'10','imagem_id':'imagem_inventada'}
    response=client.post('/admin/produtos/salvar',data=data)
    assert response.status_code == 422
    assert 'fotografia documentada' in response.text
    data['imagem_id']='chocolate'
    response=client.post('/admin/produtos/salvar',data=data,follow_redirects=False)
    assert response.status_code == 303


def test_theme_v04_and_cache_busting(setup):
    from pathlib import Path
    client, _ = setup
    html = client.get('/').text
    css = client.get('/static/style.css?v=0.4')
    assert '?v=0.5' in html
    assert css.status_code == 200
    assert 'LE CUPCAKE — PALETA 0.4' in css.text
    assert '#3D634D' in css.text
    assert '#B45C3C' in css.text
    assert '#FFF8EC' in css.text
    assert 'background:#5A4143' in css.text
