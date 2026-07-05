@echo off
REM ============================================================
REM  VLM Document Extraction API - Click dup la chay demo
REM  API Swagger:   http://localhost:8000/docs
REM  Streamlit UI:  http://localhost:8505
REM ============================================================

set PYTHON=C:\Users\LENOVO\AppData\Local\Programs\Python\Python313\python.exe
set STREAMLIT=C:\Users\LENOVO\AppData\Local\Programs\Python\Python313\Scripts\streamlit.exe
set APP_DIR=%~dp0

echo ============================================================
echo   VLM Document Extraction API Demo
echo ============================================================
echo.

echo [1/3] Khoi dong FastAPI backend (port 8000)...
cd /d "%APP_DIR%"
start "VLM API :8000" cmd /k "cd /d %APP_DIR% && "%PYTHON%" -m uvicorn app.main:app --port 8000"

echo     ... cho API khoi dong 3 giay...
timeout /t 3 /nobreak >nul

echo [2/3] Mo browser...
start "" http://localhost:8505

echo [3/3] Khoi dong Streamlit UI (port 8505)...
cd /d "%APP_DIR%"
start "VLM UI :8505" cmd /k "cd /d %APP_DIR% && "%STREAMLIT%" run ui.py --server.port 8505"

echo.
echo ============================================================
echo  XONG! Demo:
echo    Streamlit UI:  http://localhost:8505
echo    Swagger API:   http://localhost:8000/docs
echo  Dong cua so thi service tat.
echo ============================================================
pause
