@echo off
setlocal

:: Python commands
set PYTHON=python
set PIP=pip
set PYTEST=pytest
set VENV=.venv

:: Project settings
set REQUIREMENTS=requirements.txt
set MAIN=main.py
set TEST_DIR=tests
set SRC_DIR=src

:: Check for command
if "%1"=="" goto help
if "%1"=="install" goto install
if "%1"=="run" goto run
if "%1"=="test" goto test
if "%1"=="clean" goto clean
if "%1"=="dev-install" goto dev-install
if "%1"=="lint" goto lint
if "%1"=="format" goto format
if "%1"=="coverage" goto coverage
if "%1"=="backup" goto backup
if "%1"=="build" goto build
if "%1"=="build-debug" goto build-debug
if "%1"=="help" goto help

:install
echo Creating virtual environment...
%PYTHON% -m venv %VENV%
call %VENV%\Scripts\activate
echo Installing dependencies...
%PYTHON% -m pip install --upgrade pip
pip install -r %REQUIREMENTS%
echo Dependencies installed successfully!
goto end

:run
call %VENV%\Scripts\activate
echo Starting Password Manager...
%PYTHON% %MAIN%
goto end

:test
call %VENV%\Scripts\activate
echo Running tests...
%PYTHON% -m unittest discover %TEST_DIR%
goto end

:clean
echo Cleaning up...
if exist %VENV% rmdir /s /q %VENV%
if exist __pycache__ rmdir /s /q __pycache__
if exist .pytest_cache rmdir /s /q .pytest_cache
if exist .coverage del /f .coverage
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
for /r %%f in (*.pyc *.pyo *.pyd .coverage *.log) do @if exist "%%f" del /f "%%f"
echo Cleanup complete!
goto end

:dev-install
call :install
echo Installing development dependencies...
pip install black pylint pytest pytest-cov
echo Development dependencies installed!
goto end

:lint
call %VENV%\Scripts\activate
echo Running linting...
%PYTHON% -m pylint %SRC_DIR%
goto end

:format
call %VENV%\Scripts\activate
echo Formatting code...
%PYTHON% -m black %SRC_DIR% %TEST_DIR% %MAIN%
goto end

:coverage
call %VENV%\Scripts\activate
echo Running tests with coverage...
%PYTHON% -m pytest --cov=%SRC_DIR% %TEST_DIR% --cov-report=term-missing
goto end

:backup
echo Creating database backup...
if exist passwords.db (
    for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (
        set mydate=%%c-%%a-%%b
    )
    for /f "tokens=1-2 delims=: " %%a in ('time /t') do (
        set mytime=%%a%%b
    )
    copy passwords.db "passwords_backup_%mydate%_%mytime%.db"
) else (
    echo No database file found!
)
goto end

:build
call %VENV%\Scripts\activate
echo Building application...
pyinstaller --clean --onefile --windowed --name py-account-manager --add-data "src/gui/styles.py;src/gui" --icon=src/gui/assets/icon.ico main.py
echo Build complete! Check the dist folder for the executable.
goto end

:build-debug
call %VENV%\Scripts\activate
echo Building application in debug mode...
pyinstaller --clean --onefile --name py-account-manager-debug --add-data "src/gui/styles.py;src/gui" --icon=src/gui/assets/icon.ico main.py
echo Debug build complete! Check the dist folder for the executable.
goto end

:help
echo Available commands:
echo   make.bat install     - Install dependencies in a virtual environment
echo   make.bat run         - Run the Password Manager application
echo   make.bat test        - Run unit tests
echo   make.bat clean       - Clean up generated files and virtual environment
echo   make.bat dev-install - Install development dependencies
echo   make.bat lint        - Run linting checks
echo   make.bat format      - Format code using black
echo   make.bat coverage    - Run tests with coverage report
echo   make.bat backup      - Create a database backup
echo   make.bat build       - Build the application
echo   make.bat build-debug - Build the application in debug mode
echo   make.bat help        - Show this help message
goto end

:end
endlocal
