@echo off

REM Activate the virtual environment (using relative path)
call %~dp0\venv\Scripts\activate.bat

REM Run your Python script (using relative path)
python %~dp0\main.py

REM Pause to view any potential errors
pause
