"""Regressões da expansão 0.5: contas, cupons, avaliações e gestão."""
import re
import sqlite3
from fastapi.testclient import TestClient
import pytest
from app import create_app


def csrf(client, url='/'):
    html = client.get(url).text
    match = re.search(r'name="_csrf" value="([^"]+)"', html)
    assert match, html[:350]
    return match.group(1)


@pytest.fixture
def clients(tmp_path, monkeypatch):
    monkeypatch.setenv('ADMIN_EMAIL', 'admin@loja.test')
    monkeypatch.setenv('ADMIN_PASSWORD', 'UmSenhaMuitoSegura0123!')
    path=tmp_path/'lecupcake.db'
    app=create_app(path, testing=True)
    return TestClient(app), TestClient(app), path


def admin_login(client):
    return client.post('/entrar',data={'_csrf':csrf(client,'/entrar'), 'email':'admin@loja.test','senha':'UmSenhaMuitoSegura0123!'},follow_redirects=False)


def register(client):
    return client.post('/conta/cadastrar',data={'_csrf':csrf(client,'/conta/cadastrar'),
        'nome':'Maria Testadora','email':'maria@exemplo.test','senha':'UmaSenhaSegura123!' },follow_redirects=False)


def add_one(client):
    return client.post('/carrinho/adicionar',data={'_csrf':csrf(client), 'produto_id':'1','quantidade':'2'},follow_redirects=False)


def buy(client, **kwargs):
    data={'_csrf':csrf(client,'/checkout'),'nome':'Maria Testadora', 'email':'maria@exemplo.test',
          'telefone':'(65) 99999-9999', 'opcao_entrega':'1','endereco':''}
    data.update(kwargs)
    return client.post('/checkout',data=data,follow_redirects=False)


def test_customer_register_login_history(clients):
    customer,_,db_path=clients
    assert register(customer).status_code==303
    assert 'Maria Testadora' in customer.get('/minha-conta').text
    assert add_one(customer).status_code==303
    result=buy(customer)
    assert result.status_code==303
    assert 'Acompanhar' in customer.get('/minha-conta').text
    with sqlite3.connect(db_path) as db:
        user=db.execute("SELECT id,senha_hash FROM usuarios WHERE email='maria@exemplo.test'").fetchone()
        assert user and user[1].startswith('pbkdf2_sha256')
        assert db.execute('SELECT usuario_id FROM pedidos').fetchone()[0]==user[0]
    assert customer.post('/conta/sair', data={'_csrf':csrf(customer)},follow_redirects=False).status_code==303
    assert customer.get('/minha-conta').status_code==403
    assert customer.post('/conta/entrar',data={'_csrf':csrf(customer,'/conta/entrar'),
        'email':'maria@exemplo.test','senha':'UmaSenhaSegura123!'},follow_redirects=False).status_code==303
    assert 'Acompanhar' in customer.get('/minha-conta').text


def test_prevent_duplicate_customer_and_invalid_password(clients):
    customer,_,_=clients
    register(customer)
    csrf_token=csrf(customer,'/conta/cadastrar')
    duplicate=customer.post('/conta/cadastrar',data={'_csrf':csrf_token,'nome':'Outro Cliente',
         'email':'maria@exemplo.test','senha':'UmaSenhaSegura123!'})
    assert duplicate.status_code==422
    weak=customer.post('/conta/cadastrar',data={'_csrf':csrf(customer,'/conta/cadastrar'),
         'nome':'Outro Cliente','email':'outro@exemplo.test','senha':'curta'})
    assert weak.status_code==422


def test_coupon_and_discount_on_server(clients):
    buyer,admin,db_path=clients
    assert admin_login(admin).status_code==303
    response=admin.post('/admin/cupons/criar',data={'_csrf':csrf(admin,'/admin/cupons'),
        'codigo':'DOCE10','tipo':'percentual','valor':'10','minimo':'0','limite':'1'},follow_redirects=False)
    assert response.status_code==303
    add_one(buyer)
    result=buy(buyer,cupom='DOCE10')
    assert result.status_code==303
    with sqlite3.connect(db_path) as db:
        assert db.execute('SELECT subtotal_centavos,desconto_centavos,total_centavos FROM pedidos').fetchone()==(2500,250,2250)
        assert db.execute('SELECT COUNT(*) FROM cupom_utilizacoes').fetchone()[0]==1
    another=TestClient(buyer.app)
    add_one(another)
    response=buy(another,cupom='DOCE10')
    assert response.status_code==422
    assert 'limite de usos' in response.text
    with sqlite3.connect(db_path) as db:
        assert db.execute('SELECT COUNT(*) FROM pedidos').fetchone()[0]==1


