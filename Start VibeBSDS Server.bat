@echo off
rem Starts the VibeBSDS V49 Brawl Stars game server on the home network.
rem The port comes from "Port" in Configuration.py and must match the app's
rem redirectPort. Close this window or press Ctrl+C to stop the server.
title VibeBSDS V49 Brawl Stars server
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found. Install Python 3 and try again.
    pause
    exit /b 1
)

for /f %%p in ('python -c "import Configuration; print(Configuration.settings['Port'])"') do set "PORT=%%p"

rem Other private servers (for example OpenMoco) may use the same port.
rem Only one can listen on it, so refuse to start if the port is taken.
netstat -ano -p tcp | findstr /r /c:":%PORT% .*LISTENING" >nul
if not errorlevel 1 (
    echo Port %PORT% is already in use, so the VibeBSDS server was not started.
    echo Another server is running - often the OpenMoco server window.
    echo Close that server first, then run this again.
    pause
    exit /b 1
)

echo Starting the VibeBSDS V49 Brawl Stars server on port %PORT%...
echo Open the VibeBSDS-V49 app on the tablet once it says it is listening.
python -u Core.py
echo.
echo The VibeBSDS server stopped.
pause
