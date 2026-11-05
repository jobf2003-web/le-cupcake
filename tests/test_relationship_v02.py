"""Aceitação do Ciclo C. Todos os testes de SMTP são locais, sem envio externo."""
import re
import sqlite3
from datetime import datetime, timedelta, timezone, date

import pytest
from fastapi.testclient import TestClient
from app import create_app
from customer_relationship import valid_dates


def csrf(client, url='/'):
    r = client.get(url)
    assert r.status_code == 200, r.text[:400]
    match = re.search(r'name="_csrf" value="([^"]+)"', r.text)
    assert match
    return match.group(1)


@pytest.fixture
def fixture(tmp_path, monkeypatch):
    monkeypatch.setenv('ADMIN_EMAIL', 'admin@le.test')
    monkeypatch.setenv('ADMIN_PASSWORD', 'SenhaForteDaLoja123!')
    monkeypatch.delenv('SMTP_HOST', raising=False)
    monkeypatch.delenv('PUBLIC_BASE_URL', raising=False)
    path = tmp_path / 'loja.db'
    app = create_app(path, testing=True)
    return TestClient(app), TestClient(app), path, app


def register(client, email='cliente@le.test'):
    return client.post('/conta/cadastrar', data={
        '_csrf':csrf(client,'/conta/cadastrar'), 'nome':'Cliente de Teste',
        'email':email, 'senha':'SenhaInicialMuitoForte123!'}, follow_redirects=False)


def admin_login(admin):
    return admin.post('/entrar', data={'_csrf':csrf(admin,'/entrar'),
        'email':'admin@le.test','senha':'SenhaForteDaLoja123!'},follow_redirects=False)


def add_one(client, id='1'):
    return client.post('/carrinho/adicionar',data={'_csrf':csrf(client),
        'produto_id':id,'quantidade':'1'},follow_redirects=False)


def purchase(client):
    return client.post('/checkout',data={'_csrf':csrf(client,'/checkout'),
        'nome':'Cliente de Teste','email':'cliente@le.test','telefone':'(65) 99999-1111',
        'opcao_entrega':'1','endereco':''},follow_redirects=False)


def test_reset_requires_email_delivery_outside_tests(tmp_path, monkeypatch):
    monkeypatch.delenv('SMTP_HOST',raising=False)
    monkeypatch.delenv('PUBLIC_BASE_URL',raising=False)
    app = create_app(tmp_path/'no-mail.db',testing=False)
    client = TestClient(app)
    html = client.get('/conta/recuperar').text
    assert 'não está configurado' in html
    r = client.post('/conta/recuperar', data={'_csrf':csrf(client,'/conta/entrar'),
                       'email':'alguem@le.test'})
    assert r.status_code==503
    with sqlite3.connect(app.state.db_path) as db:
        assert db.execute('SELECT COUNT(*) FROM password_reset_tokens').fetchone()[0]==0


def test_reset_single_use_no_enumeration_old_sessions_expire(fixture):
    client,other,path,app=fixture
    assert register(client).status_code==303
    assert 'Cliente de Teste' in client.get('/minha-conta').text
    token=csrf(client,'/conta/recuperar')
    wrong=client.post('/conta/recuperar',data={'_csrf':token,'email':'ninguem@le.test'})
    good=client.post('/conta/recuperar',data={'_csrf':token,'email':'cliente@le.test'})
    assert wrong.status_code==good.status_code==200
    assert 'envi' in wrong.text and 'envi' in good.text
    assert len(app.state.test_reset_links)==1
    reset_path=app.state.test_reset_links[0].split('testserver')[-1]
    assert reset_path not in good.text
    assert client.get(reset_path).status_code==200
    with sqlite3.connect(path) as db:
        row=db.execute('SELECT token_digest FROM password_reset_tokens').fetchone()[0]
        assert row not in reset_path and len(row)==64
    resp=other.post(reset_path,data={'_csrf':csrf(other,reset_path),
        'senha':'NovaSenhaMuitoForte321!', 'confirmar':'NovaSenhaMuitoForte321!'},follow_redirects=False)
    assert resp.status_code==303
    assert other.get(reset_path).status_code==200
    assert 'já foi usado' in other.get(reset_path).text
    assert client.get('/minha-conta').status_code==403 # outros cookies revogados
    assert client.post('/conta/entrar', data={'_csrf':csrf(client,'/conta/entrar'),
        'email':'cliente@le.test','senha':'SenhaInicialMuitoForte123!'}).status_code==401
    assert client.post('/conta/entrar', data={'_csrf':csrf(client,'/conta/entrar'),
        'email':'cliente@le.test','senha':'NovaSenhaMuitoForte321!'},follow_redirects=False).status_code==303
    assert other.post(reset_path,data={'_csrf':csrf(other,'/conta/entrar'),
        'senha':'OutraSenhaMuitoForte123!','confirmar':'OutraSenhaMuitoForte123!'}).status_code==422


