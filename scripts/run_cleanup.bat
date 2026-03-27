@echo off
REM ============================================================
REM Play Insights - Cleanup Database Script
REM Carrega variaveis de ambiente e executa o cleanup
REM ============================================================

REM Mudar para o diretorio do projeto
cd /d "%~dp0.."

REM Carrega .env
for /F "usebackq tokens=*" %%i in (.env) do @set %%i

REM Executar o script de cleanup
python scripts/cleanup_database.py %*

exit /b %ERRORLEVEL%
