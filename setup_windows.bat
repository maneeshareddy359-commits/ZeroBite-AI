@echo off
setlocal
cd /d %~dp0
if not exist backend\venv python -m venv backend\venv
call backend\venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
if not exist backend\.env copy backend\.env.example backend\.env
cd backend
python manage.py makemigrations users donations
python manage.py migrate
python ml\train_model.py
python ml\expiry_model.py
python manage.py seed_demo
start "ZeroBite Backend" cmd /k "python manage.py runserver 127.0.0.1:8000"
cd ..\frontend
call npm install
start "ZeroBite Frontend" cmd /k "npm run dev"
echo.
echo ZeroBite is starting. Open http://localhost:5173
pause
