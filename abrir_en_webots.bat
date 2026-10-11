@echo off
title Simulacion Webots - Robot Limpiador Cienaga
echo =================================================================
echo   INICIANDO SIMULACION EN WEBOTS
echo   Proyecto: Robot Limpiador de Basura (Cienaga, Magdalena)
echo =================================================================
echo.

set "WEBOTS_EXE=C:\Program Files\Webots\msys64\mingw64\bin\webots.exe"
set "WORLD_PATH=%~dp0worlds\cienaga_limpiador.wbt"

if not exist "%WEBOTS_EXE%" (
    echo [ERROR] No se encontro Webots en %WEBOTS_EXE%
    echo Verifique la ruta de instalacion de Webots.
    pause
    exit /b 1
)

if not exist "%WORLD_PATH%" (
    echo [ERROR] No se encontro el archivo del mundo: %WORLD_PATH%
    pause
    exit /b 1
)

echo Abriendo mundo en Webots...
start "" "%WEBOTS_EXE%" "%WORLD_PATH%"
exit /b 0
