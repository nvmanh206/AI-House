@echo off
cd /d "%~dp0"
docker info >nul 2>&1
if errorlevel 1 exit /b 1
docker compose up -d --build --wait
if errorlevel 1 exit /b 1
docker compose ps
echo App: http://localhost:3000 - Register your own first administrator account.
echo pgAdmin: http://localhost:5050 - See DOCKER_GUIDE.md for local credentials.
