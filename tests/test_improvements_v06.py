"""Verificações dos ajustes de clareza e acessibilidade da interface v0.6."""
import re
import pytest
from fastapi.testclient import TestClient
from app import create_app

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_EMAIL", "admin@doce.test")
    monkeypatch.setenv("ADMIN_PASSWORD", "SenhaUltraForte123!")
    return TestClient(create_app(tmp_path / "loja.db", testing=True))

def token(client, path="/"):
    page = client.get(path)
    assert page.status_code == 200
    return re.search(r'name="_csrf" value="([^"]+)"', page.text).group(1)

def test_shortcut_and_visual_style_remain_available(client):
    page = client.get("/")
    assert page.status_code == 200
    assert "Pular para o conteúdo principal" in page.text
    assert 'id="conteudo" tabindex="-1"' in page.text
    assert "?v=0.6" in page.text
    assert "Chocolate da Casa" in page.text
    css = client.get("/static/style.css").text
    assert "#3D634D" in css and "#B45C3C" in css
    assert ".skip-link:focus" in css
    assert "prefers-reduced-motion:reduce" in css

def test_checkout_delivery_guidance_and_readable_error(client):
    csrf = token(client)
    assert client.post("/carrinho/adicionar", data={
        "_csrf": csrf, "produto_id": "1", "quantidade": "1"
    }, follow_redirects=False).status_code == 303
    checkout = client.get("/checkout")
    assert checkout.status_code == 200
    assert 'id="delivery-guidance"' in checkout.text
    assert 'aria-live="polite"' in checkout.text
    assert 'aria-describedby="address-tip"' in checkout.text
    assert "Informe rua, número, bairro e cidade." in checkout.text
    csrf = token(client, "/checkout")
    bad = client.post("/checkout", data={
        "_csrf": csrf, "nome": "A", "email": "incorreto",
        "telefone": "00", "opcao_entrega": "2", "endereco": ""
    })
    assert bad.status_code == 422
    assert 'id="checkout-errors"' in bad.text
    assert 'role="alert" tabindex="-1"' in bad.text
    assert "Informe o endereço completo" in bad.text

def test_photo_fallback_behavior_is_present_and_original_urls_preserved(client):
    page = client.get("/").text
    assert 'class="product-photo"' in page
    assert "Cupcake Chocolate da Casa" in page
    js = client.get("/static/app.js")
    assert js.status_code == 200
    assert "photo.addEventListener('error', showFallback" in js.text
    assert "photo.replaceWith(fallback)" in js.text
    assert "photo.classList.contains('admin-thumb')" in js.text
