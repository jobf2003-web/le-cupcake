@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Preparando ambiente Python...
  py -3 -m venv .venv
  if errorlevel 1 (
    echo Nao foi possivel criar o ambiente. Instale o Python 3.11 ou superior.
    pause
    exit /b 1
  )
)
echo Instalando dependencias, se necessario...
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
  echo Verifique sua conexao com a internet e tente novamente.
  pause
  exit /b 1
)
if not exist .env copy .env.example .env >nul
echo.
echo Abrindo o servidor da loja (modo local).
echo Acesse http://127.0.0.1:8000 no navegador.
echo Para habilitar o painel administrativo, edite ADMIN_EMAIL e ADMIN_PASSWORD no arquivo .env.
.venv\Scripts\python.exe iniciar.py
pause
