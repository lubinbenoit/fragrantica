@echo off
REM run.bat - Lancer les scrapers

call venv\Scripts\activate.bat
python run_scrapers.py %*