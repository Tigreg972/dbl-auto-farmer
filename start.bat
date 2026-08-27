@echo off
chcp 65001 >nul
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
echo  [1] Installer / mettre à jour les dépendances
echo  [2] Calibrer les boutons de l'interface
echo  [3] Test sans clic - détection uniquement
echo  [4] Lancer le bot
echo  [5] Lancer les tests
echo  [6] Afficher les captures obligatoires manquantes
echo  [7] Quitter
echo.
set /p choice=Choix (1-7) : 

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
