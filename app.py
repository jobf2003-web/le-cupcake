"""Loja Le Cupcake — MVP acadêmico PIT II.

Aplicação Python/FastAPI, páginas Jinja2 e SQLite. Não processa pagamentos reais.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation
from datetime import date
from pathlib import Path
import re
import secrets
import sqlite3
from typing import Any

from photo_sources import PHOTOS, PRODUCT_PHOTO_KEYS, ALLOWED_PHOTO_URLS
from migrations import apply_migrations

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment
from starlette.middleware.sessions import SessionMiddleware
from starlette.templating import Jinja2Templates

ROOT = Path(__file__).resolve().parent
STATUS = ['recebido', 'confirmado', 'preparo', 'pronto', 'em_entrega', 'concluido', 'cancelado']
NEXT_STATUS = {
    'recebido': ['confirmado', 'cancelado'],
    'confirmado': ['preparo', 'cancelado'],
    'preparo': ['pronto'],
    'pronto': ['em_entrega', 'concluido'],
    'em_entrega': ['concluido'],
    'concluido': [], 'cancelado': [],
}
SAMPLE_PRODUCTS = [
    ('Clássicos', 'Chocolate da Casa', 'Massa fofinha de chocolate com cobertura cremosa.', 1250, 30, 'chocolate'),
    ('Clássicos', 'Baunilha Encantada', 'Baunilha delicada e cobertura suave.', 1150, 25, 'baunilha'),
    ('Frutados', 'Morango dos Sonhos', 'Massa leve e finalização com toque de morango.', 1400, 20, 'morango'),
    ('Frutados', 'Limão Fresquinho', 'Cupcake cítrico de limão com cobertura delicada.', 1350, 22, 'limao'),
    ('Especiais', 'Red Velvet', 'Bolo vermelho aveludado com cobertura cremosa.', 1550, 18, 'red_velvet'),
    ('Especiais', 'Doce de Leite', 'Recheio generoso de doce de leite.', 1500, 18, 'caramelo'),
    ('Veganos', 'Cacau Vegano', 'Cupcake de cacau com receita sem ingredientes animais.', 1450, 16, 'vegano'),
    ('Clássicos', 'Cenoura & Chocolate', 'Cupcake de cenoura com cobertura de chocolate.', 1300, 26, 'cenoura'),
]


def reais(centavos: int) -> str:
    valor = int(centavos) / 100
    return f'R$ {valor:,.2f}'.replace(',', '#').replace('.', ',').replace('#', '.')


def parse_brl(value: str) -> int:
    """Accept 12,50 or 12.50, but reject negatives and floating-point rounding."""
    s = str(value).strip().replace('R$', '').replace(' ', '')
    if not re.fullmatch(r'\d{1,6}([,.]\d{1,2})?', s):
        raise ValueError('Informe um preço válido (ex.: 12,50).')
    try:
        money = Decimal(s.replace(',', '.'))
        cents = int(money * 100)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError('Preço inválido.') from exc
    if cents < 0 or cents > 99999999:
        raise ValueError('Preço fora do intervalo permitido.')
    return cents


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 310_000)
    return f'pbkdf2_sha256$310000${salt.hex()}${digest.hex()}'


def verify_password(password: str, password_hash: str) -> bool:
    try:
        alg, iters, salt, expected = password_hash.split('$')
        if alg != 'pbkdf2_sha256':
            return False
        actual = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), int(iters))
        return hmac.compare_digest(actual, bytes.fromhex(expected))
    except (ValueError, TypeError):
        return False


def get_secret(folder: Path) -> str:
    value = os.environ.get('SECRET_KEY', '').strip()
    if value:
        if len(value) < 32:
            raise RuntimeError('SECRET_KEY deve ter pelo menos 32 caracteres.')
        return value
    folder.mkdir(parents=True, exist_ok=True)
    secret_file = folder / '.local_secret'
    if secret_file.exists():
        return secret_file.read_text(encoding='utf-8').strip()
    value = secrets.token_urlsafe(48)
    secret_file.write_text(value, encoding='utf-8')
    try:
        secret_file.chmod(0o600)
    except OSError:
        pass
    return value


def create_app(db_path: str | Path | None = None, *, testing: bool = False) -> FastAPI:
    db_path = Path(db_path) if db_path is not None else Path(os.environ.get('DATABASE_PATH', ROOT / 'instance' / 'cupcakes.db'))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    app = FastAPI(title='Le Cupcake — Loja de Cupcakes', docs_url='/api/docs' if testing else None,
                  redoc_url=None)
    secret = 'testing-secret-key-with-32-chars-minimum' if testing else get_secret(db_path.parent)
    app.add_middleware(SessionMiddleware, secret_key=secret, same_site='lax',
                       https_only=bool(os.environ.get('COOKIE_SECURE') == '1'), max_age=60 * 60 * 12)
    app.mount('/static', StaticFiles(directory=ROOT / 'static'), name='static')
    templates = Jinja2Templates(directory=str(ROOT / 'templates'))
    templates.env.filters['reais'] = reais
    templates.env.filters['status_nome'] = lambda x: {'recebido':'Recebido', 'confirmado':'Confirmado', 'preparo':'Em preparo', 'pronto':'Pronto', 'em_entrega':'Em entrega', 'concluido':'Concluído', 'cancelado':'Cancelado'}.get(x, x)
    app.state.db_path = db_path

    campos_produto = ('nome', 'descricao', 'categoria_id', 'preco_centavos',
                      'estoque', 'imagem_url', 'informacoes_nutricionais',
                      'ativo', 'excluido_em')

    def snapshot_produto(row):
        return {chave: row[chave] for chave in campos_produto}

    def auditar_produto(db, usuario_id, produto_id, acao, antes, depois):
        dados = {'antes': antes, 'depois': depois}
        db.execute('''INSERT INTO auditoria(usuario_id,entidade,entidade_id,acao,descricao)
                      VALUES (?,?,?,?,?)''',
                   (usuario_id, 'cupcakes', produto_id, acao,
                    json.dumps(dados, ensure_ascii=False, sort_keys=True)))

    @contextmanager
    def db_connect():
        db = sqlite3.connect(db_path, timeout=20)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys = ON')
        db.execute('PRAGMA busy_timeout = 20000')
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def init_database():
        with db_connect() as db:
            db.executescript((ROOT / 'schema.sql').read_text(encoding='utf-8')) if not db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'").fetchone() else None
            apply_migrations(db)  # Opera tanto em banco novo quanto em banco legado.
            if not db.execute('SELECT 1 FROM categorias LIMIT 1').fetchone():
                for category in ('Clássicos', 'Frutados', 'Especiais', 'Veganos'):
                    db.execute('INSERT INTO categorias (nome) VALUES (?)', (category,))
            if not db.execute('SELECT 1 FROM cupcakes LIMIT 1').fetchone():
                mapping = {r['nome']: r['id'] for r in db.execute('SELECT id, nome FROM categorias')}
                for cat, name, desc, price, stock, emoji in SAMPLE_PRODUCTS:
                    db.execute('INSERT INTO cupcakes(categoria_id,nome,descricao,preco_centavos,estoque,imagem_url) VALUES (?,?,?,?,?,?)',
                               (mapping[cat], name, desc, price, stock, PHOTOS[emoji]['imagem_url']))
            # Atualiza apenas as imagens demonstrativas anteriores (emojis) dos oito produtos iniciais.
            # Nao substitui imagens aprovadas em cadastros alterados pelo administrador.
            for cat, name, desc, price, stock, photo_key in SAMPLE_PRODUCTS:
                current_photo = db.execute('SELECT imagem_url FROM cupcakes WHERE nome = ?', (name,)).fetchone()
                if current_photo and (not current_photo['imagem_url'] or not current_photo['imagem_url'].startswith('https://')):
                    db.execute('UPDATE cupcakes SET imagem_url=? WHERE nome=?', (PHOTOS[photo_key]['imagem_url'], name))
            if not db.execute('SELECT 1 FROM opcoes_entrega LIMIT 1').fetchone():
                db.executemany('INSERT INTO opcoes_entrega(tipo,descricao,custo_base_centavos) VALUES (?,?,?)',
                               [('retirada', 'Retirar na loja', 0),
                                ('entrega', 'Entrega local (taxa fixa)', 800)])
            # Uma avaliação por cliente/produto, inclusive após migrar uma instalação anterior.
            db.execute('CREATE UNIQUE INDEX IF NOT EXISTS ux_avaliacoes_cliente_produto ON avaliacoes(usuario_id,cupcake_id)')
            # Atualiza apenas descrições antigas incluídas pela versão anterior.
            db.execute("UPDATE opcoes_entrega SET descricao='Retirar na loja' WHERE descricao='Retirar na loja (demonstração)'")
            db.execute("UPDATE opcoes_entrega SET descricao='Entrega local (taxa fixa)' WHERE descricao='Entrega local (taxa fixa demonstrativa)'")
            admin_email = os.environ.get('ADMIN_EMAIL', '').strip().lower()
            admin_password = os.environ.get('ADMIN_PASSWORD', '')
            if admin_email or admin_password:
                if not admin_email or len(admin_password) < 12 or '@' not in admin_email:
                    raise RuntimeError('Configure ADMIN_EMAIL válido e ADMIN_PASSWORD com pelo menos 12 caracteres.')
                if not db.execute('SELECT 1 FROM usuarios WHERE email = ?', (admin_email,)).fetchone():
                    db.execute("INSERT INTO usuarios(nome,email,senha_hash,papel) VALUES (?,?,?,'admin')",
                               ('Administrador', admin_email, hash_password(admin_password)))

    init_database()

    def flash(request: Request, message: str, category: str = 'info'):
        request.session['flash'] = (message, category)

    def csrf(request: Request) -> str:
        token = request.session.get('csrf_token')
        if not token:
            token = secrets.token_urlsafe(24)
            request.session['csrf_token'] = token
        return token

    async def valid_form(request: Request) -> Any:
        form = await request.form()
        submitted = str(form.get('_csrf', ''))
        expected = str(request.session.get('csrf_token', ''))
        if not expected or not hmac.compare_digest(submitted, expected):
            raise HTTPException(403, 'Formulário inválido ou expirado. Atualize a página e tente novamente.')
        return form

    def read_cart(request: Request) -> dict[int, int]:
        raw = request.session.get('cart', {})
        if not isinstance(raw, dict):
            return {}
        clean: dict[int, int] = {}
        for key, qty in raw.items():
            try:
                product_id, amount = int(key), int(qty)
                if product_id > 0 and 0 < amount <= 99:
                    clean[product_id] = amount
            except (ValueError, TypeError):
                pass
        return clean

    def save_cart(request: Request, cart: dict[int, int]):
        request.session['cart'] = {str(k): v for k, v in cart.items()}

    def cart_lines(db: sqlite3.Connection, cart: dict[int, int]):
        if not cart:
            return [], 0
        qs = ','.join('?' for _ in cart)
        products = db.execute(
            f'SELECT c.*, k.nome categoria FROM cupcakes c JOIN categorias k ON k.id=c.categoria_id WHERE c.id IN ({qs})',
            list(cart)
        ).fetchall()
        result = []
        subtotal = 0
        for p in products:
            qty = cart[p['id']]
            line_sum = int(p['preco_centavos']) * qty
            result.append({'product': p, 'qty': qty, 'total': line_sum,
                           'available': bool(p['ativo']) and int(p['estoque']) >= qty})
            subtotal += line_sum
        return result, subtotal

    def current_customer(request: Request):
        user_id = request.session.get('customer_id')
        if not isinstance(user_id, int):
            return None
        with db_connect() as db:
            return db.execute("SELECT id,nome,email,criado_em FROM usuarios WHERE id=? AND papel='cliente' AND ativo=1",
                              (user_id,)).fetchone()

    def require_customer(request: Request):
        user = current_customer(request)
        if user is None:
            raise HTTPException(403, 'Entre com sua conta de cliente para continuar.')
        return user

    def discount_for(db, code: str, subtotal: int):
        code = code.strip().upper()
        if not code:
            return None, 0
        if len(code) > 30 or not re.fullmatch(r'[A-Z0-9_-]+', code):
            raise ValueError('Código de cupom inválido.')
        cupom = db.execute('SELECT * FROM cupons WHERE codigo=? AND ativo=1', (code,)).fetchone()
        if not cupom:
            raise ValueError('Cupom não encontrado ou indisponível.')
        today = date.today().isoformat()
        if (cupom['valido_de'] and today < cupom['valido_de']) or (cupom['valido_ate'] and today > cupom['valido_ate']):
            raise ValueError('Este cupom está fora da validade.')
        if subtotal < cupom['valor_minimo_centavos']:
            raise ValueError(f'Este cupom exige um subtotal de {reais(cupom["valor_minimo_centavos"])}.')
        usage = db.execute('SELECT COUNT(*) FROM cupom_utilizacoes WHERE cupom_id=?', (cupom['id'],)).fetchone()[0]
        if cupom['limite_uso'] is not None and usage >= cupom['limite_uso']:
            raise ValueError('O limite de usos deste cupom foi atingido.')
        discount = (subtotal * cupom['valor'] // 100 if cupom['tipo'] == 'percentual' else cupom['valor'])
        return cupom, min(subtotal, discount)

    def page(request: Request, filename: str, *, status_code: int = 200, **context):
        message = request.session.pop('flash', None)
        context.update(photos=PHOTOS, cart_count=sum(read_cart(request).values()), csrf=csrf(request),
                       flash=message, admin=bool(request.session.get('admin_id')),
                       path=request.url.path, customer=current_customer(request))
        return templates.TemplateResponse(request, filename, context, status_code=status_code)

    def redirect(url: str):
        return RedirectResponse(url=url, status_code=303)

    def admin_id(request: Request) -> int:
        user_id = request.session.get('admin_id')
        if not isinstance(user_id, int):
            raise HTTPException(status_code=403, detail='Acesso reservado ao administrador.')
        with db_connect() as db:
            check = db.execute("SELECT id FROM usuarios WHERE id=? AND papel='admin' AND ativo=1", (user_id,)).fetchone()
            if not check:
                raise HTTPException(status_code=403, detail='Acesso reservado ao administrador.')
        return user_id

    @app.exception_handler(403)
    async def forbidden_handler(request: Request, exc: HTTPException):
        return page(request, 'mensagem.html', status_code=403, title='Acesso não autorizado',
                    message=str(exc.detail))


    def select_catalog(busca: str = '', categoria: str = ''):
        """Mesma consulta para a vitrine HTML e os resultados sem recarga."""
        search = busca.strip()[:80]
        category = categoria.strip()[:80]
        params: list[Any] = []
        sql = '''SELECT c.*, k.nome categoria FROM cupcakes c JOIN categorias k ON k.id=c.categoria_id
                 WHERE c.ativo=1 AND k.ativa=1'''
        if search:
            sql += ' AND (LOWER(c.nome) LIKE ? OR LOWER(c.descricao) LIKE ?)'
            params += [f'%{search.lower()}%', f'%{search.lower()}%']
        if category:
            sql += ' AND k.nome=?'
            params.append(category)
        # A vitrine geral sinaliza esgotados, mas filtros exibem apenas disponíveis.
        if search or category:
            sql += ' AND c.estoque > 0'
        sql += ' ORDER BY c.id'
        with db_connect() as db:
            products = db.execute(sql, params).fetchall()
        return products, search, category

    @app.get('/', response_class=HTMLResponse)
    def home(request: Request, busca: str = '', categoria: str = ''):
        products, search, category = select_catalog(busca, categoria)
        with db_connect() as db:
            categories = db.execute('SELECT nome FROM categorias WHERE ativa=1 ORDER BY id').fetchall()
        return page(request, 'index.html', products=products, categories=categories,
                    busca=search, categoria=category)

    @app.get('/catalogo/resultados', response_class=HTMLResponse)
    def catalog_partial(request: Request, busca: str = '', categoria: str = ''):
        """Fragmento HTML escapado pelo Jinja2 para atualização progressiva do catálogo."""
        products, _, _ = select_catalog(busca, categoria)
        return templates.TemplateResponse(
            request, 'catalogo_resultados.html', {'products': products, 'csrf': csrf(request)},
            headers={'X-Total-Results': str(len(products)), 'Cache-Control': 'no-store'},
        )

    @app.get('/produto/{product_id}', response_class=HTMLResponse)
    def product_detail(request: Request, product_id: int):
        with db_connect() as db:
            p = db.execute('''SELECT c.*, k.nome categoria FROM cupcakes c JOIN categorias k ON k.id=c.categoria_id
                              WHERE c.id=? AND c.ativo=1''', (product_id,)).fetchone()
            if not p:
                raise HTTPException(404, 'Produto não encontrado.')
            reviews = db.execute('''SELECT nota,comentario,resposta_admin FROM avaliacoes
                    WHERE cupcake_id=? AND status='publicada' ORDER BY id DESC LIMIT 25''', (product_id,)).fetchall()
            recommendations = db.execute('''SELECT id,nome,imagem_url,preco_centavos FROM cupcakes
                    WHERE categoria_id=? AND id<>? AND ativo=1 AND estoque>0 ORDER BY id LIMIT 3''',
                    (p['categoria_id'], product_id)).fetchall()
            already_reviewed = False
            customer = current_customer(request)
            if customer:
                already_reviewed = bool(db.execute('SELECT 1 FROM avaliacoes WHERE usuario_id=? AND cupcake_id=?',
                                                 (customer['id'], product_id)).fetchone())
        return page(request, 'produto.html', product=p, reviews=reviews,
                    recommendations=recommendations, already_reviewed=already_reviewed)

    @app.post('/carrinho/adicionar')
    async def add_cart(request: Request):
        form = await valid_form(request)
        try:
            product_id, quantity = int(form.get('produto_id', 0)), int(form.get('quantidade', 1))
        except (ValueError, TypeError):
            raise HTTPException(422, 'Produto ou quantidade inválidos.')
        if not 1 <= quantity <= 99:
            raise HTTPException(422, 'Quantidade inválida.')
        with db_connect() as db:
            p = db.execute('SELECT id, nome, estoque FROM cupcakes WHERE id=? AND ativo=1', (product_id,)).fetchone()
        if not p:
            raise HTTPException(404, 'Produto indisponível.')
        cart = read_cart(request)
        new_count = cart.get(product_id, 0) + quantity
        if new_count > int(p['estoque']):
            flash(request, f'Estoque insuficiente para {p["nome"]}.', 'erro')
            return redirect('/carrinho')
        cart[product_id] = new_count
        save_cart(request, cart)
        flash(request, f'{p["nome"]} adicionado ao carrinho.', 'sucesso')
        return redirect('/carrinho')

    @app.get('/carrinho', response_class=HTMLResponse)
    def shopping_cart(request: Request):
        with db_connect() as db:
            lines, subtotal = cart_lines(db, read_cart(request))
        return page(request, 'carrinho.html', lines=lines, subtotal=subtotal)

    @app.post('/carrinho/atualizar')
    async def update_cart(request: Request):
        form = await valid_form(request)
        try:
            product_id, quantity = int(form.get('produto_id', 0)), int(form.get('quantidade', -1))
        except (ValueError, TypeError):
            raise HTTPException(422, 'Quantidade inválida.')
        cart = read_cart(request)
        if product_id not in cart or quantity < 0 or quantity > 99:
            raise HTTPException(422, 'Item ou quantidade inválidos.')
        with db_connect() as db:
            product = db.execute('SELECT estoque FROM cupcakes WHERE id=? AND ativo=1', (product_id,)).fetchone()
        if quantity and (not product or quantity > product['estoque']):
            flash(request, 'Quantidade maior do que o estoque disponível.', 'erro')
            return redirect('/carrinho')
        if quantity == 0:
            del cart[product_id]
        else:
            cart[product_id] = quantity
        save_cart(request, cart)
        flash(request, 'Carrinho atualizado.', 'sucesso')
        return redirect('/carrinho')

    @app.post('/carrinho/remover')
    async def remove_cart(request: Request):
        form = await valid_form(request)
        try:
            product_id = int(form.get('produto_id', 0))
        except (ValueError, TypeError):
            raise HTTPException(422, 'Produto inválido.')
        cart = read_cart(request)
        cart.pop(product_id, None)
        save_cart(request, cart)
        flash(request, 'Item removido.', 'info')
        return redirect('/carrinho')

    @app.get('/checkout', response_class=HTMLResponse)
    def checkout_form(request: Request):
        with db_connect() as db:
            lines, subtotal = cart_lines(db, read_cart(request))
            shipping = db.execute('SELECT * FROM opcoes_entrega WHERE ativa=1 ORDER BY custo_base_centavos').fetchall()
        if not lines:
            flash(request, 'Adicione cupcakes ao carrinho antes de finalizar.', 'erro')
            return redirect('/carrinho')
        user = current_customer(request)
        return page(request, 'checkout.html', lines=lines, subtotal=subtotal, shipping=shipping,
                    values={'nome':user['nome'],'email':user['email']} if user else {}, errors=[])

    @app.post('/checkout')
    async def place_order(request: Request):
        form = await valid_form(request)
        cart = read_cart(request)
        name = str(form.get('nome', '')).strip()[:120]
        email = str(form.get('email', '')).strip().lower()[:200]
        phone = str(form.get('telefone', '')).strip()[:30]
        address = str(form.get('endereco', '')).strip()[:400]
        coupon_code = str(form.get('cupom', '')).strip().upper()[:30]
        try:
            shipping_id = int(form.get('opcao_entrega', '0'))
        except (ValueError, TypeError):
            shipping_id = 0
        errors = []
        if len(name) < 3:
            errors.append('Informe seu nome completo.')
        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
            errors.append('Informe um e-mail válido.')
        if len(re.sub(r'\D', '', phone)) < 10:
            errors.append('Informe um telefone com DDD.')
        with db_connect() as db:
            lines, subtotal = cart_lines(db, cart)
            shipping = db.execute('SELECT * FROM opcoes_entrega WHERE ativa=1 ORDER BY custo_base_centavos').fetchall()
            ship = db.execute('SELECT * FROM opcoes_entrega WHERE id=? AND ativa=1', (shipping_id,)).fetchone()
        if not lines:
            errors.append('O carrinho está vazio.')
        if not ship:
            errors.append('Escolha uma modalidade de entrega.')
        if ship and ship['tipo'] == 'entrega' and len(address) < 10:
            errors.append('Informe o endereço completo para a entrega.')
        try:
            with db_connect() as db:
                discount_for(db, coupon_code, subtotal)
        except ValueError as exc:
            errors.append(str(exc))
        if any(not x['available'] for x in lines):
            errors.append('Há itens indisponíveis ou sem estoque suficiente no carrinho.')
        if errors:
            return page(request, 'checkout.html', status_code=422, lines=lines,
                        subtotal=subtotal, shipping=shipping, values=dict(form), errors=errors)
        token = secrets.token_urlsafe(24)
        try:
            with db_connect() as db:
                db.execute('BEGIN IMMEDIATE')
                for line in lines:
                    p = line['product']
                    actual = db.execute('''SELECT id, nome, estoque, preco_centavos FROM cupcakes
                                           WHERE id=? AND ativo=1''', (p['id'],)).fetchone()
                    if not actual or actual['estoque'] < line['qty']:
                        raise ValueError('Um dos produtos acabou de ficar indisponível. Volte ao carrinho.')
                subtotal_real = 0
                for line in lines:
                    p = db.execute('SELECT preco_centavos FROM cupcakes WHERE id=?', (line['product']['id'],)).fetchone()
                    subtotal_real += p['preco_centavos'] * line['qty']
                ship_now = db.execute('SELECT * FROM opcoes_entrega WHERE id=? AND ativa=1', (shipping_id,)).fetchone()
                if ship_now is None:
                    raise ValueError('A forma de entrega não está mais disponível.')
                freight = int(ship_now['custo_base_centavos'])
                coupon, discount = discount_for(db, coupon_code, subtotal_real)
                total = subtotal_real + freight - discount
                logged = current_customer(request)
                cur = db.execute('''INSERT INTO pedidos(usuario_id,opcao_entrega_id, contato_nome,contato_email,contato_telefone,
                    endereco_entrega,token_acesso,subtotal_centavos,frete_centavos,desconto_centavos,total_centavos)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (logged['id'] if logged else None, shipping_id, name, email, phone,
                    address if ship_now['tipo']=='entrega' else None, token, subtotal_real, freight, discount, total))
                order_id = cur.lastrowid
                if coupon:
                    db.execute('INSERT INTO cupom_utilizacoes(cupom_id,pedido_id) VALUES (?,?)', (coupon['id'], order_id))
                for line in lines:
                    p = db.execute('SELECT id,nome,preco_centavos FROM cupcakes WHERE id=?', (line['product']['id'],)).fetchone()
                    changed = db.execute('UPDATE cupcakes SET estoque=estoque-? WHERE id=? AND estoque>=?',
                                         (line['qty'], p['id'], line['qty']))
                    if changed.rowcount != 1:
                        raise ValueError('Estoque insuficiente. Revise o carrinho.')
                    db.execute('''INSERT INTO pedido_itens(pedido_id,cupcake_id,nome_snapshot,quantidade,preco_unitario_centavos)
                        VALUES (?,?,?,?,?)''', (order_id, p['id'], p['nome'], line['qty'], p['preco_centavos']))
                    db.execute('INSERT INTO estoque_movimentos(cupcake_id,pedido_id,variacao,motivo) VALUES (?,?,?,?)',
                               (p['id'], order_id, -line['qty'], 'Pedido recebido'))
                db.execute('INSERT INTO eventos_pedido(pedido_id,status,observacao) VALUES (?, ?, ?)',
                           (order_id, 'recebido', 'Pedido registrado pelo site'))
                db.execute('''INSERT INTO pagamentos(pedido_id,metodo,provedor,status,valor_centavos)
                              VALUES (?, ?, ?, ?, ?)''', (order_id, 'a_combinar', 'demonstracao', 'pendente', total))
        except ValueError as exc:
            flash(request, str(exc), 'erro')
            return redirect('/carrinho')
        save_cart(request, {})
        return redirect(f'/pedido/{token}')

    @app.get('/pedido/{token}', response_class=HTMLResponse)
    def order_success(request: Request, token: str):
        if len(token) > 100:
            raise HTTPException(404, 'Pedido não encontrado.')
        with db_connect() as db:
            order = db.execute('''SELECT p.*, d.descricao entrega FROM pedidos p
                                   JOIN opcoes_entrega d ON d.id=p.opcao_entrega_id WHERE p.token_acesso=?''',
                               (token,)).fetchone()
            if not order:
                raise HTTPException(404, 'Pedido não encontrado.')
            items = db.execute('SELECT * FROM pedido_itens WHERE pedido_id=?', (order['id'],)).fetchall()
        return page(request, 'pedido.html', order=order, items=items)

    @app.get('/conta/cadastrar', response_class=HTMLResponse)
    def register_form(request: Request):
        return page(request, 'conta_cadastrar.html', error=None, values={})

    @app.post('/conta/cadastrar')
    async def register(request: Request):
        form = await valid_form(request)
        name = str(form.get('nome', '')).strip()[:100]
        email = str(form.get('email', '')).strip().lower()[:200]
        password = str(form.get('senha', ''))
        if len(name) < 3 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email) or len(password) < 12 or len(password)>128:
            return page(request, 'conta_cadastrar.html', status_code=422, values={'nome': name, 'email': email},
                        error='Informe nome, e-mail válido e uma senha de 12 a 128 caracteres.')
        with db_connect() as db:
            if db.execute('SELECT 1 FROM usuarios WHERE email=?', (email,)).fetchone():
                return page(request, 'conta_cadastrar.html', status_code=422, values={'nome': name, 'email': email},
                            error='Este e-mail já está cadastrado.')
            cursor = db.execute("INSERT INTO usuarios(nome,email,senha_hash,papel) VALUES (?,?,?,'cliente')",
                                (name, email, hash_password(password)))
            cid = cursor.lastrowid
        saved_cart = read_cart(request)
        request.session.clear()
        save_cart(request, saved_cart)
        request.session['customer_id'] = cid
        flash(request, 'Sua conta foi criada com sucesso.', 'sucesso')
        return redirect('/minha-conta')

    @app.get('/conta/entrar', response_class=HTMLResponse)
    def customer_login_form(request: Request):
        return page(request, 'conta_entrar.html', error=None)

    @app.post('/conta/entrar')
    async def customer_login(request: Request):
        form = await valid_form(request)
        email = str(form.get('email', '')).strip().lower()
        password = str(form.get('senha', ''))
        with db_connect() as db:
            user = db.execute("SELECT * FROM usuarios WHERE email=? AND papel='cliente' AND ativo=1", (email,)).fetchone()
        if not user or not verify_password(password, user['senha_hash']):
            return page(request, 'conta_entrar.html', status_code=401, error='E-mail ou senha incorretos.')
        cart = read_cart(request)
        request.session.clear()
        save_cart(request, cart)
        request.session['customer_id'] = user['id']
        flash(request, 'Bem-vindo de volta!', 'sucesso')
        return redirect('/minha-conta')

    @app.post('/conta/sair')
    async def customer_logout(request: Request):
        await valid_form(request)
        request.session.pop('customer_id', None)
        flash(request, 'Você saiu da sua conta.', 'info')
        return redirect('/')

    @app.get('/minha-conta', response_class=HTMLResponse)
    def my_account(request: Request):
        user = require_customer(request)
        with db_connect() as db:
            orders = db.execute('''SELECT p.*,o.descricao entrega FROM pedidos p
                JOIN opcoes_entrega o ON o.id=p.opcao_entrega_id
                WHERE p.usuario_id=? ORDER BY p.id DESC LIMIT 100''', (user['id'],)).fetchall()
        return page(request, 'minha_conta.html', orders=orders, user=user)

    @app.post('/produto/{product_id}/avaliar')
    async def create_review(request: Request, product_id: int):
        user = require_customer(request)
        form = await valid_form(request)
        try:
            rating = int(form.get('nota', 0))
        except (ValueError, TypeError):
            rating = 0
        comment = str(form.get('comentario', '')).strip()[:900]
        if rating not in range(1,6) or len(comment) < 8:
            flash(request, 'Escolha de 1 a 5 estrelas e escreva um comentário de ao menos 8 caracteres.', 'erro')
            return redirect(f'/produto/{product_id}')
        with db_connect() as db:
            if not db.execute('SELECT 1 FROM cupcakes WHERE id=? AND ativo=1', (product_id,)).fetchone():
                raise HTTPException(404, 'Produto não encontrado.')
            if db.execute('SELECT id FROM avaliacoes WHERE usuario_id=? AND cupcake_id=?', (user['id'], product_id)).fetchone():
                flash(request, 'Você já avaliou este produto.', 'erro')
                return redirect(f'/produto/{product_id}')
            db.execute("INSERT INTO avaliacoes(usuario_id,cupcake_id,nota,comentario,status) VALUES (?,?,?,?,'pendente')",
                       (user['id'], product_id, rating, comment))
        flash(request, 'Obrigado! Sua avaliação será analisada antes de aparecer na loja.', 'sucesso')
        return redirect(f'/produto/{product_id}')

    @app.get('/entrar', response_class=HTMLResponse)
    def login_form(request: Request):
        return page(request, 'entrar.html', error=None)

    @app.post('/entrar')
    async def login(request: Request):
        form = await valid_form(request)
        email = str(form.get('email', '')).strip().lower()
        password = str(form.get('senha', ''))
        with db_connect() as db:
            user = db.execute("SELECT * FROM usuarios WHERE email=? AND papel='admin' AND ativo=1", (email,)).fetchone()
        if not user or not verify_password(password, user['senha_hash']):
            return page(request, 'entrar.html', status_code=401, error='E-mail ou senha incorretos.')
        request.session.clear()
        request.session['admin_id'] = user['id']
        request.session['csrf_token'] = secrets.token_urlsafe(24)
        flash(request, 'Acesso administrativo autorizado.', 'sucesso')
        return redirect('/admin')

    @app.post('/sair')
    async def logout(request: Request):
        await valid_form(request)
        request.session.clear()
        return redirect('/')

    @app.get('/admin', response_class=HTMLResponse)
    def admin_home(request: Request):
        admin_id(request)
        with db_connect() as db:
            stats = {'pedidos': db.execute('SELECT COUNT(*) FROM pedidos').fetchone()[0],
                     'produtos': db.execute('SELECT COUNT(*) FROM cupcakes WHERE ativo=1').fetchone()[0],
                     'pendentes': db.execute("SELECT COUNT(*) FROM pedidos WHERE status IN ('recebido','confirmado','preparo')").fetchone()[0]}
            products = db.execute('''SELECT c.*,k.nome categoria FROM cupcakes c JOIN categorias k ON k.id=c.categoria_id
                                      WHERE c.excluido_em IS NULL ORDER BY c.ativo DESC,c.id''').fetchall()
            archived = db.execute('''SELECT id,nome,excluido_em FROM cupcakes WHERE excluido_em IS NOT NULL
                                     ORDER BY excluido_em DESC, id DESC LIMIT 100''').fetchall()
            orders = db.execute('SELECT * FROM pedidos ORDER BY id DESC LIMIT 6').fetchall()
        return page(request, 'admin.html', stats=stats, products=products, orders=orders, archived=archived)

    @app.get('/admin/produtos/novo', response_class=HTMLResponse)
    def new_product(request: Request):
        admin_id(request)
        with db_connect() as db:
            categories = db.execute('SELECT * FROM categorias ORDER BY id').fetchall()
        return page(request, 'admin_produto.html', product=None, categories=categories, error=None)

    @app.get('/admin/produtos/{product_id}/editar', response_class=HTMLResponse)
    def edit_product(request: Request, product_id: int):
        admin_id(request)
        with db_connect() as db:
            product = db.execute('SELECT * FROM cupcakes WHERE id=? AND excluido_em IS NULL', (product_id,)).fetchone()
            categories = db.execute('SELECT * FROM categorias ORDER BY id').fetchall()
        if not product:
            raise HTTPException(404, 'Produto não encontrado.')
        return page(request, 'admin_produto.html', product=product, categories=categories, error=None)

    @app.post('/admin/produtos/salvar')
    async def save_product(request: Request):
        user_id = admin_id(request)
        form = await valid_form(request)
        name = str(form.get('nome', '')).strip()[:100]
        description = str(form.get('descricao', '')).strip()[:500]
        nutrition = str(form.get('informacoes_nutricionais', '')).strip()[:1000]
        photo_key = str(form.get('imagem_id', 'chocolate')).strip()
        icon = PHOTOS.get(photo_key, {}).get('imagem_url', '')
        errors = []
        try:
            product_id = int(form.get('id', 0) or 0)
            category_id = int(form.get('categoria_id', 0))
            stock = int(form.get('estoque', 0))
            price = parse_brl(str(form.get('preco', '')))
            if product_id < 0:
                raise ValueError('Identificador do produto inválido.')
        except (ValueError, TypeError) as exc:
            errors.append(str(exc) or 'Valores inválidos.')
            product_id, category_id, stock, price = 0, 0, 0, 0
        if not icon or icon not in ALLOWED_PHOTO_URLS:
            errors.append('Selecione uma fotografia documentada da lista.')
        if len(name) < 3:
            errors.append('Informe um nome com pelo menos três caracteres.')
        if not description:
            errors.append('Informe uma descrição.')
        if stock < 0 or stock > 100000:
            errors.append('Estoque inválido.')
        with db_connect() as db:
            categories = db.execute('SELECT * FROM categorias ORDER BY id').fetchall()
            if not db.execute('SELECT id FROM categorias WHERE id=?', (category_id,)).fetchone():
                errors.append('Categoria inválida.')
            if product_id and not db.execute('''SELECT id FROM cupcakes WHERE id=? AND excluido_em IS NULL''',
                                             (product_id,)).fetchone():
                errors.append('Produto inexistente ou já excluído.')
            if not errors:
                db.execute('BEGIN IMMEDIATE')
                if product_id:
                    before_row = db.execute('''SELECT * FROM cupcakes WHERE id=? AND excluido_em IS NULL''',
                                            (product_id,)).fetchone()
                    if before_row is None:
                        raise HTTPException(409, 'Produto excluído durante a edição.')
                    before = snapshot_produto(before_row)
                    db.execute('''UPDATE cupcakes SET categoria_id=?,nome=?,descricao=?,preco_centavos=?,
                                  estoque=?,imagem_url=?,informacoes_nutricionais=? WHERE id=?''',
                               (category_id, name, description, price, stock, icon, nutrition or None, product_id))
                else:
                    before = None
                    cur = db.execute('''INSERT INTO cupcakes(categoria_id,nome,descricao,preco_centavos,estoque,
                                        imagem_url,informacoes_nutricionais) VALUES (?,?,?,?,?,?,?)''',
                                     (category_id, name, description, price, stock, icon, nutrition or None))
                    product_id = cur.lastrowid
                after_row = db.execute('SELECT * FROM cupcakes WHERE id=?', (product_id,)).fetchone()
                after = snapshot_produto(after_row)
                if before is None or before != after:
                    auditar_produto(db, user_id, product_id,
                                   'criar produto' if before is None else 'editar produto', before, after)
                if before is not None and before['estoque'] != after['estoque']:
                    db.execute('''INSERT INTO estoque_movimentos(cupcake_id,variacao,motivo) VALUES (?,?,?)''',
                               (product_id, after['estoque'] - before['estoque'],
                                'Ajuste manual pelo administrador'))
        if errors:
            return page(request, 'admin_produto.html', status_code=422, product=None,
                        categories=categories, error=' '.join(errors), form_values=dict(form))
        flash(request, 'Produto salvo com sucesso.', 'sucesso')
        return redirect('/admin')

    @app.post('/admin/produtos/{product_id}/alternar')
    async def toggle_product(request: Request, product_id: int):
        user_id = admin_id(request)
        await valid_form(request)
        with db_connect() as db:
            p = db.execute('SELECT * FROM cupcakes WHERE id=? AND excluido_em IS NULL', (product_id,)).fetchone()
            if not p:
                raise HTTPException(404, 'Produto não encontrado.')
            db.execute('UPDATE cupcakes SET ativo=? WHERE id=?', (0 if p['ativo'] else 1, product_id))
            depois = db.execute('SELECT * FROM cupcakes WHERE id=?', (product_id,)).fetchone()
            auditar_produto(db, user_id, product_id, 'alterar visibilidade',
                           snapshot_produto(p), snapshot_produto(depois))
        flash(request, 'Visibilidade atualizada.', 'sucesso')
        return redirect('/admin')

    @app.post('/admin/produtos/{product_id}/excluir')
    async def archive_product(request: Request, product_id: int):
        # Exclusão lógica mantém integridade de pedidos concluídos, avaliações e auditoria.
        usuario = admin_id(request)
        await valid_form(request)
        with db_connect() as db:
            db.execute('BEGIN IMMEDIATE')
            item = db.execute('SELECT * FROM cupcakes WHERE id=? AND excluido_em IS NULL',
                              (product_id,)).fetchone()
            if item is None:
                raise HTTPException(404, 'Produto inexistente ou já excluído.')
            active = db.execute('''SELECT 1 FROM pedido_itens i JOIN pedidos p ON p.id=i.pedido_id
                                   WHERE i.cupcake_id=? AND p.status NOT IN ('concluido','cancelado')
                                   LIMIT 1''', (product_id,)).fetchone()
            if active is not None:
                raise HTTPException(422, 'Este cupcake possui pedido ativo e não pode ser excluído.')
            in_combo = db.execute('''SELECT 1 FROM combo_itens i JOIN combos c ON c.id=i.combo_id
                                     WHERE i.cupcake_id=? AND c.ativo=1 LIMIT 1''',
                                  (product_id,)).fetchone()
            if in_combo is not None:
                raise HTTPException(422, 'Este cupcake pertence a um combo ativo e não pode ser excluído.')
            db.execute('''UPDATE cupcakes SET ativo=0, excluido_em=CURRENT_TIMESTAMP
                          WHERE id=? AND excluido_em IS NULL''', (product_id,))
            depois = db.execute('SELECT * FROM cupcakes WHERE id=?', (product_id,)).fetchone()
            auditar_produto(db, usuario, product_id, 'excluir produto',
                           snapshot_produto(item), snapshot_produto(depois))
        flash(request, 'Produto excluído da vitrine e arquivado para preservar o histórico.', 'sucesso')
        return redirect('/admin')

    @app.get('/admin/produtos/{product_id}/historico', response_class=HTMLResponse)
    def product_history(request: Request, product_id: int):
        admin_id(request)
        with db_connect() as db:
            produto = db.execute('SELECT id, nome, excluido_em FROM cupcakes WHERE id=?',
                                 (product_id,)).fetchone()
            if produto is None:
                raise HTTPException(404, 'Produto não encontrado.')
            rows = db.execute('''SELECT a.acao,a.descricao,a.criado_em,u.nome usuario_nome
                                 FROM auditoria a LEFT JOIN usuarios u ON u.id=a.usuario_id
                                 WHERE a.entidade='cupcakes' AND a.entidade_id=?
                                 ORDER BY a.id DESC LIMIT 150''', (product_id,)).fetchall()
            history = []
            for row in rows:
                desc = row['descricao'] or ''
                try:
                    data = json.loads(desc)
                    if isinstance(data, dict) and set(data) == {'antes','depois'}:
                        antes = data['antes'] or {}
                        depois = data['depois'] or {}
                        changes = [key for key in depois if antes.get(key) != depois.get(key)]
                        desc = 'Campos alterados: ' + ', '.join(changes) if changes else 'Sem alterações de campos'
                except (ValueError, TypeError, AttributeError):
                    pass
                history.append({'acao':row['acao'],'descricao':desc,
                                'criado_em':row['criado_em'], 'usuario_nome':row['usuario_nome'] or 'Sistema'})
        return page(request, 'admin_produto_historico.html', product=produto, history=history)

    @app.get('/admin/pedidos', response_class=HTMLResponse)
    def admin_orders(request: Request):
        admin_id(request)
        with db_connect() as db:
            orders = db.execute('''SELECT p.*, o.descricao entrega FROM pedidos p JOIN opcoes_entrega o ON o.id=p.opcao_entrega_id
                                   ORDER BY p.id DESC LIMIT 150''').fetchall()
        return page(request, 'admin_pedidos.html', orders=orders, next_status=NEXT_STATUS)

    @app.post('/admin/pedidos/{order_id}/status')
    async def update_status(request: Request, order_id: int):
        user_id = admin_id(request)
        form = await valid_form(request)
        target = str(form.get('status', '')).strip()
        with db_connect() as db:
            db.execute('BEGIN IMMEDIATE')
            order = db.execute('SELECT * FROM pedidos WHERE id=?', (order_id,)).fetchone()
            if not order:
                raise HTTPException(404, 'Pedido não encontrado.')
            if target not in NEXT_STATUS.get(order['status'], []):
                raise HTTPException(422, 'Mudança de status não permitida.')
            if target == 'cancelado':
                items = db.execute('SELECT cupcake_id,quantidade FROM pedido_itens WHERE pedido_id=?', (order_id,)).fetchall()
                # Um cupom de uso limitado volta a ficar disponível se o pedido for cancelado.
                db.execute('DELETE FROM cupom_utilizacoes WHERE pedido_id=?', (order_id,))
                for item in items:
                    if item['cupcake_id'] is not None:
                        db.execute('UPDATE cupcakes SET estoque=estoque+? WHERE id=?', (item['quantidade'], item['cupcake_id']))
                        db.execute('INSERT INTO estoque_movimentos(cupcake_id,pedido_id,variacao,motivo) VALUES (?,?,?,?)',
                                   (item['cupcake_id'], order_id, item['quantidade'], 'Pedido cancelado'))
            db.execute('UPDATE pedidos SET status=? WHERE id=?', (target, order_id))
            db.execute('INSERT INTO eventos_pedido(pedido_id,status,observacao) VALUES (?,?,?)',
                       (order_id, target, 'Atualizado pela administração'))
            db.execute('INSERT INTO auditoria(usuario_id,entidade,entidade_id,acao,descricao) VALUES (?,?,?,?,?)',
                       (user_id, 'pedidos', order_id, 'alterar status', f'{order["status"]} -> {target}'))
        flash(request, 'Status do pedido atualizado.', 'sucesso')
        return redirect('/admin/pedidos')

    @app.get('/admin/cupons', response_class=HTMLResponse)
    def admin_coupons(request: Request):
        admin_id(request)
        with db_connect() as db:
            coupons = db.execute('''SELECT c.*,(SELECT COUNT(*) FROM cupom_utilizacoes u WHERE u.cupom_id=c.id) usos
                                    FROM cupons c ORDER BY c.id DESC''').fetchall()
        return page(request, 'admin_cupons.html', coupons=coupons, error=None)

    @app.post('/admin/cupons/criar')
    async def create_coupon(request: Request):
        uid = admin_id(request)
        form = await valid_form(request)
        code = str(form.get('codigo', '')).strip().upper()
        kind = str(form.get('tipo', ''))
        try:
            amount = int(form.get('valor', -1)) if kind == 'percentual' else parse_brl(str(form.get('valor', '')))
            minimum = parse_brl(str(form.get('minimo', '0')))
            limit = int(form.get('limite', '0') or 0)
        except (ValueError, TypeError):
            raise HTTPException(422, 'Valores inválidos no cupom.')
        if (not re.fullmatch(r'[A-Z0-9_-]{3,30}', code) or kind not in ('percentual','fixo') or
            amount <= 0 or (kind=='percentual' and amount>100) or limit < 0 or limit>100000):
            raise HTTPException(422, 'Cupom inválido. Use código de 3 a 30 caracteres, desconto positivo e percentual até 100.')
        with db_connect() as db:
            if db.execute('SELECT 1 FROM cupons WHERE codigo=?', (code,)).fetchone():
                flash(request, 'Já existe um cupom com esse código.', 'erro')
                return redirect('/admin/cupons')
            db.execute('''INSERT INTO cupons(codigo,tipo,valor,valor_minimo_centavos,limite_uso,ativo)
                         VALUES (?,?,?,?,?,1)''', (code,kind,amount,minimum,limit or None))
            db.execute("INSERT INTO auditoria(usuario_id,entidade,acao,descricao) VALUES (?,'cupons','criar',?)",(uid,code))
        flash(request, 'Cupom criado.', 'sucesso')
        return redirect('/admin/cupons')

    @app.post('/admin/cupons/{coupon_id}/alternar')
    async def toggle_coupon(request: Request, coupon_id: int):
        uid = admin_id(request)
        await valid_form(request)
        with db_connect() as db:
            item = db.execute('SELECT * FROM cupons WHERE id=?', (coupon_id,)).fetchone()
            if not item: raise HTTPException(404, 'Cupom não encontrado.')
            db.execute('UPDATE cupons SET ativo=? WHERE id=?', (0 if item['ativo'] else 1,coupon_id))
            db.execute("INSERT INTO auditoria(usuario_id,entidade,acao,descricao) VALUES (?,'cupons','alternar',?)",(uid,item['codigo']))
        return redirect('/admin/cupons')

    @app.get('/admin/avaliacoes', response_class=HTMLResponse)
    def admin_reviews(request: Request):
        admin_id(request)
        with db_connect() as db:
            reviews = db.execute('''SELECT a.*,c.nome produto FROM avaliacoes a
                       JOIN cupcakes c ON c.id=a.cupcake_id ORDER BY (a.status='pendente') DESC,a.id DESC LIMIT 200''').fetchall()
        return page(request, 'admin_avaliacoes.html', reviews=reviews)

    @app.post('/admin/avaliacoes/{review_id}/moderacao')
    async def review_moderation(request: Request, review_id: int):
        uid = admin_id(request)
        form = await valid_form(request)
        status = str(form.get('status', ''))
        answer = str(form.get('resposta', '')).strip()[:600]
        if status not in ('publicada','oculta','pendente'):
            raise HTTPException(422, 'Estado inválido.')
        with db_connect() as db:
            if not db.execute('SELECT 1 FROM avaliacoes WHERE id=?', (review_id,)).fetchone():
                raise HTTPException(404, 'Avaliação não encontrada.')
            db.execute('''UPDATE avaliacoes SET status=?,resposta_admin=?,respondida_em=CASE WHEN ?<>''
                          THEN CURRENT_TIMESTAMP ELSE NULL END WHERE id=?''', (status,answer,answer,review_id))
            db.execute("INSERT INTO auditoria(usuario_id,entidade,entidade_id,acao) VALUES (?,'avaliacoes',?,'moderar')",(uid,review_id))
        flash(request, 'Avaliação atualizada.', 'sucesso')
        return redirect('/admin/avaliacoes')

    @app.get('/admin/relatorios', response_class=HTMLResponse)
    def reports(request: Request, mes: str = ''):
        admin_id(request)
        if mes and not re.fullmatch(r'20\d\d-(0[1-9]|1[0-2])',mes):
            raise HTTPException(422, 'Mês inválido.')
        condition = " AND strftime('%Y-%m',p.criado_em)=?" if mes else ''
        params = (mes,) if mes else ()
        with db_connect() as db:
            overview = db.execute('''SELECT COUNT(*) pedidos,COALESCE(SUM(total_centavos),0) receita,
                    COALESCE(SUM(desconto_centavos),0) descontos FROM pedidos p
                    WHERE status<>'cancelado' ''' + condition, params).fetchone()
            top = db.execute('''SELECT pi.nome_snapshot nome,SUM(pi.quantidade) unidades
                    FROM pedido_itens pi JOIN pedidos p ON p.id=pi.pedido_id
                    WHERE p.status<>'cancelado' '''+condition+''' GROUP BY pi.nome_snapshot
                    ORDER BY unidades DESC LIMIT 10''',params).fetchall()
            by_status = db.execute('SELECT status,COUNT(*) quantidade FROM pedidos GROUP BY status ORDER BY quantidade DESC').fetchall()
        return page(request, 'admin_relatorios.html', overview=overview, top=top, by_status=by_status, mes=mes)

    @app.get('/admin/entregas', response_class=HTMLResponse)
    def deliveries_admin(request: Request):
        admin_id(request)
        with db_connect() as db:
            options = db.execute('SELECT * FROM opcoes_entrega ORDER BY id').fetchall()
        return page(request, 'admin_entregas.html', options=options)

    @app.post('/admin/entregas/{delivery_id}/salvar')
    async def update_delivery(request: Request, delivery_id: int):
        uid = admin_id(request)
        form = await valid_form(request)
        description = str(form.get('descricao','')).strip()[:100]
        active = bool(form.get('ativo'))
        try: cost = parse_brl(str(form.get('custo','0')))
        except ValueError: raise HTTPException(422, 'Custo inválido.')
        if len(description)<4:
            raise HTTPException(422, 'Informe uma descrição válida.')
        with db_connect() as db:
            target = db.execute('SELECT id,ativa FROM opcoes_entrega WHERE id=?',(delivery_id,)).fetchone()
            if not target: raise HTTPException(404, 'Modalidade não encontrada.')
            if not active and target['ativa'] and db.execute('SELECT COUNT(*) FROM opcoes_entrega WHERE ativa=1').fetchone()[0]<=1:
                flash(request, 'Mantenha pelo menos uma modalidade ativa.', 'erro')
                return redirect('/admin/entregas')
            db.execute('UPDATE opcoes_entrega SET descricao=?,custo_base_centavos=?,ativa=? WHERE id=?',
                       (description,cost,int(active),delivery_id))
            db.execute("INSERT INTO auditoria(usuario_id,entidade,entidade_id,acao) VALUES (?,'opcoes_entrega',?,'editar')",(uid,delivery_id))
        flash(request, 'Modalidade de entrega salva.', 'sucesso')
        return redirect('/admin/entregas')

    @app.get('/admin/clientes', response_class=HTMLResponse)
    def admin_customers(request: Request):
        admin_id(request)
        with db_connect() as db:
            users = db.execute("SELECT id,nome,email,ativo,criado_em FROM usuarios WHERE papel='cliente' ORDER BY id DESC").fetchall()
        return page(request, 'admin_clientes.html', users=users)

    @app.post('/admin/clientes/{user_id}/alternar')
    async def toggle_customer(request: Request, user_id: int):
        uid = admin_id(request)
        await valid_form(request)
        with db_connect() as db:
            user = db.execute("SELECT ativo FROM usuarios WHERE id=? AND papel='cliente'",(user_id,)).fetchone()
            if not user: raise HTTPException(404, 'Conta não encontrada.')
            db.execute('UPDATE usuarios SET ativo=? WHERE id=?', (0 if user['ativo'] else 1,user_id))
            db.execute("INSERT INTO auditoria(usuario_id,entidade,entidade_id,acao) VALUES (?,'usuarios',?,'alternar acesso')",(uid,user_id))
        return redirect('/admin/clientes')

    @app.get('/saude')
    def health():
        return {'status': 'ok', 'servico': 'loja-cupcakes'}

    return app


app = create_app()
