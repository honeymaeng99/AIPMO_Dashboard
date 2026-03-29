@echo off
set PATH=%PATH%;C:\Program Files\nodejs

echo ============================================
echo   MTC AI 과제 관리 플랫폼 (Vue 버전) 시작
echo ============================================
echo.

echo [1/2] Vue 프론트엔드 빌드 중...
cd /d "%~dp0frontend"
call npm run build
echo.

echo [2/2] FastAPI 서버 시작 중...
cd /d "%~dp0backend"
call venv\Scripts\python.exe server.py

pause
