@echo off

echo Creating virtual environment...
python -m venv .venv

echo Activating virtual environment...
call .venv\Scripts\activate

echo Installing requirements...
pip install -r requirements.txt

echo Creating folders...
python setup_folders.py

echo Setup complete.

pause