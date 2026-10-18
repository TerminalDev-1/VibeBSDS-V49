@echo off
rem Starts the VibeBSDS V49 Brawl Stars game server on the home network.
rem The VibeBSDS-V49 Android app connects to this computer on port 9339.
rem Close this window or press Ctrl+C to stop the server.
title VibeBSDS V49 Brawl Stars server
cd /d "%~dp0"

rem Port 9339 is also used by other private servers (for example OpenMoco).
rem Only one can run at a time, so refuse to start if the port is taken.
netstat -ano -p tcp | findstr /r /c:":9339 .*LISTENING" >nul
if not errorlevel 1 (
    echo Port 9339 is already in use, so the VibeBSDS server was not started.
    echo Another server is running - often the OpenMoco server window.
    echo Close that server first, then run this again.
    pause
    exit /b 1
)

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found. Install Python 3 and try again.
    pause
    exit /b 1
)

echo Starting the VibeBSDS V49 Brawl Stars server on port 9339...
echo Open the VibeBSDS-V49 app on the tablet once it says it is listening.
python -u Core.py
echo.
echo The VibeBSDS server stopped.
pause
