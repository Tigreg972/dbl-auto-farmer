@echo off
setlocal
cd /d "%~dp0"
set PYTHONPATH=%~dp0src

if not "%~1"=="" (
    python app.py %*
    exit /b %errorlevel%
)

:menu
cls
echo ========================================
echo   DBL Auto Farmer - BlueStacks 5
echo ========================================
echo.
echo  [1] Install / update dependencies
echo  [2] Calibrate UI templates
echo  [3] Dry run - detect only, no clicks
echo  [4] Launch live bot
echo  [5] Run tests
echo  [6] Show missing required templates
echo  [7] Quit
echo.
set /p choice=Choice (1-7): 

if "%choice%"=="1" goto install
if "%choice%"=="2" goto calibrate
if "%choice%"=="3" goto dryrun
if "%choice%"=="4" goto live
if "%choice%"=="5" goto tests
if "%choice%"=="6" goto missing
if "%choice%"=="7" goto done
goto menu

:install
python -m pip install -r requirements.txt
pause
goto menu

:calibrate
python tools\calibrate.py
pause
goto menu

:dryrun
python app.py --dry-run
pause
goto menu

:live
python app.py
pause
goto menu

:tests
python -m pytest -q
pause
goto menu

:missing
python tools\calibrate.py --list --required-only
pause
goto menu

:done
endlocal