def test_reset_expiration_wrong_csrf_throttle(fixture):
    client,_,path,app=fixture
    register(client)
    assert client.post('/conta/recuperar',data={'email':'cliente@le.test'}).status_code==403
    token=csrf(client,'/conta/recuperar')
    for _ in range(5):
        assert client.post('/conta/recuperar',data={'_csrf':token,'email':'cliente@le.test'}).status_code==200
    assert len(app.state.test_reset_links)==3
    with sqlite3.connect(path) as db:
        db.execute('UPDATE password_reset_tokens SET expiracao_em=?',
            ((datetime.now(timezone.utc)-timedelta(minutes=1)).isoformat(),))
    reset_path=app.state.test_reset_links[0].split('testserver')[-1]
    assert 'inválido' in client.get(reset_path).text
    with sqlite3.connect(path) as db:
        assert db.execute('PRAGMA user_version').fetchone()[0]==5
        assert db.execute('PRAGMA foreign_key_check').fetchall()==[]


def test_recommendations_after_purchase_use_history_and_stock(fixture):
    client,_,path,_=fixture
    register(client)
    assert 'Sugestões para você' not in client.get('/').text
    assert add_one(client,'1').status_code==303
    assert purchase(client).status_code==303
    html=client.get('/').text
    assert 'Sugestões para você' in html
    block=html.split('Sugestões para você')[1].split('</section>')[0]
    assert 'Baunilha Encantada' in block or 'Cenoura &amp; Chocolate' in block
    assert block.count('recommendation-card')>=3
    with sqlite3.connect(path) as db:
        db.execute('UPDATE cupcakes SET estoque=0 WHERE id=2')
    html=client.get('/').text
    block=html.split('Sugestões para você')[1].split('</section>')[0]
    assert 'Baunilha Encantada' not in block


def test_coupon_dates_and_promotion_visibility(fixture):
    client,admin,path,_=fixture
    assert admin_login(admin).status_code==303
    today=date.today()
    valid={'_csrf':csrf(admin,'/admin/cupons'),'codigo':'PROMONOVO',
        'tipo':'percentual','valor':'15','minimo':'10','limite':'1',
        'valido_de':(today-timedelta(days=1)).isoformat(),
        'valido_ate':(today+timedelta(days=1)).isoformat()}
    assert admin.post('/admin/cupons/criar',data=valid,follow_redirects=False).status_code==303
    assert 'PROMONOVO' in client.get('/').text
    expired=dict(valid,codigo='EXPIRADO',valido_de=(today-timedelta(days=3)).isoformat(),
                 valido_ate=(today-timedelta(days=1)).isoformat())
    assert admin.post('/admin/cupons/criar',data=expired,follow_redirects=False).status_code==303
    assert 'EXPIRADO' not in client.get('/').text
    bad=dict(valid,codigo='ERRADO',valido_de=(today+timedelta(days=2)).isoformat(),
             valido_ate=(today+timedelta(days=1)).isoformat())
    assert admin.post('/admin/cupons/criar',data=bad).status_code==422
    assert valid_dates('2026-01-01','2026-12-31')
    assert not valid_dates('2026-13-01','2026-12-31')
    assert not valid_dates('2026-12-31','2026-01-01')


