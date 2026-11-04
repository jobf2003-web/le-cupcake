"""Início simplificado da aplicação localmente.

Lê .env do diretório atual sem instalar uma biblioteca adicional.
"""
import os
from pathlib import Path
import uvicorn

HERE = Path(__file__).resolve().parent
config = HERE / '.env'
if config.exists():
    for raw_line in config.read_text(encoding='utf-8-sig').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key in {'SECRET_KEY', 'ADMIN_EMAIL', 'ADMIN_PASSWORD', 'DATABASE_PATH', 'COOKIE_SECURE'} and value:
            os.environ.setdefault(key, value)

if __name__ == '__main__':
    print('Loja de cupcakes disponível em http://127.0.0.1:8000')
    print('Para interromper o servidor, pressione Ctrl+C.')
    uvicorn.run('app:app', host='127.0.0.1', port=8000, reload=False, log_level='info')
