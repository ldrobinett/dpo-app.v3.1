# ---- DEV STARTUP SCRIPT ----

Write-Host "Starting development environment..." -ForegroundColor Cyan

# Activate virtual environment (create if missing)
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
} else {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
}

# Dev-only encryption key (LOCAL ONLY)
#if (-not $env:STORE_PASSWORD_ENCRYPTION_KEY) {
    #$env:STORE_PASSWORD_ENCRYPTION_KEY = "1234"
#}

# Set Flask environment variables
$env:FLASK_APP="app:create_app"
$env:FLASK_ENV="development"

# Switch to dev branch
Write-Host "Switching to dev branch..." -ForegroundColor Yellow
git checkout dev

# Pull latest changes
Write-Host "Pulling latest changes from origin/dev..." -ForegroundColor Yellow
git pull origin dev

# Show migration state
Write-Host "Current migration head:" -ForegroundColor Yellow
flask db current

Write-Host "Development environment ready." -ForegroundColor Green
Write-Host "Run 'flask run' when ready." -ForegroundColor Cyan