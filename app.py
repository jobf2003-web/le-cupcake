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
from datetime import date, timedelta, datetime, timezone
from pathlib import Path
import re
import secrets
import sqlite3
from typing import Any

from photo_sources import PHOTOS, PRODUCT_PHOTO_KEYS, ALLOWED_PHOTO_URLS
from commerce_delivery import frete_por_regiao, validar_agenda, cep_normalizado
from commerce_combos import build_bundle, sanitize_combos, COMBO_NOME, MIN_PECAS, MAX_PECAS, MAX_COMBOS
from migrations import apply_migrations
from order_notifications import (notify_new_order,notify_status_change,user_notifications,
                                 mark_user_notifications_read,STATUS_LABELS)
from sales_reporting import report_data
from payment_demo import (PAYMENT_METHODS, DEMO_METHODS, payment_label,
                          validate_payment_method, simulate_decision,
                          restore_order_stock, log_payment_event)
from customer_relationship import send_password_reset_email, make_reset_digest, get_recommendations, active_promotions, valid_dates

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
    app.state.test_reset_links = [] if testing else None  # Somente testes; nunca renderizado em páginas.

    campos_produto = ('nome', 'descricao', 'categoria_id', 'preco_centavos',
                      'estoque', 'imagem_url', 'informacoes_nutricionais',
                      'ativo', 'excluido_em', 'ingredientes')

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
            if not db.execute('SELECT 1 FROM combos WHERE nome=?', (COMBO_NOME,)).fetchone():
                db.execute('INSERT INTO combos(nome,descricao,preco_centavos) VALUES (?,?,0)',
                           (COMBO_NOME,'Combinação do cliente, preços calculados por componente'))
            if not db.execute('SELECT 1 FROM opcoes_entrega LIMIT 1').fetchone():
                db.executemany('INSERT INTO opcoes_entrega(tipo,descricao,custo_base_centavos) VALUES (?,?,?)',
                               [('retirada', 'Retirar na loja', 0),
                                ('entrega', 'Entrega local (taxa fixa)', 800)])
            # Catálogo administrativo de alergênicos. Não associar automaticamente a receitas desconhecidas.
            for allergen in ('Leite', 'Ovos', 'Trigo (glúten)', 'Soja', 'Amendoim', 'Castanhas'):
                db.execute('INSERT OR IGNORE INTO alergenos(nome) VALUES (?)', (allergen,))
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

    def read_combos(request: Request) -> list[dict[int,int]]:
        return sanitize_combos(request.session.get('custom_combos', []))

    def save_combos(request: Request, combos: list[dict[int,int]]):
        request.session['custom_combos'] = [{str(k):v for k,v in item.items()} for item in combos]

    def bundle_cart(db: sqlite3.Connection, request: Request):
        lines, subtotal = cart_lines(db, read_cart(request))
        combos, combo_total, allocations, all_available = build_bundle(db, read_cart(request), read_combos(request))
        return lines, combos, subtotal+combo_total, allocations, all_available

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
            user = db.execute("SELECT id,nome,email,criado_em,sessao_versao FROM usuarios WHERE id=? AND papel='cliente' AND ativo=1",
                              (user_id,)).fetchone()
            if user and int(request.session.get('customer_auth_version', 0)) != int(user['sessao_versao']):
                request.session.pop('customer_id', None)
                request.session.pop('customer_auth_version', None)
                return None
            return user

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
        context.update(photos=PHOTOS, cart_count=sum(read_cart(request).values())+
                       sum(sum(c.values()) for c in read_combos(request)), csrf=csrf(request),
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
            customer = current_customer(request)
            recommendations = get_recommendations(db, customer['id']) if customer else []
            promotions = active_promotions(db)
        return page(request, 'index.html', products=products, categories=categories,
                    busca=search, categoria=category, recommendations=recommendations,
                    promotions=promotions, recommendations_personalized=bool(customer))

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
            allergens = db.execute('''SELECT a.nome FROM alergenos a
                    JOIN cupcake_alergenos ca ON ca.alergeno_id=a.id
                    WHERE ca.cupcake_id=? ORDER BY a.nome''', (product_id,)).fetchall()
            already_reviewed = False
            customer = current_customer(request)
            if customer:
                already_reviewed = bool(db.execute('SELECT 1 FROM avaliacoes WHERE usuario_id=? AND cupcake_id=?',
                                                 (customer['id'], product_id)).fetchone())
        return page(request, 'produto.html', product=p, reviews=reviews,
                    recommendations=recommendations, already_reviewed=already_reviewed, allergens=allergens)

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

    @app.get('/combos', response_class=HTMLResponse)
    def combo_builder(request: Request):
        with db_connect() as db:
            products = db.execute('''SELECT id,nome,preco_centavos,estoque FROM cupcakes
                WHERE ativo=1 AND excluido_em IS NULL AND estoque>0 ORDER BY id''').fetchall()
        return page(request,'combos.html',products=products,min_pieces=MIN_PECAS,max_pieces=MAX_PECAS)

    @app.post('/combos/adicionar')
    async def add_combo(request: Request):
        form=await valid_form(request)
        raw={}
        for k,v in form.multi_items():
            if not k.startswith('q_'):
                continue
            try:
                product_id, qty=int(k[2:]),int(v)
            except (TypeError,ValueError):
                raise HTTPException(422,'Quantidade inválida para combo.')
            if qty<0 or qty>MAX_PECAS:
                raise HTTPException(422,'Quantidade de combo fora do limite.')
            if qty:
                raw[str(product_id)] = qty
        combination=sanitize_combos([raw])
        if not combination:
            raise HTTPException(422,f'Monte um combo com {MIN_PECAS} a {MAX_PECAS} cupcakes.')
        combos=read_combos(request)
        if len(combos)>=MAX_COMBOS:
            raise HTTPException(422,'Limite de combos do carrinho atingido.')
        combos.append(combination[0])
        with db_connect() as db:
            _,_,_,available=build_bundle(db,read_cart(request),combos)
            if not available:
                raise HTTPException(422,'Estoque insuficiente para a composição do combo.')
        save_combos(request,combos)
        flash(request,'Combo personalizado adicionado ao carrinho.','sucesso')
        return redirect('/carrinho')

    @app.post('/combos/remover')
    async def remove_combo(request: Request):
        form=await valid_form(request)
        try:
            index=int(form.get('indice','-1'))
        except (TypeError,ValueError):
            raise HTTPException(422,'Combo inválido.')
        combos=read_combos(request)
        if index<0 or index>=len(combos):
            raise HTTPException(422,'Combo não encontrado no carrinho.')
        combos.pop(index)
        save_combos(request,combos)
        return redirect('/carrinho')

    @app.get('/carrinho', response_class=HTMLResponse)
    def shopping_cart(request: Request):
        with db_connect() as db:
            lines, combos, subtotal, allocations, all_available = bundle_cart(db,request)
        return page(request, 'carrinho.html', lines=lines, combos=combos,
                    subtotal=subtotal, all_available=all_available)

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

    @app.get('/api/frete')
    def shipping_quote(opcao_entrega: int, cep: str = ''):
        with db_connect() as db:
            option = db.execute('SELECT * FROM opcoes_entrega WHERE id=? AND ativa=1', (opcao_entrega,)).fetchone()
            if not option:
                raise HTTPException(422, 'Modalidade de recebimento indisponível.')
            try:
                fee, region_id = frete_por_regiao(db, option, cep)
            except ValueError as exc:
                raise HTTPException(422, str(exc)) from None
        return {'frete_centavos':fee, 'regiao_id':region_id,
                'demonstrativo':True, 'descricao':'Taxa local configurada; não é cotação de transportadora.'}

    @app.get('/checkout', response_class=HTMLResponse)
    def checkout_form(request: Request):
        with db_connect() as db:
            lines, combo_lines, subtotal, allocations, all_available = bundle_cart(db,request)
            shipping = db.execute('SELECT * FROM opcoes_entrega WHERE ativa=1 ORDER BY custo_base_centavos').fetchall()
            windows = db.execute('''SELECT j.*,o.tipo FROM janelas_entrega j JOIN opcoes_entrega o
                          ON o.id=j.opcao_entrega_id WHERE o.ativa=1 ORDER BY j.inicio''').fetchall()
            region_count = db.execute('SELECT COUNT(*) FROM regioes_entrega WHERE ativa=1').fetchone()[0]
        if not lines and not combo_lines:
            flash(request, 'Adicione cupcakes ou combos ao carrinho antes de finalizar.', 'erro')
            return redirect('/carrinho')
        user = current_customer(request)
        return page(request, 'checkout.html', lines=lines, combos=combo_lines, subtotal=subtotal, shipping=shipping,
                    windows=windows, region_count=region_count,
                    values={'nome':user['nome'],'email':user['email']} if user else {}, errors=[],
                    payment_methods=PAYMENT_METHODS)

    @app.post('/checkout')
    async def place_order(request: Request):
        form = await valid_form(request)
        cart = read_cart(request)
        name = str(form.get('nome', '')).strip()[:120]
        email = str(form.get('email', '')).strip().lower()[:200]
        phone = str(form.get('telefone', '')).strip()[:30]
        address = str(form.get('endereco', '')).strip()[:400]
        coupon_code = str(form.get('cupom', '')).strip().upper()[:30]
        payment_method = str(form.get('metodo_pagamento', 'a_combinar')).strip()[:40]
        cep = str(form.get('cep', '')).strip()[:12]
        scheduled_for = str(form.get('data_agendada', '')).strip()[:30]
        try:
            window_id = int(form.get('janela_entrega', '0') or '0')
        except (ValueError, TypeError):
            window_id = 0
        try:
            shipping_id = int(form.get('opcao_entrega', '0'))
        except (ValueError, TypeError):
            shipping_id = 0
        errors = []
        try:
            validate_payment_method(payment_method)
        except ValueError as exc:
            errors.append(str(exc))
        if len(name) < 3:
            errors.append('Informe seu nome completo.')
        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
            errors.append('Informe um e-mail válido.')
        if len(re.sub(r'\D', '', phone)) < 10:
            errors.append('Informe um telefone com DDD.')
        with db_connect() as db:
            lines, combo_lines, subtotal, allocations, all_available = bundle_cart(db,request)
            shipping = db.execute('SELECT * FROM opcoes_entrega WHERE ativa=1 ORDER BY custo_base_centavos').fetchall()
            windows = db.execute('''SELECT j.*,o.tipo FROM janelas_entrega j JOIN opcoes_entrega o
                          ON o.id=j.opcao_entrega_id WHERE o.ativa=1 ORDER BY j.inicio''').fetchall()
            region_count = db.execute('SELECT COUNT(*) FROM regioes_entrega WHERE ativa=1').fetchone()[0]
            ship = db.execute('SELECT * FROM opcoes_entrega WHERE id=? AND ativa=1', (shipping_id,)).fetchone()
            if ship:
                try:
                    if ship['tipo']=='entrega' and cep:
                        cep_normalizado(cep)
                    frete_por_regiao(db, ship, cep)
                    validar_agenda(db, shipping_id, scheduled_for, window_id)
                except ValueError as exc:
                    errors.append(str(exc))
        if not lines and not combo_lines:
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
        if any(not x['available'] for x in lines) or not all_available:
            errors.append('Há itens indisponíveis ou sem estoque suficiente no carrinho e combos.')
        if errors:
            return page(request, 'checkout.html', status_code=422, lines=lines, combos=combo_lines,
                        subtotal=subtotal, shipping=shipping, windows=windows, region_count=region_count,
                        values=dict(form), errors=errors, payment_methods=PAYMENT_METHODS)
        token = secrets.token_urlsafe(24)
        try:
            with db_connect() as db:
                db.execute('BEGIN IMMEDIATE')
                lines_now, combos_now, subtotal_real, allocations, all_available = bundle_cart(db,request)
                if not all_available or any(not line['available'] for line in lines_now):
                    raise ValueError('Estoque insuficiente para os itens e combos. Volte ao carrinho.')
                ship_now = db.execute('SELECT * FROM opcoes_entrega WHERE id=? AND ativa=1', (shipping_id,)).fetchone()
                if ship_now is None:
                    raise ValueError('A forma de entrega não está mais disponível.')
                freight, region_id = frete_por_regiao(db, ship_now, cep)
                date_selected, window_selected = validar_agenda(db, shipping_id, scheduled_for, window_id)
                coupon, discount = discount_for(db, coupon_code, subtotal_real)
                total = subtotal_real + freight - discount
                logged = current_customer(request)
                cur = db.execute('''INSERT INTO pedidos(usuario_id,opcao_entrega_id, contato_nome,contato_email,contato_telefone,
                    endereco_entrega,token_acesso,subtotal_centavos,frete_centavos,desconto_centavos,total_centavos,
                    cep_entrega,regiao_entrega_id,agendado_para,janela_entrega_id)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (logged['id'] if logged else None, shipping_id, name, email, phone,
                    address if ship_now['tipo']=='entrega' else None, token, subtotal_real, freight, discount, total,
                    cep_normalizado(cep) if ship_now['tipo']=='entrega' and cep.strip() else None,
                    region_id, date_selected, window_selected))
                order_id = cur.lastrowid
                if coupon:
                    db.execute('INSERT INTO cupom_utilizacoes(cupom_id,pedido_id) VALUES (?,?)', (coupon['id'], order_id))
                for line in lines_now:
                    p = db.execute('SELECT id,nome,preco_centavos FROM cupcakes WHERE id=?', (line['product']['id'],)).fetchone()
                    changed = db.execute('UPDATE cupcakes SET estoque=estoque-? WHERE id=? AND estoque>=?',
                                         (line['qty'], p['id'], line['qty']))
                    if changed.rowcount != 1:
                        raise ValueError('Estoque insuficiente. Revise o carrinho.')
                    db.execute('''INSERT INTO pedido_itens(pedido_id,cupcake_id,nome_snapshot,quantidade,preco_unitario_centavos)
                        VALUES (?,?,?,?,?)''', (order_id, p['id'], p['nome'], line['qty'], p['preco_centavos']))
                    db.execute('INSERT INTO estoque_movimentos(cupcake_id,pedido_id,variacao,motivo) VALUES (?,?,?,?)',
                               (p['id'], order_id, -line['qty'], 'Pedido recebido'))
                if combos_now:
                    default_combo=db.execute('SELECT id FROM combos WHERE nome=?',(COMBO_NOME,)).fetchone()
                    if default_combo is None:
                        raise ValueError('Configuração de combos não encontrada.')
                    for combo in combos_now:
                        itemcur=db.execute('''INSERT INTO pedido_itens(pedido_id,combo_id,nome_snapshot,quantidade,preco_unitario_centavos)
                            VALUES (?,?,?,?,?)''',(order_id,default_combo['id'],COMBO_NOME,1,combo['total']))
                        for part in combo['parts']:
                            changed=db.execute('UPDATE cupcakes SET estoque=estoque-? WHERE id=? AND estoque>=? AND ativo=1',
                                         (part['qty'],part['id'],part['qty']))
                            if changed.rowcount != 1:
                                raise ValueError('Estoque insuficiente para o combo. Revise o carrinho.')
                            db.execute('''INSERT INTO pedido_combo_componentes(pedido_item_id,cupcake_id,quantidade,nome_snapshot,preco_unitario_centavos)
                                VALUES (?,?,?,?,?)''',(itemcur.lastrowid,part['id'],part['qty'],part['nome'],part['price']))
                            db.execute('''INSERT INTO estoque_movimentos(cupcake_id,pedido_id,variacao,motivo)
                                VALUES (?,?,?,?)''',(part['id'],order_id,-part['qty'],'Combo personalizado no pedido'))
                db.execute('INSERT INTO eventos_pedido(pedido_id,status,observacao) VALUES (?, ?, ?)',
                           (order_id, 'recebido', 'Pedido registrado pelo site'))
                db.execute('''INSERT INTO pagamentos(pedido_id,metodo,provedor,status,valor_centavos)
                              VALUES (?, ?, ?, ?, ?)''',
                           (order_id, payment_method,
                            'simulador_local' if payment_method in DEMO_METHODS else 'pagamento_posterior',
                            'pendente', total))
                # Avisos internos transacionais; não envia SMS ou e-mail externo.
                notify_new_order(db, order_id, logged['id'] if logged else None)
        except ValueError as exc:
            flash(request, str(exc), 'erro')
            return redirect('/carrinho')
        save_cart(request, {})
        save_combos(request, [])
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
            payment = db.execute('''SELECT * FROM pagamentos WHERE pedido_id=? ORDER BY id DESC LIMIT 1''',
                                 (order['id'],)).fetchone()
            items = db.execute('SELECT * FROM pedido_itens WHERE pedido_id=?', (order['id'],)).fetchall()
            slot = db.execute('SELECT inicio,fim FROM janelas_entrega WHERE id=?', (order['janela_entrega_id'],)).fetchone() if order['janela_entrega_id'] else None
            components = db.execute('''SELECT pc.pedido_item_id,pc.nome_snapshot,pc.quantidade FROM pedido_combo_componentes pc
                        JOIN pedido_itens i ON i.id=pc.pedido_item_id WHERE i.pedido_id=?''', (order['id'],)).fetchall()
            components_by_line = {}
            for comp in components:
                components_by_line.setdefault(comp['pedido_item_id'], []).append(comp)
        return page(request, 'pedido.html', order=order, items=items, slot=slot,
                    payment=payment, payment_label=payment_label,
                    components_by_line=components_by_line, demo_methods=DEMO_METHODS)

    @app.post('/pedido/{token}/simular-pagamento')
    async def simulate_payment_request(request: Request, token: str):
        # Token secreto do pedido + CSRF. A ação NÃO envolve dinheiro ou gateway.
        await valid_form(request)
        if not re.fullmatch(r'[A-Za-z0-9_-]{10,100}', token):
            raise HTTPException(404, 'Pedido não encontrado.')
        form = await request.form()
        decision = str(form.get('decisao','')).strip()
        with db_connect() as db:
            db.execute('BEGIN IMMEDIATE')
            order = db.execute('SELECT id,usuario_id FROM pedidos WHERE token_acesso=?', (token,)).fetchone()
            if not order:
                raise HTTPException(404, 'Pedido não encontrado.')
            try:
                status, changed = simulate_decision(db, order_id=order['id'], decision=decision)
            except ValueError as exc:
                raise HTTPException(422, str(exc)) from None
            if changed:
                if status == 'recusado':
                    notify_status_change(db, order['id'], order['usuario_id'], 'cancelado')
                db.execute('''INSERT INTO auditoria(usuario_id,entidade,entidade_id,acao,descricao)
                              VALUES (NULL,'pagamentos',?,'simulacao',?)''',
                           (order['id'], f'{decision}: sem cobrança real'))
        flash(request, ('Aprovação simulada registrada — nenhuma cobrança realizada.' if status == 'aprovado'
                        else 'Recusa simulada: pedido cancelado e estoque devolvido.'), 'info')
        return redirect('/pedido/'+token)

    @app.get('/api/pedido/{token}/status')
    def order_status_api(token: str):
        # O token de alta entropia funciona como credencial da página de pedido.
        # A API expõe somente status, ETA e eventos, nunca dados pessoais.
        if not re.fullmatch(r'[A-Za-z0-9_-]{10,100}', token):
            raise HTTPException(404, 'Pedido não encontrado.')
        with db_connect() as db:
            order = db.execute('SELECT id,status,previsao_entrega_em,agendado_para FROM pedidos WHERE token_acesso=?',
                               (token,)).fetchone()
            if not order:
                raise HTTPException(404, 'Pedido não encontrado.')
            payment = db.execute('''SELECT metodo,status,provedor FROM pagamentos WHERE pedido_id=?
                                     ORDER BY id DESC LIMIT 1''', (order['id'],)).fetchone()
            events = db.execute('''SELECT status,ocorrido_em FROM eventos_pedido
                         WHERE pedido_id=? ORDER BY id DESC LIMIT 12''', (order['id'],)).fetchall()
        from fastapi.responses import JSONResponse
        return JSONResponse({'status':order['status'],
                             'status_nome': STATUS_LABELS[order['status']],
                             'previsao_entrega_em':order['previsao_entrega_em'],
                             'agendado_para':order['agendado_para'],
                             'eventos':[{'status':r['status'],'data':r['ocorrido_em']} for r in events],
                             'pagamento': {'tipo':payment['metodo'], 'status':payment['status'],
                                           'demonstrativo':payment['provedor']=='simulador_local'} if payment else None,
                             'atualizacao':'consulta periódica de status (não é push)'},
                            headers={'Cache-Control':'no-store'})

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
        request.session['customer_auth_version'] = 0
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
        request.session['customer_auth_version'] = int(user['sessao_versao'])
        flash(request, 'Bem-vindo de volta!', 'sucesso')
        return redirect('/minha-conta')

    @app.get('/conta/recuperar', response_class=HTMLResponse)
    def password_recovery_form(request: Request):
        return page(request, 'conta_recuperar.html', error=None, sent=False,
                    enabled=bool(testing or send_password_reset_email.configured()))

    @app.post('/conta/recuperar')
    async def password_recovery(request: Request):
        form = await valid_form(request)
        email = str(form.get('email', '')).strip().lower()[:200]
        enabled = bool(testing or send_password_reset_email.configured())
        if not enabled:
            return page(request, 'conta_recuperar.html', status_code=503,
                        error='O envio de e-mail não está configurado neste ambiente de demonstração.',
                        sent=False, enabled=False)
        # Resposta idêntica para endereços existentes e desconhecidos.
        with db_connect() as db:
            user = db.execute("SELECT id,email FROM usuarios WHERE email=? AND papel='cliente' AND ativo=1", (email,)).fetchone()
            if user:
                since = datetime.now(timezone.utc) - timedelta(minutes=15)
                recent = db.execute('''SELECT COUNT(*) FROM password_reset_tokens
                    WHERE usuario_id=? AND criado_em>=?''', (user['id'], since.isoformat())).fetchone()[0]
                if recent < 3:
                    token = secrets.token_urlsafe(32)
                    now = datetime.now(timezone.utc)
                    db.execute('''INSERT INTO password_reset_tokens(usuario_id,token_digest,expiracao_em,criado_em)
                        VALUES (?,?,?,?)''', (user['id'],make_reset_digest(token),
                                            (now+timedelta(minutes=30)).isoformat(),now.isoformat()))
                    if testing:
                        app.state.test_reset_links.append(f'http://testserver/conta/redefinir/{token}')
                    else:
                        try:
                            sent = send_password_reset_email(user['email'], token)
                        except Exception:
                            # Não expor detalhes de SMTP ou dados de conta no HTML.
                            sent = False
                        if not sent:
                            db.execute('UPDATE password_reset_tokens SET usado_em=? WHERE token_digest=?',
                                       (now.isoformat(),make_reset_digest(token)))
        return page(request, 'conta_recuperar.html', sent=True, enabled=enabled, error=None)

    def reset_token_user(db, token: str):
        if not re.fullmatch(r'[A-Za-z0-9_-]{32,128}', token):
            return None
        return db.execute('''SELECT t.id,t.usuario_id FROM password_reset_tokens t
                JOIN usuarios u ON u.id=t.usuario_id
                WHERE t.token_digest=? AND t.usado_em IS NULL AND t.expiracao_em>?
                AND u.ativo=1 AND u.papel='cliente' ''',
                (make_reset_digest(token), datetime.now(timezone.utc).isoformat())).fetchone()

    @app.get('/conta/redefinir/{token}', response_class=HTMLResponse)
    def password_reset_form(request: Request, token: str):
        with db_connect() as db:
            valid = bool(reset_token_user(db, token))
        response = page(request, 'conta_redefinir.html', token=token if valid else '', valid=valid,
                        error=None)
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Referrer-Policy'] = 'no-referrer'
        return response

    @app.post('/conta/redefinir/{token}')
    async def password_reset(request: Request, token: str):
        form = await valid_form(request)
        password = str(form.get('senha', ''))
        confirmation = str(form.get('confirmar', ''))
        if not (12 <= len(password) <= 128) or password != confirmation:
            return page(request, 'conta_redefinir.html', status_code=422, token=token,
                        valid=True, error='Informe duas senhas idênticas de 12 a 128 caracteres.')
        with db_connect() as db:
            db.execute('BEGIN IMMEDIATE')
            record = reset_token_user(db, token)
            if not record:
                return page(request, 'conta_redefinir.html', status_code=422,
                            token='', valid=False, error='Link inválido, expirado ou já utilizado.')
            now = datetime.now(timezone.utc).isoformat()
            db.execute('UPDATE usuarios SET senha_hash=?,sessao_versao=sessao_versao+1 WHERE id=?',
                       (hash_password(password), record['usuario_id']))
            db.execute('''UPDATE password_reset_tokens SET usado_em=?
                WHERE usuario_id=? AND usado_em IS NULL''', (now,record['usuario_id']))
            db.execute("INSERT INTO auditoria(usuario_id,entidade,entidade_id,acao) VALUES (?,'usuarios',?,'redefinir senha')",
                       (record['usuario_id'], record['usuario_id']))
        request.session.pop('customer_id', None)
        request.session.pop('customer_auth_version', None)
        flash(request, 'Senha redefinida. Entre novamente.', 'sucesso')
        return redirect('/conta/entrar')

    @app.post('/conta/sair')
    async def customer_logout(request: Request):
        await valid_form(request)
        request.session.pop('customer_id', None)
        request.session.pop('customer_auth_version', None)
        flash(request, 'Você saiu da sua conta.', 'info')
        return redirect('/')

    @app.get('/minha-conta', response_class=HTMLResponse)
    def my_account(request: Request):
        user = require_customer(request)
        with db_connect() as db:
            orders = db.execute('''SELECT p.*,o.descricao entrega FROM pedidos p
                JOIN opcoes_entrega o ON o.id=p.opcao_entrega_id
                WHERE p.usuario_id=? ORDER BY p.id DESC LIMIT 100''', (user['id'],)).fetchall()
            alerts = user_notifications(db, user['id'])
        return page(request, 'minha_conta.html', orders=orders, user=user, alerts=alerts)

    @app.post('/minha-conta/notificacoes/ler')
    async def customer_read_notifications(request: Request):
        user = require_customer(request)
        await valid_form(request)
        with db_connect() as db:
            mark_user_notifications_read(db, user['id'])
        return redirect('/minha-conta')

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
        admin_user=admin_id(request)
        with db_connect() as db:
            stats = {'pedidos': db.execute('SELECT COUNT(*) FROM pedidos').fetchone()[0],
                     'produtos': db.execute('SELECT COUNT(*) FROM cupcakes WHERE ativo=1').fetchone()[0],
                     'pendentes': db.execute("SELECT COUNT(*) FROM pedidos WHERE status IN ('recebido','confirmado','preparo')").fetchone()[0]}
            products = db.execute('''SELECT c.*,k.nome categoria FROM cupcakes c JOIN categorias k ON k.id=c.categoria_id
                                      WHERE c.excluido_em IS NULL ORDER BY c.ativo DESC,c.id''').fetchall()
            archived = db.execute('''SELECT id,nome,excluido_em FROM cupcakes WHERE excluido_em IS NOT NULL
                                     ORDER BY excluido_em DESC, id DESC LIMIT 100''').fetchall()
            orders = db.execute('SELECT * FROM pedidos ORDER BY id DESC LIMIT 6').fetchall()
            stats['avisos'] = db.execute('''SELECT COUNT(*) FROM notificacoes WHERE usuario_id=?
                              AND canal='app' AND status='pendente' ''',(admin_user,)).fetchone()[0]
        return page(request, 'admin.html', stats=stats, products=products, orders=orders, archived=archived)

    @app.get('/admin/produtos/novo', response_class=HTMLResponse)
    def new_product(request: Request):
        admin_id(request)
        with db_connect() as db:
            categories = db.execute('SELECT * FROM categorias ORDER BY id').fetchall()
        with db_connect() as db:
            allergens = db.execute('SELECT * FROM alergenos ORDER BY nome').fetchall()
        return page(request, 'admin_produto.html', product=None, categories=categories,
                    allergens=allergens, selected_allergens=[], error=None)

    @app.get('/admin/produtos/{product_id}/editar', response_class=HTMLResponse)
    def edit_product(request: Request, product_id: int):
        admin_id(request)
        with db_connect() as db:
            product = db.execute('SELECT * FROM cupcakes WHERE id=? AND excluido_em IS NULL', (product_id,)).fetchone()
            categories = db.execute('SELECT * FROM categorias ORDER BY id').fetchall()
        if not product:
            raise HTTPException(404, 'Produto não encontrado.')
        with db_connect() as db:
            allergens = db.execute('SELECT * FROM alergenos ORDER BY nome').fetchall()
            selected_allergens = [r[0] for r in db.execute(
                'SELECT alergeno_id FROM cupcake_alergenos WHERE cupcake_id=?',(product_id,)).fetchall()]
        return page(request, 'admin_produto.html', product=product, categories=categories,
                    allergens=allergens, selected_allergens=selected_allergens, error=None)

    @app.post('/admin/produtos/salvar')
    async def save_product(request: Request):
        user_id = admin_id(request)
        form = await valid_form(request)
        name = str(form.get('nome', '')).strip()[:100]
        description = str(form.get('descricao', '')).strip()[:500]
        nutrition = str(form.get('informacoes_nutricionais', '')).strip()[:1000]
        ingredients = str(form.get('ingredientes', '')).strip()[:800]
        try:
            selected = {int(aid) for aid in form.getlist('alergenos')}
        except ValueError:
            selected = {-1}
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
            allergens = db.execute('SELECT * FROM alergenos ORDER BY nome').fetchall()
            valid_allergens = {a['id'] for a in allergens}
            if not selected.issubset(valid_allergens):
                errors.append('Selecione apenas alergênicos cadastrados.')
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
                                  estoque=?,imagem_url=?,informacoes_nutricionais=?,ingredientes=? WHERE id=?''',
                               (category_id, name, description, price, stock, icon, nutrition or None,
                                ingredients or None, product_id))
                else:
                    before = None
                    cur = db.execute('''INSERT INTO cupcakes(categoria_id,nome,descricao,preco_centavos,estoque,
                                        imagem_url,informacoes_nutricionais,ingredientes) VALUES (?,?,?,?,?,?,?,?)''',
                                     (category_id, name, description, price, stock, icon, nutrition or None,
                                      ingredients or None))
                    product_id = cur.lastrowid
                before_allergens = {r[0] for r in db.execute(
                    'SELECT alergeno_id FROM cupcake_alergenos WHERE cupcake_id=?',(product_id,))}
                db.execute('DELETE FROM cupcake_alergenos WHERE cupcake_id=?', (product_id,))
                db.executemany('INSERT INTO cupcake_alergenos(cupcake_id,alergeno_id) VALUES (?,?)',
                               [(product_id, aid) for aid in sorted(selected)])
                after_row = db.execute('SELECT * FROM cupcakes WHERE id=?', (product_id,)).fetchone()
                after = snapshot_produto(after_row)
                if before_allergens != selected:
                    db.execute('INSERT INTO auditoria(usuario_id,entidade,entidade_id,acao,descricao) VALUES (?,?,?,?,?)',
                               (user_id,'cupcakes',product_id,'editar alergenicos',
                                json.dumps({'antes':sorted(before_allergens),'depois':sorted(selected)})))
                if before is None or before != after:
                    auditar_produto(db, user_id, product_id,
                                   'criar produto' if before is None else 'editar produto', before, after)
                if before is not None and before['estoque'] != after['estoque']:
                    db.execute('''INSERT INTO estoque_movimentos(cupcake_id,variacao,motivo) VALUES (?,?,?)''',
                               (product_id, after['estoque'] - before['estoque'],
                                'Ajuste manual pelo administrador'))
        if errors:
            return page(request, 'admin_produto.html', status_code=422, product=None,
                        categories=categories, allergens=allergens, selected_allergens=sorted(selected),
                        error=' '.join(errors), form_values=dict(form))
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
            orders = db.execute('''SELECT p.*, o.descricao entrega, j.inicio janela_inicio, j.fim janela_fim,
                              pg.metodo metodo_pagamento, pg.status status_pagamento
                       FROM pedidos p JOIN opcoes_entrega o ON o.id=p.opcao_entrega_id
                       LEFT JOIN janelas_entrega j ON j.id=p.janela_entrega_id
                       LEFT JOIN pagamentos pg ON pg.id=(SELECT MAX(id) FROM pagamentos WHERE pedido_id=p.id)
                       ORDER BY p.id DESC LIMIT 150''').fetchall()
        return page(request, 'admin_pedidos.html', orders=orders, next_status=NEXT_STATUS)

    @app.post('/admin/pedidos/{order_id}/status')
    async def update_status(request: Request, order_id: int):
        user_id = admin_id(request)
        form = await valid_form(request)
        target = str(form.get('status', '')).strip()
        eta_raw = str(form.get('previsao_entrega', '')).strip()
        eta_value = None
        if eta_raw:
            try:
                eta_value = datetime.strptime(eta_raw, '%Y-%m-%dT%H:%M').isoformat(timespec='minutes')
            except ValueError:
                raise HTTPException(422, 'Previsão de entrega inválida.') from None
        with db_connect() as db:
            db.execute('BEGIN IMMEDIATE')
            order = db.execute('SELECT * FROM pedidos WHERE id=?', (order_id,)).fetchone()
            if not order:
                raise HTTPException(404, 'Pedido não encontrado.')
            if target not in NEXT_STATUS.get(order['status'], []):
                raise HTTPException(422, 'Mudança de status não permitida.')
            payment = db.execute('''SELECT * FROM pagamentos WHERE pedido_id=? ORDER BY id DESC LIMIT 1''',
                                 (order_id,)).fetchone()
            if target == 'confirmado' and payment and payment['metodo'] in DEMO_METHODS and payment['status'] != 'aprovado':
                raise HTTPException(422, 'O pagamento demonstrativo precisa ser aprovado na simulação antes da confirmação do pedido.')
            if target == 'cancelado':
                restore_order_stock(db, order_id)
                if payment and payment['metodo'] in DEMO_METHODS and payment['status']=='aprovado':
                    db.execute("UPDATE pagamentos SET status='estornado',atualizado_em=CURRENT_TIMESTAMP WHERE id=?",
                               (payment['id'],))
                    log_payment_event(db, payment['id'], 'aprovado', 'estornado', 'cancelamento_administrativo_simulado')
            db.execute('''UPDATE pedidos SET status=?,
                          previsao_entrega_em=COALESCE(?,previsao_entrega_em) WHERE id=?''',
                       (target, eta_value, order_id))
            db.execute('INSERT INTO eventos_pedido(pedido_id,status,observacao) VALUES (?,?,?)',
                       (order_id, target, 'Atualizado pela administração'))
            notify_status_change(db, order_id, order['usuario_id'], target)
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
        start_date = str(form.get('valido_de','')).strip()
        end_date = str(form.get('valido_ate','')).strip()
        if not valid_dates(start_date,end_date):
            raise HTTPException(422,'Datas inválidas ou intervalo de validade invertido.')
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
            db.execute('''INSERT INTO cupons(codigo,tipo,valor,valor_minimo_centavos,limite_uso,
                         valido_de,valido_ate,ativo) VALUES (?,?,?,?,?,?,?,1)''',
                       (code,kind,amount,minimum,limit or None,start_date or None,end_date or None))
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
    def reports(request: Request, mes: str = '', categoria: str = ''):
        admin_id(request)
        if mes and not re.fullmatch(r'20\d\d-(0[1-9]|1[0-2])',mes):
            raise HTTPException(422, 'Mês inválido.')
        if categoria and (not categoria.isdigit() or len(categoria)>8):
            raise HTTPException(422, 'Categoria inválida.')
        try:
            with db_connect() as db:
                data = report_data(db, month=mes, category_id=int(categoria) if categoria else None)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from None
        return page(request,'admin_relatorios.html', **data, mes=mes, categoria=categoria)

    @app.get('/admin/entregas', response_class=HTMLResponse)
    def deliveries_admin(request: Request):
        admin_id(request)
        with db_connect() as db:
            options = db.execute('SELECT * FROM opcoes_entrega ORDER BY id').fetchall()
            regions = db.execute('SELECT * FROM regioes_entrega ORDER BY cep_inicio,id').fetchall()
            windows = db.execute('''SELECT j.*,o.descricao opcao FROM janelas_entrega j JOIN opcoes_entrega o
                             ON o.id=j.opcao_entrega_id ORDER BY j.opcao_entrega_id,j.inicio''').fetchall()
            blackouts = db.execute('''SELECT b.*,o.descricao opcao FROM agenda_bloqueios b JOIN opcoes_entrega o
                              ON b.opcao_entrega_id=o.id ORDER BY b.data''').fetchall()
        return page(request, 'admin_entregas.html', options=options, regions=regions,
                    windows=windows, blackouts=blackouts)

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
            target = db.execute('SELECT id,tipo,ativa FROM opcoes_entrega WHERE id=?',(delivery_id,)).fetchone()
            if not target: raise HTTPException(404, 'Modalidade não encontrada.')
            if not active and target['ativa'] and db.execute('SELECT COUNT(*) FROM opcoes_entrega WHERE ativa=1').fetchone()[0]<=1:
                flash(request, 'Mantenha pelo menos uma modalidade ativa.', 'erro')
                return redirect('/admin/entregas')
            if target['tipo']=='retirada':
                cost=0
            db.execute('UPDATE opcoes_entrega SET descricao=?,custo_base_centavos=?,ativa=? WHERE id=?',
                       (description,cost,int(active),delivery_id))
            db.execute("INSERT INTO auditoria(usuario_id,entidade,entidade_id,acao) VALUES (?,'opcoes_entrega',?,'editar')",(uid,delivery_id))
        flash(request, 'Modalidade de entrega salva.', 'sucesso')
        return redirect('/admin/entregas')

    @app.post('/admin/entregas/regioes/criar')
    async def admin_create_region(request: Request):
        uid = admin_id(request)
        f = await valid_form(request)
        description = str(f.get('descricao', '')).strip()[:100]
        try:
            start, end = cep_normalizado(f.get('cep_inicio','')), cep_normalizado(f.get('cep_fim',''))
            value = parse_brl(str(f.get('adicional','0')))
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from None
        if not description or start > end:
            raise HTTPException(422, 'Informe descrição e intervalo de CEP em ordem crescente.')
        with db_connect() as db:
            overlap = db.execute('''SELECT 1 FROM regioes_entrega WHERE ativa=1
                               AND cep_inicio<=? AND cep_fim>=? LIMIT 1''', (end,start)).fetchone()
            if overlap:
                raise HTTPException(422, 'Esta faixa se sobrepõe a outra região ativa.')
            cur = db.execute('''INSERT INTO regioes_entrega(descricao,cep_inicio,cep_fim,taxa_adicional_centavos)
                                VALUES (?,?,?,?)''', (description,start,end,value))
            db.execute("INSERT INTO auditoria(usuario_id,entidade,entidade_id,acao) VALUES (?,'regioes_entrega',?,'criar')",(uid,cur.lastrowid))
        flash(request, 'Região atendida cadastrada.', 'sucesso')
        return redirect('/admin/entregas')

    @app.post('/admin/entregas/regioes/{region_id}/alternar')
    async def admin_toggle_region(request: Request, region_id: int):
        uid = admin_id(request)
        await valid_form(request)
        with db_connect() as db:
            region = db.execute('SELECT * FROM regioes_entrega WHERE id=?',(region_id,)).fetchone()
            if not region: raise HTTPException(404, 'Região inexistente.')
            if not region['ativa']:
                overlap = db.execute('''SELECT 1 FROM regioes_entrega WHERE ativa=1 AND id<>?
                            AND cep_inicio<=? AND cep_fim>=?''', (region_id,region['cep_fim'],region['cep_inicio'])).fetchone()
                if overlap: raise HTTPException(422, 'Há sobreposição com uma região ativa.')
            db.execute('UPDATE regioes_entrega SET ativa=? WHERE id=?',(0 if region['ativa'] else 1,region_id))
            db.execute("INSERT INTO auditoria(usuario_id,entidade,entidade_id,acao) VALUES (?,'regioes_entrega',?,'alternar')",(uid,region_id))
        return redirect('/admin/entregas')

    @app.post('/admin/entregas/janelas/criar')
    async def admin_create_window(request: Request):
        uid=admin_id(request)
        f=await valid_form(request)
        try:
            option_id,capacity=int(f.get('opcao_entrega','0')),int(f.get('capacidade','0'))
        except (ValueError,TypeError):
            raise HTTPException(422, 'Modalidade ou capacidade inválida.')
        start,end=str(f.get('inicio','')).strip(),str(f.get('fim','')).strip()
        if not re.fullmatch(r'\d{2}:\d{2}',start) or not re.fullmatch(r'\d{2}:\d{2}',end) or not '00:00' <= start < end <= '23:59' or capacity < 1 or capacity > 999:
            raise HTTPException(422, 'Informe horário HH:MM e capacidade entre 1 e 999.')
        if int(start[:2])>23 or int(end[:2])>23 or int(start[3:])>59 or int(end[3:])>59:
            raise HTTPException(422, 'Hora fora do intervalo permitido.')
        with db_connect() as db:
            if not db.execute('SELECT 1 FROM opcoes_entrega WHERE id=?',(option_id,)).fetchone():
                raise HTTPException(422, 'Modalidade inexistente.')
            overlap=db.execute('''SELECT 1 FROM janelas_entrega WHERE opcao_entrega_id=?
                          AND inicio<? AND fim>?''',(option_id,end,start)).fetchone()
            if overlap: raise HTTPException(422,'Horário sobreposto a outra janela de atendimento.')
            cur=db.execute('''INSERT INTO janelas_entrega(opcao_entrega_id,inicio,fim,capacidade) VALUES (?,?,?,?)''',
                       (option_id,start,end,capacity))
            db.execute("INSERT INTO auditoria(usuario_id,entidade,entidade_id,acao) VALUES (?,'janelas_entrega',?,'criar')",(uid,cur.lastrowid))
        flash(request,'Horário de atendimento salvo.','sucesso')
        return redirect('/admin/entregas')

    @app.post('/admin/entregas/bloqueios/criar')
    async def admin_block_schedule(request: Request):
        uid=admin_id(request)
        f=await valid_form(request)
        try:
            option_id=int(f.get('opcao_entrega','0'))
            block_date=date.fromisoformat(str(f.get('data','')))
        except (ValueError,TypeError):
            raise HTTPException(422, 'Data ou modalidade inválida.')
        if block_date < date.today():
            raise HTTPException(422,'Não é permitido bloquear data passada.')
        with db_connect() as db:
            if not db.execute('SELECT 1 FROM opcoes_entrega WHERE id=?',(option_id,)).fetchone():
                raise HTTPException(422,'Modalidade inexistente.')
            try:
                cur=db.execute('INSERT INTO agenda_bloqueios(opcao_entrega_id,data,motivo) VALUES (?,?,?)',
                             (option_id,block_date.isoformat(),str(f.get('motivo','Fechado')).strip()[:150]))
            except sqlite3.IntegrityError:
                raise HTTPException(422,'Data já bloqueada para esta modalidade.') from None
            db.execute("INSERT INTO auditoria(usuario_id,entidade,entidade_id,acao) VALUES (?,'agenda_bloqueios',?,'criar')",(uid,cur.lastrowid))
        return redirect('/admin/entregas')

    @app.post('/admin/entregas/bloqueios/{block_id}/remover')
    async def admin_unblock_schedule(request: Request, block_id: int):
        uid=admin_id(request)
        await valid_form(request)
        with db_connect() as db:
            if not db.execute('SELECT 1 FROM agenda_bloqueios WHERE id=?',(block_id,)).fetchone():
                raise HTTPException(404,'Bloqueio não encontrado.')
            db.execute('DELETE FROM agenda_bloqueios WHERE id=?',(block_id,))
            db.execute("INSERT INTO auditoria(usuario_id,entidade,entidade_id,acao) VALUES (?,'agenda_bloqueios',?,'remover')",(uid,block_id))
        return redirect('/admin/entregas')

    @app.get('/admin/clientes', response_class=HTMLResponse)
    def admin_customers(request: Request):
        admin_id(request)
        with db_connect() as db:
            users = db.execute("SELECT id,nome,email,ativo,criado_em FROM usuarios WHERE papel='cliente' ORDER BY id DESC").fetchall()
        return page(request, 'admin_clientes.html', users=users)

    @app.get('/admin/clientes/{user_id}/editar', response_class=HTMLResponse)
    def admin_customer_edit(request: Request, user_id: int):
        admin_id(request)
        with db_connect() as db:
            user = db.execute("SELECT id,nome,email,ativo FROM usuarios WHERE id=? AND papel='cliente'",(user_id,)).fetchone()
            if not user: raise HTTPException(404,'Cliente não encontrado.')
        return page(request,'admin_cliente_editar.html',user=user,error=None)

    @app.post('/admin/clientes/{user_id}/salvar')
    async def admin_customer_save(request: Request, user_id: int):
        editor_id = admin_id(request)
        form = await valid_form(request)
        name = str(form.get('nome','')).strip()[:120]
        email = str(form.get('email','')).strip().lower()[:200]
        if len(name)<3 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email):
            raise HTTPException(422,'Nome ou e-mail inválido.')
        with db_connect() as db:
            db.execute('BEGIN IMMEDIATE')
            user = db.execute("SELECT id,nome,email,ativo FROM usuarios WHERE id=? AND papel='cliente'",(user_id,)).fetchone()
            if user is None: raise HTTPException(404,'Cliente não encontrado.')
            if db.execute('SELECT 1 FROM usuarios WHERE email=? AND id<>?',(email,user_id)).fetchone():
                raise HTTPException(422,'E-mail já utilizado por outra conta.')
            previous={'nome':user['nome'],'email':user['email']}
            db.execute("UPDATE usuarios SET nome=?,email=? WHERE id=? AND papel='cliente'",(name,email,user_id))
            detail=json.dumps({'antes':previous,'depois':{'nome':name,'email':email}},ensure_ascii=False)
            db.execute('''INSERT INTO auditoria(usuario_id,entidade,entidade_id,acao,descricao)
                VALUES (?,'usuarios',?,'editar cadastro',?)''',(editor_id,user_id,detail))
        flash(request,'Cadastro do cliente atualizado.','sucesso')
        return redirect('/admin/clientes')

    @app.get('/admin/clientes/{user_id}/historico', response_class=HTMLResponse)
    def admin_customer_history(request: Request, user_id: int):
        admin_id(request)
        with db_connect() as db:
            user=db.execute("SELECT id,nome,email FROM usuarios WHERE id=? AND papel='cliente'",(user_id,)).fetchone()
            if user is None: raise HTTPException(404,'Cliente não encontrado.')
            changes=db.execute('''SELECT a.acao,a.descricao,a.criado_em, u.nome autor
                 FROM auditoria a LEFT JOIN usuarios u ON u.id=a.usuario_id
                 WHERE a.entidade='usuarios' AND a.entidade_id=? ORDER BY a.id DESC LIMIT 100''',(user_id,)).fetchall()
        return page(request,'admin_cliente_historico.html',user=user,changes=changes)

    @app.post('/admin/clientes/{user_id}/alternar')
    async def toggle_customer(request: Request, user_id: int):
        uid = admin_id(request)
        await valid_form(request)
        with db_connect() as db:
            user = db.execute("SELECT ativo FROM usuarios WHERE id=? AND papel='cliente'",(user_id,)).fetchone()
            if not user: raise HTTPException(404, 'Conta não encontrada.')
            new_active=0 if user['ativo'] else 1
            db.execute('UPDATE usuarios SET ativo=? WHERE id=?', (new_active,user_id))
            db.execute('''INSERT INTO auditoria(usuario_id,entidade,entidade_id,acao,descricao)
                        VALUES (?,'usuarios',?,'alternar acesso',?)''',
                       (uid,user_id,f"ativo: {user['ativo']} -> {new_active}"))
        return redirect('/admin/clientes')

    @app.get('/admin/notificacoes', response_class=HTMLResponse)
    def admin_notifications(request: Request):
        admin_user=admin_id(request)
        with db_connect() as db:
            alerts=user_notifications(db,admin_user,limit=100)
        return page(request,'admin_notificacoes.html',alerts=alerts)

    @app.post('/admin/notificacoes/ler')
    async def admin_read_notifications(request: Request):
        admin_user=admin_id(request)
        await valid_form(request)
        with db_connect() as db:
            mark_user_notifications_read(db,admin_user)
        return redirect('/admin/notificacoes')

    @app.get('/saude')
    def health():
        return {'status': 'ok', 'servico': 'loja-cupcakes'}

    return app


app = create_app()
