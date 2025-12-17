@echo off
echo ====================================
echo Starting Loan Application Microservices
echo ====================================

echo.
echo Starting Application Service (Port 8001)...
start "Application Service" cmd /k "cd services\application-service && python main.py"

timeout /t 3 /nobreak > nul

echo Starting Processing Service (Port 8002)...
start "Processing Service" cmd /k "cd services\processing-service && python main.py"

timeout /t 3 /nobreak > nul

echo Starting Approval Service (Port 8003)...
start "Approval Service" cmd /k "cd services\approval-service && python main.py"

timeout /t 3 /nobreak > nul

echo Starting API Gateway (Port 8000)...
start "API Gateway" cmd /k "cd services\api-gateway && python main.py"

echo.
echo ====================================
echo All services started!
echo ====================================
echo.
echo API Gateway:          http://localhost:8000
echo Application Service:  http://localhost:8001
echo Processing Service:   http://localhost:8002
echo Approval Service:     http://localhost:8003
echo.
echo API Documentation:    http://localhost:8000/docs
echo.
pause
