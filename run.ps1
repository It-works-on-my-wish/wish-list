Write-Host "Starting Wishlist Project..." -ForegroundColor Green

Write-Host "Starting Backend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { cd src\backend; python -m uvicorn app.main:app --reload --port 8000 }"

Write-Host "Starting Frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { cd frontend; npm run dev }"

Write-Host "Both services have been started in new windows!" -ForegroundColor Green

Write-Host "Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 4

Write-Host "Opening browser with default test user (test@example.com)..." -ForegroundColor Green
Start-Process "http://localhost:5173"

Write-Host "Please check the newly opened PowerShell windows for logs." -ForegroundColor Yellow
