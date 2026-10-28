@echo off
setlocal

:: Obtener el directorio actual donde se encuentra este script (bin\)
set "SCRIPT_DIR=%~dp0"

:: Quitar la barra diagonal final si la hubiera para que dirname/padre funcione bien
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: LARIMAR_HOME es el directorio padre de bin\
for %%I in ("%SCRIPT_DIR%") do set "LARIMAR_HOME=%%~dpI"
if "%LARIMAR_HOME:~-1%"=="\" set "LARIMAR_HOME=%LARIMAR_HOME:~0,-1%"
set "LARIMAR_HOME=%LARIMAR_HOME%"

:: Ejecutar el compilador (larimarc.exe) pasando todos los argumentos recibidos (%*)
"%SCRIPT_DIR%\larimarc.exe" %*