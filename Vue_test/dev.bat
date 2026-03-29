@echo off
set PATH=%PATH%;C:\Program Files\nodejs

echo ============================================
echo   MTC AI 과제 관리 플랫폼 (개발 모드)
echo ============================================
echo.

echo 백엔드 서버를 시작합니다...
cd /d "%~dp0backend"
start "Backend" cmd /k "set PATH=%PATH%;C:\Program Files\nodejs && venv\Scripts\python.exe server.py"

timeout /t 2 /nobreak > nul

echo 프론트엔드 개발 서버를 시작합니다...
cd /d "%~dp0frontend"
start "Frontend" cmd /k "set PATH=%PATH%;C:\Program Files\nodejs && npm run dev"

echo.
echo   백엔드: http://localhost:8000
echo   프론트엔드: http://localhost:5173
echo.
echo 브라우저에서 http://localhost:5173 으로 접속하세요.
pause
