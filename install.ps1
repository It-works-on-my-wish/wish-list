Write-Host "Installing Backend Dependencies..." -ForegroundColor Cyan
Set-Location -Path "src\backend"
pip install -r requirements.txt
Set-Location -Path "..\.."

Write-Host "Installing Frontend Dependencies..." -ForegroundColor Cyan
Set-Location -Path "frontend"
npm install
Set-Location -Path ".."

Write-Host "Installation Complete!" -ForegroundColor Green