def test_bad_coupon_does_not_reduce_stock(clients):
    buyer,_,db_path=clients
    add_one(buyer)
    result=buy(buyer,cupom='NAOEXISTE')
    assert result.status_code==422
    assert 'Cupom não encontrado' in result.text
    with sqlite3.connect(db_path) as db:
        assert db.execute('SELECT estoque FROM cupcakes WHERE id=1').fetchone()[0]==30


def test_coupon_fixed_discount_doesnt_overdiscount(clients):
    buyer,admin,db_path=clients
    admin_login(admin)
    resp=admin.post('/admin/cupons/criar',data={'_csrf':csrf(admin,'/admin/cupons'),
        'codigo':'PROMO50','tipo':'fixo','valor':'50,00','minimo':'0','limite':'0'},follow_redirects=False)
    assert resp.status_code==303
    add_one(buyer)
    assert buy(buyer,cupom='PROMO50').status_code==303
    with sqlite3.connect(db_path) as db:
        assert db.execute('SELECT desconto_centavos,total_centavos FROM pedidos').fetchone()==(2500,0)


def test_reviews_require_account_are_moderated_and_escape_html(clients):
    user,admin,db_path=clients
    assert user.get('/produto/1').status_code==200
    assert user.post('/produto/1/avaliar',data={'nota':'5','comentario':'bom!'}).status_code==403
    register(user)
    result=user.post('/produto/1/avaliar',data={'_csrf':csrf(user,'/produto/1'),
        'nota':'5','comentario':'Gostei muito <script>alert(1)</script>'},follow_redirects=False)
    assert result.status_code==303
    assert 'Gostei muito' not in user.get('/produto/1').text
    assert admin_login(admin).status_code==303
    assert 'Gostei muito' in admin.get('/admin/avaliacoes').text
    result=admin.post('/admin/avaliacoes/1/moderacao',data={'_csrf':csrf(admin,'/admin/avaliacoes'),
        'status':'publicada','resposta':'Obrigado pelo retorno!'},follow_redirects=False)
    assert result.status_code==303
    html=user.get('/produto/1').text
    assert 'Obrigado pelo retorno' in html
    assert '&lt;script&gt;' in html
    assert '<script>alert(1)</script>' not in html
    result=user.post('/produto/1/avaliar',data={'_csrf':csrf(user,'/produto/1'),
        'nota':'1','comentario':'Duplicada não pode'},follow_redirects=False)
    assert result.status_code==303
    with sqlite3.connect(db_path) as db:
        assert db.execute('SELECT COUNT(*) FROM avaliacoes').fetchone()[0]==1


def test_admin_report_and_delivery_settings(clients):
    buyer,admin,db_path=clients
    add_one(buyer)
    assert buy(buyer).status_code==303
    assert buyer.get('/admin/relatorios').status_code==403
    admin_login(admin)
    page=admin.get('/admin/relatorios').text
    assert 'R$ 25,00' in page
    assert 'Chocolate da Casa' in page
    result=admin.post('/admin/entregas/2/salvar',data={'_csrf':csrf(admin,'/admin/entregas'),
        'descricao':'Entrega expressa local','custo':'12,00','ativo':'1'},follow_redirects=False)
    assert result.status_code==303
    with sqlite3.connect(db_path) as db:
        assert db.execute('SELECT custo_base_centavos FROM opcoes_entrega WHERE id=2').fetchone()[0]==1200
    add_one(buyer)
    assert 'Entrega expressa local' in buyer.get('/checkout').text


def test_admin_nutrition_and_client_accounts(clients):
    user,admin,db_path=clients
    register(user)
    admin_login(admin)
    page=admin.get('/admin/produtos/1/editar')
    assert page.status_code==200
    assert 'informacoes_nutricionais' in page.text
    response=admin.post('/admin/produtos/salvar',data={'_csrf':csrf(admin,'/admin/produtos/1/editar'),
        'id':'1','categoria_id':'1','nome':'Chocolate da Casa','descricao':'Massa fofinha de chocolate com cobertura cremosa.',
        'preco':'12,50','estoque':'30','imagem_id':'chocolate',
        'informacoes_nutricionais':'Contém leite e trigo (informação de teste).'},follow_redirects=False)
    assert response.status_code==303, response.text[:300]
    assert 'Contém leite e trigo' in user.get('/produto/1').text
    assert 'Maria Testadora' in admin.get('/admin/clientes').text
    csrf_token=csrf(admin,'/admin/clientes')
    assert admin.post('/admin/clientes/2/alternar',data={'_csrf':csrf_token},follow_redirects=False).status_code==303
    assert user.get('/minha-conta').status_code==403
