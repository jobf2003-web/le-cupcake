"""Recomendações e recuperação de senha, com limites explícitos de integração."""
from __future__ import annotations
from datetime import date
import hashlib
import os
import re
import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import urlparse


def make_reset_digest(token: str) -> str:
    return hashlib.sha256(token.encode('ascii')).hexdigest()


def valid_dates(start: str, end: str) -> bool:
    try:
        if (start and not re.fullmatch(r'\d{4}-\d{2}-\d{2}', start)) or (end and not re.fullmatch(r'\d{4}-\d{2}-\d{2}', end)):
            return False
        if start: date.fromisoformat(start)
        if end: date.fromisoformat(end)
        return not (start and end and start > end)
    except ValueError:
        return False


def email_configured() -> bool:
    base = os.getenv('PUBLIC_BASE_URL', '')
    parsed = urlparse(base)
    return (parsed.scheme == 'https' and bool(parsed.hostname) and not parsed.username
            and not parsed.password and bool(os.getenv('SMTP_HOST'))
            and bool(os.getenv('SMTP_FROM')))


def send_password_reset_email(recipient: str, token: str) -> bool:
    """SMTP STARTTLS obrigatório; sem config não há envio nem falsa confirmação."""
    if not email_configured():
        return False
    base = os.environ['PUBLIC_BASE_URL'].rstrip('/')
    host = os.environ['SMTP_HOST']
    port = int(os.getenv('SMTP_PORT', '587'))
    username = os.getenv('SMTP_USER', '')
    password = os.getenv('SMTP_PASSWORD', '')
    message = EmailMessage()
    message['Subject'] = 'Le Cupcake — redefinição de senha'
    message['From'] = os.environ['SMTP_FROM']
    message['To'] = recipient
    message.set_content('Se você solicitou, redefina sua senha nos próximos 30 minutos:\n'
                        + base + '/conta/redefinir/' + token
                        + '\nSe não solicitou, ignore esta mensagem.')
    with smtplib.SMTP(host, port, timeout=8) as server:
        server.starttls(context=ssl.create_default_context())
        if username:
            server.login(username, password)
        server.send_message(message)
    return True


send_password_reset_email.configured = email_configured


def get_recommendations(db, customer_id: int, limit: int = 3):
    """Categorias priorizadas por compras reais; não inclui indisponíveis."""
    history = db.execute('''SELECT categoria_id, SUM(volume) volume FROM (
        SELECT c.categoria_id, i.quantidade volume
          FROM pedidos p JOIN pedido_itens i ON i.pedido_id=p.id
          JOIN cupcakes c ON c.id=i.cupcake_id
         WHERE p.usuario_id=? AND p.status<>'cancelado'
        UNION ALL
        SELECT c.categoria_id, pc.quantidade volume
          FROM pedidos p JOIN pedido_itens i ON i.pedido_id=p.id
          JOIN pedido_combo_componentes pc ON pc.pedido_item_id=i.id
          JOIN cupcakes c ON c.id=pc.cupcake_id
         WHERE p.usuario_id=? AND p.status<>'cancelado'
        ) historico
        GROUP BY categoria_id ORDER BY volume DESC, categoria_id''', (customer_id,customer_id)).fetchall()
    if not history:
        return []
    categories = [int(r['categoria_id']) for r in history]
    placeholders = ','.join('?' for _ in categories)
    # CASE tem apenas inteiros oriundos do próprio banco; todos os parâmetros externos são vinculados.
    priority = ' '.join(f'WHEN {cat} THEN {position}' for position,cat in enumerate(categories))
    sql = f'''SELECT id,nome,imagem_url,preco_centavos FROM cupcakes
        WHERE ativo=1 AND excluido_em IS NULL AND estoque>0
        ORDER BY CASE WHEN categoria_id IN ({placeholders}) THEN 0 ELSE 1 END,
        CASE categoria_id {priority} ELSE 999 END, id LIMIT ?'''
    return db.execute(sql, categories+[limit]).fetchall()


def active_promotions(db):
    today = date.today().isoformat()
    return db.execute('''SELECT c.codigo,c.tipo,c.valor,c.valor_minimo_centavos,c.valido_ate
            FROM cupons c WHERE c.ativo=1
             AND (c.valido_de IS NULL OR c.valido_de<=?)
             AND (c.valido_ate IS NULL OR c.valido_ate>=?)
             AND (c.limite_uso IS NULL OR (SELECT COUNT(*) FROM cupom_utilizacoes u WHERE u.cupom_id=c.id)<c.limite_uso)
            ORDER BY c.id DESC LIMIT 6''',(today,today)).fetchall()
