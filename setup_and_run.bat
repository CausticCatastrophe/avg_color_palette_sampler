@echo off
SETLOCAL

REM Set up variables
SET VENV_DIR=venv
SET REQUIREMENTS=%~dp0requirements.txt
SET MINICONDA_URL=https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe
SET MINICONDA_INSTALLER=Miniconda3-latest-Windows-x86_64.exe
SET MINICONDA_DIR=%~dp0\miniconda3
SET TEMP_DIR=%TEMP%\miniconda_install

REM Store the current directory
SET SCRIPT_DIR=%~dp0

REM Remove trailing backslash from SCRIPT_DIR if it exists
SET SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

REM Change to the script directory
CD /D %SCRIPT_DIR%

REM Check if the virtual environment already exists
IF EXIST %VENV_DIR% (
    echo Virtual environment already exists. Activating it...
    CALL %MINICONDA_DIR%\Scripts\activate.bat %SCRIPT_DIR%\%VENV_DIR%
) ELSE (
    REM Check if Miniconda is installed locally
    IF NOT EXIST %MINICONDA_DIR% (
        echo Miniconda is not installed locally. Downloading Miniconda installer...
        mkdir %TEMP_DIR%
        powershell -Command "Invoke-WebRequest -Uri %MINICONDA_URL% -OutFile %TEMP_DIR%\%MINICONDA_INSTALLER%"
        echo Installing Miniconda...
        start /wait "" %TEMP_DIR%\%MINICONDA_INSTALLER% /InstallationType=JustMe /RegisterPython=0 /AddToPath=0 /S /D=%MINICONDA_DIR%
        echo Miniconda installed successfully.
        DEL %TEMP_DIR%\%MINICONDA_INSTALLER%
        rmdir %TEMP_DIR%
    )

    REM Initialize Conda for the current session
    CALL "%MINICONDA_DIR%\Scripts\activate.bat" ""

    REM Create virtual environment
    echo Creating virtual environment...
    conda create --yes --prefix "%SCRIPT_DIR%\%VENV_DIR%" python=3.12
    IF ERRORLEVEL 1 (
        echo Failed to create the virtual environment.
        EXIT /B 1
    )

    REM Activate virtual environment
    CALL %MINICONDA_DIR%\Scripts\activate.bat "%SCRIPT_DIR%\%VENV_DIR%"
    IF ERRORLEVEL 1 (
        echo Failed to activate the virtual environment.
        EXIT /B 1
    )

    REM Install required packages
    IF EXIST %REQUIREMENTS% (
        echo Installing required packages from %REQUIREMENTS%...
        pip install -r %REQUIREMENTS% --log pip_install.log
        IF ERRORLEVEL 1 (
            echo Failed to install required packages. Check pip_install.log for details.
            EXIT /B 1
        )
    ) ELSE (
        echo %REQUIREMENTS% not found. Exiting...
        EXIT /B 1
    )
)

REM Run the Python script
echo Running the application...
start /min "" python %SCRIPT_DIR%\avg_color_palette_sampler.py

REM Check if the deactivate.bat file exists before calling it
IF EXIST %MINICONDA_DIR%\Scripts\deactivate.bat (
    REM Deactivate virtual environment
    CALL %MINICONDA_DIR%\Scripts\deactivate.bat
    IF ERRORLEVEL 1 (
        echo Failed to deactivate the virtual environment.
        EXIT /B 1
    )
) ELSE (
    echo deactivate.bat not found. Skipping deactivation...
)

ENDLOCAL
exit /b
