@echo off
echo Installing dependencies for all services...

echo.
echo [1/5] Installing shared dependencies...
cd services\shared
pip install python-dotenv asyncpg pydantic

echo.
echo [2/5] Installing Application Service dependencies...
cd ..\application-service
pip install -r requirements.txt

echo.
echo [3/5] Installing Processing Service dependencies...
cd ..\processing-service
pip install -r requirements.txt

echo.
echo [4/5] Installing Approval Service dependencies...
cd ..\approval-service
pip install -r requirements.txt

echo.
echo [5/5] Installing API Gateway dependencies...
cd ..\api-gateway
pip install -r requirements.txt

cd ..\..
echo.
echo ====================================
echo All dependencies installed!
echo ====================================
pause
