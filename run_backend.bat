@echo off
cd /d %~dp0
call backend\venv\Scripts\activate.bat
cd backend
python manage.py runserver 127.0.0.1:8000
pause
