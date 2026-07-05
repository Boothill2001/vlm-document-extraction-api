@echo off
REM ============================================================
REM  VLM Document Extraction API - Click dup la chay demo
REM  Swagger UI: http://localhost:8000/docs
REM ============================================================

set PYTHON=C:\Users\LENOVO\AppData\Local\Programs\Python\Python313\python.exe
set APP_DIR=%~dp0

echo ============================================================
echo   VLM Document Extraction API Demo
echo ============================================================
echo.

echo [1/2] Mo browser Swagger UI...
timeout /t 3 /nobreak >nul
start "" http://localhost:8000/docs

echo [2/2] Khoi dong FastAPI server...
cd /d "%APP_DIR%"
"%PYTHON%" -m uvicorn app.main:app --port 8000 --reload

pause
