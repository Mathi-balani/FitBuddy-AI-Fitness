@echo off
echo ==========================================
echo FitBuddy - Windows Setup
echo ==========================================
py -m venv venv
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt
if not exist .env copy .env.example .env
echo.
echo Setup complete.
echo Optional: Open .env and add a Gemini API key for AI-generated plans.
echo The app also works without a key using its built-in plan generator.
echo Run:
echo venv\Scripts\python.exe -m uvicorn app.main:app --reload
pause
