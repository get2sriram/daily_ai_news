# Start Backend in a new window
Write-Host "Starting Backend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python main.py"

# Start Frontend in a new window
Write-Host "Starting Frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "Both servers are starting in separate windows." -ForegroundColor Yellow
Write-Host "Backend: http://localhost:8000"
Write-Host "Frontend: Check the frontend window for the Vite URL"