def test_ingredients_allergens_and_disclaimer(fixture):
    user,admin,path,_=fixture
    assert 'não confirmadas' in user.get('/produto/1').text
    assert admin_login(admin).status_code==303
    with sqlite3.connect(path) as db:
        allergen=db.execute("SELECT id FROM alergenos WHERE nome='Leite'").fetchone()[0]
    page=admin.get('/admin/produtos/1/editar')
    assert 'Alergênicos comprovados' in page.text
    r=admin.post('/admin/produtos/salvar',data={'_csrf':csrf(admin,'/admin/produtos/1/editar'),
        'id':'1','categoria_id':'1','nome':'Chocolate da Casa',
        'descricao':'Massa fofinha de chocolate com cobertura cremosa.',
        'preco':'12,50','estoque':'30','imagem_id':'chocolate',
        'ingredientes':'Farinha, leite e cacau (somente informação ilustrativa de teste)',
        'informacoes_nutricionais':'Dados de teste, não utilizar como informação real',
        'alergenos':[str(allergen)]},follow_redirects=False)
    assert r.status_code==303, r.text[:450]
    html=user.get('/produto/1').text
    assert 'Atenção: contém alergênicos' in html and 'Leite' in html
    assert 'Farinha, leite' in html
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT COUNT(*) FROM cupcake_alergenos WHERE cupcake_id=1').fetchone()[0]==1
        assert db.execute("SELECT COUNT(*) FROM auditoria WHERE acao='editar alergenicos'").fetchone()[0]==1
    # Falsos IDs externos não podem ser cadastrados.
    invalid=admin.post('/admin/produtos/salvar',data={'_csrf':csrf(admin,'/admin/produtos/1/editar'),
        'id':'1','categoria_id':'1','nome':'Chocolate da Casa','descricao':'Descrição de teste',
        'preco':'12,50','estoque':'30','imagem_id':'chocolate','alergenos':['99999']})
    assert invalid.status_code==422
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT COUNT(*) FROM cupcake_alergenos WHERE cupcake_id=1').fetchone()[0]==1


def test_admin_cannot_reset_via_client_recovery(fixture):
    client,admin,path,app=fixture
    admin_login(admin)
    response=client.post('/conta/recuperar',data={'_csrf':csrf(client,'/conta/recuperar'),
        'email':'admin@le.test'})
    assert response.status_code==200
    assert app.state.test_reset_links==[]
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT COUNT(*) FROM password_reset_tokens').fetchone()[0]==0


def test_recommendation_includes_combo_purchase(fixture):
    buyer,_,path,_=fixture
    register(buyer)
    combo=buyer.post('/combos/adicionar',data={'_csrf':csrf(buyer,'/combos'),
        'q_3':'2', 'q_4':'1'},follow_redirects=False)
    assert combo.status_code==303
    assert purchase(buyer).status_code==303
    block=buyer.get('/').text.split('Sugestões para você')[1].split('</section>')[0]
    assert 'Morango dos Sonhos' in block
    assert 'Limão Fresquinho' in block


def test_smtp_adapter_only_sends_through_tls_when_configured(tmp_path, monkeypatch):
    monkeypatch.setenv('PUBLIC_BASE_URL','https://example.invalid')
    monkeypatch.setenv('SMTP_HOST','smtp.example.invalid')
    monkeypatch.setenv('SMTP_FROM','contato@example.invalid')
    monkeypatch.setenv('SMTP_USER','')
    monkeypatch.setenv('SMTP_PASSWORD','')
    monkeypatch.setenv('ADMIN_EMAIL','')
    monkeypatch.setenv('ADMIN_PASSWORD','')
    sent=[]
    class FakeSMTP:
        def __init__(self, host, port, timeout):
            assert host=='smtp.example.invalid'
            self.tls=False
        def __enter__(self): return self
        def __exit__(self, *_): return False
        def starttls(self, context): self.tls=True
        def send_message(self, message):
            assert self.tls
            sent.append(message)
    monkeypatch.setattr('customer_relationship.smtplib.SMTP',FakeSMTP)
    app=create_app(tmp_path/'smtp-mock.db',testing=False)
    client=TestClient(app)
    assert register(client).status_code==303
    response=client.post('/conta/recuperar', data={
        '_csrf':csrf(client,'/conta/recuperar'), 'email':'cliente@le.test'})
    assert response.status_code==200
    assert len(sent)==1
    assert 'https://example.invalid/conta/redefinir/' in sent[0].get_content()
    assert 'redefinir/' not in response.text
    with sqlite3.connect(app.state.db_path) as db:
        assert db.execute('SELECT COUNT(*) FROM password_reset_tokens WHERE usado_em IS NULL').fetchone()[0]==1
