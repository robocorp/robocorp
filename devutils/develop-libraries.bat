@echo off
pushd .

SET scriptPath=%~dp0
SET scriptPath=%scriptPath:~0,-1%
cd /D %scriptPath%

:: Get RCC
IF NOT EXIST ".\rcc.exe" (
    curl -o rcc.exe https://downloads.robocorp.com/rcc/releases/latest/windows64/rcc.exe --fail || goto :error
)

:: Go to repo root
cd ..

:: Check if .venv folder exists
IF EXIST ".\venv" (
    echo Detected existing developement environment.
    echo Do you want to create a clean environment? [Y/N]
    choice /C YN /N /M "Select Y for Yes (clean environment) or N for No (use existing):"
    IF ERRORLEVEL 2 GOTO USE_EXISTING
)

rcc venv dev-env-libraries.yaml -s dev-library-env --force

::INSTALL_DEPENDENCIES
call .\venv\Scripts\activate.bat

pip install poetry==1.7 invoke==2.2

:: Start VS Code 
code .

goto end

:USE_EXISTING
echo Using existing environment.
call .\venv\Scripts\activate.bat
code .

goto end

:error
echo.
echo Developement environment setup failed.

:end
pause
popd
